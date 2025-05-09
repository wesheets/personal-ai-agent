import json
import os
from datetime import datetime, timezone

# Define paths
PROJECT_ROOT = "/home/ubuntu/personal-ai-agent"
WIRING_MANIFEST_PATH = os.path.join(PROJECT_ROOT, "app", "memory", "wiring_manifest.json")
FILE_TREE_PATH = os.path.join(PROJECT_ROOT, "app", "memory", "file_tree.json")

# --- New entries for Batch 27.3 ---
NEW_COMPONENTS = [
    {
        "component_id": "PlanEscalationDetector",
        "module_path": "app.core.plan_escalation_detector",
        "class_name": "PlanEscalationDetector",
        "description": "Detects if all candidate plans for a loop have been rejected and handles escalation and fallback logic.",
        "dependencies": [
            "multi_plan_comparison.json",
            "plan_rejection_log.json",
            "loop_plan_selection_log.json",
            "plan_escalation_log.json"
        ],
        "outputs": ["plan_escalation_log.json"],
        "version": "1.0.0",
        "status": "active",
        "last_updated": datetime.now(timezone.utc).isoformat() + "Z"
    }
]

NEW_DATA_SURFACES = [
    {
        "surface_id": "plan_escalation_log.json",
        "description": "Logs escalation events when all plans are rejected, including details and fallback actions.",
        "location": "app/logs/plan_escalation_log.json",
        "schema_id": "plan_escalation_log.schema.json",
        "type": "log_file",
        "access_pattern": "append",
        "consumers": ["PlanEscalationDetector", "SystemAuditor"],
        "producers": ["PlanEscalationDetector"],
        "version": "1.0.0",
        "status": "active",
        "last_updated": datetime.now(timezone.utc).isoformat() + "Z"
    }
]

NEW_SCHEMAS = [
    {
        "schema_id": "plan_escalation_log.schema.json",
        "description": "Schema for the plan escalation log.",
        "location": "app/schemas/plan_escalation_log.schema.json",
        "version": "1.0.0",
        "status": "active",
        "last_updated": datetime.now(timezone.utc).isoformat() + "Z"
    }
]

NEW_FILES_FOR_FILE_TREE = [
    # Batch specific, non-application files
    "/home/ubuntu/check_batch_27_3_prerequisites.py",
    "/home/ubuntu/batch_27_3_prerequisite_check_report.json",
    "/home/ubuntu/batch_27_3_requirements_analysis.md",
    "/home/ubuntu/todo_batch_27_3.md",
    "/home/ubuntu/batch_27_3_implementation_design.md",
    # Application files
    os.path.join(PROJECT_ROOT, "app", "schemas", "plan_escalation_log.schema.json"),
    os.path.join(PROJECT_ROOT, "app", "core", "plan_escalation_detector.py"),
    os.path.join(PROJECT_ROOT, "scripts", "run_escalation_check.py"),
    # Test data files
    os.path.join(PROJECT_ROOT, "app", "test_data", "batch_27_3", "multi_plan_comparison_loop_0050.json"),
    os.path.join(PROJECT_ROOT, "app", "test_data", "batch_27_3", "multi_plan_comparison_loop_0052.json"),
    os.path.join(PROJECT_ROOT, "app", "test_data", "batch_27_3", "plan_rejection_log_loop_0050_partial_rejection.json"),
    os.path.join(PROJECT_ROOT, "app", "test_data", "batch_27_3", "plan_rejection_log_loop_0052_all_rejected.json"),
    # Test files
    os.path.join(PROJECT_ROOT, "tests", "core", "test_plan_escalation_detector.py")
]

def update_wiring_manifest():
    print(f"Updating wiring manifest at: {WIRING_MANIFEST_PATH}")
    try:
        if os.path.exists(WIRING_MANIFEST_PATH):
            with open(WIRING_MANIFEST_PATH, "r") as f:
                wiring_data = json.load(f)
        else:
            wiring_data = {"components": [], "data_surfaces": [], "schemas": [], "last_updated": ""}
            print(f"Warning: {WIRING_MANIFEST_PATH} not found. Creating a new one.")

        # Update components
        existing_component_ids = {comp["component_id"] for comp in wiring_data.get("components", [])}
        for new_comp in NEW_COMPONENTS:
            if new_comp["component_id"] not in existing_component_ids:
                wiring_data.setdefault("components", []).append(new_comp)
                print(f"Added component: {new_comp['component_id']}")
            else:
                print(f"Component {new_comp['component_id']} already exists. Skipping.")

        # Update data surfaces
        existing_surface_ids = {surf["surface_id"] for surf in wiring_data.get("data_surfaces", [])}
        for new_surf in NEW_DATA_SURFACES:
            if new_surf["surface_id"] not in existing_surface_ids:
                wiring_data.setdefault("data_surfaces", []).append(new_surf)
                print(f"Added data surface: {new_surf['surface_id']}")
            else:
                print(f"Data surface {new_surf['surface_id']} already exists. Skipping.")

        # Update schemas
        existing_schema_ids = {sch["schema_id"] for sch in wiring_data.get("schemas", [])}
        for new_sch in NEW_SCHEMAS:
            if new_sch["schema_id"] not in existing_schema_ids:
                wiring_data.setdefault("schemas", []).append(new_sch)
                print(f"Added schema: {new_sch['schema_id']}")
            else:
                print(f"Schema {new_sch['schema_id']} already exists. Skipping.")

        wiring_data["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"

        with open(WIRING_MANIFEST_PATH, "w") as f:
            json.dump(wiring_data, f, indent=4)
        print("Wiring manifest updated successfully.")

    except Exception as e:
        print(f"Error updating wiring manifest: {e}")

def update_file_tree():
    print(f"Updating file tree at: {FILE_TREE_PATH}")
    try:
        if os.path.exists(FILE_TREE_PATH):
            with open(FILE_TREE_PATH, "r") as f:
                file_tree_data = json.load(f)
        else:
            file_tree_data = {"project_name": "personal-ai-agent", "files": [], "last_updated": ""}
            print(f"Warning: {FILE_TREE_PATH} not found. Creating a new one.")

        existing_files = {file_entry["path"] for file_entry in file_tree_data.get("files", [])}
        
        for file_path in NEW_FILES_FOR_FILE_TREE:
            if file_path not in existing_files:
                try:
                    file_stat = os.stat(file_path)
                    file_entry = {
                        "path": file_path,
                        "size_bytes": file_stat.st_size,
                        "last_modified": datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc).isoformat() + "Z",
                        "type": "file" if os.path.isfile(file_path) else "directory", # Basic type
                        "description": f"File or directory related to Batch 27.3: Escalation & Fallback Logic. Added on {datetime.now(timezone.utc).isoformat() + 'Z'}"
                    }
                    file_tree_data.setdefault("files", []).append(file_entry)
                    print(f"Added file to tree: {file_path}")
                except FileNotFoundError:
                    print(f"Warning: File {file_path} not found during file tree update. Skipping.")
                except Exception as e_stat:
                    print(f"Warning: Could not stat file {file_path}: {e_stat}. Skipping.")
            else:
                print(f"File {file_path} already in tree. Skipping.")

        file_tree_data["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"

        with open(FILE_TREE_PATH, "w") as f:
            json.dump(file_tree_data, f, indent=4)
        print("File tree updated successfully.")

    except Exception as e:
        print(f"Error updating file tree: {e}")

if __name__ == "__main__":
    update_wiring_manifest()
    print("\n---\n")
    update_file_tree()
    # file_tree_plan.json is not updated by this script as it's more about planned structure.
    # Manual review might be needed if core application structure changes significantly.
    print("\nManifest update process complete.")

