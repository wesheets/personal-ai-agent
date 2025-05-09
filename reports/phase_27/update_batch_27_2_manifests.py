import json
import os
from datetime import datetime, timezone

# Define paths
PROJECT_ROOT = "/home/ubuntu/personal-ai-agent"
WIRING_MANIFEST_PATH = os.path.join(PROJECT_ROOT, "app", "memory", "wiring_manifest.json")
FILE_TREE_PATH = os.path.join(PROJECT_ROOT, "app", "memory", "file_tree.json")

# New components and files for Batch 27.2
BATCH_27_2_COMPONENTS = [
    {
        "component_id": "PlanRejector",
        "module_path": "app.core.plan_rejector",
        "class_name": "PlanRejector",
        "description": "Evaluates selected plans against emotional, trust, and invariant thresholds and logs rejections.",
        "dependencies": [
            "app.logs.loop_plan_selection_log.json",
            "app.logs.plan_rejection_log.json",
            "app.memory.agent_emotion_state.json",
            "app.memory.agent_trust_score.json",
            "app.memory.promethios_invariants.json"
        ],
        "outputs": ["app.logs.plan_rejection_log.json"],
        "version": "1.0.0",
        "status": "active",
        "batch": "27.2"
    }
]

BATCH_27_2_FILES = [
    {
        "path": "app/core/plan_rejector.py",
        "type": "module",
        "description": "Core logic for plan rejection based on governance thresholds.",
        "version": "1.0.0",
        "batch": "27.2"
    },
    {
        "path": "app/schemas/plan_rejection_log.schema.json",
        "type": "schema",
        "description": "JSON schema for the plan_rejection_log.json file.",
        "version": "1.0.0",
        "batch": "27.2"
    },
    {
        "path": "app/logs/plan_rejection_log.json",
        "type": "data_surface", # This is a meta-type for the script
        "manifest_type": "log_file", # This is the type for the wiring_manifest entry
        "description": "Log file for recording plan rejections.",
        "schema": "app/schemas/plan_rejection_log.schema.json",
        "version": "1.0.0",
        "batch": "27.2"
    },
    {
        "path": "scripts/run_plan_rejection_check.py",
        "type": "script",
        "description": "Script to run the plan rejection check for a given loop_id.",
        "version": "1.0.0",
        "batch": "27.2"
    },
    {
        "path": "tests/core/test_plan_rejector.py",
        "type": "test_script",
        "description": "Unit and integration tests for the PlanRejector component.",
        "version": "1.0.0",
        "batch": "27.2"
    }
]

def load_json_file(file_path, default_value=None):
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "r") as f:
                return json.load(f)
        print(f"File {file_path} is empty or does not exist. Returning default: {default_value}")
        return default_value if default_value is not None else {}
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading or parsing {file_path}: {e}. Returning default: {default_value}")
        return default_value if default_value is not None else {}

def save_json_file(file_path, data):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved {file_path}")
    except IOError as e:
        print(f"Error writing to {file_path}: {e}")

def update_wiring_manifest():
    wiring_data = load_json_file(WIRING_MANIFEST_PATH, default_value={"components": [], "data_surfaces": [], "schemas": [], "last_updated": ""})
    existing_component_ids = {comp["component_id"] for comp in wiring_data.get("components", [])}
    
    for new_comp in BATCH_27_2_COMPONENTS:
        if new_comp["component_id"] not in existing_component_ids:
            wiring_data.setdefault("components", []).append(new_comp)
            print(f"Added component {new_comp['component_id']} to wiring manifest.")
        else:
            print(f"Component {new_comp['component_id']} already exists. Updating if necessary or skipping.")

    existing_surface_paths = {ds.get("data_surface_path") for ds in wiring_data.get("data_surfaces", []) if ds.get("data_surface_path")}
    for file_entry in BATCH_27_2_FILES:
        if file_entry["type"] == "data_surface":
            data_surface_path_to_check = file_entry["path"]
            if data_surface_path_to_check not in existing_surface_paths:
                surface_entry = {
                    "component_id": os.path.basename(file_entry["path"]),
                    "data_surface_path": file_entry["path"],
                    "description": file_entry["description"],
                    "schema_path": file_entry.get("schema"),
                    "type": file_entry.get("manifest_type", "generic_data_surface"), # Use specific type from BATCH_27_2_FILES
                    "version": file_entry["version"],
                    "batch": file_entry["batch"],
                    "status": "active"
                }
                wiring_data.setdefault("data_surfaces", []).append(surface_entry)
                print(f"Added data surface {surface_entry['data_surface_path']} to wiring manifest.")
            else:
                print(f"Data surface {data_surface_path_to_check} already exists. Skipping.")

    wiring_data["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
    save_json_file(WIRING_MANIFEST_PATH, wiring_data)

def update_file_tree():
    file_tree_data = load_json_file(FILE_TREE_PATH, default_value={"files": [], "last_updated": ""})
    existing_paths = {f["path"] for f in file_tree_data.get("files", [])}

    for new_file in BATCH_27_2_FILES:
        # We only care about the path for the file tree, other details are for context if needed
        file_path_to_add = new_file["path"]
        if file_path_to_add not in existing_paths:
            # Create a more complete entry for file_tree.json
            file_tree_entry = {
                "path": file_path_to_add,
                "type": new_file["type"],
                "description": new_file["description"],
                "version": new_file["version"],
                "batch": new_file["batch"]
            }
            if new_file.get("schema"):
                file_tree_entry["schema"] = new_file["schema"]
            file_tree_data.setdefault("files", []).append(file_tree_entry)
            print(f"Added file {file_path_to_add} to file tree.")
        else:
            print(f"File {file_path_to_add} already exists in file tree. Skipping.")

    file_tree_data["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
    save_json_file(FILE_TREE_PATH, file_tree_data)

if __name__ == "__main__":
    print("Updating wiring manifest...")
    update_wiring_manifest()
    print("\nUpdating file tree...")
    update_file_tree()
    print("\nManifest updates complete.")

