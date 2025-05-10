import json
import os
import time
import datetime

CONFIG_PATH = "/home/ubuntu/personal-ai-agent/app/memory/operator_dashboard_config.json"

# --- Utility Functions ---
def load_json_safely(file_path, default_value=None):
    """Safely loads a JSON file, returning a default value if file not found or JSON is invalid."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        # print(f"Warning: File {file_path} not found or empty. Returning default.")
        return default_value if default_value is not None else [] # Default to list for most logs
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}. Returning default.")
        return default_value if default_value is not None else []
    except Exception as e:
        print(f"Error reading {file_path}: {e}. Returning default.")
        return default_value if default_value is not None else []

def get_metric_count(file_path):
    """Counts the number of entries in a JSON list file."""
    data = load_json_safely(file_path, default_value=[])
    return len(data) if isinstance(data, list) else 0

def get_active_loops_count(file_path):
    """Counts active loops from loop_summary.json (simplified)."""
    # This is a simplified interpretation. A real loop_summary might have status fields.
    # For now, we assume each entry is an active or recently completed loop.
    data = load_json_safely(file_path, default_value=[])
    return len(data) if isinstance(data, list) else 0

def get_latest_trust_score(file_path):
    """Gets the latest trust score from agent_trust_score.json."""
    data = load_json_safely(file_path, default_value=[])
    if isinstance(data, list) and data:
        # Assuming entries are timestamped and the last one is the latest
        # Or if it's a single object in a list, or just the object itself
        latest_entry = data[-1]
        if isinstance(latest_entry, dict):
            return latest_entry.get("trust_score", "N/A") # Or a more specific field
    return "N/A"

def get_drift_metric(file_path):
    """Gets a representative drift metric from legacy_alignment_tracker.json."""
    data = load_json_safely(file_path, default_value=[])
    if isinstance(data, list) and data:
        latest_entry = data[-1]
        if isinstance(latest_entry, dict):
            # Example: looking for a specific drift value or summary
            return latest_entry.get("overall_alignment_drift", "N/A") 
    return "N/A"

def display_log_tail(log_path, display_name, max_lines):
    """Displays the tail of a log file (assuming JSON list of entries)."""
    print(f"\n--- {display_name} (Last {max_lines} entries) ---")
    log_data = load_json_safely(log_path, default_value=[])
    if not isinstance(log_data, list):
        print("  Log data is not in list format.")
        return
    if not log_data:
        print("  No entries found.")
        return
    
    for entry in log_data[-max_lines:]:
        # Basic pretty print for an entry, can be customized
        if isinstance(entry, dict):
            timestamp = entry.get("timestamp", "No Timestamp")
            loop_id = entry.get("loop_id", "N/A")
            summary = entry.get("error_message", entry.get("summary", entry.get("action_taken", "No summary")))
            print(f"  [{timestamp}] Loop: {loop_id} - {summary[:100]}") # Truncate long summaries
        else:
            print(f"  {str(entry)[:120]}")

# --- Main Dashboard Logic ---
def display_dashboard(config):
    """Displays the metrics and logs based on the configuration."""
    os.system('cls' if os.name == 'nt' else 'clear') # Clear screen
    print("=== Manus AI Agent Status Dashboard ===")
    print(f"Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    metrics_config = config.get("system_status_metrics", {})
    
    print("--- Key System Metrics ---")
    if metrics_config.get("active_loops", {}).get("enabled"):
        count = get_active_loops_count(metrics_config["active_loops"].get("source_file"))
        print(f"  Active Loops: {count}")
        
    if metrics_config.get("trust_scores", {}).get("enabled"):
        score = get_latest_trust_score(metrics_config["trust_scores"].get("source_file"))
        print(f"  Latest Trust Score: {score}")
        
    if metrics_config.get("error_counts", {}).get("enabled"):
        count = get_metric_count(metrics_config["error_counts"].get("source_file"))
        print(f"  Total Runtime Errors: {count}")
        
    if metrics_config.get("escalation_counts", {}).get("enabled"):
        count = get_metric_count(metrics_config["escalation_counts"].get("source_file"))
        print(f"  Total Operator Escalations: {count}")
        
    if metrics_config.get("drift_metrics", {}).get("enabled"):
        drift = get_drift_metric(metrics_config["drift_metrics"].get("source_file"))
        print(f"  Overall Alignment Drift: {drift}")

    log_settings = config.get("log_aggregation_settings", {})
    if log_settings.get("enabled") and log_settings.get("log_files_to_monitor"):
        for log_info in log_settings["log_files_to_monitor"]:
            display_log_tail(log_info["path"], log_info["display_name"], log_info.get("max_lines_to_show", 10))
    
    print("\n=====================================")

if __name__ == "__main__":
    print("Starting Operator Dashboard Tool...")
    config_data = load_json_safely(CONFIG_PATH, default_value=None)
    
    if not config_data or not isinstance(config_data, dict):
        print(f"Error: Could not load or parse configuration from {CONFIG_PATH}. Exiting.")
        exit(1)
    
    if not config_data.get("system_status_metrics"):
        print("Warning: 'system_status_metrics' not found in config. Some features may not work.")

    refresh_interval = config_data.get("display_refresh_interval_seconds", 5)
    
    try:
        while True:
            display_dashboard(config_data)
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("\nDashboard stopped by user. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

