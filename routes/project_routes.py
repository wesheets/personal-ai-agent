from fastapi import APIRouter, Query, HTTPException, Path, Body
from typing import Optional, Dict, Any
from app.modules.project_state import read_project_state, write_project_state
from app.models.project_state import PatchProjectStateRequest

router = APIRouter()

@router.get("/test")
async def test_project_route():
    """
    Simple test endpoint to verify the project router is mounted correctly.
    
    Returns:
        Dict containing a status message
    """
    print("🔍 Test project route accessed")
    return {"status": "Project router mounted successfully", "message": "This is a test endpoint"}

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

@router.get("/{project_id}/status")
async def get_project_status(
    project_id: str = Path(..., description="The project identifier")
):
    """
    Get the live status of a project.
    
    Args:
        project_id: The project identifier (e.g., "loop_validation_001")
        
    Returns:
        Dict containing the project status information
        
    Raises:
        HTTPException: If the project is not found
    """
    try:
        # Add debug logging to trace execution
        print(f"🔍 Project route triggered for: {project_id}")
        
        # Read the project state
        state = read_project_state(project_id)
        
        # Check if project exists
        if not state:
            print(f"🚫 No memory found for: {project_id}")
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Extract required fields
        status = {
            "project_id": project_id,
            "loop_count": state.get("loop_count", 0),
            "last_completed_agent": state.get("last_completed_agent"),
            "completed_steps": state.get("completed_steps", []),
            "files_created": state.get("files_created", []),
            "next_recommended_step": state.get("next_recommended_step", "Operator review or new vertical launch")
        }
        
        # Debug output to help diagnose issues
        print(f"✅ Project status for {project_id}: {status}")
        
        return status
    except Exception as e:
        # Log the error
        print(f"❌ Error getting project status for {project_id}: {str(e)}")
        # Raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Error getting project status: {str(e)}")

# Alternative implementation using query parameter instead of path parameter
@router.get("/status")
async def get_project_status_query(
    project_id: str = Query(..., description="The project identifier")
):
    """
    Get the live status of a project using query parameter.
    
    Args:
        project_id: The project identifier (e.g., "loop_validation_001")
        
    Returns:
        Dict containing the project status information
        
    Raises:
        HTTPException: If the project is not found
    """
    try:
        # Add debug logging to trace execution
        print(f"🔍 Project route (query param) triggered for: {project_id}")
        
        # Read the project state
        state = read_project_state(project_id)
        
        # Check if project exists
        if not state:
            print(f"🚫 No memory found for: {project_id}")
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Extract required fields
        status = {
            "project_id": project_id,
            "loop_count": state.get("loop_count", 0),
            "last_completed_agent": state.get("last_completed_agent"),
            "completed_steps": state.get("completed_steps", []),
            "files_created": state.get("files_created", []),
            "next_recommended_step": state.get("next_recommended_step", "Operator review or new vertical launch")
        }
        
        # Debug output to help diagnose issues
        print(f"✅ Project status (query param) for {project_id}: {status}")
        
        return status
    except Exception as e:
        # Log the error
        print(f"❌ Error getting project status (query param) for {project_id}: {str(e)}")
        # Raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Error getting project status: {str(e)}")

@router.post("/start")
async def project_start(request: Dict[str, Any] = Body(...)):
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
    # Extract required parameters
    project_id = request.get("project_id")
    goal = request.get("goal")
    agent = request.get("agent")
    
    # Add debug logging for project start
    print(f"🧪 Project start triggered: {project_id} {goal} {agent}")
    
    # Validate required parameters
    if not project_id:
        raise HTTPException(status_code=422, detail="project_id is required")
    if not goal:
        # Raise 422 Unprocessable Entity if goal is missing (Fix for Batch 1 validation)
        raise HTTPException(status_code=422, detail="goal is required")
    if not agent:
        raise HTTPException(status_code=422, detail="agent is required")
        
    try:
        # Try to import agent runner
        try:
            from app.api.agent.run import run_agent
            from app.modules.agent_runner import AGENT_RUNNERS
            
            # Validate agent exists in AGENT_RUNNERS
            if agent not in AGENT_RUNNERS:
                raise HTTPException(status_code=422, detail=f"Unknown agent: {agent}")
            
            # Log orchestrator function call
            print(f"⚙️ Calling orchestrator agent...")
            
            try:
                # Run the specified agent
                result = run_agent(
                    agent_id=agent,
                    project_id=project_id,
                    goal=goal,
                    additional_context=request.get("additional_context", {})
                )
                
                # Log orchestrator result
                print(f"✅ Orchestrator result: {result}")
                
                return {
                    "status": "success",
                    "message": f"Project {project_id} started with {agent} agent",
                    "project_id": project_id,
                    "agent": agent,
                    "goal": goal,
                    "result": result
                }
            except Exception as e:
                print(f"❌ Agent execution failed: {e}")
                raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")
        except ImportError as e:
            print(f"❌ Import error: {e}")
            # Fallback if agent runner is not available
            raise HTTPException(status_code=500, detail=f"Failed to import agent runner: {str(e)}")
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions from validation
        raise http_exc
    except Exception as e:
        print(f"❌ Unexpected error in project_start: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start project: {str(e)}")

@router.patch("/state")
async def patch_project_state(payload: PatchProjectStateRequest):
    project_id = payload.project_id
    patch = payload.patch

    state = read_project_state(project_id)
    if not state:
        raise HTTPException(status_code=404, detail="Project not found")

    # Apply patch keys to existing state
    for key, value in patch.items():
        state[key] = value

    write_project_state(project_id, state)
    return {
        "status": "success",
        "message": "Project state updated",
        "project_id": project_id,
        "updated_fields": list(patch.keys())
    }

