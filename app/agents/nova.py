"""
NOVA Agent Module

This module provides the implementation for the NOVA agent by calling the real run_nova_agent function.
"""

import logging
import traceback
from typing import Dict, Any, List, Optional

# Import the real NOVA agent implementation
from app.modules.nova_agent import run_nova_agent as nova_agent_impl

# Configure logging
logger = logging.getLogger("agents.nova")

def run_nova_agent(task: str, project_id: str, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the NOVA agent with the given task, project_id, and tools.
    
    This function calls the real NOVA agent implementation from app.modules.nova_agent.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    try:
        logger.info(f"Running NOVA agent with task: {task}, project_id: {project_id}")
        print(f"🚀 Calling real NOVA agent implementation for task '{task}' on project '{project_id}'")
        
        # Initialize tools if None
        if tools is None:
            tools = []
        
        # Call the real NOVA agent implementation
        result = nova_agent_impl(task, project_id, tools)
        
        # Log success
        logger.info(f"NOVA agent executed successfully for project {project_id}")
        print(f"✅ NOVA agent executed successfully for project {project_id}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error running NOVA agent: {str(e)}"
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
