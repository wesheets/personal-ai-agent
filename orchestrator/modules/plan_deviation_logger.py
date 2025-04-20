"""
Plan Deviation Logger Module

This module provides functionality to log instances where loop execution
diverges from the original plan, creating transparent cognitive drift memory.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def log_plan_deviation(project_id: str, loop_id: int, cause: str, affected: Dict[str, str], 
                       resolution: Optional[str] = None, log_to_chat: bool = True) -> dict:
    """
    Logs when execution diverges from the original plan.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        cause (str): The cause of the deviation (e.g., "schema_validation_failed")
        affected (dict): The affected entities (e.g., {"agent": "nova", "file": "FormLogic.jsx"})
        resolution (str, optional): How the deviation was resolved
        log_to_chat (bool): Whether to also log to chat
        
    Returns:
        dict: The logged deviation event
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create the deviation event
    deviation = {
        "loop_id": loop_id,
        "type": "plan_deviation",
        "cause": cause,
        "affected": affected,
        "timestamp": timestamp
    }
    
    # Add resolution if provided
    if resolution:
        deviation["resolution"] = resolution
    
    # Log to loop trace
    log_to_memory(project_id, {"loop_trace": [deviation]})
    
    # Log to consolidated plan deviations
    log_to_memory(project_id, {"plan_deviations": [deviation]})
    
    # Optionally log to chat
    if log_to_chat:
        # Create a user-friendly message based on the cause
        if cause == "schema_validation_failed":
            emoji = "❌"
            message = f"{emoji} Schema validation failed for {affected.get('file', 'unknown file')}"
        elif cause == "syntax_validation_failed":
            emoji = "❌"
            message = f"{emoji} Syntax validation failed for {affected.get('file', 'unknown file')}"
        elif cause == "critic_rejection":
            emoji = "🧠"
            message = f"{emoji} CRITIC rejected {affected.get('file', 'unknown file')}"
        elif cause == "tool_unavailable":
            emoji = "⚠️"
            message = f"{emoji} Tool {affected.get('tool', 'unknown tool')} not found"
        else:
            emoji = "⚠️"
            message = f"{emoji} Plan deviation: {cause}"
        
        # Add resolution if provided
        if resolution:
            message += f". {resolution}"
        
        log_to_chat_messages(project_id, {
            "role": "orchestrator",
            "message": message,
            "timestamp": timestamp
        })
        
        # Log to CTO warnings for serious issues
        if cause in ["critic_rejection", "tool_unavailable", "schema_validation_failed"]:
            log_to_cto_warnings(project_id, {
                "type": "plan_deviation",
                "message": message,
                "details": deviation,
                "timestamp": timestamp
            })
    
    return deviation

def log_operator_override(project_id: str, loop_id: int, override_type: str, 
                         context: Dict[str, Any], log_to_chat: bool = True) -> dict:
    """
    Logs when an operator manually overrides the execution plan.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        override_type (str): The type of override (e.g., "agent_reroute", "file_modification")
        context (dict): The context of the override
        log_to_chat (bool): Whether to also log to chat
        
    Returns:
        dict: The logged override event
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create the override event
    override = {
        "loop_id": loop_id,
        "type": "operator_override",
        "override_type": override_type,
        "context": context,
        "timestamp": timestamp
    }
    
    # Log to loop trace
    log_to_memory(project_id, {"loop_trace": [override]})
    
    # Log to consolidated plan deviations
    log_to_memory(project_id, {"plan_deviations": [override]})
    
    # Optionally log to chat
    if log_to_chat:
        # Create a user-friendly message based on the override type
        emoji = "🧑"
        
        if override_type == "agent_reroute":
            from_agent = context.get("from", "unknown")
            to_agent = context.get("to", "unknown")
            reason = context.get("reason", "")
            
            message = f"{emoji} Operator replaced {from_agent.upper()} with {to_agent.upper()} for agent task"
            if reason:
                message += f". Reason: {reason}"
            message += ". Loop updated."
            
        elif override_type == "file_modification":
            file = context.get("file", "unknown file")
            message = f"{emoji} Operator modified {file}. Loop updated."
            
        elif override_type == "plan_adjustment":
            message = f"{emoji} Operator adjusted the loop plan. Loop updated."
            
        else:
            message = f"{emoji} Operator override: {override_type}. Loop updated."
        
        log_to_chat_messages(project_id, {
            "role": "orchestrator",
            "message": message,
            "timestamp": timestamp
        })
    
    return override

def log_missing_tool_deviation(project_id: str, loop_id: int, tool_name: str, 
                              agent: str, fallback: Optional[str] = None, 
                              log_to_chat: bool = True) -> dict:
    """
    Logs when a required tool is unavailable.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        tool_name (str): The name of the missing tool
        agent (str): The agent that requires the tool
        fallback (str, optional): The fallback solution
        log_to_chat (bool): Whether to also log to chat
        
    Returns:
        dict: The logged deviation event
    """
    # Create affected entity information
    affected = {
        "tool": tool_name,
        "agent": agent
    }
    
    # Create resolution message if fallback provided
    resolution = f"Agent rerouted to use {fallback}" if fallback else "No fallback available"
    
    # Log using the general deviation logger
    return log_plan_deviation(
        project_id=project_id,
        loop_id=loop_id,
        cause="tool_unavailable",
        affected=affected,
        resolution=resolution,
        log_to_chat=log_to_chat
    )

def log_validation_failure(project_id: str, loop_id: int, validation_type: str, 
                          file: str, agent: str, errors: List[str],
                          resolution: Optional[str] = None, 
                          log_to_chat: bool = True) -> dict:
    """
    Logs when a file fails validation.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        validation_type (str): The type of validation that failed (e.g., "schema", "syntax")
        file (str): The file that failed validation
        agent (str): The agent that created the file
        errors (list): The validation errors
        resolution (str, optional): How the failure was resolved
        log_to_chat (bool): Whether to also log to chat
        
    Returns:
        dict: The logged deviation event
    """
    # Create affected entity information
    affected = {
        "file": file,
        "agent": agent,
        "errors": errors
    }
    
    # Determine the cause based on validation type
    if validation_type == "schema":
        cause = "schema_validation_failed"
    elif validation_type == "syntax":
        cause = "syntax_validation_failed"
    else:
        cause = f"{validation_type}_validation_failed"
    
    # Create resolution message if not provided
    if not resolution and len(errors) > 0:
        resolution = f"Failed with error: {errors[0]}"
    
    # Log using the general deviation logger
    return log_plan_deviation(
        project_id=project_id,
        loop_id=loop_id,
        cause=cause,
        affected=affected,
        resolution=resolution,
        log_to_chat=log_to_chat
    )

def log_critic_rejection(project_id: str, loop_id: int, file: str, 
                        agent: str, reason: str,
                        resolution: Optional[str] = None, 
                        log_to_chat: bool = True) -> dict:
    """
    Logs when CRITIC rejects work.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        file (str): The file that was rejected
        agent (str): The agent that created the file
        reason (str): The reason for rejection
        resolution (str, optional): How the rejection was resolved
        log_to_chat (bool): Whether to also log to chat
        
    Returns:
        dict: The logged deviation event
    """
    # Create affected entity information
    affected = {
        "file": file,
        "agent": agent,
        "reason": reason
    }
    
    # Create resolution message if not provided
    if not resolution:
        resolution = "Loop rerouted to another agent"
    
    # Log using the general deviation logger
    return log_plan_deviation(
        project_id=project_id,
        loop_id=loop_id,
        cause="critic_rejection",
        affected=affected,
        resolution=resolution,
        log_to_chat=log_to_chat
    )

def get_plan_deviations(project_id: str, loop_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retrieves plan deviations for a project or specific loop.
    
    Args:
        project_id (str): The project identifier
        loop_id (int, optional): The loop identifier to filter by
        
    Returns:
        list: The plan deviations
    """
    # In a real implementation, this would retrieve data from a database or file
    # For now, we'll just print a message
    if loop_id:
        print(f"Retrieving plan deviations for loop {loop_id} in project {project_id}")
    else:
        print(f"Retrieving all plan deviations for project {project_id}")
    
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

def log_to_cto_warnings(project_id: str, warning: dict):
    """
    Logs a warning to the CTO warnings.
    
    Args:
        project_id (str): The project ID
        warning (dict): The warning to log
    """
    # In a real implementation, this would add the warning to the CTO warnings
    print(f"Logging to CTO warnings for project {project_id}:")
    print(json.dumps(warning, indent=2))

if __name__ == "__main__":
    # Example usage
    project_id = "lifetree_001"
    loop_id = 30
    
    # Log a schema validation failure
    log_validation_failure(
        project_id=project_id,
        loop_id=loop_id,
        validation_type="schema",
        file="FormLogic.jsx",
        agent="nova",
        errors=["Missing required field 'onSubmit'"],
        resolution="Rerouted to HAL"
    )
    
    # Log an operator override
    log_operator_override(
        project_id=project_id,
        loop_id=loop_id,
        override_type="agent_reroute",
        context={
            "from": "nova",
            "to": "hal",
            "reason": "Incorrect logic in review"
        }
    )
    
    # Log a missing tool
    log_missing_tool_deviation(
        project_id=project_id,
        loop_id=loop_id,
        tool_name="form_validator",
        agent="nova",
        fallback="manual_validation"
    )
    
    # Log a CRITIC rejection
    log_critic_rejection(
        project_id=project_id,
        loop_id=loop_id,
        file="Timeline.jsx",
        agent="nova",
        reason="Component does not follow design system",
        resolution="Loop rerouted to HAL"
    )
