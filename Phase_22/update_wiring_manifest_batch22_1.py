import json
import os
from datetime import datetime, timezone

# Define paths
PROJECT_ROOT = "/home/ubuntu/personal-ai-agent"
LOGS_DIR = "/home/ubuntu/logs"
PREVIOUS_WIRING_MANIFEST_PATH = "/home/ubuntu/wiring_manifest.updated_phase22_36.json"
NEW_WIRING_MANIFEST_PATH = "/home/ubuntu/wiring_manifest.updated_phase22_batch22_1.json"

BATCH_ID = "22.1"
PHASE_ID = "22"

def load_json_file(path, default_value=None):
    if not os.path.exists(path):
        print(f"Warning: File {path} not found. Returning default.")
        return default_value
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content.strip(): # Check if file is empty or whitespace only
                print(f"Warning: File {path} is empty. Returning default.")
                return default_value
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {path}. Returning default.")
        return default_value
    except Exception as e:
        print(f"An error occurred while loading {path}: {e}. Returning default.")
        return default_value

def save_json_file(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
    print(f"Saved wiring manifest to {path}")

def create_loop_entry(loop_id, phase_id, batch_id, intent_file, execution_log, output_files, description):
    entry_id = f"loop_entry_{loop_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    return {
        entry_id: {
            "loop_id": loop_id,
            "phase_id": phase_id,
            "batch_id": batch_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "intent_file": intent_file,
            "execution_log": execution_log,
            "input_files": [intent_file],
            "output_files": output_files,
            "description": description,
            "status": "completed" # Assuming execution was attempted
        }
    }

def main():
    loaded_data = load_json_file(PREVIOUS_WIRING_MANIFEST_PATH, default_value=None)
    
    wiring_manifest = {}

    if isinstance(loaded_data, dict) and "wiring_entries" in loaded_data and isinstance(loaded_data["wiring_entries"], dict):
        wiring_manifest = loaded_data
    elif isinstance(loaded_data, dict):
        print(f"Warning: Previous wiring manifest at {PREVIOUS_WIRING_MANIFEST_PATH} was a dictionary but 'wiring_entries' was missing or invalid. Initializing 'wiring_entries'.")
        wiring_manifest = {key: value for key, value in loaded_data.items() if key != "wiring_entries"}
        wiring_manifest["wiring_entries"] = {}
    else:
        if loaded_data is not None: # It was a list or some other unexpected type
             print(f"Warning: Previous wiring manifest at {PREVIOUS_WIRING_MANIFEST_PATH} was not in the expected dictionary format (was {type(loaded_data)}). Initializing a new manifest structure.")
        else: # File not found, empty, or JSON decode error, and default_value (None) was returned
            print(f"Info: Previous wiring manifest at {PREVIOUS_WIRING_MANIFEST_PATH} not found or invalid. Initializing a new manifest structure.")
        wiring_manifest["wiring_entries"] = {}

    # Files related to Batch 22.1 development (not specific loops but part of the batch context)
    batch_dev_files = [
        os.path.join(PROJECT_ROOT, "app/validators/archetype_classifier.py"),
        os.path.join(PROJECT_ROOT, "app/schemas/loop_summary.schema.json"),
        os.path.join(PROJECT_ROOT, "app/controllers/loop_controller.py"), # Modified
    ]

    # Loop 0030a
    loop_0030a_id = "0030a"
    loop_0030a_intent = os.path.join(PROJECT_ROOT, "app/memory/loop_intent_loop_0030a.json")
    loop_0030a_log = os.path.join(LOGS_DIR, "loop_0030a_execution.log")
    loop_0030a_outputs = [
        loop_0030a_log,
        os.path.join(PROJECT_ROOT, "app/memory/loop_summary.json"), # Modified
        os.path.join(PROJECT_ROOT, "app/memory/complexity_budget.json"), # Modified
        os.path.join(PROJECT_ROOT, "app/memory/agent_cognitive_budget.json"), # Modified
    ]
    loop_0030a_outputs.extend(batch_dev_files) 
    loop_0030a_desc = "Integration test for archetype classification and complexity budget tracking (within budget)."
    wiring_manifest["wiring_entries"].update(create_loop_entry(loop_0030a_id, PHASE_ID, BATCH_ID, loop_0030a_intent, loop_0030a_log, list(set(loop_0030a_outputs)), loop_0030a_desc))

    # Loop 0030b
    loop_0030b_id = "0030b"
    loop_0030b_intent = os.path.join(PROJECT_ROOT, "app/memory/loop_intent_loop_0030b.json")
    loop_0030b_log = os.path.join(LOGS_DIR, "loop_0030b_execution.log")
    loop_0030b_outputs = [
        loop_0030b_log,
        os.path.join(PROJECT_ROOT, "app/memory/loop_summary.json"), # Modified
        os.path.join(PROJECT_ROOT, "app/memory/complexity_budget.json"), # Modified
        os.path.join(PROJECT_ROOT, "app/memory/agent_cognitive_budget.json"), # Modified
        os.path.join(PROJECT_ROOT, "app/memory/operator_override_log.json") # Potentially modified
    ]
    loop_0030b_outputs.extend(batch_dev_files) 
    loop_0030b_desc = "Integration test for archetype classification and complexity budget influence (designed for over-budget, expecting gating/escalation)."
    wiring_manifest["wiring_entries"].update(create_loop_entry(loop_0030b_id, PHASE_ID, BATCH_ID, loop_0030b_intent, loop_0030b_log, list(set(loop_0030b_outputs)), loop_0030b_desc))
    
    wiring_manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    wiring_manifest["updated_by"] = "update_wiring_manifest_batch22_1.py"
    wiring_manifest["description"] = f"Wiring manifest updated after Phase {PHASE_ID}, Batch {BATCH_ID}. Includes archetype classifier and complexity budget implementation and tests."

    save_json_file(wiring_manifest, NEW_WIRING_MANIFEST_PATH)

if __name__ == "__main__":
    main()

