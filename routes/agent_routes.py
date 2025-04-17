from fastapi import APIRouter
router = APIRouter()

@router.get("/agent/ping")
def agent_ping():
    return {"status": "Agent router recovered"}

@router.post("/agent/run")
async def agent_run(request_data: dict):
    """
    Run an agent with the provided input.
    """
    return {
        "status": "success",
        "message": "Agent run request received",
        "agent": request_data.get("agent", "unknown"),
        "input": request_data.get("input", ""),
        "project_id": request_data.get("project_id", "default")
    }

@router.post("/agent/loop")
async def agent_loop(request_data: dict):
    """
    Continue an agent conversation loop.
    """
    return {
        "status": "success",
        "message": "Agent loop request received",
        "agent": request_data.get("agent", "unknown"),
        "input": request_data.get("input", ""),
        "project_id": request_data.get("project_id", "default")
    }

@router.get("/agent/list")
async def agent_list():
    """
    List all available agents.
    """
    return {
        "status": "success",
        "agents": ["hal", "ash", "nova", "critic", "orchestrator"],
        "message": "Agent list recovered"
    }

@router.post("/agent/delegate")
async def agent_delegate(request_data: dict):
    """
    Delegate a task to an agent.
    """
    return {
        "status": "success",
        "message": "Task delegation request received",
        "agent": request_data.get("agent", "unknown"),
        "task": request_data.get("task", ""),
        "project_id": request_data.get("project_id", "default")
    }
