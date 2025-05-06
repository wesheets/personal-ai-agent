import json
import os
from datetime import datetime, timezone

# Define paths
input_wiring_manifest_path = "/home/ubuntu/wiring_manifest.updated_phase22_batch22_2.json"
output_wiring_manifest_path = "/home/ubuntu/wiring_manifest.updated_phase22_batch22_3.json"
project_root = "/home/ubuntu/personal-ai-agent"

# Files created or significantly modified in Batch 22.3
# Ensure these paths are relative to the project_root for the manifest key
# and absolute for checking existence and getting modification time.
files_for_batch_22_3 = [
    {
        "path": "app/validators/schema_updater.py",
        "description": "Handles the application of schema changes to schema files (simulated).",
        "tags": ["validator", "schema_management", "batch_22.3"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "app/schemas/schema_change_request.schema.json",
        "description": "JSON schema for schema change proposals.",
        "tags": ["schema", "schema_management", "batch_22.3"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "app/memory/schema_change_request.json",
        "description": "Memory surface for storing schema change proposals.",
        "tags": ["memory_surface", "schema_management", "batch_22.3"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "app/memory/loop_intent_loop_0032a.json",
        "description": "Test loop intent for Batch 22.3 (schema change approval scenario).",
        "tags": ["test_data", "loop_intent", "batch_22.3"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "app/memory/loop_intent_loop_0032b.json",
        "description": "Test loop intent for Batch 22.3 (schema change rejection scenario).",
        "tags": ["test_data", "loop_intent", "batch_22.3"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "app/controllers/loop_controller.py",
        "description": "Main loop controller, modified to integrate schema change proposal review and application logic, and robust agent_trust_score loading.",
        "tags": ["controller", "orchestration", "batch_22.3_modified"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "app/core/agent_registry.py",
        "description": "Agent registry, modified to include SchemaManagerAgent import.",
        "tags": ["core", "agent_management", "batch_22.3_modified"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    # Non-project files (logs, operator inputs) - these are typically not in the primary wiring manifest for source code
    # but can be noted for completeness if the manifest tracks all runtime artifacts.
    # For now, focusing on project files.
]

# Files that are primarily updated (runtime data, logs, documentation)
# These might already exist in the manifest and just need their last_modified updated, or are new log-type entries.
runtime_and_log_files_22_3 = [
    {
        "path": "/home/ubuntu/operator_input/review_decision_loop_0032a_schema_change_proposal_0032a_test.json",
        "description": "Simulated operator decision for schema change proposal in loop 0032a.",
        "tags": ["operator_input", "test_data", "batch_22.3"],
        "phase": "Phase 22",
        "batch": "22.3",
        "is_project_file": False
    },
    {
        "path": "/home/ubuntu/operator_input/review_decision_loop_0032b_schema_change_proposal_0032b_test.json",
        "description": "Simulated operator decision for schema change proposal in loop 0032b.",
        "tags": ["operator_input", "test_data", "batch_22.3"],
        "phase": "Phase 22",
        "batch": "22.3",
        "is_project_file": False
    },
    {
        "path": "/home/ubuntu/logs/loop_0032a_execution.log",
        "description": "Execution log for test loop 0032a (Batch 22.3).",
        "tags": ["log", "execution_trace", "batch_22.3"],
        "phase": "Phase 22",
        "batch": "22.3",
        "is_project_file": False
    },
    {
        "path": "/home/ubuntu/logs/loop_0032b_execution.log",
        "description": "Execution log for test loop 0032b (Batch 22.3).",
        "tags": ["log", "execution_trace", "batch_22.3"],
        "phase": "Phase 22",
        "batch": "22.3",
        "is_project_file": False
    },
    {
        "path": "app/memory/loop_summary.json", 
        "description": "Log of loop summaries, updated by Batch 22.3 test loops.",
        "tags": ["memory_surface", "log", "batch_22.3_updated"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "app/memory/operator_override_log.json",
        "description": "Log of operator overrides/decisions, updated by Batch 22.3 schema review simulation.",
        "tags": ["memory_surface", "log", "batch_22.3_updated"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "/home/ubuntu/drift_violation_log.json",
        "description": "Log of agent/schema drift violations, potentially updated if new drifts occurred.",
        "tags": ["log", "drift_tracking", "batch_22.3_updated"],
        "phase": "Phase 22",
        "batch": "22.3",
        "is_project_file": False
    },
    {
        "path": "app/memory/complexity_budget.json",
        "description": "Complexity budget data, updated by Batch 22.3 test loops.",
        "tags": ["memory_surface", "resource_management", "batch_22.3_updated"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "app/memory/agent_cognitive_budget.json",
        "description": "Agent cognitive budget data, potentially updated by Batch 22.3 test loops.",
        "tags": ["memory_surface", "resource_management", "batch_22.3_updated"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "app/memory/loop_summary_rejection_log.json",
        "description": "Log of loop summary rejections, updated by Batch 22.3 test loops.",
        "tags": ["memory_surface", "log", "batch_22.3_updated"],
        "phase": "Phase 22",
        "batch": "22.3"
    },
    {
        "path": "/home/ubuntu/personal-ai-agent/phase22_batch22_3_schema_memory_requirements.md",
        "description": "Documentation for schema and memory requirements for Batch 22.3.",
        "tags": ["documentation", "requirements", "batch_22.3"],
        "phase": "Phase 22",
        "batch": "22.3",
        "is_project_file": True # This is a project file
    }
]

def get_file_metadata(file_path_abs):
    try:
        stat = os.stat(file_path_abs)
        return {
            "size_bytes": stat.st_size,
            "last_modified_timestamp_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            "created_timestamp_utc": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat()
        }
    except FileNotFoundError:
        print(f"Warning: File not found for metadata: {file_path_abs}")
        return None

def main():
    # Load existing wiring manifest
    if os.path.exists(input_wiring_manifest_path):
        with open(input_wiring_manifest_path, 'r') as f:
            wiring_manifest = json.load(f)
    else:
        wiring_manifest = {"files": {}}
        print(f"Input wiring manifest {input_wiring_manifest_path} not found. Starting fresh.")

    all_files_to_process = files_for_batch_22_3 + runtime_and_log_files_22_3

    for file_info in all_files_to_process:
        is_project_file = file_info.get("is_project_file", True) # Default to True if not specified
        
        if is_project_file:
            manifest_key = file_info["path"] # Path relative to project root
            absolute_path = os.path.join(project_root, manifest_key)
        else:
            manifest_key = file_info["path"] # Absolute path used as key for non-project files
            absolute_path = manifest_key

        metadata = get_file_metadata(absolute_path)
        if not metadata:
            print(f"Skipping {manifest_key} due to missing file or metadata error.")
            continue

        entry = {
            "description": file_info["description"],
            "tags": file_info["tags"],
            "version": wiring_manifest.get("files", {}).get(manifest_key, {}).get("version", 0) + 1, # Increment version if modified
            "last_modified_timestamp_utc": metadata["last_modified_timestamp_utc"],
            "created_timestamp_utc": metadata["created_timestamp_utc"],
            "size_bytes": metadata["size_bytes"],
            "phase_introduced": file_info.get("phase", "Unknown"),
            "batch_introduced_or_modified": file_info.get("batch", "Unknown"),
            "dependencies": [], # Populate if known
            "status": "active"
        }
        
        # If it's a new file or a file that was just created (e.g. logs), use its creation time as created_timestamp_utc
        # If it's an existing file being modified, retain its original created_timestamp_utc if available
        if manifest_key in wiring_manifest.get("files", {}):
            entry["created_timestamp_utc"] = wiring_manifest["files"][manifest_key].get("created_timestamp_utc", metadata["created_timestamp_utc"])
        else: # New file
            entry["version"] = 1 # Reset version for new files

        if "files" not in wiring_manifest:
            wiring_manifest["files"] = {}
        wiring_manifest["files"][manifest_key] = entry
        print(f"Processed and updated/added entry for: {manifest_key}")

    wiring_manifest["last_updated_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    wiring_manifest["last_updated_by_script"] = os.path.basename(__file__)
    wiring_manifest["last_updated_for_batch"] = "22.3"

    # Save the updated wiring manifest
    with open(output_wiring_manifest_path, 'w') as f:
        json.dump(wiring_manifest, f, indent=2)
    
    print(f"Successfully updated wiring manifest saved to {output_wiring_manifest_path}")

if __name__ == "__main__":
    main()

