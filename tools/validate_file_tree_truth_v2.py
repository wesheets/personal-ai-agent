# validate_file_tree_truth_v2.py

import os
import json

CRITICAL_SURFACES = [
    "app/memory/loop_intent.json",
    "app/core/schema_integrity_guard.py",
    "app/core/loop_execution_mode_enforcer.py"
]

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return []

def scan_disk_files(base_dir="app"):
    entries = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".py") or f.endswith(".json"):
                full_path = os.path.join(root, f)
                entries.append(full_path.replace("\", "/"))
    return entries

def validate_truth(plan_path, file_tree_path="app/memory/file_tree.json", base_dir="app"):
    plan = load_json(plan_path)
    file_tree = load_json(file_tree_path)
    disk_paths = set(scan_disk_files(base_dir))

    plan_by_path = {entry["path"]: entry for entry in plan}
    tree_by_path = {entry["path"]: entry for entry in file_tree}

    plan_paths = set(plan_by_path.keys())
    tree_paths = set(tree_by_path.keys())

    missing_from_disk = []
    missing_from_plan = []
    field_mismatches = []
    critical_files_missing = []
    trust_issues = []

    for path in plan_paths - disk_paths:
        missing_from_disk.append({
            "path": path,
            "declared_in": plan_path,
            "explanation": "File was declared in the plan but not found on disk"
        })
        if path in CRITICAL_SURFACES:
            critical_files_missing.append(path)

    for path in disk_paths - plan_paths:
        missing_from_plan.append({
            "path": path,
            "found_on_disk": True,
            "explanation": "Exists on disk but is not tracked in the plan",
            "suggested_fix": "Register this file in promethios_file_tree_plan.json or delete if obsolete"
        })

    for path in tree_paths & plan_paths:
        plan_entry = plan_by_path[path]
        tree_entry = tree_by_path.get(path, {})
        if plan_entry.get("type") != tree_entry.get("type"):
            field_mismatches.append({
                "path": path,
                "plan_type": plan_entry.get("type"),
                "tree_type": tree_entry.get("type"),
                "note": "Type mismatch between plan and file_tree.json"
            })

    trust_summary = {
        "safe_to_run": len(missing_from_disk) == 0 and len(field_mismatches) == 0 and len(critical_files_missing) == 0,
        "issues_found": len(missing_from_disk) + len(missing_from_plan) + len(field_mismatches),
        "highest_risk": critical_files_missing[0] if critical_files_missing else None
    }

    result = {
        "missing_from_disk": missing_from_disk,
        "missing_from_plan": missing_from_plan,
        "field_mismatches": field_mismatches,
        "critical_files_missing": critical_files_missing,
        "trust_summary": trust_summary,
        "verified": trust_summary["safe_to_run"]
    }

    return result

if __name__ == "__main__":
    report = validate_truth("promethios_file_tree_plan.v3.1.1_operator_patched.json")
    with open("truth_diff_log.json", "w") as log_file:
        json.dump(report, log_file, indent=2)
    print(json.dumps(report, indent=2))
