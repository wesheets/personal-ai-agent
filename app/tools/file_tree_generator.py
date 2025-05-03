# file_tree_generator.py

import json

def generate_file_tree_from_plan(plan_path="promethios_file_tree_plan.v3.1_prewiring_locked.json", output_path="app/memory/file_tree.json"):
    with open(plan_path, "r") as f:
        plan = json.load(f)

    filtered_tree = []

    for entry in plan:
        if entry.get("status") not in ["stubbed", "deprecated"]:
            filtered_tree.append({
                "file": entry.get("file"),
                "path": entry.get("path"),
                "type": entry.get("type"),
                "status": entry.get("status")
            })

    with open(output_path, "w") as f:
        json.dump(filtered_tree, f, indent=2)

    print(f"[✔] file_tree.json generated from {plan_path} with {len(filtered_tree)} entries.")

if __name__ == "__main__":
    generate_file_tree_from_plan()
