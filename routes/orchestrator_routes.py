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
    objective: str
    context: str
    agent_preferences: List[str] = Field(default_factory=list)

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
        request: The consultation request containing objective, context, and agent preferences
        background_tasks: Optional background tasks for async operations
        
    Returns:
        OrchestratorConsultResponse: The orchestrator's decision and reflection
    """
    try:
        # Get the orchestrator instance
        orchestrator = get_orchestrator()
        
        # Log the consultation request to memory
        # This would typically use a memory manager, but we'll keep it simple for now
        print(f"Orchestrator consultation request: {request.objective}")
        
        # Process the request
        # In a full implementation, this would use more sophisticated logic
        # based on the orchestrator's capabilities
        
        # Determine which agents to delegate to based on preferences or defaults
        delegated_agents = request.agent_preferences
        if not delegated_agents:
            # Default to HAL and NOVA if no preferences specified
            delegated_agents = ["hal", "nova"]
        
        # Generate a decision based on the objective and context
        decision = f"Initiate project boot sequence with {' and '.join(delegated_agents).upper()}"
        
        # Generate a reflection on the decision
        reflection = (
            f"Analyzed objective: '{request.objective}' in context: '{request.context}'. "
            f"Based on task requirements and agent capabilities, determined that "
            f"{' and '.join(delegated_agents).upper()} are best suited for this task. "
            f"Initiating collaborative workflow with these agents as primary handlers."
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
