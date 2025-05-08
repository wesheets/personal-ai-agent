import json
import os
from datetime import datetime, timezone

# Define absolute paths
PROJECT_ROOT = "/home/ubuntu/personal-ai-agent"
LOGS_DIR = os.path.join(PROJECT_ROOT, "app/logs")
MEMORY_DIR = os.path.join(PROJECT_ROOT, "app/memory")

# Input log files for the assessor
MUTATION_GUARD_LOG_PATH = os.path.join(LOGS_DIR, "mutation_guard.log")
REFLEX_TRIGGER_LOG_PATH = os.path.join(MEMORY_DIR, "reflex_trigger_log.json")
LOOP_SHAPING_LOG_PATH = os.path.join(MEMORY_DIR, "loop_shaping_log.json")
LOOP_SUMMARY_REJECTION_LOG_PATH = os.path.join(MEMORY_DIR, "loop_summary_rejection_log.json")

# Output report file
GOVERNANCE_REPORT_PATH = os.path.join(LOGS_DIR, "phase_24_governance_report.json")

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Created directory: {directory_path}")
        except OSError as e:
            print(f"Error creating directory {directory_path}: {e}")
            raise

def load_json_log_file(file_path, default_value=None):
    ensure_directory_exists(os.path.dirname(file_path))
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"Warning: JSON log file {file_path} not found or empty. Returning default value.")
        return default_value if default_value is not None else []
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data] # Ensure list for iteration
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}. Returning default value.")
        return default_value if default_value is not None else []
    except Exception as e:
        print(f"Error loading file {file_path}: {e}. Returning default value.")
        return default_value if default_value is not None else []

def load_text_log_file(file_path):
    ensure_directory_exists(os.path.dirname(file_path))
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"Warning: Text log file {file_path} not found or empty. Returning empty list of lines.")
        return []
    try:
        with open(file_path, "r") as f:
            return f.readlines()
    except Exception as e:
        print(f"Error loading text file {file_path}: {e}. Returning empty list of lines.")
        return []

def save_json_report(data, file_path):
    ensure_directory_exists(os.path.dirname(file_path))
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved report to {file_path}")
    except Exception as e:
        print(f"Error saving report to {file_path}: {e}")
        raise

def analyze_phase_24_governance():
    print("Starting Phase 24 self-governance assessment...")
    metrics = {
        "assessment_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "phase_id": "24",
        "metrics_calculated": {
            "mutation_refusals_by_reflex": 0,
            "loop_shaping_by_reflex": 0,
            "loops_halted_by_self_opposition": 0,
            "details": {
                "mutation_refusal_reasons": {},
                "loop_shaping_triggers": {},
                "self_opposition_halt_reasons": {}
            }
        },
        "data_sources_summary": {
            "mutation_guard_log_entries": 0,
            "reflex_trigger_log_entries": 0,
            "loop_shaping_log_entries": 0,
            "loop_summary_rejection_log_entries": 0
        }
    }

    # 1. Analyze mutation_guard.log for reflex-driven refusals (Batch 24.0)
    mutation_guard_lines = load_text_log_file(MUTATION_GUARD_LOG_PATH)
    metrics["data_sources_summary"]["mutation_guard_log_entries"] = len(mutation_guard_lines)
    for line in mutation_guard_lines:
        if "Mutation blocked due to active" in line or "rejected mutation due to active reflex" in line.lower():
            metrics["metrics_calculated"]["mutation_refusals_by_reflex"] += 1
            reason = "unknown_reflex_reason"
            if "high-uncertainty flag" in line:
                reason = "high_uncertainty_flag"
            elif "Emergency Reflection Mode" in line:
                reason = "emergency_reflection_mode"
            metrics["metrics_calculated"]["details"]["mutation_refusal_reasons"][reason] = \
                metrics["metrics_calculated"]["details"]["mutation_refusal_reasons"].get(reason, 0) + 1

    # 2. Analyze reflex_trigger_log.json and loop_shaping_log.json for loop shaping (Batch 24.1)
    reflex_trigger_data = load_json_log_file(REFLEX_TRIGGER_LOG_PATH, default_value=[])
    loop_shaping_data = load_json_log_file(LOOP_SHAPING_LOG_PATH, default_value=[])
    metrics["data_sources_summary"]["reflex_trigger_log_entries"] = len(reflex_trigger_data)
    metrics["data_sources_summary"]["loop_shaping_log_entries"] = len(loop_shaping_data)
    
    combined_shaping_logs = reflex_trigger_data + loop_shaping_data
    for entry in combined_shaping_logs:
        if isinstance(entry, dict) and ("shaping_action" in entry or "new_intent" in entry or "modified_intent" in entry):
            metrics["metrics_calculated"]["loop_shaping_by_reflex"] += 1
            trigger = entry.get("trigger", entry.get("trigger_reason", "unknown_shaping_trigger"))
            metrics["metrics_calculated"]["details"]["loop_shaping_triggers"][trigger] = \
                metrics["metrics_calculated"]["details"]["loop_shaping_triggers"].get(trigger, 0) + 1

    # 3. Analyze loop_summary_rejection_log.json for self-opposition halts (Batch 24.2)
    rejection_data = load_json_log_file(LOOP_SUMMARY_REJECTION_LOG_PATH, default_value=[])
    metrics["data_sources_summary"]["loop_summary_rejection_log_entries"] = len(rejection_data)
    for entry in rejection_data:
        if isinstance(entry, dict):
            decision_source = entry.get("decision_source", entry.get("rejection_source"))
            reason = entry.get("reason", entry.get("rejection_reason", "unknown_halt_reason"))
            if decision_source and "self-opposition" in decision_source.lower():
                metrics["metrics_calculated"]["loops_halted_by_self_opposition"] += 1
                metrics["metrics_calculated"]["details"]["self_opposition_halt_reasons"][reason] = \
                    metrics["metrics_calculated"]["details"]["self_opposition_halt_reasons"].get(reason, 0) + 1
            elif "halted" in entry.get("status", "").lower() and "self-opposition" in reason.lower():
                 metrics["metrics_calculated"]["loops_halted_by_self_opposition"] += 1
                 metrics["metrics_calculated"]["details"]["self_opposition_halt_reasons"][reason] = \
                    metrics["metrics_calculated"]["details"]["self_opposition_halt_reasons"].get(reason, 0) + 1

    print(f"Phase 24 governance assessment complete. Metrics: {json.dumps(metrics['metrics_calculated'], indent=2)}")
    save_json_report(metrics, GOVERNANCE_REPORT_PATH)
    return metrics

if __name__ == "__main__":
    ensure_directory_exists(LOGS_DIR)
    ensure_directory_exists(MEMORY_DIR)
    analysis_results = analyze_phase_24_governance()
    print(f"Governance report generated at: {GOVERNANCE_REPORT_PATH}")

