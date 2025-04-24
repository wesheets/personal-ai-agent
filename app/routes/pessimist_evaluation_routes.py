"""
PESSIMIST Pre-Run Evaluation Routes

This module defines the FastAPI routes for the PESSIMIST Pre-Run Evaluation.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

from app.modules.pessimist_evaluation import evaluate_loop_plan
from app.schemas.pessimist_evaluation_schema import (
    PessimistCheckRequest,
    PessimistCheckResult,
    PessimistCheckError
)

# Create router
router = APIRouter(
    prefix="/api/pessimist",
    tags=["pessimist"],
    responses={404: {"description": "Not found"}},
)

@router.post("/evaluate", response_model=PessimistCheckResult)
async def evaluate_loop_plan_endpoint(request: PessimistCheckRequest = Body(...)):
    """
    Evaluate a loop plan before execution.
    
    This endpoint evaluates loop plans, identifies potential risks,
    and provides confidence scores. If confidence is below 0.6,
    the loop will be blocked and the reason logged.
    
    Args:
        request: PESSIMIST check request
        
    Returns:
        PESSIMIST check result
    """
    try:
        result = evaluate_loop_plan(request.dict())
        return result
    except Exception as e:
        error_response = PessimistCheckError(
            message=f"Error evaluating loop plan: {str(e)}",
            project_id=request.project_id,
            loop_id=request.loop_id
        )
        return error_response
