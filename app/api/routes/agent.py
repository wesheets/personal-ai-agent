from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

router = APIRouter()

class TaskPayload(BaseModel):
    id: str
    type: str
    input: str

class AgentTaskRequest(BaseModel):
    agent_id: str
    task: TaskPayload

@router.post("/api/agent/delegate")
async def delegate_task(request: AgentTaskRequest, background_tasks: BackgroundTasks):
    print(f"[DELEGATE] Background task starting for {request.task.id}")
    background_tasks.add_task(run_task, request)
    return {"message": "Task delegation started"}

def run_task(request: AgentTaskRequest):
    print(f"[TOOL EXECUTION] Agent {request.agent_id} executing tool task: {request.task.type}")
