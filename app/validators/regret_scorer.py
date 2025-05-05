#!/usr/bin/env python3.11
import json
import os
import argparse
from datetime import datetime
import statistics

# Define paths relative to the script location assuming it's in app/validators/
VALIDATOR_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(VALIDATOR_DIR)
PROJECT_ROOT = os.path.dirname(APP_DIR)

LOOP_SUMMARY_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary.json")
REJECTION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary_rejection_log.json")
JUSTIFICATION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_justification_log.json")
REGRET_SCORE_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_regret_score.json")

# --- Helper functions for JSON loading/saving ---
def load_json(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content:
                return [] # Return empty list for empty file
            return json.loads(content)
    except FileNotFoundError:
        print(f"Warning: File not found at {path}. Returning empty list.")
        return []
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {path}. Returning empty list.")
        return []

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
# --- End Helper functions ---

def calculate_regret(loop_id):
    """Calculates and logs the regret score for a given loop_id."""
    print(f"Calculating regret score for loop: {loop_id}")

    # 1. Determine Final Status
    final_status = None
    summary_log = load_json(LOOP_SUMMARY_PATH)
    rejection_log = load_json(REJECTION_LOG_PATH)

    # Check rejection log first
    for entry in rejection_log:
        if entry.get("loop_id") == loop_id:
            final_status = "rejected"
            break
    
    # If not rejected, check summary log for success
    if final_status is None:
        for entry in summary_log:
            if entry.get("loop_id") == loop_id and entry.get("status") == "success":
                final_status = "success"
                break

    if final_status is None:
        print(f"Error: Could not determine final status for loop {loop_id}. Aborting regret calculation.")
        return

    print(f"Final status for loop {loop_id}: {final_status}")

    # 2. Extract Initial Confidence and Risk
    justification_log = load_json(JUSTIFICATION_LOG_PATH)
    initial_confidence = None
    initial_risk = None
    confidence_scores = []
    risk_scores = []

    for entry in justification_log:
        if entry.get("loop_id") == loop_id:
            # Example: Look for Architect's confidence in the plan
            if entry.get("agent_id") == "architect" and "Generated plan" in entry.get("action_decision", ""):
                conf = entry.get("confidence_score")
                if isinstance(conf, (int, float)):
                    confidence_scores.append(conf)
            
            # Example: Look for Pessimist's risk score
            if entry.get("agent_id") == "pessimist" and "risk_score" in entry: # Check if key exists
                 risk = entry.get("risk_score")
                 if isinstance(risk, (int, float)):
                     risk_scores.append(risk)
            elif entry.get("agent_id") == "loop_controller" and "Pessimist Assessment Received" in entry.get("action_decision", ""):
                 # Fallback: Try to parse from controller log if direct agent log missing
                 try:
                     # Example text: "Pessimist assessed risk for plan ... Score: 0.75. Reason: ..."
                     score_part = entry.get("action_decision", "").split("Score: ")[1]
                     risk = float(score_part.split(".")[0] + "." + score_part.split(".")[1].split(" ")[0]) # Extract float
                     risk_scores.append(risk)
                 except (IndexError, ValueError):
                     pass # Ignore if parsing fails

    # Use average if multiple scores found, otherwise the single score, or None
    initial_confidence = statistics.mean(confidence_scores) if confidence_scores else None
    initial_risk = statistics.mean(risk_scores) if risk_scores else None

    print(f"Initial Confidence (avg): {initial_confidence}")
    print(f"Initial Risk (avg): {initial_risk}")

    # 3. Calculate Regret Score
    expectation = 0.5 # Default expectation if no confidence/risk
    if initial_confidence is not None:
        if initial_risk is not None:
            expectation = initial_confidence * (1.0 - initial_risk)
        else:
            expectation = initial_confidence # Use confidence directly if risk is missing
    elif initial_risk is not None:
         expectation = 1.0 - initial_risk # Infer expectation from risk if confidence missing

    regret_score = 0.0
    if final_status == "success":
        regret_score = expectation - 1.0 # Range -1.0 to 0.0
    elif final_status == "rejected":
        regret_score = expectation - 0.0 # Range 0.0 to 1.0

    # Clamp score to [-1.0, 1.0] just in case
    regret_score = max(-1.0, min(1.0, regret_score))

    print(f"Calculated Expectation: {expectation:.2f}")
    print(f"Calculated Regret Score: {regret_score:.2f}")

    # 4. Generate Reason
    reason = f"Loop {final_status} with expectation score {expectation:.2f} (Confidence: {initial_confidence}, Risk: {initial_risk})."
    if regret_score > 0.75:
        reason += " High regret due to failure despite high expectation."
    elif regret_score > 0.25:
        reason += " Moderate regret due to failure with moderate/high expectation."
    elif regret_score >= 0:
        reason += " Low regret, failure was somewhat expected or confidence was low."
    elif regret_score < -0.75:
        reason += " Pleasant surprise, success occurred despite very low expectation."
    elif regret_score < -0.25:
        reason += " Mild surprise, success occurred with low/moderate expectation."
    else: # regret_score close to 0 and negative
        reason += " Low regret, success occurred largely as expected."
        
    print(f"Reason: {reason}")

    # 5. Log the Result
    regret_log = load_json(REGRET_SCORE_LOG_PATH)
    if not isinstance(regret_log, list):
        print(f"Warning: {REGRET_SCORE_LOG_PATH} is not a list. Reinitializing.")
        regret_log = []

    entry = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "final_status": final_status,
        "initial_confidence": initial_confidence,
        "initial_risk": initial_risk,
        "regret_score": round(regret_score, 4), # Round for cleaner logging
        "reason": reason
    }
    regret_log.append(entry)
    save_json(regret_log, REGRET_SCORE_LOG_PATH)
    print(f"Successfully logged regret score for loop {loop_id} to {REGRET_SCORE_LOG_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate and log regret score for a completed loop.")
    parser.add_argument("--loop_id", required=True, help="Unique ID of the loop to analyze")
    args = parser.parse_args()

    calculate_regret(args.loop_id)

