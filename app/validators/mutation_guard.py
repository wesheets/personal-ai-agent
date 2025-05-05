import json
import os
from datetime import datetime
import traceback

# Define paths
GUARD_LOG_PATH = "/home/ubuntu/personal-ai-agent/app/logs/mutation_guard.log"
MUTATION_LOG_PATH = "/home/ubuntu/personal-ai-agent/app/memory/mutation_log.json"

# --- Helper functions for JSON loading/saving ---
def load_json(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content:
                return [] # Return empty list for empty file
            return json.loads(content)
    except FileNotFoundError:
        print(f"Warning: Log file not found at {path}. Returning empty list.")
        return []
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {path}. Returning empty list.")
        return []

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
# --- End Helper functions ---

def log_guard_event(loop_id, mutation_details, status, reason=""):
    """Logs mutation events (attempt, success, failure) to the guard log."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "loop_id": loop_id,
        "status": status, # e.g., 'attempting', 'success', 'failure'
        "mutation_details": mutation_details,
        "reason": reason
    }
    # Ensure log directory exists
    os.makedirs(os.path.dirname(GUARD_LOG_PATH), exist_ok=True)
    # Append to log file
    with open(GUARD_LOG_PATH, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

# --- Batch 19.2: Log Intended Mutation --- 
def log_intended_mutation(loop_id, file_path, action):
    """Logs the intention to perform a mutation to mutation_log.json."""
    mutation_log = load_json(MUTATION_LOG_PATH)
    if not isinstance(mutation_log, list):
        print(f"Warning: {MUTATION_LOG_PATH} is not a list. Reinitializing.")
        mutation_log = []
    
    entry = {
        "loop_id": loop_id,
        "timestamp_intended": datetime.utcnow().isoformat(),
        "timestamp_finalized": None, # Will be updated later
        "component_modified": file_path,
        "diff_summary": f"{action.capitalize()} operation intended", # Basic summary
        "status": "intended",
        "reason": None
    }
    mutation_log.append(entry)
    save_json(mutation_log, MUTATION_LOG_PATH)
    print(f"Mutation Guard: Logged intended mutation for {file_path} in loop {loop_id}")
# --- End Batch 19.2 ---

def execute_file_write(file_path, content):
    """Attempts to write content to a file."""
    # Basic validation
    if not file_path or not os.path.isabs(file_path):
        raise ValueError("Invalid or non-absolute file path provided.")
    
    # Ensure parent directory exists
    parent_dir = os.path.dirname(file_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
        
    with open(file_path, 'w') as f:
        f.write(content)

def process_mutation_request(loop_id, mutation_details):
    """Processes a mutation request, logging intention, attempting execution, and handling basic errors."""
    print(f"Mutation Guard: Received mutation request for loop {loop_id}: {mutation_details}")
    log_guard_event(loop_id, mutation_details, 'attempting')
    
    mutated_files_list = [] # Keep track of files successfully mutated
    mutation_success = False
    mutation_message = ""

    try:
        # --- Batch 19.2: Extract details and Log Intention --- 
        # Assuming mutation_details comes from intent parameters like:
        # "parameters": { "mutation_request": { "action": "write", "file_path": "/path/to/file", "content": "..." } }
        request_params = mutation_details.get("intent_params", {}).get("mutation_request", {})
        action = request_params.get('action')
        file_path = request_params.get('file_path') # Changed from 'file' to 'file_path' based on loop_0014 intent
        content = request_params.get('content')

        if not action or not file_path:
             raise ValueError("Missing 'action' or 'file_path' in mutation request parameters.")

        log_intended_mutation(loop_id, file_path, action)
        # --- End Batch 19.2 ---

        # Basic Role Check (Placeholder - Allow all for now)
        # allowed_roles = ["ArchitectAgent", "DeveloperAgent"] # Example
        # requesting_agent = mutation_details.get("agent_id")
        # if requesting_agent not in allowed_roles:
        #     raise PermissionError(f"Agent '{requesting_agent}' not authorized for mutations.")

        if action == 'write':
            if content is not None:
                execute_file_write(file_path, content)
                print(f"Mutation Guard: Successfully executed write action for {file_path}")
                log_guard_event(loop_id, request_params, 'success') # Log request_params used
                mutated_files_list.append(file_path)
                mutation_success = True
                mutation_message = f"Successfully wrote to {file_path}"
            else:
                raise ValueError("Missing 'content' for write action.")
        # Add other actions like 'append', 'delete' here later
        else:
            raise ValueError(f"Unsupported mutation action: {action}")

    except Exception as e:
        error_message = f"Mutation failed: {type(e).__name__} - {e}"
        print(f"Mutation Guard: {error_message}")
        # print(traceback.format_exc()) # Optional: for more detailed debugging
        log_guard_event(loop_id, request_params, 'failure', reason=error_message) # Log request_params used
        mutation_success = False
        mutation_message = error_message
        # Note: We don't update mutation_log.json status here; controller does that based on overall outcome.

    # Return success status, list of mutated files, and a message
    return mutation_success, mutated_files_list, mutation_message

# Example usage (if run directly) - Updated for new structure
if __name__ == "__main__":
    print("Mutation Guard (Execution Enabled with Intention Logging)")
    # Example request - Success
    example_request_success = {
        "intent_params": {
            "mutation_request": {
                "action": "write",
                "file_path": "/home/ubuntu/test_mutation_success.txt",
                "content": "This is a test mutation executed successfully."
            }
        }
    }
    print("\nTesting successful mutation...")
    process_mutation_request("loop_direct_test_success", example_request_success)

    # Example request - Failure (Invalid Path)
    example_request_fail_path = {
         "intent_params": {
            "mutation_request": {
                "action": "write",
                "file_path": "invalid/relative/path.txt",
                "content": "This should fail."
            }
        }
    }
    print("\nTesting failed mutation (invalid path)...")
    process_mutation_request("loop_direct_test_fail_path", example_request_fail_path)
    
    # Example request - Failure (Permission Denied - simulated)
    example_request_fail_perm = {
         "intent_params": {
            "mutation_request": {
                "action": "write",
                "file_path": "/root/test_mutation_fail_perm.txt", # Assuming no root access
                "content": "This should fail due to permissions."
            }
        }
    }
    print("\nTesting failed mutation (permission error)...")
    process_mutation_request("loop_direct_test_fail_perm", example_request_fail_perm)

    # Clean up success file if created
    if os.path.exists("/home/ubuntu/test_mutation_success.txt"):
        os.remove("/home/ubuntu/test_mutation_success.txt")

