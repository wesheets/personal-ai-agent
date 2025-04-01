from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.core.task_state_manager import get_task_state_manager

# Define models for API responses
class TaskModel(BaseModel):
    task_id: str
    title: str
    description: Optional[str] = None
    status: str
    assigned_agent: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    dependencies: Optional[List[str]] = None
    retry_count: Optional[int] = 0
    error: Optional[str] = None
    prompt: Optional[str] = None

class GoalModel(BaseModel):
    goal_id: str
    title: str
    description: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    tasks: List[TaskModel]

# Create router
router = APIRouter()

@router.get("/goals", response_model=List[GoalModel])
@router.post("/goals", response_model=List[GoalModel])
async def get_goals():
    """
    Get all active goals with their subtasks
    """
    try:
        task_manager = get_task_state_manager()
        
        # Get all goals
        goals_data = []
        for goal_id, goal in task_manager.goals.items():
            # Get tasks for this goal
            goal_tasks = []
            for task_id, task in task_manager.tasks.items():
                if task.goal_id == goal_id:
                    goal_tasks.append(TaskModel(
                        task_id=task.task_id,
                        title=task.title,
                        description=task.description,
                        status=task.status,
                        assigned_agent=task.assigned_agent,
                        created_at=task.created_at,
                        started_at=task.started_at,
                        completed_at=task.completed_at,
                        dependencies=task.dependencies,
                        retry_count=task.retry_count,
                        error=task.error
                    ))
            
            # Create goal model with tasks
            goals_data.append(GoalModel(
                goal_id=goal.goal_id,
                title=goal.title,
                description=goal.description,
                status=goal.status,
                created_at=goal.created_at,
                completed_at=goal.completed_at,
                tasks=goal_tasks
            ))
        
        return goals_data
    except Exception:
        # Return empty goals list as fallback
        return []

@router.get("/task-state", response_model=Dict[str, Any])
async def get_task_state():
    """
    Get the current state of all tasks
    """
    try:
        task_manager = get_task_state_manager()
        
        # Convert tasks to response model
        tasks_data = []
        for task_id, task in task_manager.tasks.items():
            tasks_data.append(TaskModel(
                task_id=task.task_id,
                title=task.title,
                description=task.description,
                status=task.status,
                assigned_agent=task.assigned_agent,
                created_at=task.created_at,
                started_at=task.started_at,
                completed_at=task.completed_at,
                dependencies=task.dependencies,
                retry_count=task.retry_count,
                error=task.error
            ))
        
        return {"tasks": tasks_data}
    except Exception:
        # Return empty tasks list as fallback
        return {"tasks": []}

@router.post("/task-state/{task_id}/kill")
async def kill_task(task_id: str):
    """
    Kill a running task
    """
    task_manager = get_task_state_manager()
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if task.status != "in_progress":
        raise HTTPException(status_code=400, detail=f"Task {task_id} is not in progress")
    
    # Update task status to killed
    await task_manager.update_task_status(task_id, "killed", error="Task killed by user")
    
    return {"message": f"Task {task_id} killed successfully"}

@router.post("/task-state/{task_id}/restart")
async def restart_task(task_id: str):
    """
    Restart a task
    """
    task_manager = get_task_state_manager()
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if task.status == "in_progress":
        raise HTTPException(status_code=400, detail=f"Task {task_id} is already in progress")
    
    # Reset task status to pending
    await task_manager.update_task_status(task_id, "pending")
    
    return {"message": f"Task {task_id} restarted successfully"}

# Export router
goals_router = router
