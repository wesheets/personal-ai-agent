import json
import os

OPERATOR_INPUT_FILE = "/home/ubuntu/personal-ai-agent/app/memory/operator_input.json"

def load_json_data(file_path):
    """Loads JSON data from a file."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"Info: File {file_path} is empty or does not exist.")
        return []
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_path} contains invalid JSON.")
        return []
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []

def main():
    operator_inputs = load_json_data(OPERATOR_INPUT_FILE)

    if not operator_inputs:
        print("No operator inputs found.")
        return

    # Group inputs by loop_id for better readability
    inputs_by_loop = {}
    for entry in operator_inputs:
        loop_id = entry.get("loop_id", "Unknown_Loop_ID")
        if loop_id not in inputs_by_loop:
            inputs_by_loop[loop_id] = []
        inputs_by_loop[loop_id].append(entry)

    print("--- Operator Input Log ---")
    for loop_id, entries in inputs_by_loop.items():
        print(f"\nLoop ID: {loop_id}")
        for entry in entries:
            print(f"  Timestamp: {entry.get("timestamp", "N/A")}")
            print(f"  Decision Point: {entry.get("decision_point", "N/A")}")
            print(f"  Response Type: {entry.get("operator_response_type", "N/A")}")
            print(f"  Rationale: {entry.get("rationale", "N/A")}")
            confidence = entry.get("confidence_score")
            if confidence is not None:
                print(f"  Confidence: {confidence}")
            print("  -----")

if __name__ == "__main__":
    main()

