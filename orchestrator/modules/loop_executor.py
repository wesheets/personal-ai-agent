"""
Loop Executor Module

This module provides functionality to safely execute loops only when all necessary
conditions are met: schema validation, tool availability, and operator confirmation.
"""

import json
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.plan_validator import validate_and_log
from orchestrator.modules.tool_predictor import predict_required_tools, check_tool_availability

def check_loop_execution_readiness(loop_plan: dict) -> tuple:
    """
    Checks if a loop plan is ready for execution by verifying:
    1. It is confirmed by the operator
    2. All required tools are available
    3. It passes schema validation
    
    Args:
        loop_plan (dict): The loop plan to check
        
    Returns:
        tuple: (is_ready, reason, missing_tools)
    """
    if not loop_plan or not isinstance(loop_plan, dict):
        return False, "Invalid loop plan object", []
    
    # Check if the plan is confirmed
    if not loop_plan.get("confirmed", False):
        return False, "Loop plan not confirmed by operator", []
    
    # Validate the plan against the schema
    is_valid, errors, _ = validate_and_log(loop_plan)
    if not is_valid:
        return False, f"Loop plan failed schema validation: {'; '.join(errors)}", []
    
    # Check if all required tools are available
    required_tools = predict_required_tools(loop_plan)
    tool_availability = check_tool_availability(required_tools)
    
    missing_tools = [tool for tool, status in tool_availability.items() if status == "missing"]
    if missing_tools:
        return False, f"Missing required tools: {', '.join(missing_tools)}", missing_tools
    
    # All checks passed
    return True, "All conditions met", []

def prepare_loop_for_execution(project_id: str, loop_plan: dict) -> dict:
    """
    Prepares a loop for execution by checking readiness and logging appropriate messages.
    
    Args:
        project_id (str): The project identifier
        loop_plan (dict): The loop plan to prepare
        
    Returns:
        dict: Status information about the loop preparation
    """
    loop_id = loop_plan.get("loop_id", "unknown")
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Check if the loop is ready for execution
    is_ready, reason, missing_tools = check_loop_execution_readiness(loop_plan)
    
    if is_ready:
        # Create a trace entry for successful kickoff
        trace_entry = {
            "trace_id": f"loop_{loop_id}_kickoff",
            "status": "ready_to_execute",
            "confirmed_by": loop_plan.get("confirmed_by", "operator"),
            "tools": predict_required_tools(loop_plan),
            "timestamp": timestamp
        }
        
        # Log to memory
        log_to_memory(project_id, {"loop_trace": [trace_entry]})
        
        # Log to chat
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"🧠 All systems ready. Loop {loop_id} confirmed. Awaiting agent activation.",
            "timestamp": timestamp
        })
        
        return {
            "loop_id": loop_id,
            "status": "ready",
            "timestamp": timestamp,
            "trace_id": trace_entry["trace_id"]
        }
    else:
        # Create a trace entry for blocked execution
        block_entry = {
            "loop_id": loop_id,
            "status": "blocked",
            "reason": reason,
            "timestamp": timestamp
        }
        
        # Log to memory
        log_to_memory(project_id, {"loop_trace": [block_entry]})
        
        # Log to chat
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"⚠️ Loop {loop_id} execution blocked: {reason}",
            "timestamp": timestamp
        })
        
        # If missing tools, log them for action
        if missing_tools:
            for tool in missing_tools:
                missing_tool_entry = {
                    "loop_id": loop_id,
                    "tool": tool,
                    "status": "missing",
                    "action_required": "generate_tool",
                    "timestamp": timestamp
                }
                log_to_memory(project_id, {"missing_tools": [missing_tool_entry]})
        
        return block_entry

def execute_loop(project_id: str, loop_plan: dict) -> dict:
    """
    Executes a loop only if it passes all readiness checks.
    
    Args:
        project_id (str): The project identifier
        loop_plan (dict): The loop plan to execute
        
    Returns:
        dict: Status information about the loop execution
    """
    # First, check if the loop is ready for execution
    preparation_status = prepare_loop_for_execution(project_id, loop_plan)
    
    if preparation_status["status"] == "ready":
        # In a real implementation, this would trigger the actual loop execution
        # For now, we'll just log that execution would begin
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        execution_start = {
            "loop_id": loop_plan.get("loop_id", "unknown"),
            "status": "execution_started",
            "agents": loop_plan.get("agents", []),
            "timestamp": timestamp
        }
        
        # Log to memory
        log_to_memory(project_id, {"loop_execution": [execution_start]})
        
        # Log to chat
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"🚀 Loop {loop_plan.get('loop_id', 'unknown')} execution started with agents: {', '.join(loop_plan.get('agents', []))}",
            "timestamp": timestamp
        })
        
        return execution_start
    else:
        # Return the preparation status which contains the block reason
        return preparation_status

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

def log_to_chat(project_id: str, message: dict):
    """
    Logs a message to the chat.
    
    Args:
        project_id (str): The project ID
        message (dict): The message to log
    """
    # In a real implementation, this would add the message to the chat
    print(f"Logging to chat for project {project_id}:")
    print(json.dumps(message, indent=2))

if __name__ == "__main__":
    # Example usage
    example_plan = {
        "loop_id": 30,
        "agents": ["hal", "nova", "critic"],
        "goals": ["Create a React component for user profile", "Implement form validation"],
        "planned_files": ["src/components/UserProfile.jsx", "src/utils/validation.js"],
        "confirmed": True,
        "confirmed_by": "operator",
        "confirmed_at": "2025-04-20T12:00:00Z"
    }
    
    project_id = "lifetree_001"
    
    # Test execution
    execution_status = execute_loop(project_id, example_plan)
    
    print("\nExecution status:")
    print(json.dumps(execution_status, indent=2))
