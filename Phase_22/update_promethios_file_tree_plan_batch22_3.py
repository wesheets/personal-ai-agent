import json
import os
from datetime import datetime, timezone

# Define paths
input_promethios_plan_path = "/home/ubuntu/promethios_file_tree_plan.v3.1.6_runtime_synced.json"
output_promethios_plan_path = "/home/ubuntu/promethios_file_tree_plan.v3.1.7_runtime_synced.json"
wiring_manifest_path = "/home/ubuntu/wiring_manifest.updated_phase22_batch22_3.json"
project_root_dir_for_promethios = "/home/ubuntu/personal-ai-agent" # Promethios keys are relative to this

def main():
    # Load existing Promethios plan
    if os.path.exists(input_promethios_plan_path):
        with open(input_promethios_plan_path, 'r') as f:
            promethios_plan = json.load(f)
        # Ensure "files" key exists and is a dictionary
        if "files" not in promethios_plan or not isinstance(promethios_plan.get("files"), dict):
            print(f"Warning: 'files' key in {input_promethios_plan_path} is missing or not a dictionary. Reinitializing 'files' as an empty dictionary.")
            promethios_plan["files"] = {}
    else:
        promethios_plan = {
            "plan_version": "3.1.7",
            "plan_description": "Canonical file tree and metadata for Promethios AI Agent Framework, Phase 22, Batch 22.3",
            "project_root": project_root_dir_for_promethios,
            "files": {},
            "last_updated_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "last_updated_by_script": os.path.basename(__file__),
            "last_updated_for_batch": "22.3"
        }
        print(f"Input Promethios plan {input_promethios_plan_path} not found. Starting with a base structure for v3.1.7.")

    # Load the wiring manifest
    if not os.path.exists(wiring_manifest_path):
        print(f"Error: Wiring manifest {wiring_manifest_path} not found. Cannot update Promethios plan.")
        return
    
    with open(wiring_manifest_path, 'r') as f:
        wiring_manifest = json.load(f)

    if "files" not in wiring_manifest:
        print("Error: Wiring manifest does not contain a 'files' key.")
        return

    updated_files_count = 0
    added_files_count = 0

    for manifest_key, file_data in wiring_manifest["files"].items():
        is_project_file = not manifest_key.startswith("/") 

        if is_project_file:
            promethios_file_key = manifest_key
        else:
            if project_root_dir_for_promethios in manifest_key:
                 promethios_file_key = os.path.relpath(manifest_key, project_root_dir_for_promethios)
            else:
                continue 
        
        promethios_entry = {
            "description": file_data.get("description", "N/A"),
            "tags": file_data.get("tags", []),
            "version": file_data.get("version", 1),
            "size_bytes": file_data.get("size_bytes", 0),
            "last_modified_timestamp_utc": file_data.get("last_modified_timestamp_utc", datetime.now(timezone.utc).isoformat()),
            "created_timestamp_utc": file_data.get("created_timestamp_utc", datetime.now(timezone.utc).isoformat()),
            "phase_introduced": file_data.get("phase_introduced", "Unknown"),
            "batch_introduced_or_modified": file_data.get("batch_introduced_or_modified", "Unknown"),
            "dependencies": file_data.get("dependencies", []),
            "status": file_data.get("status", "active"),
            "purpose": "Runtime artifact or source code component",
            "data_sensitivity": "low"
        }

        if promethios_file_key in promethios_plan.get("files", {}):
            updated_files_count += 1
        else:
            added_files_count += 1
        
        # This check is now implicitly handled by the load logic, but good for robustness
        if not isinstance(promethios_plan.get("files"), dict):
             promethios_plan["files"] = {}

        promethios_plan["files"][promethios_file_key] = promethios_entry

    promethios_plan["plan_version"] = "3.1.7"
    promethios_plan["last_updated_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    promethios_plan["last_updated_by_script"] = os.path.basename(__file__)
    promethios_plan["last_updated_for_batch"] = "22.3"

    with open(output_promethios_plan_path, 'w') as f:
        json.dump(promethios_plan, f, indent=2)
    
    print(f"Successfully updated Promethios file tree plan. Added: {added_files_count}, Updated: {updated_files_count} project file entries.")
    print(f"Output saved to {output_promethios_plan_path}")

if __name__ == "__main__":
    main()

