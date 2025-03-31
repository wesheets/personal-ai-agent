from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from app.core.behavior_manager import get_behavior_manager
from app.core.escalation_manager import get_escalation_manager

router = APIRouter(prefix="/agent", tags=["agent"])

class PerformanceResponse(BaseModel):
    agent_name: str
    total_tasks: int
    avg_confidence: Optional[float] = None
    escalation_count: int
    recent_success_rate: float
    success_rate: float
    total_feedback_count: int
    recent_feedback_count: int
    timestamp: str = datetime.now().isoformat()

@router.get("/{agent_name}/performance", response_model=PerformanceResponse)
async def get_agent_performance(
    agent_name: str,
    recent_count: int = Query(10, description="Number of recent tasks to consider for recent metrics")
):
    """
    Get performance metrics for a specific agent
    
    This endpoint returns performance metrics including total tasks, average confidence,
    escalation count, and success rates.
    """
    # Get behavior manager and escalation manager
    behavior_manager = get_behavior_manager()
    escalation_manager = get_escalation_manager()
    
    # Get behavior feedback summary
    feedback_summary = await behavior_manager.get_feedback_summary(agent_name, recent_count=recent_count)
    
    # Get escalation count
    escalation_count = await escalation_manager.get_escalation_count(agent_name=agent_name)
    
    # Calculate average confidence (placeholder - will be implemented in agent execution flow)
    avg_confidence = None  # This will be populated from confidence data in the future
    
    # Create response
    response = PerformanceResponse(
        agent_name=agent_name,
        total_tasks=feedback_summary.get("total_tasks", 0),
        avg_confidence=avg_confidence,
        escalation_count=escalation_count,
        recent_success_rate=feedback_summary.get("recent_success_rate", 0.0),
        success_rate=feedback_summary.get("success_rate", 0.0),
        total_feedback_count=feedback_summary.get("total_tasks", 0),
        recent_feedback_count=feedback_summary.get("recent_count", 0)
    )
    
    return response

class FeedbackRequest(BaseModel):
    task_id: str
    was_successful: bool
    user_notes: Optional[str] = None

@router.post("/{agent_name}/feedback", response_model=Dict[str, Any])
async def submit_agent_feedback(
    agent_name: str,
    feedback: FeedbackRequest
):
    """
    Submit feedback for an agent task
    
    This endpoint allows users to provide feedback on agent performance,
    including success status and optional notes.
    """
    # Get behavior manager
    behavior_manager = get_behavior_manager()
    
    # TODO: In a real implementation, we would retrieve the task details from a database
    # For now, we'll use a placeholder task description
    task_description = f"Task {feedback.task_id}"
    
    # Record feedback
    feedback_id = await behavior_manager.record_feedback(
        agent_name=agent_name,
        task_description=task_description,
        was_successful=feedback.was_successful,
        user_notes=feedback.user_notes,
        task_metadata={"task_id": feedback.task_id}
    )
    
    return {
        "feedback_id": feedback_id,
        "agent_name": agent_name,
        "task_id": feedback.task_id,
        "was_successful": feedback.was_successful,
        "status": "recorded"
    }

@router.get("/{agent_name}/feedback", response_model=List[Dict[str, Any]])
async def get_agent_feedback(
    agent_name: str,
    limit: int = Query(10, description="Maximum number of feedback entries to return"),
    offset: int = Query(0, description="Offset for pagination"),
    successful_only: Optional[bool] = Query(None, description="Filter by success status")
):
    """
    Get feedback for a specific agent
    
    This endpoint returns feedback entries for an agent, with optional filtering.
    """
    # Get behavior manager
    behavior_manager = get_behavior_manager()
    
    # Get feedback
    feedback = await behavior_manager.get_agent_feedback(
        agent_name=agent_name,
        limit=limit,
        offset=offset,
        successful_only=successful_only
    )
    
    return feedback

@router.get("/escalations", response_model=List[Dict[str, Any]])
async def get_escalations(
    limit: int = Query(10, description="Maximum number of escalations to return"),
    offset: int = Query(0, description="Offset for pagination"),
    agent_name: Optional[str] = Query(None, description="Filter by agent name"),
    status: Optional[str] = Query(None, description="Filter by status (pending, resolved, forwarded)")
):
    """
    Get escalation events
    
    This endpoint returns escalation events with optional filtering.
    """
    # Get escalation manager
    escalation_manager = get_escalation_manager()
    
    # Get escalations
    escalations = await escalation_manager.get_escalations(
        limit=limit,
        offset=offset,
        agent_name=agent_name,
        status=status
    )
    
    return escalations

@router.get("/escalations/{escalation_id}", response_model=Dict[str, Any])
async def get_escalation(
    escalation_id: str
):
    """
    Get a specific escalation event
    
    This endpoint returns details for a specific escalation event.
    """
    # Get escalation manager
    escalation_manager = get_escalation_manager()
    
    # Get escalation
    escalation = await escalation_manager.get_escalation(escalation_id)
    
    if not escalation:
        raise HTTPException(status_code=404, detail=f"Escalation not found: {escalation_id}")
    
    return escalation.dict()

class ForwardEscalationRequest(BaseModel):
    target_agent: str

@router.post("/escalations/{escalation_id}/forward", response_model=Dict[str, Any])
async def forward_escalation(
    escalation_id: str,
    request: ForwardEscalationRequest
):
    """
    Forward an escalation to another agent
    
    This endpoint forwards an escalation to another agent for handling.
    """
    # Get escalation manager
    escalation_manager = get_escalation_manager()
    
    # Forward escalation
    result = await escalation_manager.forward_escalation(
        escalation_id=escalation_id,
        target_agent=request.target_agent
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

class ResolveEscalationRequest(BaseModel):
    resolution_notes: Optional[str] = None

@router.post("/escalations/{escalation_id}/resolve", response_model=Dict[str, Any])
async def resolve_escalation(
    escalation_id: str,
    request: ResolveEscalationRequest
):
    """
    Resolve an escalation
    
    This endpoint marks an escalation as resolved.
    """
    # Get escalation manager
    escalation_manager = get_escalation_manager()
    
    # Resolve escalation
    result = await escalation_manager.resolve_escalation(
        escalation_id=escalation_id,
        resolution_notes=request.resolution_notes
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result
