import json
import os
from datetime import datetime

# Configuration
AGENT_ID = "manus_agent_batch_22.0"
BATCH_ID = "22.0"

WIRING_MANIFEST_PATH = "/home/ubuntu/wiring_manifest.updated_phase22_36.json"
FILE_TREE_PATH = "/home/ubuntu/file_tree.updated_post_phase36.json"
PROMETHEUS_PLAN_PATH = "/home/ubuntu/promethios_file_tree_plan.v3.1.5_runtime_synced.json"

FILES_CREATED_OR_MODIFIED = [
    {
        "path": "/home/ubuntu/personal-ai-agent/phase22_execution_plan_content.json",
        "status": "created",
        "type": "file"
    },
    {
        "path": "/home/ubuntu/personal-ai-agent/phase22_objectives.md",
        "status": "created",
        "type": "file"
    },
    {
        "path": "/home/ubuntu/personal-ai-agent/todo_phase22.md",
        "status": "created", # Or modified if it existed, but for this script, assume created for simplicity in this batch
        "type": "file"
    },
    {
        "path": "/home/ubuntu/personal-ai-agent/phase22_schema_surface_identification.md",
        "status": "created",
        "type": "file"
    },
    {
        "path": "/home/ubuntu/personal-ai-agent/app/schemas/complexity_budget.schema.json",
        "status": "created",
        "type": "file"
    },
    {
        "path": "/home/ubuntu/personal-ai-agent/app/memory/complexity_budget.json",
        "status": "created",
        "type": "file"
    }
]

def read_json_file(file_path, default_content_if_not_found):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {file_path} contains invalid JSON. Using default content.")
                return default_content_if_not_found
    return default_content_if_not_found

def write_json_file(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Successfully wrote to {file_path}")

# 1. Handle Wiring Manifest
# Since no loops were executed in Batch 22.0, we ensure the file exists (as an empty list if new).
print(f"Processing {WIRING_MANIFEST_PATH}...")
wiring_data = read_json_file(WIRING_MANIFEST_PATH, [])
# No new entries for loops in this batch as per plan (only definition/creation)
write_json_file(WIRING_MANIFEST_PATH, wiring_data)

# 2. Handle File Tree
print(f"Processing {FILE_TREE_PATH}...")
file_tree_data = read_json_file(FILE_TREE_PATH, [])
existing_paths_in_file_tree = {entry['path'] for entry in file_tree_data}

for file_info in FILES_CREATED_OR_MODIFIED:
    if file_info['path'] not in existing_paths_in_file_tree:
        file_tree_data.append({
            "path": file_info['path'],
            "status": file_info['status'],
            "type": file_info['type'],
            "added_by": AGENT_ID
        })
    else:
        # Update existing entry if necessary (e.g., status or added_by if rules change)
        for entry in file_tree_data:
            if entry['path'] == file_info['path']:
                entry['status'] = file_info['status'] # Update status
                entry['added_by'] = AGENT_ID # Update agent
                break
write_json_file(FILE_TREE_PATH, file_tree_data)

# 3. Handle Promethios File Tree Plan
print(f"Processing {PROMETHEUS_PLAN_PATH}...")
prometheus_plan_data = read_json_file(PROMETHEUS_PLAN_PATH, []) # Assuming it's a list of entries
existing_paths_in_prometheus_plan = {entry['path'] for entry in prometheus_plan_data}

for file_info in FILES_CREATED_OR_MODIFIED:
    if file_info['path'] not in existing_paths_in_prometheus_plan:
        prometheus_plan_data.append({
            "path": file_info['path'],
            "type": file_info['type'],
            "status": file_info['status'],
            "batch_id": BATCH_ID,
            "added_by": AGENT_ID
        })
    else:
        for entry in prometheus_plan_data:
            if entry['path'] == file_info['path']:
                entry['status'] = file_info['status']
                entry['batch_id'] = BATCH_ID
                entry['added_by'] = AGENT_ID
                break
write_json_file(PROMETHEUS_PLAN_PATH, prometheus_plan_data)

print("Metadata update script finished.")


