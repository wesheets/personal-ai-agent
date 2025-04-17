from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
from app.modules.project_state import read_project_state

router = APIRouter()


@router.get("/state")
async def get_project_state(
    project_id: str = Query(..., description="The project identifier")
):
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


@router.post("/start")
async def project_start(request: Dict[str, Any]):
    """
    Start a new project or resume an existing project.
    
    Args:
        request: Dictionary containing project parameters
            - project_id: The project identifier
            - goal: The project goal
            - agent: The agent to use (e.g., "orchestrator")
            
    Returns:
        Dict containing the project start status and details
    """
    try:
        # Extract required parameters
        project_id = request.get("project_id")
        goal = request.get("goal")
        agent = request.get("agent")
        
        # Validate required parameters
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")
        if not goal:
            raise HTTPException(status_code=400, detail="goal is required")
        if not agent:
            raise HTTPException(status_code=400, detail="agent is required")
        
        # Try to import agent runner
        try:
            from app.api.agent.run import run_agent
            
            # Run the specified agent
            result = run_agent(
                agent_id=agent,
                project_id=project_id,
                goal=goal,
                additional_context=request.get("additional_context", {})
            )
            
            return {
                "status": "success",
                "message": f"Project {project_id} started with {agent} agent",
                "project_id": project_id,
                "agent": agent,
                "goal": goal,
                "result": result
            }
        except ImportError:
            # Fallback if agent runner is not available
            return {
                "status": "success",
                "message": f"Project {project_id} start request received (fallback implementation)",
                "project_id": project_id,
                "agent": agent,
                "goal": goal
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to start project: {str(e)}",
            "error_details": str(e)
        }
