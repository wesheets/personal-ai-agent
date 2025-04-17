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
    agent_id: str
    project_id: str
    task: str
    objective: Optional[str] = None
    context: Optional[str] = None

class OrchestratorConsultResponse(BaseModel):
    """Response model for the orchestrator/consult endpoint"""
    decision: str
    delegated_to: List[str]
    reflection: str
    status: str = "orchestrator_approved"

@router.post("/orchestrator/consult", response_model=OrchestratorConsultResponse)
async def orchestrator_consult(request: OrchestratorConsultRequest, background_tasks: BackgroundTasks = None):
    """
    Consult the Orchestrator for task routing and decision making.
    
    This endpoint allows the Orchestrator to reflect on an objective,
    determine which agents should handle it, and provide a decision
    with reflection.
    
    Args:
        request: The consultation request containing project_id, task, agent_id, and optional objective and context
        background_tasks: Optional background tasks for async operations
        
    Returns:
        OrchestratorConsultResponse: The orchestrator's decision and reflection
    """
    try:
        # Get the orchestrator instance
        orchestrator = get_orchestrator()
        
        # Log the consultation request to memory
        # This would typically use a memory manager, but we'll keep it simple for now
        print(f"Orchestrator consultation request: {request.task}")
        
        # Process the request
        # In a full implementation, this would use more sophisticated logic
        # based on the orchestrator's capabilities
        
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
        
        # Create and return the response
        response = OrchestratorConsultResponse(
            decision=decision,
            delegated_to=delegated_agents,
            reflection=reflection,
            status="orchestrator_approved"
        )
        
        return response
        
    except Exception as e:
        # Log the error
        print(f"Error in orchestrator_consult: {str(e)}")
        # Raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Orchestrator consultation failed: {str(e)}")
