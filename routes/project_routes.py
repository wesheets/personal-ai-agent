from fastapi import APIRouter, Query
from typing import Optional
from app.modules.project_state import read_project_state

router = APIRouter()

@router.get("/project/state")
async def get_project_state(project_id: str = Query(..., description="The project identifier")):
    """
    Get the current state of a project.
    
    Args:
        project_id: The project identifier (e.g., "demo_writer_001")
            
    Returns:
        Dict containing the current project state
    """
    # Read the project state
    state = read_project_state(project_id)
    
    # Return the state
    return state
