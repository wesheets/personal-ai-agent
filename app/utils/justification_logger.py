"""
Utility function for logging agent justifications.
"""

import json
import os
from datetime import datetime

# Define path relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JUSTIFICATION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_justification_log.json")

def log_justification(loop_id: str, agent_id: str, action_decision: str, justification_text: str, confidence_score: float):
    """Appends a justification entry to the log file."""
    entry = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat() + "Z", # Add Z for UTC
        "agent_id": agent_id,
        "action_decision": action_decision,
        "justification_text": justification_text,
        "confidence_score": confidence_score
    }
    
    try:
        # Load existing log or initialize
        try:
            with open(JUSTIFICATION_LOG_PATH, 'r') as f:
                content = f.read()
                log_data = json.loads(content) if content else []
        except FileNotFoundError:
            log_data = []
        except json.JSONDecodeError:
            print(f"Warning: Error decoding {JUSTIFICATION_LOG_PATH}. Reinitializing.")
            log_data = []

        if not isinstance(log_data, list):
            print(f"Warning: {JUSTIFICATION_LOG_PATH} is not a list. Reinitializing.")
            log_data = []

        # Append new entry
        log_data.append(entry)

        # Save updated log
        os.makedirs(os.path.dirname(JUSTIFICATION_LOG_PATH), exist_ok=True)
        with open(JUSTIFICATION_LOG_PATH, 'w') as f:
            json.dump(log_data, f, indent=2)
            f.write('\n')
        print(f"Successfully logged justification for agent: {agent_id} in loop: {loop_id}")

    except Exception as e:
        print(f"Error logging justification for agent {agent_id}: {e}")

