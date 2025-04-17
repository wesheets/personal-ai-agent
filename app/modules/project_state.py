"""
Project State Module
This module provides functionality for tracking and persisting the evolving state of a vertical build.
It maintains a centralized record of project status, files created, agents involved, and other metadata.
"""
import logging
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

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
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Read the state from the file
        with open(state_file, 'r') as f:
            state = json.load(f)
            logger.info(f"Project state read for {project_id}")
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
            "error": str(e)
        }

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
        
        # Update the remaining fields
        for key, value in patch_dict.items():
            current_state[key] = value
        
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
