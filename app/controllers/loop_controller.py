import json
import argparse
import os
import sys
from datetime import datetime

# Add validators directory to path to import mutation_guard
APP_DIR = os.path.dirname(os.path.abspath(__file__))
VALIDATORS_DIR = os.path.join(os.path.dirname(APP_DIR), "validators")
sys.path.append(os.path.dirname(APP_DIR)) # Add parent directory (app) to path

from validators.mutation_guard import process_mutation_request

# Define paths
LOOP_SUMMARY_PATH = "/home/ubuntu/personal-ai-agent/app/memory/loop_summary.json"
REJECTION_LOG_PATH = "/home/ubuntu/personal-ai-agent/app/memory/loop_summary_rejection_log.json"
LOOP_INTENT_DIR = "/home/ubuntu/personal-ai-agent/app/memory/"
MEMORY_DIR = "/home/ubuntu/personal-ai-agent/app/memory/"

def load_json(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content:
                if os.path.basename(path).startswith("loop_intent"):
                    return None
                elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json"]:
                     return {}
                else:
                    return []
            return json.loads(content)
    except FileNotFoundError:
        print(f"Warning: File not found at {path}. Returning default value.")
        if os.path.basename(path).startswith("loop_intent"):
            return None
        elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json"]:
             return {}
        else:
            return []
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {path}. Returning default value.")
        if os.path.basename(path).startswith("loop_intent"):
            return None
        elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json"]:
             return {}
        else:
            return []

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def log_loop_summary(loop_id, intent_description, status):
    summary_log = load_json(LOOP_SUMMARY_PATH)
    if not isinstance(summary_log, list):
        print(f"Warning: {LOOP_SUMMARY_PATH} is not a list. Reinitializing.")
        summary_log = []
    entry = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "intent": intent_description,
        "status": status
    }
    summary_log.append(entry)
    save_json(summary_log, LOOP_SUMMARY_PATH)

def log_rejection(loop_id, reason):
    rejection_log = load_json(REJECTION_LOG_PATH)
    if not isinstance(rejection_log, list):
        print(f"Warning: {REJECTION_LOG_PATH} is not a list. Reinitializing.")
        rejection_log = []
    entry = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "reason": reason
    }
    rejection_log.append(entry)
    save_json(rejection_log, REJECTION_LOG_PATH)

def get_loop_intent_data(loop_id):
    """Loads the full intent data for a given loop ID."""
    intent_path = os.path.join(LOOP_INTENT_DIR, f"loop_intent_{loop_id}.json")
    renamed_intent_path = os.path.join(LOOP_INTENT_DIR, f"loop_intent_loop_{loop_id}.json")

    actual_path = None
    if os.path.exists(renamed_intent_path):
        actual_path = renamed_intent_path
        print(f"Note: Using renamed intent file: {actual_path}")
    elif os.path.exists(intent_path):
        actual_path = intent_path
    else:
        print(f"Warning: Intent file not found at {intent_path} or {renamed_intent_path}")
        return None

    intent_data = load_json(actual_path)
    if intent_data and isinstance(intent_data, dict):
        return intent_data
    else:
        print(f"Warning: Intent file {actual_path} is invalid.")
        return None

def read_memory_surface(surface_name):
    surface_path = os.path.join(MEMORY_DIR, surface_name)
    print(f"Attempting to read memory surface: {surface_path}")
    data = load_json(surface_path)
    if data is not None:
        print(f"Successfully read memory surface: {surface_name}")
        return True
    else:
        print(f"Failed to read memory surface: {surface_name}")
        return False

def initialize_loop(loop_id):
    print(f"Initializing loop: {loop_id}")

def run_loop_steps(loop_id, intent_data):
    """Runs loop steps, including memory read and mutation guard call."""
    print(f"Running steps for loop: {loop_id}")

    # --- Batch 16.2: Read from belief_surface.json ---
    read_success = read_memory_surface("belief_surface.json")
    if not read_success:
        print("Warning: Failed to read belief_surface.json during loop steps.")

    # --- Batch 16.3: Call Mutation Guard if intent involves mutation ---
    # Basic check: Does intent_data exist and contain a non-empty 'parameters' field?
    # A more robust check would look for specific mutation actions.
    if intent_data and intent_data.get("parameters") and intent_data["parameters"]:
        print("Intent suggests mutation. Calling Mutation Guard (Dry Run)...")
        mutation_details = {
            "loop_id": loop_id,
            "intent_params": intent_data.get("parameters", {})
            # Add more details about the intended mutation if available
        }
        mutation_allowed = process_mutation_request(mutation_details)
        if not mutation_allowed:
            print("Mutation Guard blocked the mutation (Dry Run).")
            # In a real scenario, this might halt the loop or change its course.
    else:
        print("Intent does not appear to involve mutation. Skipping Mutation Guard.")
    # --- End Batch 16.3 ---

    # Simulate overall success for now
    return True, "Loop completed successfully"

def finalize_loop(loop_id, intent_description, status, message):
    print(f"Finalizing loop: {loop_id} with status: {status}")
    if status:
        log_loop_summary(loop_id, intent_description, "success")
    else:
        log_rejection(loop_id, message)
        log_loop_summary(loop_id, intent_description, "rejected")
    print(f"Loop {loop_id} finished.")

def main():
    parser = argparse.ArgumentParser(description="Basic Loop Controller")
    parser.add_argument("--loop_id", required=True, help="Unique ID for the loop execution")
    parser.add_argument("--reject", action='store_true', help="Flag to simulate a rejection")
    parser.add_argument("--reason", default="Simulated rejection", help="Reason for rejection if --reject is used")
    args = parser.parse_args()

    intent_data = get_loop_intent_data(args.loop_id)
    intent_description = intent_data.get("intent_description", "Intent data not found or invalid") if intent_data else "Intent data not found or invalid"
    print(f"Loop Intent: {intent_description}")

    initialize_loop(args.loop_id)

    if args.reject:
        success = False
        result_message = args.reason
    else:
        # Pass full intent_data to run_loop_steps
        success, result_message = run_loop_steps(args.loop_id, intent_data)

    finalize_loop(args.loop_id, intent_description, success, result_message)

if __name__ == "__main__":
    main()

