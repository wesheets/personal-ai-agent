"""
HAL Memory Patch Module

This module provides functions for updating project state after HAL agent execution.
It's designed to be imported and used by the HAL agent to ensure memory is properly updated
after task execution, enabling the full agent autonomy loop.
"""

import logging
import traceback
from typing import Dict, Any, List, Optional

# Import project state functions
from app.modules.project_state import update_project_state, increment_loop_count

# Configure logging
logger = logging.getLogger("modules.hal_memory_patch")

def update_hal_memory(
    project_id: str, 
    files_created: List[str] = None, 
    next_step: str = None
) -> Dict[str, Any]:
    """
    Update project state after HAL agent execution.
    
    This function:
    1. Increments the loop_count
    2. Sets last_completed_agent to "hal"
    3. Adds files_created by HAL
    4. Sets a new next_recommended_step
    
    Args:
        project_id: The project identifier
        files_created: List of files created by HAL (optional)
        next_step: The next recommended step (optional, defaults to NOVA)
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        logger.info(f"Updating HAL memory for project: {project_id}")
        print(f"🧠 Updating HAL memory for project: {project_id}")
        
        # Initialize files_created if None
        if files_created is None:
            files_created = []
            
        # Set default next step if None
        if next_step is None:
            next_step = "Run NOVA to build UI components for the project"
            
        # First, increment loop count and update last_completed_agent
        increment_result = increment_loop_count(project_id, "hal")
        
        if increment_result.get("status") != "success":
            error_msg = f"Failed to increment loop count: {increment_result.get('message', 'Unknown error')}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return increment_result
            
        # Next, update files_created and next_recommended_step
        update_dict = {
            "files_created": files_created,
            "next_recommended_step": next_step
        }
        
        update_result = update_project_state(project_id, update_dict)
        
        if update_result.get("status") != "success":
            error_msg = f"Failed to update project state: {update_result.get('message', 'Unknown error')}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return update_result
            
        logger.info(f"HAL memory updated successfully for project: {project_id}")
        print(f"✅ HAL memory updated successfully for project: {project_id}")
        print(f"📋 Files created: {files_created}")
        print(f"➡️ Next recommended step: {next_step}")
        
        return {
            "status": "success",
            "message": "HAL memory updated successfully",
            "project_id": project_id,
            "files_created": files_created,
            "next_recommended_step": next_step
        }
        
    except Exception as e:
        error_msg = f"Error updating HAL memory: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id
        }
