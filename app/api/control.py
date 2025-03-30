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

class TaskDelegationModel(BaseModel):
    task_id: str
    target_agent: str

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
    orchestrator = get_orchestrator()
    
    # Get agent status from orchestrator
    agents_data = []
    for agent_name in orchestrator.prompt_manager.get_available_agents():
        # Get agent config
        agent_config = orchestrator.prompt_manager.get_prompt_chain(agent_name)
        
        # Get current task for this agent
        current_task = None
        for chain in orchestrator.active_chains:
            if chain.current_agent == agent_name:
                if chain.steps and chain.steps[-1].agent_name == agent_name:
                    current_step = chain.steps[-1]
                    current_task = {
                        "title": current_step.input_text[:50] + "..." if len(current_step.input_text) > 50 else current_step.input_text,
                        "chain_id": chain.chain_id,
                        "step_number": len(chain.steps)
                    }
        
        # Get agent status
        status = "idle"
        if current_task:
            status = "active"
        
        # Get errors for this agent
        errors = []
        for chain in orchestrator.execution_chain_logger.get_chains():
            for step in chain.steps:
                if step.agent_name == agent_name and step.error:
                    errors.append({
                        "timestamp": step.timestamp,
                        "message": step.error,
                        "chain_id": chain.chain_id
                    })
        
        # Get metrics for this agent
        metrics = {
            "tasks_completed": len([step for chain in orchestrator.execution_chain_logger.get_chains() 
                                   for step in chain.steps 
                                   if step.agent_name == agent_name and step.status == "completed"]),
            "avg_response_time": "N/A",  # Would need to calculate from timestamps
            "success_rate": "N/A"  # Would need to calculate from success/failure counts
        }
        
        agents_data.append(AgentStatusModel(
            id=agent_name,
            name=agent_config.get("name", agent_name),
            type=agent_name,
            status=status,
            current_task=current_task,
            completion_state="N/A",  # Would need additional tracking
            errors=errors,
            retry_count=len(errors),
            metrics=metrics
        ))
    
    return AgentStatusResponseModel(agents=agents_data)

@router.post("/agent/delegate", response_model=Dict[str, str])
async def delegate_task(delegation: TaskDelegationModel):
    """
    Delegate a task to a different agent
    """
    orchestrator = get_orchestrator()
    task_manager = orchestrator.task_state_manager
    
    # Get task
    task = await task_manager.get_task(delegation.task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {delegation.task_id} not found")
    
    # Validate target agent
    available_agents = orchestrator.prompt_manager.get_available_agents()
    if delegation.target_agent not in available_agents:
        raise HTTPException(status_code=400, detail=f"Invalid target agent: {delegation.target_agent}")
    
    # Update task assignment
    task.assigned_agent = delegation.target_agent
    await task_manager._save_state_to_log()
    
    return {"message": f"Task {delegation.task_id} delegated to {delegation.target_agent}"}

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
