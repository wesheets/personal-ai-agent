"""
HAL Agent Module

This module provides the HAL agent implementation for the agent runner system.
It wraps the functionality from hal_agent.py to provide a consistent interface.
"""

import logging
import traceback
from typing import Dict, Any, List, Optional

# Import the HAL agent implementation
from app.agents.hal_agent import handle_hal_task

# Configure logging
logger = logging.getLogger("agents.hal")

def run_hal_agent(task: str, project_id: str, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the HAL agent with the given task, project_id, and tools.
    
    This function wraps the handle_hal_task function to provide a consistent
    interface for the agent runner system.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    try:
        logger.info(f"Running HAL agent with task: {task}, project_id: {project_id}")
        print(f"🤖 Running HAL agent with task: {task}, project_id: {project_id}")
        
        # Initialize tools if None
        if tools is None:
            tools = []
        
        # Process the task through HAL's handler
        result = handle_hal_task(task)
        
        # Format the response in the expected structure
        return {
            "status": "success",
            "message": f"HAL agent executed successfully for project {project_id}",
            "output": result,
            "task": task,
            "tools": tools,
            "project_id": project_id
        }
    except Exception as e:
        error_msg = f"Error running HAL agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        # Return error response
        return {
            "status": "error",
            "message": error_msg,
            "task": task,
            "tools": tools if tools else [],
            "project_id": project_id
        }
