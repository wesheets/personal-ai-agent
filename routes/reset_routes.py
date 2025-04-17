from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Import reset_flags module
try:
    from app.modules.reset_flags import reset_agent_state, reset_project_state, get_reset_status
    RESET_FLAGS_AVAILABLE = True
except ImportError:
    RESET_FLAGS_AVAILABLE = False
    print("❌ reset_flags import failed")

# Create router
router = APIRouter()

class ResetAgentRequest(BaseModel):
    project_id: str
    agent_id: str

class ResetProjectRequest(BaseModel):
    project_id: str
    full_reset: bool = False

@router.post("/reset/agent")
async def api_reset_agent_state(request: ResetAgentRequest) -> Dict[str, Any]:
    """
    Reset the state of a specific agent for a project.
    """
    if not RESET_FLAGS_AVAILABLE:
        raise HTTPException(status_code=500, detail="Reset flags module not available")
    
    result = reset_agent_state(request.project_id, request.agent_id)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
    
    return result

@router.post("/reset/project")
async def api_reset_project_state(request: ResetProjectRequest) -> Dict[str, Any]:
    """
    Reset the state of an entire project.
    """
    if not RESET_FLAGS_AVAILABLE:
        raise HTTPException(status_code=500, detail="Reset flags module not available")
    
    result = reset_project_state(request.project_id, request.full_reset)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
    
    return result

@router.get("/reset/status")
async def api_get_reset_status(project_id: str = Query(..., description="Project ID")) -> Dict[str, Any]:
    """
    Get the reset status of a project.
    """
    if not RESET_FLAGS_AVAILABLE:
        raise HTTPException(status_code=500, detail="Reset flags module not available")
    
    result = get_reset_status(project_id)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
    
    return result
