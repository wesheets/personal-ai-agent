"""
Project Memory Module

This module provides project memory management functionality for the application.
It maintains a global dictionary of project memories that can be accessed by other modules.
"""

from typing import Dict, Any
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("memory.project_memory")

# Global project memory dictionary
# This dictionary stores all project-related memory objects
# Structure: {project_id: {key: value}}
PROJECT_MEMORY: Dict[str, Dict[str, Any]] = {}


def initialize_project_memory(project_id: str) -> None:
    """
    Initialize project memory for a given project ID if it doesn't exist.
    
    Args:
        project_id: The project identifier
    """
    if project_id not in PROJECT_MEMORY:
        PROJECT_MEMORY[project_id] = {
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "loop_count": 1,
            "completed_steps": [],
            "orchestrator_decisions": [],
            "reflections": [],
            "orchestrator_execution_log": [],
            "deviation_logs": [],
            "reroute_trace": [],
            "operator_actions": [],
            "loop_complete": False,
            "next_recommended_agent": None,
            "autospawn": False
        }
        logger.info(f"Initialized project memory for project {project_id}")


def get_project_memory(project_id: str) -> Dict[str, Any]:
    """
    Get the memory for a specific project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The project memory dictionary
        
    Raises:
        KeyError: If the project doesn't exist
    """
    if project_id not in PROJECT_MEMORY:
        raise KeyError(f"Project {project_id} not found in memory")
    
    return PROJECT_MEMORY[project_id]


def update_project_memory(project_id: str, key: str, value: Any) -> None:
    """
    Update a specific key in the project memory.
    
    Args:
        project_id: The project identifier
        key: The key to update
        value: The value to set
        
    Raises:
        KeyError: If the project doesn't exist
    """
    if project_id not in PROJECT_MEMORY:
        raise KeyError(f"Project {project_id} not found in memory")
    
    PROJECT_MEMORY[project_id][key] = value
    PROJECT_MEMORY[project_id]["last_updated"] = datetime.utcnow().isoformat()
    logger.debug(f"Updated {key} for project {project_id}")


def clear_project_memory(project_id: str) -> None:
    """
    Clear the memory for a specific project.
    
    Args:
        project_id: The project identifier
        
    Raises:
        KeyError: If the project doesn't exist
    """
    if project_id not in PROJECT_MEMORY:
        raise KeyError(f"Project {project_id} not found in memory")
    
    PROJECT_MEMORY.pop(project_id)
    logger.info(f"Cleared memory for project {project_id}")


def list_projects() -> list:
    """
    List all projects in memory.
    
    Returns:
        List of project IDs
    """
    return list(PROJECT_MEMORY.keys())
