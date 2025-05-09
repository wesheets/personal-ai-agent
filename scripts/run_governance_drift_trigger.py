#!/usr/bin/env python3

import os
import json
import uuid
from datetime import datetime, timezone

PROJECT_ROOT = "/home/ubuntu/personal-ai-agent"
ALIGNMENT_LOG_PATH = os.path.join(PROJECT_ROOT, "app/logs/governance_value_alignment_log.json")
RESPONSE_LOG_PATH = os.path.join(PROJECT_ROOT, "app/logs/governance_drift_response_log.json")
# RESPONSE_LOG_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "app/schemas/governance_drift_response_log.schema.json") # Schema path for reference if needed by other tools

# Configurable Parameters
DEFAULT_ALIGNMENT_SCORE_THRESHOLD = 0.7 # Trigger response if score is below this
CRITICAL_ALIGNMENT_SCORE_THRESHOLD = 0.3 # For more severe escalation
VALID_RESPONSE_ACTIONS = ["escalate_to_operator", "reset_emotion_state", "reweight_beliefs", "schedule_plan_retry"]

def load_json_file(file_path):
    """Loads and parses a JSON file. Returns (data, error_message_or_None)."""
    if not os.path.exists(file_path):
        return None, f"File not found: {file_path}"
    if os.path.getsize(file_path) == 0:
        return [], None # Treat empty file as an empty list of entries
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"JSONDecodeError in {file_path}: {e}"
    except Exception as e:
        return None, f"Error loading {file_path}: {e}"

def identify_drift(alignment_entry, score_threshold):
    """Identifies if an alignment entry signifies drift.
    Returns (is_drift_bool, drift_details_dict).
    """
    is_drift = False
    misalignments = alignment_entry.get("misalignments", [])
    alignment_score = alignment_entry.get("alignment_score")

    drift_details = {
        "alignment_score_at_detection": alignment_score,
        "misalignment_count": len(misalignments),
        "misalignment_severities": [m.get("severity", "unknown").lower() for m in misalignments]
    }

    if misalignments: # Any misalignment is a potential drift
        is_drift = True
    
    if isinstance(alignment_score, (int, float)) and alignment_score < score_threshold:
        is_drift = True
        
    # If alignment_score is "N/A - No decision data" or similar, it's a critical issue already
    if isinstance(alignment_score, str) and "N/A" in alignment_score:
        is_drift = True # This is a form of drift (data availability issue)
        # Ensure severities reflect this if not already in misalignments
        if not any(s == "critical" for s in drift_details["misalignment_severities"]):
             # Often, an N/A score comes with a critical misalignment about missing data.
             # If not, we can infer one for action selection.
             pass # The misalignment should already exist from Batch 28.1 logic

    return is_drift, drift_details

def select_response_action(alignment_entry, drift_details):
    """Selects a response action based on the drift details.
    Returns (selected_action_str, rationale_str, action_details_dict).
    """
    alignment_score = drift_details["alignment_score_at_detection"]
    misalignment_severities = drift_details["misalignment_severities"]
    misalignments = alignment_entry.get("misalignments", [])
    action_details = {"triggering_misalignment_ids": [m.get("misalignment_id") for m in misalignments if m.get("misalignment_id")]}

    # Rule 1: Critical issues or very low score
    if "critical" in misalignment_severities or (isinstance(alignment_score, (int, float)) and alignment_score < CRITICAL_ALIGNMENT_SCORE_THRESHOLD) or (isinstance(alignment_score, str) and "N/A" in alignment_score):
        return "escalate_to_operator", "Critical misalignment(s) detected, data unavailability, or extremely low alignment score requiring immediate operator attention.", action_details

    # Rule 2: Emotion-specific severe misalignments
    emotion_misalignments_high = [m for m in misalignments if m.get("governance_surface_type") == "emotion_state" and m.get("severity", "").lower() == "high"]
    if emotion_misalignments_high:
        action_details["emotion_issues"] = [m.get("discrepancy_description") for m in emotion_misalignments_high]
        return "reset_emotion_state", "Significant emotional state misalignment (high severity) detected, attempting automated state reset.", action_details

    # Rule 3: Belief-specific severe misalignments
    belief_misalignments_high = [m for m in misalignments if m.get("governance_surface_type") == "beliefs" and m.get("severity", "").lower() == "high"]
    if belief_misalignments_high:
        action_details["belief_issues"] = [m.get("discrepancy_description") for m in belief_misalignments_high]
        return "reweight_beliefs", "Significant belief misalignment (high severity) detected, recommending belief re-evaluation.", action_details

    # Rule 4: Suboptimal plan due to trust/other moderate issues
    if isinstance(alignment_score, (int, float)) and alignment_score < DEFAULT_ALIGNMENT_SCORE_THRESHOLD:
        if any(s == "medium" for s in misalignment_severities):
            trust_issues = [m for m in misalignments if m.get("governance_surface_type") == "trust_score"]
            if trust_issues:
                action_details["trust_issues"] = [m.get("discrepancy_description") for m in trust_issues]
                return "schedule_plan_retry", "Suboptimal plan selection potentially linked to trust score issues and moderate governance misalignments; scheduling plan retry.", action_details
            return "schedule_plan_retry", "Suboptimal plan selection indicated by moderate governance misalignments and low score; scheduling plan retry.", action_details

    # Rule 5: General low score or multiple medium misalignments not caught above
    if ((isinstance(alignment_score, (int, float)) and alignment_score < DEFAULT_ALIGNMENT_SCORE_THRESHOLD) or
        len([s for s in misalignment_severities if s == "medium"]) > 1): # More than one medium severity issue
        return "escalate_to_operator", "Overall low governance alignment or multiple moderate issues detected, requiring operator review.", action_details

    # Fallback for any other drift detected (e.g., only low severity misalignments but still flagged by identify_drift)
    if drift_details["misalignment_count"] > 0:
        return "escalate_to_operator", "Minor governance misalignments detected, flagging for operator awareness.", action_details
        
    # Default if drift was identified by score alone without specific misalignments matching above rules
    if isinstance(alignment_score, (int, float)) and alignment_score < DEFAULT_ALIGNMENT_SCORE_THRESHOLD:
        return "escalate_to_operator", f"Alignment score ({alignment_score}) below threshold ({DEFAULT_ALIGNMENT_SCORE_THRESHOLD}), flagging for operator review.", action_details

    # Should not be reached if identify_drift returned True, but as a safeguard:
    return "escalate_to_operator", "Undefined drift condition detected, escalating for operator review.", action_details

def write_response_log(all_responses, output_path):
    """Writes the list of all_responses to the output_path as a JSON array."""
    try:
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")
        with open(output_path, "w") as f:
            json.dump(all_responses, f, indent=2)
        print(f"Successfully wrote {len(all_responses)} entries to {output_path}")
    except Exception as e:
        print(f"Error writing response log to {output_path}: {e}")

def process_alignment_log():
    """Main orchestrator function."""
    print(f"Loading alignment log from: {ALIGNMENT_LOG_PATH}")
    alignment_data, error = load_json_file(ALIGNMENT_LOG_PATH)

    if error:
        print(f"Error loading alignment log: {error}. Aborting.")
        return

    if not isinstance(alignment_data, list):
        print(f"Alignment log is not a list as expected. Found type: {type(alignment_data)}. Aborting.")
        return
    
    print(f"Loaded {len(alignment_data)} entries from alignment log.")
    all_responses = []

    for entry in alignment_data:
        if not isinstance(entry, dict):
            print(f"Skipping non-dictionary entry in alignment log: {type(entry)}")
            continue

        triggering_entry_id = entry.get("log_entry_id", "MISSING_ID_IN_ALIGNMENT_LOG")
        triggering_loop_id = entry.get("loop_id", "MISSING_LOOP_ID")

        is_drift, drift_details = identify_drift(entry, DEFAULT_ALIGNMENT_SCORE_THRESHOLD)

        if is_drift:
            print(f"Drift detected for loop_id: {triggering_loop_id} (entry_id: {triggering_entry_id})")
            action, rationale, action_details_dict = select_response_action(entry, drift_details)
            
            response_entry_data = {
                "response_id": str(uuid.uuid4()),
                "response_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "triggering_alignment_log_entry_id": triggering_entry_id,
                "triggering_loop_id": triggering_loop_id,
                "detected_drift_summary": drift_details,
                "selected_response_action": action,
                "response_rationale": rationale,
                "action_details": action_details_dict,
                "status": "logged" # Or "execution_simulated" as actual execution is out of scope
            }
            all_responses.append(response_entry_data)
        else:
            print(f"No significant drift detected for loop_id: {triggering_loop_id} (entry_id: {triggering_entry_id})")

    write_response_log(all_responses, RESPONSE_LOG_PATH)
    print(f"Processing complete. {len(all_responses)} responses logged.")

if __name__ == "__main__":
    print("Starting Governance Drift Suppression Trigger script...")
    process_alignment_log()
    print("Governance Drift Suppression Trigger script finished.")

