"""
Loop Trace Logger Module

This module provides functionality to log all events and actions during loop execution,
creating a transparent, replayable cognitive audit trail.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def log_loop_event(project_id: str, loop_id: int, event: dict) -> dict:
    """
    Logs a general event to the loop trace.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        event (dict): The event details to log
        
    Returns:
        dict: The logged event with timestamp added
    """
    if not event:
        return {}
    
    # Ensure event has a timestamp
    if "timestamp" not in event:
        event["timestamp"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Ensure event has the loop_id
    if "loop_id" not in event:
        event["loop_id"] = loop_id
    
    # Log to memory
    log_to_memory(project_id, {"loop_trace": [event]})
    
    return event

def log_agent_action(project_id: str, loop_id: int, agent: str, file: str, 
                    status: str, notes: Optional[str] = None, 
                    log_to_chat: bool = True) -> dict:
    """
    Logs an agent action during loop execution.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        agent (str): The agent that performed the action (e.g., "hal", "nova")
        file (str): The file that was affected
        status (str): The status of the action (e.g., "success", "failed")
        notes (str, optional): Additional notes about the action
        log_to_chat (bool): Whether to also log to chat
        
    Returns:
        dict: The logged event
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create the event object
    event = {
        "type": "agent_execution",
        "loop_id": loop_id,
        "agent": agent,
        "file": file,
        "status": status,
        "timestamp": timestamp
    }
    
    # Add notes if provided
    if notes:
        event["notes"] = notes
    
    # Log to memory
    log_to_memory(project_id, {"loop_trace": [event]})
    
    # Optionally log to chat
    if log_to_chat:
        # Create a user-friendly message
        status_emoji = "✅" if status == "success" else "❌"
        notes_text = f" ({notes})" if notes else ""
        message = f"{status_emoji} Agent {agent.upper()} {status} on {file}{notes_text}"
        
        log_to_chat_messages(project_id, {
            "role": "orchestrator",
            "message": message,
            "timestamp": timestamp
        })
        
        # Optionally update orchestrator sandbox
        update_orchestrator_sandbox(project_id, {
            "agent": agent,
            "file": file,
            "status": status,
            "timestamp": timestamp,
            "message": message
        })
    
    return event

def log_loop_status(project_id: str, loop_id: int, status: str, 
                   reason: Optional[str] = None, 
                   log_to_chat: bool = True) -> dict:
    """
    Logs the overall status of a loop.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        status (str): The status of the loop (e.g., "completed", "aborted", "rerouted")
        reason (str, optional): The reason for the status
        log_to_chat (bool): Whether to also log to chat
        
    Returns:
        dict: The logged event
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create the event object
    event = {
        "type": "loop_status",
        "loop_id": loop_id,
        "status": status,
        "timestamp": timestamp
    }
    
    # Add reason if provided
    if reason:
        event["reason"] = reason
    
    # Log to memory
    log_to_memory(project_id, {"loop_trace": [event]})
    
    # Optionally log to chat
    if log_to_chat:
        # Create a user-friendly message with appropriate emoji
        if status == "completed":
            emoji = "✅"
            message = f"{emoji} Loop {loop_id} completed successfully"
        elif status == "aborted":
            emoji = "❌"
            message = f"{emoji} Loop {loop_id} aborted"
        elif status == "rerouted":
            emoji = "🔄"
            message = f"{emoji} Loop {loop_id} rerouted"
        else:
            emoji = "ℹ️"
            message = f"{emoji} Loop {loop_id} status: {status}"
        
        # Add reason if provided
        if reason:
            message += f" - {reason}"
        
        log_to_chat_messages(project_id, {
            "role": "orchestrator",
            "message": message,
            "timestamp": timestamp
        })
    
    return event

def log_file_operation(project_id: str, loop_id: int, agent: str, file: str, 
                      operation: str, status: str, 
                      notes: Optional[str] = None, 
                      log_to_chat: bool = True) -> dict:
    """
    Logs a file operation during loop execution.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        agent (str): The agent that performed the operation
        file (str): The file that was affected
        operation (str): The operation performed (e.g., "create", "modify", "delete")
        status (str): The status of the operation (e.g., "success", "failed")
        notes (str, optional): Additional notes about the operation
        log_to_chat (bool): Whether to also log to chat
        
    Returns:
        dict: The logged event
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create the event object
    event = {
        "type": "file_operation",
        "loop_id": loop_id,
        "agent": agent,
        "file": file,
        "operation": operation,
        "status": status,
        "timestamp": timestamp
    }
    
    # Add notes if provided
    if notes:
        event["notes"] = notes
    
    # Log to memory
    log_to_memory(project_id, {"loop_trace": [event]})
    
    # Optionally log to chat
    if log_to_chat:
        # Create a user-friendly message
        status_emoji = "✅" if status == "success" else "❌"
        operation_past = {
            "create": "created",
            "modify": "modified",
            "delete": "deleted"
        }.get(operation, operation)
        
        notes_text = f" ({notes})" if notes else ""
        message = f"{status_emoji} Agent {agent.upper()} {operation_past} {file}{notes_text}"
        
        log_to_chat_messages(project_id, {
            "role": "orchestrator",
            "message": message,
            "timestamp": timestamp
        })
    
    return event

def log_validation_event(project_id: str, loop_id: int, agent: str, 
                        file: str, validation_type: str, 
                        status: str, errors: Optional[List[str]] = None, 
                        log_to_chat: bool = True) -> dict:
    """
    Logs a validation event during loop execution.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        agent (str): The agent that performed the validation
        file (str): The file that was validated
        validation_type (str): The type of validation (e.g., "schema", "syntax")
        status (str): The status of the validation (e.g., "passed", "failed")
        errors (list, optional): List of validation errors
        log_to_chat (bool): Whether to also log to chat
        
    Returns:
        dict: The logged event
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create the event object
    event = {
        "type": "validation",
        "loop_id": loop_id,
        "agent": agent,
        "file": file,
        "validation_type": validation_type,
        "status": status,
        "timestamp": timestamp
    }
    
    # Add errors if provided
    if errors:
        event["errors"] = errors
    
    # Log to memory
    log_to_memory(project_id, {"loop_trace": [event]})
    
    # Optionally log to chat
    if log_to_chat:
        # Create a user-friendly message
        status_emoji = "✅" if status == "passed" else "❌"
        message = f"{status_emoji} {validation_type.capitalize()} validation {status} for {file}"
        
        # Add first error if there are any
        if errors and len(errors) > 0:
            message += f" - {errors[0]}"
            if len(errors) > 1:
                message += f" (+{len(errors)-1} more)"
        
        log_to_chat_messages(project_id, {
            "role": "orchestrator",
            "message": message,
            "timestamp": timestamp
        })
    
    return event

def get_loop_trace(project_id: str, loop_id: int) -> List[Dict[str, Any]]:
    """
    Retrieves the full trace for a specific loop.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        
    Returns:
        list: The full trace for the specified loop
    """
    # In a real implementation, this would retrieve data from a database or file
    # For now, we'll just print a message
    print(f"Retrieving trace for loop {loop_id} in project {project_id}")
    
    # Return an empty list for demonstration
    return []

def log_to_memory(project_id: str, data: dict):
    """
    Logs data to project memory.
    
    Args:
        project_id (str): The project ID
        data (dict): The data to log
    """
    # In a real implementation, this would store data in a database or file
    print(f"Logging to memory for project {project_id}:")
    print(json.dumps(data, indent=2))

def log_to_chat_messages(project_id: str, message: dict):
    """
    Logs a message to the chat.
    
    Args:
        project_id (str): The project ID
        message (dict): The message to log
    """
    # In a real implementation, this would add the message to the chat
    print(f"Logging to chat for project {project_id}:")
    print(json.dumps(message, indent=2))

def update_orchestrator_sandbox(project_id: str, data: dict):
    """
    Updates the orchestrator sandbox with real-time data.
    
    Args:
        project_id (str): The project ID
        data (dict): The data to update
    """
    # In a real implementation, this would update the orchestrator sandbox
    print(f"Updating orchestrator sandbox for project {project_id}:")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    # Example usage
    project_id = "lifetree_001"
    loop_id = 30
    
    # Log an agent action
    log_agent_action(project_id, loop_id, "hal", "Timeline.jsx", "success", "File scaffolded")
    
    # Log a file operation
    log_file_operation(project_id, loop_id, "nova", "styles.css", "create", "success")
    
    # Log a validation event
    log_validation_event(project_id, loop_id, "critic", "Timeline.jsx", "schema", "passed")
    
    # Log loop completion
    log_loop_status(project_id, loop_id, "completed")
