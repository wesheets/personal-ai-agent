"""
Debug Routes Module

This module provides debug endpoints for inspecting the state of the application,
particularly for development and troubleshooting purposes.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional

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


# Operator Override Routes

# Create a separate router for operator routes
operator_router = APIRouter(prefix="/api/operator", tags=["operator"])


@operator_router.post("/override/next-agent")
def override_next_agent(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Override the next recommended agent for a project.
    
    Args:
        payload: Dict containing:
            - project_id: The project identifier
            - agent: The agent to set as next recommended
            - reason: (Optional) The reason for the override
            
    Returns:
        Dict containing the override action record
        
    Raises:
        HTTPException: If the project doesn't exist or payload is invalid
    """
    # Validate payload
    if "project_id" not in payload:
        raise HTTPException(status_code=400, detail="Missing project_id in payload")
    
    if "agent" not in payload:
        raise HTTPException(status_code=400, detail="Missing agent in payload")
    
    # Check if project exists
    project_id = payload["project_id"]
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Import set_next_agent function
    from app.modules.orchestrator_logic import set_next_agent
    
    # Set next agent
    result = set_next_agent(
        project_id=project_id,
        agent=payload["agent"],
        reason=payload.get("reason", "manual override")
    )
    
    return result


@operator_router.post("/override/loop-complete")
def override_loop_complete(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Override the loop complete status for a project.
    
    Args:
        payload: Dict containing:
            - project_id: The project identifier
            - status: The loop complete status to set (True or False)
            
    Returns:
        Dict containing the override action record
        
    Raises:
        HTTPException: If the project doesn't exist or payload is invalid
    """
    # Validate payload
    if "project_id" not in payload:
        raise HTTPException(status_code=400, detail="Missing project_id in payload")
    
    if "status" not in payload:
        raise HTTPException(status_code=400, detail="Missing status in payload")
    
    # Check if project exists
    project_id = payload["project_id"]
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Import force_loop_complete function
    from app.modules.orchestrator_logic import force_loop_complete
    
    # Force loop complete status
    result = force_loop_complete(
        project_id=project_id,
        status=payload["status"]
    )
    
    return result


@operator_router.post("/override/loop-skip")
def override_loop_skip(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Force a loop skip by marking the current loop as complete and starting a new one.
    
    Args:
        payload: Dict containing:
            - project_id: The project identifier
            - reason: (Optional) The reason for the loop skip
            
    Returns:
        Dict containing the override action record
        
    Raises:
        HTTPException: If the project doesn't exist or payload is invalid
    """
    # Validate payload
    if "project_id" not in payload:
        raise HTTPException(status_code=400, detail="Missing project_id in payload")
    
    # Check if project exists
    project_id = payload["project_id"]
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Import force_loop_skip function
    from app.modules.orchestrator_logic import force_loop_skip
    
    # Force loop skip
    result = force_loop_skip(
        project_id=project_id,
        reason=payload.get("reason", "manual loop skip")
    )
    
    return result


@operator_router.post("/override/loop-reroute")
def override_loop_reroute(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Force a loop reroute by setting the next recommended agent and creating a reroute trace.
    
    Args:
        payload: Dict containing:
            - project_id: The project identifier
            - agent: The agent to reroute to
            - reason: (Optional) The reason for the reroute
            
    Returns:
        Dict containing the override action record
        
    Raises:
        HTTPException: If the project doesn't exist or payload is invalid
    """
    # Validate payload
    if "project_id" not in payload:
        raise HTTPException(status_code=400, detail="Missing project_id in payload")
    
    if "agent" not in payload:
        raise HTTPException(status_code=400, detail="Missing agent in payload")
    
    # Check if project exists
    project_id = payload["project_id"]
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Import force_loop_reroute function
    from app.modules.orchestrator_logic import force_loop_reroute
    
    # Force loop reroute
    result = force_loop_reroute(
        project_id=project_id,
        agent=payload["agent"],
        reason=payload.get("reason", "manual loop reroute")
    )
    
    return result


@operator_router.get("/actions/{project_id}")
def get_operator_actions(project_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Get the operator actions for a project.
    
    Args:
        project_id: The project identifier
        limit: Optional limit on the number of actions to return (most recent first)
        
    Returns:
        Dict containing the operator actions
        
    Raises:
        HTTPException: If the project doesn't exist
    """
    # Check if project exists
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Import get_operator_actions function
    from app.modules.orchestrator_logic import get_operator_actions
    
    # Get operator actions
    actions = get_operator_actions(project_id, limit)
    
    return {"operator_actions": actions, "count": len(actions)}


# Include the operator router in the main app
# This would typically be done in the main app file, but for this example
# we'll assume it's included when this module is imported
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)
app.include_router(operator_router)
