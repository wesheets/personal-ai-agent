from fastapi import APIRouter, HTTPException
from app.memory import PROJECT_MEMORY

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
