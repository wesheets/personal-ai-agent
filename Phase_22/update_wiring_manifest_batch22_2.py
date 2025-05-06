import json
import os
from datetime import datetime, timezone

# Define paths
PROJECT_ROOT = "/home/ubuntu/personal-ai-agent"
LOGS_DIR = "/home/ubuntu/logs"
WIRING_MANIFEST_PATH = "/home/ubuntu/wiring_manifest.updated_phase22_batch22_2.json"
EXISTING_WIRING_MANIFEST_PATH = "/home/ubuntu/wiring_manifest.updated_phase22_batch22_1.json"

# Helper to load JSON
def load_json_data(path, default_value=None):
    if default_value is None:
        default_value = {"execution_logs": [], "critical_file_versions": {}}
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return default_value
    except (json.JSONDecodeError, FileNotFoundError):
        return default_value

# Helper to save JSON
def save_json_data(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

# Load existing manifest or initialize a new one
wiring_data = load_json_data(EXISTING_WIRING_MANIFEST_PATH)
if not isinstance(wiring_data.get("execution_logs"), list):
    wiring_data["execution_logs"] = []
if not isinstance(wiring_data.get("critical_file_versions"), dict):
    wiring_data["critical_file_versions"] = {}

# Loops executed in Batch 22.2
loops_executed = ["0031a", "0031b", "0031c"]

for loop_id in loops_executed:
    log_file_path = os.path.join(LOGS_DIR, f"loop_{loop_id}_execution.log")
    intent_file_path = os.path.join(PROJECT_ROOT, "app/memory", f"loop_intent_loop_{loop_id}.json")
    summary_entry_path = os.path.join(PROJECT_ROOT, "app/memory/loop_summary.json") # Points to the whole file
    rejection_log_entry_path = os.path.join(PROJECT_ROOT, "app/memory/loop_summary_rejection_log.json") # Points to the whole file
    drift_log_entry_path = "/home/ubuntu/drift_violation_log.json" # Points to the whole file

    # Check if log entry already exists for this loop_id to avoid duplicates
    if any(entry.get("loop_id") == loop_id for entry in wiring_data["execution_logs"]):
        print(f"Log entry for loop {loop_id} already exists. Skipping.")
        continue

    log_entry = {
        "loop_id": loop_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_log_path": log_file_path if os.path.exists(log_file_path) else None,
        "intent_file_path": intent_file_path if os.path.exists(intent_file_path) else None,
        "output_artifacts": {
            "loop_summary_entry": summary_entry_path, # General reference
            "loop_summary_rejection_log_entry": rejection_log_entry_path if loop_id == "0031b" else None, # Specific to 0031b
            "drift_violation_log_entry": drift_log_entry_path if loop_id == "0031c" else None # Specific to 0031c
        },
        "batch_id": "22.2"
    }
    # Remove None values from output_artifacts
    log_entry["output_artifacts"] = {k: v for k, v in log_entry["output_artifacts"].items() if v is not None}
    
    wiring_data["execution_logs"].append(log_entry)

# Update critical file versions (example, add more as needed)
# For Batch 22.2, loop_controller.py and loop_summary.schema.json were modified.
CRITICAL_FILES_BATCH_22_2 = [
    "app/controllers/loop_controller.py",
    "app/schemas/loop_summary.schema.json",
    "app/memory/loop_summary_rejection_log.json", # New log surface
    "/home/ubuntu/drift_violation_log.json" # New log surface (outside project)
]

for f_path_rel in CRITICAL_FILES_BATCH_22_2:
    full_path = os.path.join(PROJECT_ROOT, f_path_rel) if not f_path_rel.startswith("/") else f_path_rel
    if os.path.exists(full_path):
        # Simple versioning: timestamp of last modification
        version_timestamp = datetime.fromtimestamp(os.path.getmtime(full_path), tz=timezone.utc).isoformat()
        wiring_data["critical_file_versions"][f_path_rel] = {
            "path": full_path,
            "version": version_timestamp,
            "batch_updated": "22.2"
        }
    else:
        print(f"Warning: Critical file {full_path} not found for versioning.")

save_json_data(wiring_data, WIRING_MANIFEST_PATH)
print(f"Wiring manifest updated and saved to {WIRING_MANIFEST_PATH}")
