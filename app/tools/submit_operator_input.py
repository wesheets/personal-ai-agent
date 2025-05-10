import json
import datetime
import argparse
import os

OPERATOR_INPUT_FILE = "/home/ubuntu/personal-ai-agent/app/memory/operator_input.json"
SCHEMA_FILE = "/home/ubuntu/personal-ai-agent/app/schemas/operator_input.schema.json"

def load_json_data(file_path):
    """Loads JSON data from a file."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return [] # Return empty list for a new or empty file
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_path} contains invalid JSON. Initializing with empty list.")
        return []
    except FileNotFoundError:
        return []

def save_json_data(file_path, data):
    """Saves JSON data to a file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def validate_with_schema(data_instance, schema_instance):
    """Basic validation (existence of required keys for the last item). 
       A more robust validation would use a library like jsonschema.
    """
    if not data_instance: # no data to validate
        return True
    item_to_validate = data_instance[-1] # Validate the last added item
    required_keys = schema_instance.get("items", {}).get("required", [])
    for key in required_keys:
        if key not in item_to_validate:
            print(f"Validation Error: Missing required key '{key}' in item: {item_to_validate}")
            return False
    # Validate enum for operator_response_type
    if "operator_response_type" in item_to_validate:
        allowed_responses = schema_instance.get("items", {}).get("properties", {}).get("operator_response_type", {}).get("enum", [])
        if item_to_validate["operator_response_type"] not in allowed_responses:
            print(f"Validation Error: Invalid operator_response_type '{item_to_validate['operator_response_type']}'. Allowed: {allowed_responses}")
            return False
    # Validate confidence_score range
    if "confidence_score" in item_to_validate and item_to_validate["confidence_score"] is not None:
        min_val = schema_instance.get("items", {}).get("properties", {}).get("confidence_score", {}).get("minimum", 0)
        max_val = schema_instance.get("items", {}).get("properties", {}).get("confidence_score", {}).get("maximum", 1)
        if not (min_val <= item_to_validate["confidence_score"] <= max_val):
            print(f"Validation Error: confidence_score '{item_to_validate['confidence_score']}' out of range [{min_val}-{max_val}].")
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Submit Operator Input")
    parser.add_argument("--loop_id", required=True, help="Loop ID")
    parser.add_argument("--decision_point", required=True, help="Decision Point")
    parser.add_argument("--operator_response_type", required=True, choices=["approve", "reject", "escalate", "override", "comment"], help="Operator Response Type")
    parser.add_argument("--rationale", required=True, help="Rationale for the decision")
    parser.add_argument("--confidence_score", type=float, help="Confidence score (0.0-1.0)")

    args = parser.parse_args()

    # Load existing data (Critical File Handling: Load Full)
    operator_inputs = load_json_data(OPERATOR_INPUT_FILE)

    # Create new entry
    new_entry = {
        "loop_id": args.loop_id,
        "decision_point": args.decision_point,
        "operator_response_type": args.operator_response_type,
        "rationale": args.rationale,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    if args.confidence_score is not None:
        new_entry["confidence_score"] = args.confidence_score
    else: # Ensure confidence_score is present if not provided, for schema compliance if it becomes required without default
        if "confidence_score" in load_json_data(SCHEMA_FILE).get("items",{}).get("required",[]):
             # if schema makes it required, but we don't have a value, this will fail validation later
             # for now, we allow it to be optional as per current schema in thought process
             pass 

    operator_inputs.append(new_entry)

    # Validate (basic)
    schema = load_json_data(SCHEMA_FILE)
    if not schema:
        print(f"Error: Could not load schema from {SCHEMA_FILE}. Cannot validate.")
        return
        
    if validate_with_schema(operator_inputs, schema):
        # Save updated data (Critical File Handling: Save Full)
        save_json_data(OPERATOR_INPUT_FILE, operator_inputs)
        print(f"Operator input successfully submitted and saved to {OPERATOR_INPUT_FILE}")
    else:
        print("Operator input failed validation. Not saved.")

if __name__ == "__main__":
    main()

