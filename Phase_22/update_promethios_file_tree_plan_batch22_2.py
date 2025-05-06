import json
import os
from datetime import datetime, timezone

# Define paths
PROJECT_ROOT = "/home/ubuntu/personal-ai-agent"
LOGS_DIR_PROJECT_RELATIVE = "logs" # Relative to project root for Promethios plan
LOGS_DIR_ABSOLUTE = "/home/ubuntu/logs"

PREVIOUS_PROMETHIOS_PLAN_PATH = "/home/ubuntu/promethios_file_tree_plan.v3.1.5_runtime_synced.json"
NEW_PROMETHIOS_PLAN_PATH = "/home/ubuntu/promethios_file_tree_plan.v3.1.6_runtime_synced.json"

# Helper to load JSON
def load_json_data(path, default_value=None):
    if default_value is None:
        default_value = {"project_name": "Personal AI Agent", "version": "0.0.0", "files": []}
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read()
                if not content.strip(): # Handle empty file
                    print(f"Warning: Promethios plan {path} is empty. Initializing with default.")
                    return default_value
                return json.load(f)
        print(f"Warning: Promethios plan {path} not found. Initializing with default.")
        return default_value
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {path}: {e}. Initializing with default.")
        return default_value

# Helper to save JSON
def save_json_data(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

# Load existing Promethios plan
promethios_data = load_json_data(PREVIOUS_PROMETHIOS_PLAN_PATH)

# --- Remediation for AttributeError --- 
# Ensure promethios_data is a dictionary with expected structure
default_plan_structure = {"project_name": "Personal AI Agent", "version": "0.0.0", "files": []}
if not isinstance(promethios_data, dict):
    print(f"Warning: Loaded Promethios data from {PREVIOUS_PROMETHIOS_PLAN_PATH} is not a dict (type: {type(promethios_data)}). Attempting to recover or reset.")
    if isinstance(promethios_data, list) and all(isinstance(item, dict) and "path" in item for item in promethios_data):
        print("Loaded data is a list of file entries. Wrapping in default structure.")
        promethios_data = {**default_plan_structure, "files": promethios_data}
        # Try to infer version if possible, or set to a base one
        if promethios_data["files"]:
             # This is a guess; a more robust version recovery might be needed
            promethios_data["version"] = "3.1.5_recovered" 
    else:
        print("Cannot recover structure. Resetting to default plan structure.")
        promethios_data = default_plan_structure

# Ensure basic structure exists after loading/recovery
if "files" not in promethios_data or not isinstance(promethios_data.get("files"), list):
    print(f"Warning: \"files\" key missing or not a list in Promethios data. Initializing \"files\" to empty list.")
    promethios_data["files"] = []
if "project_name" not in promethios_data:
    promethios_data["project_name"] = default_plan_structure["project_name"]
if "version" not in promethios_data:
    promethios_data["version"] = default_plan_structure["version"]
# --- End Remediation ---


promethios_data["version"] = "3.1.6" 
promethios_data["last_updated"] = datetime.now(timezone.utc).isoformat()

files_batch_22_2 = [
    {"path": "app/controllers/loop_controller.py", "description": "Modified to include summary rejection, Critic invocation, and agent drift logging.", "type": "code", "batch": "22.2"},
    {"path": "app/schemas/loop_summary.schema.json", "description": "Updated to include summary_status field.", "type": "schema", "batch": "22.2"},
    {"path": "app/memory/loop_intent_loop_0031a.json", "description": "Test intent for Batch 22.2 (valid summary).", "type": "data_intent", "batch": "22.2"},
    {"path": "app/memory/loop_intent_loop_0031b.json", "description": "Test intent for Batch 22.2 (summary rejection).", "type": "data_intent", "batch": "22.2"},
    {"path": "app/memory/loop_intent_loop_0031c.json", "description": "Test intent for Batch 22.2 (agent drift).", "type": "data_intent", "batch": "22.2"},
    {"path": "app/memory/loop_summary_rejection_log.json", "description": "Log for loop summary rejections.", "type": "log_surface_memory", "batch": "22.2"},
    {"path": f"{LOGS_DIR_PROJECT_RELATIVE}/loop_0031a_execution.log", "description": "Execution log for test loop 0031a (Batch 22.2).", "type": "log_runtime", "batch": "22.2", "location_note": "Absolute path /home/ubuntu/logs/"},
    {"path": f"{LOGS_DIR_PROJECT_RELATIVE}/loop_0031b_execution.log", "description": "Execution log for test loop 0031b (Batch 22.2).", "type": "log_runtime", "batch": "22.2", "location_note": "Absolute path /home/ubuntu/logs/"},
    {"path": f"{LOGS_DIR_PROJECT_RELATIVE}/loop_0031c_execution.log", "description": "Execution log for test loop 0031c (Batch 22.2).", "type": "log_runtime", "batch": "22.2", "location_note": "Absolute path /home/ubuntu/logs/"},
    {"path": "/home/ubuntu/drift_violation_log.json", "description": "Log for agent registration and other system drifts.", "type": "log_surface_system", "batch": "22.2", "location_note": "Absolute path"},
    {"path": "/home/ubuntu/wiring_manifest.updated_phase22_batch22_2.json", "description": "Wiring manifest updated for Batch 22.2.", "type": "metadata_wiring", "batch": "22.2", "location_note": "Absolute path"},
    {"path": "/home/ubuntu/update_wiring_manifest_batch22_2.py", "description": "Script to update wiring manifest for Batch 22.2.", "type": "script_utility", "batch": "22.2", "location_note": "Absolute path"},
    {"path": "/home/ubuntu/update_promethios_file_tree_plan_batch22_2.py", "description": "Script to update Promethios file tree plan for Batch 22.2.", "type": "script_utility", "batch": "22.2", "location_note": "Absolute path"}
]

existing_file_paths = {file_entry["path"]: file_entry for file_entry in promethios_data.get("files", [])}

for new_file_entry in files_batch_22_2:
    if new_file_entry["path"] in existing_file_paths:
        existing_file_paths[new_file_entry["path"]].update(new_file_entry)
        existing_file_paths[new_file_entry["path"]]["last_modified_batch"] = "22.2"
    else:
        new_file_entry["created_batch"] = "22.2"
        promethios_data.setdefault("files", []).append(new_file_entry)

updated_files_dict = {file_entry["path"]: file_entry for file_entry in promethios_data.get("files", [])}
promethios_data["files"] = list(updated_files_dict.values())

save_json_data(promethios_data, NEW_PROMETHIOS_PLAN_PATH)
print(f"Promethios file tree plan updated and saved to {NEW_PROMETHIOS_PLAN_PATH}")

print(f"Generated: {NEW_PROMETHIOS_PLAN_PATH}")
