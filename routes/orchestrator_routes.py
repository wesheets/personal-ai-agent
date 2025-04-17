"""
Orchestrator Routes Module

This module defines the FastAPI routes for the Orchestrator component,
including the /api/orchestrator/consult endpoint that allows the Orchestrator
to reflect, route tasks, and respond to operator input.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.core.orchestrator import get_orchestrator

# Create router
router = APIRouter()

# Define request and response models
class OrchestratorConsultRequest(BaseModel):
    """Request model for the orchestrator/consult endpoint"""
<<<<<<< HEAD
    project_id: str = Field(..., description="Project context")
    task: str = Field(..., description="Primary task to evaluate")
    context: Optional[str] = Field(None, description="Optional context")
=======
    agent_id: str
    project_id: str
    task: str
    objective: Optional[str] = None
    context: Optional[str] = None
>>>>>>> origin/main

@router.post("/orchestrator/consult")
async def orchestrator_consult(request: OrchestratorConsultRequest, background_tasks: BackgroundTasks = None):
    """
    Consult the Orchestrator for task routing and decision making.
    
    This endpoint allows the Orchestrator to reflect on a task,
    determine which agents should handle it, and provide a decision
    with reasoning.
    
    Args:
<<<<<<< HEAD
        request: The consultation request containing project_id, task, and optional context
=======
        request: The consultation request containing project_id, task, agent_id, and optional objective and context
>>>>>>> origin/main
        background_tasks: Optional background tasks for async operations
        
    Returns:
        JSON response with agent recommendation and reasoning
    """
    try:
        # Get the orchestrator instance
        orchestrator = get_orchestrator()
        
        # Log the consultation request to memory
        # This would typically use a memory manager, but we'll keep it simple for now
<<<<<<< HEAD
        print(f"Orchestrator consultation request: {request.task} for project {request.project_id}")
=======
        print(f"Orchestrator consultation request: {request.task}")
>>>>>>> origin/main
        
        # Process the request
        # In a full implementation, this would use more sophisticated logic
        # based on the orchestrator's capabilities
        
<<<<<<< HEAD
        # Determine the best agent for the task
        # For now, we'll use a simple rule-based approach
        task_lower = request.task.lower()
        
        if "bootstrap" in task_lower or "initialize" in task_lower or "create file" in task_lower:
            agent_id = "hal"
            reasoning = "HAL is specialized in file creation and project bootstrapping."
        elif "ui" in task_lower or "interface" in task_lower or "component" in task_lower:
            agent_id = "nova"
            reasoning = "NOVA is specialized in UI component creation and design."
        elif "review" in task_lower or "evaluate" in task_lower or "critique" in task_lower:
            agent_id = "critic"
            reasoning = "CRITIC is specialized in code review and evaluation."
        elif "deploy" in task_lower or "publish" in task_lower:
            agent_id = "ash"
            reasoning = "ASH is specialized in deployment and publishing."
        else:
            agent_id = "hal"  # Default to HAL
            reasoning = "Default agent selection based on general-purpose capabilities."
=======
        # Use the specified agent_id or determine which agents to delegate to
        delegated_agents = [request.agent_id] if request.agent_id else ["hal", "nova"]
        
        # Generate a decision based on the task and context
        objective_text = request.objective if request.objective else request.task
        context_text = request.context if request.context else "No additional context provided"
        
        decision = f"Initiate project {request.project_id} with {' and '.join(delegated_agents).upper()}"
        
        # Generate a reflection on the decision
        reflection = (
            f"Analyzed task: '{request.task}' with objective: '{objective_text}' in context: '{context_text}'. "
            f"Based on task requirements and agent capabilities, determined that "
            f"{' and '.join(delegated_agents).upper()} are best suited for this task. "
            f"Initiating collaborative workflow with these agents as primary handlers for project {request.project_id}."
        )
>>>>>>> origin/main
        
        # Create and return the response
        return {
            "status": "success",
            "message": "Consultation complete",
            "agent_id": agent_id,
            "reasoning": reasoning
        }
        
    except Exception as e:
        # Log the error
        print(f"Error in orchestrator_consult: {str(e)}")
        # Raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Consultation failed: {str(e)}")
