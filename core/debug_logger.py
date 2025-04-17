import datetime
import os

def log_test_result(module: str, endpoint: str, status: str, result: str, notes: str = ""):
    """
    Logs test results to the debug_tracker.md file.
    
    Args:
        module: The module being tested (e.g., "Delegation", "Memory")
        endpoint: The API endpoint being tested (e.g., "/api/delegate")
        status: The status of the test (e.g., "PASS", "FAIL")
        result: The result of the test
        notes: Additional notes about the test (optional)
    """
    timestamp = datetime.datetime.now().isoformat()
    
    # Determine the path to the debug_tracker.md file
    # First check if it exists in the logs directory
    debug_tracker_path = os.path.join(os.getcwd(), "logs", "debug_tracker.md")
    if not os.path.exists(debug_tracker_path):
        # If not in logs directory, check project root
        debug_tracker_path = os.path.join(os.getcwd(), "debug_tracker.md")
    
    # Create log entry
    log_entry = f"| {timestamp} | {module} | {endpoint} | {status} | {result} | {notes} |\n"
    
    # Append log entry to debug_tracker.md
    with open(debug_tracker_path, "a") as f:
        f.write(log_entry)
