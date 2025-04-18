"""
ASH Agent Module

This module provides the routing to the real ASH agent implementation.
"""

import logging
import traceback
from typing import Dict, Any, List, Optional

from app.modules.ash_agent import run_ash_agent as ash_agent_impl

# Configure logging
logger = logging.getLogger("agents.ash")

def run_ash_agent(task: str, project_id: str, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the ASH agent with the given task, project_id, and tools.
    
    This function routes to the real implementation in app.modules.ash_agent.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    try:
        logger.info(f"Routing ASH agent call to real implementation for task: {task}, project_id: {project_id}")
        print(f"📝 Calling real ASH agent implementation for task '{task}' on project '{project_id}'")
        
        # Initialize tools if None
        if tools is None:
            tools = []
        
        # Call the real implementation
        return ash_agent_impl(task, project_id, tools)
    except Exception as e:
        error_msg = f"Error running ASH agent: {str(e)}"
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
