import json

plan_file = '/home/ubuntu/personal-ai-agent/batch_15_execution_plan.json'
batch_id_to_update = "15.36"

try:
    with open(plan_file, 'r') as f:
        plan_data = json.load(f)
except FileNotFoundError:
    print(f"Error: Plan file not found at {plan_file}")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {plan_file}")
    exit(1)

batch_updated = False
for batch in plan_data:
    # Use .get() to safely access dictionary keys
    if batch.get("batch") == batch_id_to_update:
        batch["verified"] = True
        batch_updated = True
        print(f"Updated batch {batch_id_to_update} status to verified: True")
        break

if not batch_updated:
    print(f"Error: Batch {batch_id_to_update} not found in the plan.")
    # Optionally, exit with an error code if the batch must exist
    # exit(1)

# Write the updated data back to the file
try:
    with open(plan_file, 'w') as f:
        json.dump(plan_data, f, indent=2)
    print(f"Successfully updated {plan_file}")
except IOError as e:
    print(f"Error writing updated plan file: {e}")
    exit(1)

