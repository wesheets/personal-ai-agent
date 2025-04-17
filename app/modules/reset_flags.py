"""
Intelligent Reset Flags Module

This module provides functionality for resetting agent state when needed,
allowing for intelligent recovery from errors or inconsistent states.
"""
import logging
import json
import os
import time
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger("app.modules.reset_flags")

# Import project_state for tracking project status
try:
    from app.modules.project_state import read_project_state, update_project_state
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    print("❌ project_state import failed")

# Import agent_retry for retry and recovery flow
try:
    from app.modules.agent_retry import get_retry_status, mark_agent_retry_attempted
    AGENT_RETRY_AVAILABLE = True
except ImportError:
    AGENT_RETRY_AVAILABLE = False
    print("❌ agent_retry import failed")

def reset_agent_state(project_id: str, agent_id: str) -> Dict[str, Any]:
    """
    Reset the state of a specific agent for a project.
    
    Args:
        project_id: The project identifier
        agent_id: The agent identifier
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        if not PROJECT_STATE_AVAILABLE:
            error_msg = "Project state not available, cannot reset agent state"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "agent_id": agent_id
            }
        
        # Read current project state
        project_state = read_project_state(project_id)
        
        # Check if agent is in agents_involved
        if agent_id not in project_state.get("agents_involved", []):
            return {
                "status": "success",
                "message": f"Agent {agent_id} not found in project state, nothing to reset",
                "project_id": project_id,
                "agent_id": agent_id
            }
        
        # Reset agent-specific state
        update_data = {
            "latest_agent_action": {
                "agent": agent_id,
                "action": f"State reset for {agent_id}"
            }
        }
        
        # Handle agent-specific reset logic
        if agent_id == "hal":
            # For HAL, we might want to reset README.md creation flag
            if "files_created" in project_state:
                files_created = project_state.get("files_created", [])
                if "README.md" in files_created:
                    files_created.remove("README.md")
                    update_data["files_created"] = files_created
        
        elif agent_id == "nova":
            # For NOVA, we might want to reset frontend creation flag
            if "frontend_created" in project_state:
                update_data["frontend_created"] = False
        
        elif agent_id == "critic":
            # For CRITIC, we might want to reset review status
            if "review_complete" in project_state:
                update_data["review_complete"] = False
        
        elif agent_id == "ash":
            # For ASH, we might want to reset documentation status
            if "documentation_complete" in project_state:
                update_data["documentation_complete"] = False
        
        # Reset any blocked status for this agent
        if AGENT_RETRY_AVAILABLE:
            retry_status = get_retry_status(project_id, agent_id)
            if retry_status and retry_status.get("status") in ["blocked", "unblocked"]:
                mark_agent_retry_attempted(project_id, agent_id)
                update_data["unblocked_agents"] = [agent_id]
        
        # Update project state
        result = update_project_state(project_id, update_data)
        
        if result.get("status") == "success":
            logger.info(f"Reset state for agent {agent_id} in project {project_id}")
            print(f"🔄 Reset state for agent {agent_id} in project {project_id}")
            return {
                "status": "success",
                "message": f"Reset state for agent {agent_id}",
                "project_id": project_id,
                "agent_id": agent_id,
                "reset_data": update_data
            }
        else:
            error_msg = f"Error updating project state: {result.get('error', 'unknown error')}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "agent_id": agent_id
            }
        
    except Exception as e:
        error_msg = f"Error resetting agent state for {agent_id} in project {project_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "agent_id": agent_id,
            "error": str(e)
        }

def reset_project_state(project_id: str, full_reset: bool = False) -> Dict[str, Any]:
    """
    Reset the state of an entire project.
    
    Args:
        project_id: The project identifier
        full_reset: Whether to perform a full reset (clear all state) or a partial reset
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        if not PROJECT_STATE_AVAILABLE:
            error_msg = "Project state not available, cannot reset project state"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id
            }
        
        # Read current project state
        project_state = read_project_state(project_id)
        
        if full_reset:
            # For full reset, we create a new empty state
            update_data = {
                "agents_involved": [],
                "files_created": [],
                "latest_agent_action": {
                    "agent": "system",
                    "action": f"Full project state reset for {project_id}"
                },
                "status": "initialized",
                "reset_timestamp": time.time()
            }
        else:
            # For partial reset, we keep some metadata but reset agent-specific state
            agents_involved = project_state.get("agents_involved", [])
            update_data = {
                "agents_involved": agents_involved,
                "files_created": project_state.get("files_created", []),
                "latest_agent_action": {
                    "agent": "system",
                    "action": f"Partial project state reset for {project_id}"
                },
                "status": "reset",
                "reset_timestamp": time.time()
            }
            
            # Reset agent-specific flags
            if "hal" in agents_involved:
                update_data["hal_complete"] = False
            if "nova" in agents_involved:
                update_data["frontend_created"] = False
            if "critic" in agents_involved:
                update_data["review_complete"] = False
            if "ash" in agents_involved:
                update_data["documentation_complete"] = False
        
        # Update project state
        result = update_project_state(project_id, update_data)
        
        if result.get("status") == "success":
            logger.info(f"Reset project state for {project_id} (full_reset={full_reset})")
            print(f"🔄 Reset project state for {project_id} (full_reset={full_reset})")
            return {
                "status": "success",
                "message": f"Reset project state for {project_id}",
                "project_id": project_id,
                "full_reset": full_reset,
                "reset_data": update_data
            }
        else:
            error_msg = f"Error updating project state: {result.get('error', 'unknown error')}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id
            }
        
    except Exception as e:
        error_msg = f"Error resetting project state for {project_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def get_reset_status(project_id: str) -> Dict[str, Any]:
    """
    Get the reset status of a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the reset status
    """
    try:
        if not PROJECT_STATE_AVAILABLE:
            error_msg = "Project state not available, cannot get reset status"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id
            }
        
        # Read current project state
        project_state = read_project_state(project_id)
        
        # Check if project has been reset
        if "reset_timestamp" in project_state:
            reset_timestamp = project_state.get("reset_timestamp")
            reset_type = "full" if project_state.get("status") == "initialized" else "partial"
            
            return {
                "status": "success",
                "message": f"Project {project_id} was reset at {reset_timestamp}",
                "project_id": project_id,
                "reset_status": "reset",
                "reset_timestamp": reset_timestamp,
                "reset_type": reset_type
            }
        else:
            return {
                "status": "success",
                "message": f"Project {project_id} has not been reset",
                "project_id": project_id,
                "reset_status": "not_reset"
            }
        
    except Exception as e:
        error_msg = f"Error getting reset status for {project_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }
