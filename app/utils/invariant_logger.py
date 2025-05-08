import json
import os
from datetime import datetime

INVARIANT_VIOLATION_LOG_PATH = "/home/ubuntu/personal-ai-agent/app/logs/invariant_violation_log.json"

class InvariantLogger:
    def __init__(self, log_file_path=INVARIANT_VIOLATION_LOG_PATH):
        self.log_file_path = log_file_path
        # Ensure the directory for the log file exists
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

    def log_violation(self, component: str, invariant_id: str, details: str, proposed_action: dict, status: str = "logged_only"):
        """
        Logs an invariant violation to the specified log file.

        Args:
            component (str): The system component that detected the violation.
            invariant_id (str): The ID of the invariant that was violated.
            details (str): A human-readable description of the violation and the context.
            proposed_action (dict): The action that was being attempted when the violation was detected.
            status (str): Indicates if the action was 'prevented' or 'logged_only'. Defaults to 'logged_only'.
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        violation_entry = {
            "timestamp": timestamp,
            "component": component,
            "invariant_id": invariant_id,
            "details": details,
            "proposed_action": proposed_action,
            "status": status
        }

        log_data = []
        if os.path.exists(self.log_file_path):
            try:
                with open(self.log_file_path, "r") as f:
                    # Handle empty or invalid JSON file
                    content = f.read()
                    if content.strip(): # Check if file is not empty
                        log_data = json.loads(content)
                        if not isinstance(log_data, list):
                            print(f"Warning: Log file {self.log_file_path} does not contain a JSON array. Reinitializing as an empty list.")
                            log_data = [] # Reinitialize if not a list
                    else:
                        log_data = [] # Initialize as empty list if file is empty
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {self.log_file_path}. The file might be corrupted or not a valid JSON array. Reinitializing as an empty list.")
                log_data = [] # Reinitialize if decode error
            except Exception as e:
                print(f"Error reading log file {self.log_file_path}: {e}. Reinitializing as an empty list.")
                log_data = []
        
        log_data.append(violation_entry)

        try:
            with open(self.log_file_path, "w") as f:
                json.dump(log_data, f, indent=2)
            print(f"Successfully logged invariant violation to {self.log_file_path}")
        except IOError as e:
            print(f"Error: Could not write to log file at {self.log_file_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while writing to log file: {e}")

if __name__ == "__main__":
    # Example usage (for testing the logger directly)
    logger = InvariantLogger()
    
    # Ensure the logs directory exists for the example
    os.makedirs("/home/ubuntu/personal-ai-agent/app/logs/", exist_ok=True)

    logger.log_violation(
        component="test_script.py",
        invariant_id="TEST_INVARIANT_001",
        details="This is a test violation for demonstration purposes.",
        proposed_action={"action_type": "test_action", "parameters": {"param1": "value1"}},
        status="logged_only"
    )

    logger.log_violation(
        component="another_module.py",
        invariant_id="TEST_INVARIANT_002",
        details="Another test violation with different details.",
        proposed_action={"action_type": "another_action", "data": [1, 2, 3]},
        status="logged_only"
    )

    # Test reading and appending to an existing log
    if os.path.exists(INVARIANT_VIOLATION_LOG_PATH):
        with open(INVARIANT_VIOLATION_LOG_PATH, "r") as f:
            print(f"\nCurrent content of {INVARIANT_VIOLATION_LOG_PATH}:\n{f.read()}")

