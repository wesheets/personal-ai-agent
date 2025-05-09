#!/usr/bin/env python3.11
import json
import argparse
import os
import sys
import asyncio

# Get the directory of the current script (loop_controller.py)
CONTROLLER_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the 'app' directory
APP_DIR = os.path.dirname(CONTROLLER_DIR)
# Get the project root directory (one level above 'app')
PROJECT_ROOT = os.path.dirname(APP_DIR)

# Add the project root directory to sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Batch 21.4: Explicitly import app.agents to trigger __init__.py and agent registration ---
import app.agents
# --- End Batch 21.4 ---

from app.validators.track_emotion_drift import track_emotion_drift
# Batch 26.1: Import assess_drift_awareness
from app.validators.assess_drift_awareness import assess_drift_awareness
# Batch 26.2: Import generate_refactor_suggestion
from app.validators.refactor_monitor import generate_refactor_suggestion

# Define paths relative to PROJECT_ROOT
LOOP_SUMMARY_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary.json")
LOOP_SUMMARY_REJECTION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary_rejection_log.json")
OPERATOR_INPUT_PATH = os.path.join(PROJECT_ROOT, "app/memory/operator_input.json") # Corrected path
AGENT_TRUST_SCORE_PATH = os.path.join(PROJECT_ROOT, "app/memory/agent_trust_score.json")
BELIEF_SURFACE_PATH = os.path.join(PROJECT_ROOT, "app/memory/belief_surface.json")
COMPLEXITY_BUDGET_PATH = os.path.join(PROJECT_ROOT, "app/memory/complexity_budget.json")
# Batch 23.3: Paths for System Invariants and Violation Logging
SYSTEM_INVARIANTS_PATH = os.path.join(PROJECT_ROOT, "app/memory/system_invariants.json")
INVARIANT_VIOLATION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/invariant_violation_log.json")
# Batch 26.1: Path for emotion drift alert log
EMOTION_DRIFT_ALERT_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/emotion_drift_alert_log.json")
# Batch 26.2: Path for refactor suggestion log
REFACTOR_SUGGESTION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/refactor_suggestion_log.json")

def load_json(path, is_list_default=True):
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content.strip():
                return [] if is_list_default else {}
            f.seek(0) # Rewind after reading to allow json.load to work
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found at {path}. Returning default value.")
        return [] if is_list_default else {}
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {path}. Returning default value.")
        return [] if is_list_default else {}

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

# Batch 26.2: Modified loop_controller to integrate refactor suggestions
async def run_loop(loop_id: str, iteration: int):
    print(f"Starting Loop {loop_id}, Iteration {iteration}...")

    # Simulate loop execution and outcome
    agent_id = "test_agent" # Example agent ID
    outcome = "success" if iteration % 2 == 0 else "failure" # Alternate success/failure for testing
    regret_score = 0.2 if outcome == "success" else 0.8 # Example regret score
    justification_ref = f"justification_for_loop_{loop_id}_iteration_{iteration}"

    # Call track_emotion_drift after loop completion
    track_emotion_drift(agent_id, loop_id, outcome, regret_score, justification_ref)

    # Batch 26.1: Call assess_drift_awareness
    current_emotion_profile = {} # Placeholder, should be loaded from memory
    historical_emotion_data = [] # Placeholder, should be loaded from memory
    
    # Load current emotion profile for the agent
    try:
        with open(AGENT_TRUST_SCORE_PATH, 'r') as f:
            all_profiles = json.load(f)
            if agent_id in all_profiles:
                current_emotion_profile = all_profiles[agent_id]
    except FileNotFoundError:
        print(f"Warning: Agent emotion profile file not found at {AGENT_TRUST_SCORE_PATH}")
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {AGENT_TRUST_SCORE_PATH}")

    # Load historical emotion data (this is a simplified example)
    try:
        with open(EMOTION_DRIFT_TRACKER_PATH, 'r') as f:
            all_drift_data = json.load(f)
            # Filter for the current agent's historical data
            historical_emotion_data = [entry for entry in all_drift_data if entry.get('agent_id') == agent_id]
    except FileNotFoundError:
        print(f"Warning: Emotion drift tracker file not found at {EMOTION_DRIFT_TRACKER_PATH}")
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {EMOTION_DRIFT_TRACKER_PATH}")

    awareness_score = assess_drift_awareness(agent_id, current_emotion_profile, historical_emotion_data)
    print(f"Awareness score for {agent_id}: {awareness_score}")

    # Example: Log an alert if awareness is low (e.g., below 0.3)
    if awareness_score < 0.3:
        alert_message = f"Low emotion drift awareness detected for agent {agent_id} in loop {loop_id}. Score: {awareness_score}"
        print(alert_message)
        alerts = load_json(EMOTION_DRIFT_ALERT_LOG_PATH, True)
        alerts.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": agent_id,
            "loop_id": loop_id,
            "awareness_score": awareness_score,
            "message": alert_message
        })
        save_json(alerts, EMOTION_DRIFT_ALERT_LOG_PATH)

    # Batch 26.2: Call generate_refactor_suggestion based on some criteria
    # This is a simplified example. In a real system, these thresholds and conditions would be more complex.
    if regret_score > 0.7: # Example: High regret
        generate_refactor_suggestion(
            trigger_reason="High Regret Score",
            loop_id=loop_id,
            component="DecisionMakingUnit", # Example component
            recommended_action="Re-evaluate decision parameters and logic.",
            confidence_score=regret_score # Using regret_score as a proxy for confidence
        )
    
    # Example: Trigger based on emotional instability (e.g., rapid changes or extreme values)
    # This would require more sophisticated analysis of current_emotion_profile and historical_emotion_data
    # For simplicity, let's assume a high sadness score triggers a suggestion
    if current_emotion_profile.get("sadness", 0.0) > 0.8:
         generate_refactor_suggestion(
            trigger_reason="High Sadness Score",
            loop_id=loop_id,
            component="EmotionRegulationModule", # Example component
            recommended_action="Investigate potential negative feedback loops or stressors.",
            confidence_score=current_emotion_profile.get("sadness", 0.0)
        )

    print(f"Loop {loop_id}, Iteration {iteration} completed with outcome: {outcome}.")


async def main():
    # This is a simple wrapper to call run_loop for testing purposes.
    # In a real application, this would be part of a larger system.
    await run_loop("test_loop_1", 1)
    await run_loop("test_loop_2", 2) 

if __name__ == "__main__":
    asyncio.run(main())

