from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.orchestrator import get_orchestrator

# Define models for API requests and responses
class ControlModeModel(BaseModel):
    mode: str  # 'auto', 'manual', or 'paused'

class AgentStatusModel(BaseModel):
    id: str
    name: str
    type: str
    status: str
    current_task: Optional[Dict[str, Any]] = None
    completion_state: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None
    retry_count: int = 0
    metrics: Optional[Dict[str, Any]] = None

class AgentStatusResponseModel(BaseModel):
    agents: List[AgentStatusModel]

class TaskModel(BaseModel):
    description: str
    priority: str
    agent_type: str

class TaskDelegationModel(BaseModel):
    task_id: str
    target_agent: str
    task: TaskModel

class EditPromptModel(BaseModel):
    prompt: str

# Create router
router = APIRouter()

@router.get("/system/control-mode", response_model=Dict[str, Any])
async def get_control_mode():
    """
    Get the current system control mode and active agents
    """
    orchestrator = get_orchestrator()
    
    # Get current mode from orchestrator
    mode = orchestrator.execution_mode
    
    # Get list of active agents
    active_agents = orchestrator.prompt_manager.get_available_agents()
    
    return {
        "mode": mode,
        "active_agents": active_agents
    }

@router.post("/system/control-mode", response_model=Dict[str, str])
async def set_control_mode(mode_data: ControlModeModel):
    """
    Set the system control mode
    """
    orchestrator = get_orchestrator()
    
    # Validate mode
    if mode_data.mode not in ["auto", "manual", "paused"]:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode_data.mode}")
    
    # Set mode in orchestrator
    orchestrator.execution_mode = mode_data.mode
    
    return {"message": f"Control mode set to {mode_data.mode}"}

@router.get("/agent/status", response_model=AgentStatusResponseModel)
async def get_agent_status():
    """
    Get status of all active agents
    """
    import logging
    logger = logging.getLogger("api")
    
    try:
        logger.info("Fetching agent status")
        orchestrator = get_orchestrator()
        
        # Get agent status from orchestrator
        agents_data = []
        
        # Simplified implementation to avoid potential errors
        for agent_name in orchestrator.prompt_manager.get_available_agents():
            try:
                # Get agent config - handle potential errors
                try:
                    agent_config = orchestrator.prompt_manager.get_prompt_chain(agent_name)
                except Exception as e:
                    logger.error(f"Error getting prompt chain for {agent_name}: {str(e)}")
                    agent_config = {"name": agent_name}
                
                # Get actual agent status from task state manager
                try:
                    # Check if agent has any active tasks
                    agent_status = "idle"
                    for task_key, task in orchestrator.task_state_manager.tasks.items():
                        if task["agent"] == agent_name and task["state"] == "working":
                            agent_status = "working"
                            break
                except Exception as e:
                    logger.error(f"Error getting agent status: {str(e)}")
                    agent_status = "idle"
                
                # Simplified agent status model
                agents_data.append(AgentStatusModel(
                    id=agent_name,
                    name=agent_config.get("name", agent_name),
                    type=agent_name,
                    status=agent_status,
                    current_task=None,
                    completion_state="N/A",
                    errors=[],
                    retry_count=0,
                    metrics={"tasks_completed": 0, "avg_response_time": "N/A", "success_rate": "N/A"}
                ))
                logger.info(f"Added agent {agent_name} to status response")
            except Exception as e:
                logger.error(f"Error processing agent {agent_name}: {str(e)}")
        
        logger.info(f"Returning status for {len(agents_data)} agents")
        return AgentStatusResponseModel(agents=agents_data)
    except Exception as e:
        logger.error(f"Error in get_agent_status: {str(e)}")
        # Return a minimal response instead of throwing 500
        return AgentStatusResponseModel(agents=[])

@router.post("/agent/delegate", response_model=Dict[str, str])
async def delegate_task(delegation: TaskDelegationModel):
    """
    Delegate a task to a different agent
    """
    orchestrator = get_orchestrator()
    task_manager = orchestrator.task_state_manager
    
    # Validate target agent
    available_agents = orchestrator.prompt_manager.get_available_agents()
    if delegation.target_agent not in available_agents:
        raise HTTPException(status_code=400, detail=f"Invalid target agent: {delegation.target_agent}")
    
    # Import task persistence manager
    from app.core.task_persistence import get_task_persistence_manager
    task_persistence = get_task_persistence_manager()
    
    # Create a new task from the payload
    try:
        task_id = await task_persistence.store_pending_task(
            task_description=delegation.task.description,
            origin_agent="api",
            suggested_agent=delegation.target_agent,
            priority=delegation.task.priority == "high",
            metadata={
                "agent_type": delegation.task.agent_type,
                "task_id": delegation.task_id
            }
        )
        
        # Update task state to mark agent as working on this task
        await task_manager.update_task_state(
            agent_name=delegation.target_agent,
            task_id=delegation.task_id,
            state="working"
        )
        
        # Return success message
        return {"message": f"Task {delegation.task_id} delegated to {delegation.target_agent}"}
    except Exception as e:
        import logging
        logger = logging.getLogger("api")
        logger.error(f"Error delegating task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error delegating task: {str(e)}")

@router.post("/agent/goal/{task_id}/edit-prompt", response_model=Dict[str, str])
async def edit_task_prompt(task_id: str, prompt_data: EditPromptModel):
    """
    Edit the prompt for a task (Manual Mode only)
    """
    orchestrator = get_orchestrator()
    
    # Check if in manual mode
    if orchestrator.execution_mode != "manual":
        raise HTTPException(status_code=400, detail="Prompt editing is only available in Manual Mode")
    
    task_manager = orchestrator.task_state_manager
    
    # Get task
    task = await task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # Update task prompt
    task.prompt = prompt_data.prompt
    await task_manager._save_state_to_log()
    
    return {"message": f"Prompt updated for task {task_id}"}

# Export router
control_router = router
