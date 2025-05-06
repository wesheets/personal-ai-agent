import json
import os
from datetime import datetime, timezone

# Define paths
PROJECT_ROOT = "/home/ubuntu/personal-ai-agent"
LOGS_DIR = "/home/ubuntu/logs"
PREVIOUS_FILE_TREE_PATH = "/home/ubuntu/file_tree.updated_post_phase36.json"
NEW_FILE_TREE_PATH = "/home/ubuntu/file_tree.updated_batch22_1.json"

BATCH_ID = "22.1"
PHASE_ID = "22"

def load_json_file(path, default_value=None):
    if not os.path.exists(path):
        print(f"Warning: File {path} not found. Returning default.")
        return default_value if default_value is not None else {}
    try:
        with open(path, "r") as f:
            content = f.read()
            if not content.strip():
                print(f"Warning: File {path} is empty. Returning default.")
                return default_value if default_value is not None else {}
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {path}. Returning default.")
        return default_value if default_value is not None else {}
    except Exception as e:
        print(f"An error occurred while loading {path}: {e}. Returning default.")
        return default_value if default_value is not None else {}

def save_json_file(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Saved file tree to {path}")

def get_file_details(file_path):
    try:
        stat = os.stat(file_path)
        return {
            "size_bytes": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "permissions": oct(stat.st_mode)[-3:],
            "owner_uid": stat.st_uid,
            "group_gid": stat.st_gid
        }
    except FileNotFoundError:
        return {
            "size_bytes": 0,
            "last_modified": datetime.now(timezone.utc).isoformat(), # Or None
            "permissions": "N/A",
            "error": "File not found during scan"
        }
    except Exception as e:
        return {
            "size_bytes": 0,
            "last_modified": datetime.now(timezone.utc).isoformat(),
            "permissions": "N/A",
            "error": str(e)
        }

def main():
    file_tree = load_json_file(PREVIOUS_FILE_TREE_PATH, default_value={ "files": {} })
    if "files" not in file_tree or not isinstance(file_tree["files"], dict):
        print(f"Warning: Previous file tree at {PREVIOUS_FILE_TREE_PATH} was invalid. Initializing 'files' dictionary.")
        file_tree["files"] = {}

    files_to_update = [
        # Batch 22.1 Core Implementation Files
        os.path.join(PROJECT_ROOT, "app/validators/archetype_classifier.py"),
        os.path.join(PROJECT_ROOT, "app/schemas/loop_summary.schema.json"),
        os.path.join(PROJECT_ROOT, "app/controllers/loop_controller.py"), # Modified
        
        # Batch 22.1 Test Intent Files
        os.path.join(PROJECT_ROOT, "app/memory/loop_intent_loop_0030a.json"),
        os.path.join(PROJECT_ROOT, "app/memory/loop_intent_loop_0030b.json"),
        
        # Batch 22.1 Log Files
        os.path.join(LOGS_DIR, "loop_0030a_execution.log"),
        os.path.join(LOGS_DIR, "loop_0030b_execution.log"),
        
        # Batch 22.1 Modified Memory Surfaces
        os.path.join(PROJECT_ROOT, "app/memory/loop_summary.json"),
        os.path.join(PROJECT_ROOT, "app/memory/complexity_budget.json"),
        os.path.join(PROJECT_ROOT, "app/memory/agent_cognitive_budget.json"),
        os.path.join(PROJECT_ROOT, "app/memory/operator_override_log.json"), # Potentially modified

        # Batch 22.1 Metadata and Scripts
        "/home/ubuntu/update_wiring_manifest_batch22_1.py",
        "/home/ubuntu/wiring_manifest.updated_phase22_batch22_1.json"
    ]

    for file_path in files_to_update:
        details = get_file_details(file_path)
        file_tree["files"][file_path] = {
            "phase_id": PHASE_ID,
            "batch_id": BATCH_ID,
            "description": f"File related to Phase {PHASE_ID}, Batch {BATCH_ID}",
            "tags": ["phase_22", "batch_22_1"],
            "details": details
        }
        if "error" in details:
            print(f"Warning: Could not get full details for {file_path}: {details['error']}")

    file_tree["last_updated"] = datetime.now(timezone.utc).isoformat()
    file_tree["updated_by"] = "update_file_tree_batch22_1.py"
    file_tree["description"] = f"File tree updated after Phase {PHASE_ID}, Batch {BATCH_ID}. Includes archetype classifier, complexity budget, and integration test files."

    save_json_file(file_tree, NEW_FILE_TREE_PATH)

if __name__ == "__main__":
    main()

