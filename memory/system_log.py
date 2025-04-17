import logging
from typing import Dict, List, Any, Optional
import time
from datetime import datetime

# In-memory storage for system log events
system_log = []

def log_event(agent_name: str, event_description: str, project_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Log an event to the system delegation log.
    
    Args:
        agent_name: Name of the agent generating the event (HAL, NOVA, CRITIC, ASH)
        event_description: Description of the event
        project_id: ID of the project this event belongs to
        metadata: Optional additional metadata about the event
        
    Returns:
        The created log entry
    """
    try:
        timestamp = time.time()
        formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = {
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "agent": agent_name,
            "event": event_description,
            "project_id": project_id,
            "metadata": metadata or {}
        }
        
        # Add to in-memory log
        system_log.append(log_entry)
        
        # Also log to standard logger for backup
        logging.info(f"SYSTEM_LOG: {agent_name} - {event_description} - Project: {project_id}")
        
        return log_entry
    except Exception as e:
        logging.error(f"Error logging event: {str(e)}")
        # Return a minimal log entry even if there's an error
        return {
            "timestamp": time.time(),
            "agent": agent_name,
            "event": f"Error logging event: {str(e)}",
            "project_id": project_id
        }

def get_system_log(project_id: Optional[str] = None, limit: int = 100, agent_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve events from the system delegation log.
    
    Args:
        project_id: Optional project ID to filter by
        limit: Maximum number of events to return (default 100)
        agent_filter: Optional agent name to filter by
        
    Returns:
        List of log entries, sorted by timestamp (newest first)
    """
    try:
        # Filter logs based on parameters
        filtered_logs = system_log
        
        if project_id:
            filtered_logs = [log for log in filtered_logs if log["project_id"] == project_id]
            
        if agent_filter:
            filtered_logs = [log for log in filtered_logs if log["agent"].lower() == agent_filter.lower()]
        
        # Sort by timestamp (newest first)
        sorted_logs = sorted(filtered_logs, key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        return sorted_logs[:limit]
    except Exception as e:
        logging.error(f"Error retrieving system log: {str(e)}")
        return []

def clear_system_log() -> bool:
    """
    Clear the system delegation log.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        global system_log
        system_log = []
        return True
    except Exception as e:
        logging.error(f"Error clearing system log: {str(e)}")
        return False
