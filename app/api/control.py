from fastapi import APIRouter, HTTPException, Body, Request, Response, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.orchestrator import get_orchestrator
import logging
import uuid
from datetime import datetime
from fastapi.responses import JSONResponse
from app.models.agent import DelegateRequestModel
from app.core.agent_manager import get_agent_by_name

# Configure logging
logger = logging.getLogger("api")

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

class TaskDelegationModel(BaseModel):
    task_id: Optional[str] = None
    target_agent: Optional[str] = None
    task: Optional[str] = None
    agent: Optional[str] = None

class EditPromptModel(BaseModel):
    prompt: str

# Create router
router = APIRouter()

@router.get("/system/control-mode", response_model=Dict[str, Any])
async def get_control_mode():
    """
    Get the current system control mode and active agents
    """
    logger.info("Getting control mode")
    orchestrator = get_orchestrator()
    
    # Get current mode from orchestrator
    mode = orchestrator.execution_mode
    
    # Get list of active agents
    active_agents = orchestrator.prompt_manager.get_available_agents()
    
    response = {
        "mode": mode,
        "active_agents": active_agents
    }
    logger.info(f"Control mode response: {response}")
    return response

@router.post("/system/control-mode", response_model=Dict[str, str])
async def set_control_mode(mode_data: ControlModeModel):
    """
    Set the system control mode
    """
    logger.info(f"Setting control mode to: {mode_data.mode}")
    orchestrator = get_orchestrator()
    
    # Validate mode
    if mode_data.mode not in ["auto", "manual", "paused"]:
        logger.error(f"Invalid mode: {mode_data.mode}")
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode_data.mode}")
    
    # Set mode in orchestrator
    orchestrator.execution_mode = mode_data.mode
    
    response = {"message": f"Control mode set to {mode_data.mode}"}
    logger.info(f"Control mode set response: {response}")
    return response

@router.get("/system/control", response_model=Dict[str, Any])
async def get_system_control():
    """
    Get the system control state
    
    This endpoint returns the current system control state, including interrupt settings.
    """
    logger.info("Getting system control state")
    try:
        # Mock control state as specified in requirements
        control_state = {
            "interrupt_enabled": False
        }
        logger.info(f"System control state response: {control_state}")
        return control_state
    except Exception as e:
        logger.error(f"Error getting system control state: {str(e)}")
        # Return default state instead of throwing 500
        return {"interrupt_enabled": False}

@router.get("/agent/status", response_model=AgentStatusResponseModel)
async def get_agent_status():
    """
    Get status of all active agents
    """
    logger.info("Fetching agent status")
    
    try:
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
                
                # Simplified agent status model
                agents_data.append(AgentStatusModel(
                    id=agent_name,
                    name=agent_config.get("name", agent_name),
                    type=agent_name,
                    status="idle",
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

@router.post("/agent/delegate")
async def delegate_task(
    payload: DelegateRequestModel,
    background_tasks: BackgroundTasks
):
    logger.info(f"[DELEGATE] Received task for agent '{payload.target_agent}' with ID '{payload.task.id}'")
    
    # Offload the processing to background
    background_tasks.add_task(process_delegate, payload)

    return {"status": "accepted", "message": "Task is being processed in the background."}


async def process_delegate(payload: DelegateRequestModel):
    try:
        logger.info(f"[DELEGATE] Starting background task for '{payload.task.id}'")

        agent = get_agent_by_name(payload.target_agent)
        if not agent:
            logger.error(f"[DELEGATE] Agent '{payload.target_agent}' not found.")
            return

        logger.info(f"[DELEGATE] Found agent '{payload.target_agent}' – invoking handle_task")

        await agent.handle_task(payload.task)

        logger.info(f"[DELEGATE] Task '{payload.task.id}' completed successfully for agent '{payload.target_agent}'")
    
    except Exception as e:
        logger.exception(f"[DELEGATE] Error handling task '{payload.task.id}': {str(e)}")

@router.post("/agent/goal/{task_id}/edit-prompt", response_model=Dict[str, str])
async def edit_task_prompt(task_id: str, prompt_data: EditPromptModel):
    """
    Edit the prompt for a task (Manual Mode only)
    """
    logger.info(f"Editing prompt for task {task_id}")
    orchestrator = get_orchestrator()
    
    # Check if in manual mode
    if orchestrator.execution_mode != "manual":
        logger.error("Prompt editing is only available in Manual Mode")
        raise HTTPException(status_code=400, detail="Prompt editing is only available in Manual Mode")
    
    task_manager = orchestrator.task_state_manager
    
    # Get task
    task = await task_manager.get_task(task_id)
    if not task:
        logger.error(f"Task {task_id} not found")
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # Update task prompt
    task.prompt = prompt_data.prompt
    await task_manager._save_state_to_log()
    
    response = {"message": f"Prompt updated for task {task_id}"}
    logger.info(f"Edit prompt response: {response}")
    return response

# Export router
control_router = router
