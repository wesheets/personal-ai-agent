"""
GUARDIAN Agent Routes

This module defines the FastAPI routes for the GUARDIAN agent.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

from app.agents.guardian_agent import process_alert, process_rollback
from app.schemas.guardian_schema import (
    GuardianAlertRequest,
    GuardianResponse,
    GuardianRollbackRequest,
    GuardianRollbackResult,
    GuardianErrorResult
)

# Create router
router = APIRouter(
    prefix="/api/guardian",
    tags=["guardian"],
    responses={404: {"description": "Not found"}},
)

@router.post("/override", response_model=GuardianResponse)
async def guardian_override(request: GuardianAlertRequest = Body(...)):
    """
    Process an alert using the GUARDIAN agent.
    
    Args:
        request: Alert request
        
    Returns:
        Alert response
    """
    try:
        result = process_alert(request.dict())
        return result
    except Exception as e:
        error_response = GuardianErrorResult(
            message=f"Error processing alert: {str(e)}",
            alert_type=request.alert_type,
            severity=request.severity,
            loop_id=request.loop_id
        )
        return error_response

@router.post("/rollback", response_model=GuardianRollbackResult)
async def guardian_rollback(request: GuardianRollbackRequest = Body(...)):
    """
    Process a rollback request using the GUARDIAN agent.
    
    Args:
        request: Rollback request
        
    Returns:
        Rollback result
    """
    try:
        result = process_rollback(request.dict())
        return result
    except Exception as e:
        error_response = GuardianErrorResult(
            message=f"Error processing rollback: {str(e)}",
            loop_id=request.loop_id
        )
        return error_response
