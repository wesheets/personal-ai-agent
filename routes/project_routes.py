from fastapi import APIRouter

router = APIRouter()

@router.get("/project/state")
async def get_project_state_route(project_id: str):
    """
    Retrieve the current state of a project as JSON.
    
    Args:
        project_id: The ID of the project to retrieve state for
        
    Returns:
        JSON response with project state data
    """
    from memory.project_state import read_project_state
    try:
        # In a real implementation, this would fetch from a database
        # For now, we'll simulate getting project state
        state = {
            "id": project_id,
            "name": f"Project {project_id}",
            "created_at": "2025-04-17T00:00:00",
            "updated_at": "2025-04-17T01:00:00",
            "status": "active",
            "metadata": {
                "description": f"This is a simulated state for project {project_id}",
                "version": "1.0.0"
            },
            "resources": [
                {"type": "document", "name": "README.md", "path": f"/projects/{project_id}/README.md"},
                {"type": "code", "name": "main.py", "path": f"/projects/{project_id}/main.py"}
            ]
        }
        
        return {
            "status": "success",
            "state": state
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not retrieve project state: {str(e)}"
        }
