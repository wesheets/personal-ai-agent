"""
Loop Sanity Validator Routes

This module defines the FastAPI routes for the Loop Sanity Validator.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

from app.modules.loop_validation import validate_loop
from app.schemas.loop_validation_schema import (
    LoopValidationRequest,
    LoopValidationResult,
    LoopValidationError
)

# Create router
router = APIRouter(
    prefix="/api/loop",
    tags=["loop"],
    responses={404: {"description": "Not found"}},
)

@router.post("/validate", response_model=LoopValidationResult)
async def validate_loop_endpoint(request: LoopValidationRequest = Body(...)):
    """
    Validate a loop configuration before execution.
    
    This endpoint should be called by ORCHESTRATOR before each loop starts
    to ensure structural integrity and prevent invalid loop plans.
    
    Args:
        request: Loop validation request
        
    Returns:
        Loop validation result
    """
    try:
        result = validate_loop(request.dict())
        return result
    except Exception as e:
        error_response = LoopValidationError(
            message=f"Error validating loop: {str(e)}",
            project_id=request.project_id,
            loop_id=request.loop_id
        )
        return error_response
