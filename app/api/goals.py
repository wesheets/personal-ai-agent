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
async def get_goals():
    """
    Get all active goals with their subtasks
    """
    try:
        # Get task manager with error handling
        try:
            task_manager = get_task_state_manager()
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error getting task state manager: {str(e)}")
            return []  # Return empty list if task manager can't be initialized
        
        # Validate task_manager has required attributes
        if not hasattr(task_manager, 'goals') or not hasattr(task_manager, 'tasks'):
            import logging
            logger = logging.getLogger("api")
            logger.error("Task manager missing required attributes (goals or tasks)")
            return []
            
        # Get all goals
        goals_data = []
        
        # Safely iterate through goals
        try:
            goals_items = task_manager.goals.items() if hasattr(task_manager.goals, 'items') else []
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error accessing goals: {str(e)}")
            goals_items = []
            
        for goal_id, goal in goals_items:
            # Skip invalid goals
            if not goal:
                continue
                
            # Get tasks for this goal with defensive programming
            goal_tasks = []
            
            # Safely iterate through tasks
            try:
                tasks_items = task_manager.tasks.items() if hasattr(task_manager.tasks, 'items') else []
            except Exception as e:
                import logging
                logger = logging.getLogger("api")
                logger.error(f"Error accessing tasks: {str(e)}")
                tasks_items = []
                
            for task_id, task in tasks_items:
                # Skip invalid tasks
                if not task:
                    continue
                    
                # Check if task belongs to this goal
                try:
                    task_goal_id = getattr(task, 'goal_id', None)
                    if task_goal_id != goal_id:
                        continue
                except Exception:
                    continue
                
                # Create task model with safe attribute access
                try:
                    goal_tasks.append(TaskModel(
                        task_id=getattr(task, 'task_id', task_id),
                        title=getattr(task, 'title', 'Untitled Task'),
                        description=getattr(task, 'description', None),
                        status=getattr(task, 'status', 'unknown'),
                        assigned_agent=getattr(task, 'assigned_agent', None),
                        created_at=getattr(task, 'created_at', ''),
                        started_at=getattr(task, 'started_at', None),
                        completed_at=getattr(task, 'completed_at', None),
                        dependencies=getattr(task, 'dependencies', None),
                        retry_count=getattr(task, 'retry_count', 0),
                        error=getattr(task, 'error', None)
                    ))
                except Exception as e:
                    import logging
                    logger = logging.getLogger("api")
                    logger.error(f"Error creating task model: {str(e)}")
                    # Continue to next task
            
            # Create goal model with safe attribute access
            try:
                goals_data.append(GoalModel(
                    goal_id=getattr(goal, 'goal_id', goal_id),
                    title=getattr(goal, 'title', 'Untitled Goal'),
                    description=getattr(goal, 'description', ''),
                    status=getattr(goal, 'status', 'unknown'),
                    created_at=getattr(goal, 'created_at', ''),
                    completed_at=getattr(goal, 'completed_at', None),
                    tasks=goal_tasks
                ))
            except Exception as e:
                import logging
                logger = logging.getLogger("api")
                logger.error(f"Error creating goal model: {str(e)}")
                # Continue to next goal
        
        return goals_data
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger("api")
        logger.error(f"Error in get_goals: {str(e)}")
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
        for task_key, task in task_manager.tasks.items():
            # The task is now a simple dictionary with agent, task_id, state, updated_at
            tasks_data.append({
                "task_id": task["task_id"],
                "agent": task["agent"],
                "state": task["state"],
                "updated_at": task["updated_at"]
            })
        
        return {"tasks": tasks_data}
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger("api")
        logger.error(f"Error getting task state: {str(e)}")
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
