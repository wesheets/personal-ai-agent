"""
Debug Routes Module

This module provides debug endpoints for inspecting the state of the application,
particularly for development and troubleshooting purposes.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# Import PROJECT_MEMORY
from app.memory.project_memory import PROJECT_MEMORY

# Create router
router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/orchestrator/reflection/{project_id}")
def get_last_reflection(project_id: str) -> Dict[str, Any]:
    """
    Get the last reflection for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The last reflection record
        
    Raises:
        HTTPException: If the project doesn't exist or has no reflection
    """
    # Check if project exists
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Get the last reflection
    last_reflection = PROJECT_MEMORY[project_id].get("last_reflection")
    
    # Check if reflection exists
    if not last_reflection:
        raise HTTPException(status_code=404, detail=f"No reflection found for project {project_id}")
    
    return last_reflection


@router.get("/orchestrator/reflections/{project_id}")
def get_all_reflections(project_id: str) -> Dict[str, Any]:
    """
    Get all reflections for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing all reflection records
        
    Raises:
        HTTPException: If the project doesn't exist
    """
    # Check if project exists
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Get all reflections
    reflections = PROJECT_MEMORY[project_id].get("reflections", [])
    
    return {"reflections": reflections, "count": len(reflections)}


@router.get("/orchestrator/decisions/{project_id}")
def get_orchestrator_decisions(project_id: str) -> Dict[str, Any]:
    """
    Get all orchestrator decisions for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing all decision records
        
    Raises:
        HTTPException: If the project doesn't exist
    """
    # Check if project exists
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Get all decisions
    decisions = PROJECT_MEMORY[project_id].get("orchestrator_decisions", [])
    
    return {"decisions": decisions, "count": len(decisions)}


@router.get("/orchestrator/execution/{project_id}")
def get_orchestrator_exec_log(project_id: str) -> Dict[str, Any]:
    """
    Get all execution log entries for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing all execution log entries
        
    Raises:
        HTTPException: If the project doesn't exist
    """
    # Check if project exists
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Get all execution log entries
    execution_log = PROJECT_MEMORY[project_id].get("orchestrator_execution_log", [])
    
    return {"execution_log": execution_log, "count": len(execution_log)}


@router.get("/orchestrator/deviation/{project_id}")
def check_deviation(project_id: str) -> Dict[str, Any]:
    """
    Check for deviations in the project state that might require intervention.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing identified issues, empty if no issues found
        
    Raises:
        HTTPException: If the project doesn't exist
    """
    # Check if project exists
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Import detect_deviation function
    from app.modules.orchestrator_logic import detect_deviation
    
    # Detect deviations
    issues = detect_deviation(project_id)
    
    return {
        "issues": issues,
        "has_deviations": bool(issues),
        "timestamp": PROJECT_MEMORY[project_id].get("last_check_time", None)
    }


@router.get("/orchestrator/reroute/{project_id}")
def get_reroute_trace(project_id: str) -> Dict[str, Any]:
    """
    Get the reroute trace for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the reroute trace
        
    Raises:
        HTTPException: If the project doesn't exist
    """
    # Check if project exists
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Get reroute trace
    from app.modules.orchestrator_logic import get_reroute_trace
    reroute_trace = get_reroute_trace(project_id)
    
    return {"reroute_trace": reroute_trace, "count": len(reroute_trace)}


@router.get("/memory/{project_id}")
def get_project_memory(project_id: str) -> Dict[str, Any]:
    """
    Get the entire memory for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The project memory
        
    Raises:
        HTTPException: If the project doesn't exist
    """
    # Check if project exists
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    return PROJECT_MEMORY[project_id]
