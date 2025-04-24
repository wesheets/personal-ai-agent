"""
Project State Module
This module provides functionality for tracking and persisting the evolving state of a vertical build.
It maintains a centralized record of project status, files created, agents involved, and other metadata.

MODIFIED: Added auto-expiration of orphaned projects after 24h of inactivity
MODIFIED: Added get_project_state alias for read_project_state to maintain compatibility
"""
import logging
import json
import os
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Configure logging
logger = logging.getLogger("app.modules.project_state")

def read_project_state(project_id: str) -> Dict[str, Any]:
    """
    Read the current state of a project.
    
    Args:
        project_id: The project identifier (e.g., "demo_writer_001")
            
    Returns:
        Dict containing the current project state
    """
    try:
        # Define the path to the project state file
        state_file = os.path.join(os.path.dirname(__file__), "project_states", f"{project_id}.json")
        
        # Check if the file exists
        if not os.path.exists(state_file):
            # Return a default state if no state exists yet
            logger.info(f"No existing state found for project {project_id}, returning default state")
            return {
                "project_id": project_id,
                "status": "initialized",
                "files_created": [],
                "agents_involved": [],
                "latest_agent_action": None,
                "next_recommended_step": "Run HAL to create initial files",
                "tool_usage": {},
                "timestamp": datetime.utcnow().isoformat(),
                "last_updated_at": datetime.utcnow().isoformat(),
                "last_agent_triggered_at": datetime.utcnow().isoformat(),
                "loop_status": "initialized",
                # Agent Loop Autonomy Core - New fields
                "loop_count": 0,
                "max_loops": 5,
                "last_completed_agent": None,
                "completed_steps": []
            }
        
        # Read the state from the file
        with open(state_file, 'r') as f:
            state = json.load(f)
            logger.info(f"Project state read for {project_id}")
            
            # Ensure all required fields exist (for backward compatibility)
            if "loop_count" not in state:
                state["loop_count"] = 0
            if "max_loops" not in state:
                state["max_loops"] = 5
            if "last_completed_agent" not in state:
                state["last_completed_agent"] = None
            if "completed_steps" not in state:
                state["completed_steps"] = []
            if "last_updated_at" not in state:
                state["last_updated_at"] = datetime.utcnow().isoformat()
            if "last_agent_triggered_at" not in state:
                state["last_agent_triggered_at"] = datetime.utcnow().isoformat()
            if "loop_status" not in state:
                state["loop_status"] = "initialized"
                
            return state
            
    except Exception as e:
        error_msg = f"Error reading project state for {project_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        # Return a default state in case of error
        return {
            "project_id": project_id,
            "status": "error",
            "files_created": [],
            "agents_involved": [],
            "latest_agent_action": None,
            "next_recommended_step": "Retry after resolving error",
            "tool_usage": {},
            "timestamp": datetime.utcnow().isoformat(),
            "last_updated_at": datetime.utcnow().isoformat(),
            "last_agent_triggered_at": datetime.utcnow().isoformat(),
            "loop_status": "error",
            "error": str(e),
            # Agent Loop Autonomy Core - New fields
            "loop_count": 0,
            "max_loops": 5,
            "last_completed_agent": None,
            "completed_steps": []
        }

# Add alias for read_project_state to maintain compatibility
def get_project_state(project_id: str) -> Dict[str, Any]:
    """
    Alias for read_project_state to maintain compatibility with existing code.
    
    Args:
        project_id: The project identifier (e.g., "demo_writer_001")
            
    Returns:
        Dict containing the current project state
    """
    logger.info(f"Using get_project_state alias for project {project_id}")
    return read_project_state(project_id)

def write_project_state(project_id: str, state_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write a complete project state.
    
    Args:
        project_id: The project identifier (e.g., "demo_writer_001")
        state_dict: Dictionary containing the complete project state
            
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Ensure the project states directory exists
        states_dir = os.path.join(os.path.dirname(__file__), "project_states")
        os.makedirs(states_dir, exist_ok=True)
        
        # Define the path to the project state file
        state_file = os.path.join(states_dir, f"{project_id}.json")
        
        # Ensure project_id is included in the state
        state_dict["project_id"] = project_id
        
        # Update timestamp
        state_dict["timestamp"] = datetime.utcnow().isoformat()
        state_dict["last_updated_at"] = datetime.utcnow().isoformat()
        
        # Write the state to the file
        with open(state_file, 'w') as f:
            json.dump(state_dict, f, indent=2)
        
        logger.info(f"Project state written for {project_id}")
        print(f"✅ Project state updated for {project_id}")
        
        return {
            "status": "success",
            "message": f"Project state updated for {project_id}",
            "project_id": project_id
        }
            
    except Exception as e:
        error_msg = f"Error writing project state for {project_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def update_project_state(project_id: str, patch_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update specific fields in the project state.
    
    Args:
        project_id: The project identifier (e.g., "demo_writer_001")
        patch_dict: Dictionary containing the fields to update
            
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Read the current state
        current_state = read_project_state(project_id)
        
        # Handle special cases for array fields that should be appended to
        if "files_created" in patch_dict and isinstance(patch_dict["files_created"], list):
            # Add new files to the list without duplicates
            existing_files = set(current_state.get("files_created", []))
            for file in patch_dict["files_created"]:
                if file not in existing_files:
                    existing_files.add(file)
            current_state["files_created"] = list(existing_files)
            # Remove from patch_dict since we've handled it
            del patch_dict["files_created"]
            
        if "agents_involved" in patch_dict and isinstance(patch_dict["agents_involved"], list):
            # Add new agents to the list without duplicates
            existing_agents = set(current_state.get("agents_involved", []))
            for agent in patch_dict["agents_involved"]:
                if agent not in existing_agents:
                    existing_agents.add(agent)
            current_state["agents_involved"] = list(existing_agents)
            # Remove from patch_dict since we've handled it
            del patch_dict["agents_involved"]
        
        # Handle tool_usage updates
        if "tool_usage" in patch_dict and isinstance(patch_dict["tool_usage"], dict):
            current_tool_usage = current_state.get("tool_usage", {})
            for tool, count in patch_dict["tool_usage"].items():
                current_tool_usage[tool] = current_tool_usage.get(tool, 0) + count
            current_state["tool_usage"] = current_tool_usage
            # Remove from patch_dict since we've handled it
            del patch_dict["tool_usage"]
            
        # Handle completed_steps updates (Agent Loop Autonomy Core)
        if "completed_steps" in patch_dict and isinstance(patch_dict["completed_steps"], list):
            existing_steps = current_state.get("completed_steps", [])
            for step in patch_dict["completed_steps"]:
                if step not in existing_steps:
                    existing_steps.append(step)
            current_state["completed_steps"] = existing_steps
            # Remove from patch_dict since we've handled it
            del patch_dict["completed_steps"]
            
        # Handle loop_count increment (Agent Loop Autonomy Core)
        if "increment_loop_count" in patch_dict and patch_dict["increment_loop_count"]:
            current_state["loop_count"] = current_state.get("loop_count", 0) + 1
            # Remove from patch_dict since we've handled it
            del patch_dict["increment_loop_count"]
        
        # Update the remaining fields
        for key, value in patch_dict.items():
            current_state[key] = value
        
        # Always update last_updated_at timestamp
        current_state["last_updated_at"] = datetime.utcnow().isoformat()
        
        # Write the updated state
        return write_project_state(project_id, current_state)
            
    except Exception as e:
        error_msg = f"Error updating project state for {project_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def increment_loop_count(project_id: str, agent_id: str) -> Dict[str, Any]:
    """
    Increment the loop count and update the last completed agent for a project.
    
    Args:
        project_id: The project identifier (e.g., "demo_writer_001")
        agent_id: The agent that just completed (e.g., "hal", "nova")
            
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Read the current state
        current_state = read_project_state(project_id)
        
        # Increment loop count
        current_state["loop_count"] = current_state.get("loop_count", 0) + 1
        
        # Update last completed agent
        current_state["last_completed_agent"] = agent_id
        
        # Add to completed steps
        completed_steps = current_state.get("completed_steps", [])
        if agent_id not in completed_steps:
            completed_steps.append(agent_id)
        current_state["completed_steps"] = completed_steps
        
        # Add to agents involved
        agents_involved = current_state.get("agents_involved", [])
        if agent_id not in agents_involved:
            agents_involved.append(agent_id)
        current_state["agents_involved"] = agents_involved
        
        # Update timestamps
        current_state["last_updated_at"] = datetime.utcnow().isoformat()
        current_state["last_agent_triggered_at"] = datetime.utcnow().isoformat()
        
        # Write the updated state
        return write_project_state(project_id, current_state)
            
    except Exception as e:
        error_msg = f"Error incrementing loop count for {project_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def should_continue_loop(project_id: str) -> bool:
    """
    Check if the agent loop should continue for a project.
    
    Args:
        project_id: The project identifier (e.g., "demo_writer_001")
            
    Returns:
        Boolean indicating whether the loop should continue
    """
    try:
        # Read the current state
        current_state = read_project_state(project_id)
        
        # Check if status is complete
        if current_state.get("status") == "complete":
            logger.info(f"Loop stopped for {project_id}: status is complete")
            return False
        
        # Check if loop count has reached max loops
        loop_count = current_state.get("loop_count", 0)
        max_loops = current_state.get("max_loops", 5)
        
        if loop_count >= max_loops:
            logger.info(f"Loop stopped for {project_id}: reached max loops ({loop_count}/{max_loops})")
            return False
        
        # If neither condition is met, continue the loop
        logger.info(f"Loop continuing for {project_id}: loop count {loop_count}/{max_loops}")
        return True
            
    except Exception as e:
        error_msg = f"Error checking loop continuation for {project_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        # Default to stopping the loop in case of error
        return False

# Add alias for read_project_state to maintain compatibility
def get_project_state(project_id: str) -> Dict[str, Any]:
    """
    Alias for read_project_state to maintain compatibility with existing code.
    
    Args:
        project_id: The project identifier (e.g., "demo_writer_001")
            
    Returns:
        Dict containing the project state
    """
    logger.info(f"Using get_project_state alias for project {project_id}")
    print(f"✅ Using get_project_state alias for project {project_id}")
    return read_project_state(project_id)

def cleanup_orphaned_projects() -> Dict[str, Any]:
    """
    Clean up orphaned projects that haven't been updated in 24 hours.
    
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Get the project states directory
        states_dir = os.path.join(os.path.dirname(__file__), "project_states")
        if not os.path.exists(states_dir):
            logger.info("No project states directory found, nothing to clean up")
            return {
                "status": "success",
                "message": "No project states directory found, nothing to clean up",
                "deleted_projects": []
            }
        
        # Get all project state files
        project_files = [f for f in os.listdir(states_dir) if f.endswith('.json')]
        
        deleted_projects = []
        current_time = datetime.utcnow()
        
        for project_file in project_files:
            try:
                # Extract project_id from filename
                project_id = project_file.replace('.json', '')
                
                # Read the project state
                project_state = read_project_state(project_id)
                
                # Check if the project has been updated in the last 24 hours
                last_updated_at = project_state.get("last_updated_at")
                if last_updated_at:
                    try:
                        last_updated_time = datetime.fromisoformat(last_updated_at)
                        time_diff = current_time - last_updated_time
                        
                        # If more than 24 hours have passed, delete the project
                        if time_diff > timedelta(hours=24):
                            logger.info(f"Deleting orphaned project {project_id}. Last updated: {last_updated_at}")
                            print(f"🧹 Deleting orphaned project {project_id}. Last updated: {last_updated_at}")
                            
                            # Delete the project state file
                            os.remove(os.path.join(states_dir, project_file))
                            deleted_projects.append(project_id)
                    except Exception as e:
                        logger.error(f"Error parsing last_updated_at for project {project_id}: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing project file {project_file}: {str(e)}")
        
        logger.info(f"Cleanup completed. Deleted {len(deleted_projects)} orphaned projects.")
        print(f"✅ Cleanup completed. Deleted {len(deleted_projects)} orphaned projects.")
        
        return {
            "status": "success",
            "message": f"Cleanup completed. Deleted {len(deleted_projects)} orphaned projects.",
            "deleted_projects": deleted_projects
        }
            
    except Exception as e:
        error_msg = f"Error cleaning up orphaned projects: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "error": str(e),
            "deleted_projects": []
        }
