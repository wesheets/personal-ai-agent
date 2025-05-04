import json

plan_file = '/home/ubuntu/personal-ai-agent/batch_15_execution_plan.json'
batch_id_to_update = "15.34" # Changed from 15.33

try:
    with open(plan_file, 'r') as f:
        plan_data = json.load(f)
except FileNotFoundError:
    print(f"Error: Execution plan file not found at {plan_file}")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {plan_file}")
    exit(1)

updated = False
if isinstance(plan_data, list):
    for batch in plan_data:
        if isinstance(batch, dict) and batch.get("batch") == batch_id_to_update:
            batch["verified"] = True
            updated = True
            print(f"Updated batch {batch_id_to_update} status to verified: true")
            break
elif isinstance(plan_data, dict):
    # Handle cases where the plan might be a dict with a 'batches' key
    if 'batches' in plan_data and isinstance(plan_data['batches'], list):
        for batch in plan_data['batches']:
             if isinstance(batch, dict) and batch.get("batch") == batch_id_to_update:
                batch["verified"] = True
                updated = True
                print(f"Updated batch {batch_id_to_update} status to verified: true")
                break

if not updated:
    print(f"Error: Batch {batch_id_to_update} not found in the execution plan.")
    # Optionally exit with error code if batch must be found
    # exit(1)

# Write the updated data back to the file
try:
    with open(plan_file, 'w') as f:
        json.dump(plan_data, f, indent=2)
    print(f"Successfully updated {plan_file}")
except IOError:
    print(f"Error: Could not write updated plan to {plan_file}")
    exit(1)

