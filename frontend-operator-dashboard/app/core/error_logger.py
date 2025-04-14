"""
Error memory logger for capturing and logging agent exceptions.
"""
import logging
import datetime
import traceback
from typing import Dict, Any, Optional
from app.agents.memory_agent import handle_memory_task

logger = logging.getLogger("error_logger")

def log_agent_error(agent_name: str, error_message: str, error_obj: Optional[Exception] = None) -> Dict[str, Any]:
    """
    Log an agent error to the memory system.
    
    Args:
        agent_name: The name of the agent that encountered the error
        error_message: A descriptive error message
        error_obj: The actual exception object (optional)
        
    Returns:
        A dictionary containing the logged error details
    """
    # Get current timestamp
    timestamp = datetime.datetime.now().isoformat()
    
    # Format the error message
    formatted_message = f"LOG: ERROR — agent: {agent_name} — message: '{error_message}' — time: {timestamp}"
    
    # Log to console
    logger.error(formatted_message)
    
    # Create structured error data
    error_data = {
        "timestamp": timestamp,
        "agent": agent_name,
        "error": error_message,
        "type": "error"
    }
    
    # Add stack trace if exception object is provided
    if error_obj:
        stack_trace = traceback.format_exception(type(error_obj), error_obj, error_obj.__traceback__)
        error_data["stack_trace"] = "".join(stack_trace)
    
    # Log to memory agent in both formats
    handle_memory_task(formatted_message)
    
    # Also log structured format
    try:
        import json
        structured_log = f"STRUCTURED_LOG:{json.dumps(error_data)}"
        handle_memory_task(structured_log)
    except Exception as e:
        logger.error(f"Failed to log structured error: {str(e)}")
    
    return error_data
