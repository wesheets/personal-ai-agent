from fastapi import APIRouter, HTTPException, Body, Request, Response, BackgroundTasks 
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.orchestrator import get_orchestrator
import logging
from fastapi.responses import JSONResponse

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

class AgentTaskRequest(BaseModel):
    agent_id: Optional[str] = None
    target_agent: Optional[str] = None
    task: Optional[Dict[str, Any]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "agent_id": "builder-1",
                "task": {
                    "id": "test-healthcheck-001",
                    "type": "tool",
                    "input": "reverse Hello Aegis"
                }
            }
        }
    }

class EditPromptModel(BaseModel):
    prompt: str

# Create router
router = APIRouter()

@router.get("/system/control-mode", response_model=Dict[str, Any])
async def get_control_mode():
    logger.info("Getting control mode")
    orchestrator = get_orchestrator()
    mode = orchestrator.execution_mode
    active_agents = orchestrator.prompt_manager.get_available_agents()
    response = {"mode": mode, "active_agents": active_agents}
    logger.info(f"Control mode response: {response}")
    return response

@router.post("/system/control-mode", response_model=Dict[str, str])
async def set_control_mode(mode_data: ControlModeModel):
    logger.info(f"Setting control mode to: {mode_data.mode}")
    orchestrator = get_orchestrator()
    if mode_data.mode not in ["auto", "manual", "paused"]:
        logger.error(f"Invalid mode: {mode_data.mode}")
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode_data.mode}")
    orchestrator.execution_mode = mode_data.mode
    response = {"message": f"Control mode set to {mode_data.mode}"}
    logger.info(f"Control mode set response: {response}")
    return response

@router.get("/system/control", response_model=Dict[str, Any])
async def get_system_control():
    logger.info("Getting system control state")
    try:
        control_state = {"interrupt_enabled": False}
        logger.info(f"System control state response: {control_state}")
        return control_state
    except Exception as e:
        logger.error(f"Error getting system control state: {str(e)}")
        return {"interrupt_enabled": False}

@router.get("/agent/status", response_model=AgentStatusResponseModel)
async def get_agent_status():
    logger.info("Fetching agent status")
    try:
        orchestrator = get_orchestrator()
        agents_data = []
        for agent_name in orchestrator.prompt_manager.get_available_agents():
            try:
                try:
                    agent_config = orchestrator.prompt_manager.get_prompt_chain(agent_name)
                except Exception as e:
                    logger.error(f"Error getting prompt chain for {agent_name}: {str(e)}")
                    agent_config = {"name": agent_name}

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
        return AgentStatusResponseModel(agents=[])

@router.post("/agent/goal/{task_id}/edit-prompt", response_model=Dict[str, str])
async def edit_task_prompt(task_id: str, prompt_data: EditPromptModel):
    logger.info(f"Editing prompt for task {task_id}")
    orchestrator = get_orchestrator()
    if orchestrator.execution_mode != "manual":
        logger.error("Prompt editing is only available in Manual Mode")
        raise HTTPException(status_code=400, detail="Prompt editing is only available in Manual Mode")
    task_manager = orchestrator.task_state_manager
    task = await task_manager.get_task(task_id)
    if not task:
        logger.error(f"Task {task_id} not found")
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    task.prompt = prompt_data.prompt
    await task_manager._save_state_to_log()
    response = {"message": f"Prompt updated for task {task_id}"}
    logger.info(f"Edit prompt response: {response}")
    return response

# Export router
control_router = router
