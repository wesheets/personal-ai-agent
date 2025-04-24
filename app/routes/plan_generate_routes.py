"""
Plan Generate Routes

This module defines the FastAPI routes for plan generation operations.
"""

from fastapi import APIRouter, HTTPException, Body, Query
from typing import Dict, Any, Optional

from app.modules.plan_generate import generate_plan
from app.schemas.plan_generate_schema import (
    PlanGenerateRequest,
    PlanGenerateResponse,
    PlanGenerateError,
    PlanType,
    PlanFormat
)

# Create router
router = APIRouter(
    prefix="/api/plan",
    tags=["plan"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", response_model=PlanGenerateResponse)
async def generate_plan_endpoint(request: PlanGenerateRequest = Body(...)):
    """
    Generate a plan based on the provided goal and parameters.
    
    This endpoint creates a structured plan with steps, estimated times, and dependencies.
    
    Args:
        request: Plan generation request
        
    Returns:
        Plan generation response
    """
    try:
        result = generate_plan(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = PlanGenerateError(
            message=f"Error generating plan: {str(e)}",
            goal=request.goal,
            plan_type=request.plan_type
        )
        return error_response

@router.get("/generate", response_model=PlanGenerateResponse)
async def generate_plan_get_endpoint(
    goal: str,
    plan_type: PlanType = PlanType.TASK,
    format: PlanFormat = PlanFormat.STEPS,
    context: Optional[str] = None,
    max_steps: Optional[int] = None,
    agent_id: Optional[str] = None,
    loop_id: Optional[str] = None
):
    """
    Generate a plan based on the provided goal and parameters using GET parameters.
    
    This endpoint creates a structured plan with steps, estimated times, and dependencies.
    
    Args:
        goal: Goal or objective for the plan
        plan_type: Type of plan to generate
        format: Output format for the plan
        context: Additional context for plan generation
        max_steps: Maximum number of steps in the plan
        agent_id: Agent ID requesting the plan
        loop_id: Loop ID associated with the plan
        
    Returns:
        Plan generation response
    """
    try:
        request_data = {
            "goal": goal,
            "plan_type": plan_type,
            "format": format,
            "context": context,
            "max_steps": max_steps,
            "agent_id": agent_id,
            "loop_id": loop_id
        }
        
        result = generate_plan(request_data)
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = PlanGenerateError(
            message=f"Error generating plan: {str(e)}",
            goal=goal,
            plan_type=plan_type
        )
        return error_response
