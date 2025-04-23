"""
HAL Agent Module
This module provides the HAL agent implementation for the agent runner system.
"""
import logging
import traceback
from typing import Dict, Any, List, Optional
import datetime

# Import the memory patch module
from app.modules.hal_memory_patch import update_hal_memory

# Import code generation module
from app.modules.code_generation.hal_code_generator import process_build_task

# Configure logging
logger = logging.getLogger("agents.hal")

def run_hal_agent(task: str, project_id: str, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the HAL agent with the given task, project_id, and tools.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    try:
        logger.info(f"Running HAL agent with task: {task}, project_id: {project_id}")
        print(f"🟥 HAL agent executing task '{task}' on project '{project_id}'")
        
        # Initialize tools if None
        if tools is None:
            tools = []
        
        # Check if this is a code generation task
        if "code_generation" in tools:
            # For code generation tasks, we'll return a placeholder
            # The actual code generation happens in the loop_routes.py endpoint
            # which calls process_build_task
            files_created = [f"Generated code for {project_id}"]
            next_step = "Run NOVA to build UI components based on HAL's implementation"
        else:
            # Simulate HAL's work - in a real implementation, this would be actual task execution
            # For demonstration purposes, we'll assume HAL created some files
            files_created = ["api/crm.py", "README.md"]
            
            # Determine next recommended step based on the task
            if "ui" in task.lower() or "interface" in task.lower():
                next_step = "Run NOVA to build UI components based on HAL's implementation"
            elif "document" in task.lower() or "documentation" in task.lower():
                next_step = "Run ASH to document the implementation created by HAL"
            elif "review" in task.lower() or "evaluate" in task.lower():
                next_step = "Run CRITIC to review the implementation created by HAL"
            else:
                # Default next step
                next_step = "Run NOVA to build UI components for the project"
        
        # Update project state in memory
        memory_result = update_hal_memory(
            project_id=project_id,
            files_created=files_created,
            next_step=next_step
        )
        
        if memory_result.get("status") != "success":
            logger.warning(f"Memory update warning: {memory_result.get('message', 'Unknown issue')}")
            print(f"⚠️ Memory update warning: {memory_result.get('message', 'Unknown issue')}")
        
        # Return success response
        return {
            "status": "success",
            "message": f"HAL agent executed successfully for project {project_id}",
            "output": f"HAL executed task '{task}'",
            "task": task,
            "tools": tools,
            "project_id": project_id,
            "files_created": files_created,
            "next_recommended_step": next_step
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
