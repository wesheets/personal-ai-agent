from fastapi import APIRouter, HTTPException
from app.memory import PROJECT_MEMORY
from app.agents.cto_agent import analyze_system_trends

router = APIRouter(prefix="/api/debug/cto")

@router.get("/reflection/{project_id}")
def get_cto_reflection(project_id: str):
    """
    Get the most recent CTO reflection for a project.
    
    Args:
        project_id (str): The ID of the project
        
    Returns:
        dict: The most recent CTO reflection
    """
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    cto_reflections = PROJECT_MEMORY[project_id].get("cto_reflections", [])
    
    if not cto_reflections:
        return {"message": "No CTO reflections found for this project"}
    
    return cto_reflections[-1]

@router.get("/reflections/{project_id}")
def get_all_cto_reflections(project_id: str):
    """
    Get all CTO reflections for a project.
    
    Args:
        project_id (str): The ID of the project
        
    Returns:
        list: All CTO reflections for the project
    """
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    return PROJECT_MEMORY[project_id].get("cto_reflections", [])

@router.get("/flags/{project_id}")
def get_system_flags(project_id: str):
    """
    Get all system flags for a project.
    
    Args:
        project_id (str): The ID of the project
        
    Returns:
        list: All system flags for the project
    """
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    return PROJECT_MEMORY[project_id].get("system_flags", [])

@router.get("/system-health/{project_id}")
def get_system_health(project_id: str):
    """
    Get the system health analysis for a project.
    Triggers a new analysis of system trends.
    
    Args:
        project_id (str): The ID of the project
        
    Returns:
        dict: System health analysis with score and issues
    """
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    return analyze_system_trends(project_id)

@router.get("/audit-history/{project_id}")
def get_audit_history(project_id: str):
    """
    Get the CTO audit history for a project.
    
    Args:
        project_id (str): The ID of the project
        
    Returns:
        list: CTO audit history for the project
    """
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    return PROJECT_MEMORY[project_id].get("cto_audit_history", [])

@router.get("/warnings/{project_id}")
def get_cto_warnings(project_id: str):
    """
    Get all CTO warnings for a project.
    
    Args:
        project_id (str): The ID of the project
        
    Returns:
        list: All CTO warnings for the project
    """
    if project_id not in PROJECT_MEMORY:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    return PROJECT_MEMORY[project_id].get("cto_warnings", [])
