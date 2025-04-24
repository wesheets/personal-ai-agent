"""
ASH Agent Routes

This module defines the FastAPI routes for the ASH agent.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

from app.agents.ash_agent import process_analysis, process_test
from app.schemas.ash_schema import (
    AshAnalysisRequest,
    AshAnalysisResult,
    AshTestRequest,
    AshTestResult,
    AshErrorResult
)

# Create router
router = APIRouter(
    prefix="/api/ash",
    tags=["ash"],
    responses={404: {"description": "Not found"}},
)

@router.post("/analyze", response_model=AshAnalysisResult)
async def ash_analyze(request: AshAnalysisRequest = Body(...)):
    """
    Process an analysis request using the ASH agent.
    
    Args:
        request: Analysis request
        
    Returns:
        Analysis result
    """
    try:
        result = process_analysis(request.dict())
        return result
    except Exception as e:
        error_response = AshErrorResult(
            message=f"Error processing analysis: {str(e)}",
            scenario_id=request.scenario_id
        )
        return error_response

@router.post("/test", response_model=AshTestResult)
async def ash_test(request: AshTestRequest = Body(...)):
    """
    Process a test request using the ASH agent.
    
    Args:
        request: Test request
        
    Returns:
        Test result
    """
    try:
        result = process_test(request.dict())
        return result
    except Exception as e:
        error_response = AshErrorResult(
            message=f"Error processing test: {str(e)}",
            scenario_id=request.scenario_id
        )
        return error_response
