"""
PESSIMIST Evaluation Routes
This module defines the routes for the PESSIMIST agent's evaluation functionality.
"""
import logging
import time
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List

from app.schemas.pessimist_schema import (
    PessimistEvaluationRequest,
    PessimistEvaluationResult,
    PessimistErrorResult
)
from app.modules.pessimist_evaluation import evaluate_risk

# Configure logging
logger = logging.getLogger("app.routes.pessimist_evaluation_routes")

# Create router
router = APIRouter(
    prefix="/api/pessimist",
    tags=["pessimist"],
    responses={404: {"description": "Not found"}}
)

@router.post("/evaluate", response_model=PessimistEvaluationResult)
async def evaluate_endpoint(request: PessimistEvaluationRequest):
    """
    Evaluate risks and potential failure points in a system or plan.
    
    This endpoint uses the PESSIMIST agent to analyze potential risks,
    failure modes, and security concerns in a given system or plan.
    
    Args:
        request: The evaluation request containing project_id, content to evaluate, and context
        
    Returns:
        PessimistEvaluationResult containing the risk analysis results
    """
    try:
        logger.info(f"Received evaluation request for project {request.project_id}")
        start_time = time.time()
        
        # Call the evaluate_risk function from the pessimist_evaluation module
        result = await evaluate_risk(
            project_id=request.project_id,
            content=request.content,
            context=request.context,
            risk_threshold=request.risk_threshold
        )
        
        # Log completion
        elapsed_time = time.time() - start_time
        logger.info(f"Completed risk evaluation for project {request.project_id} in {elapsed_time:.2f}s")
        
        return PessimistEvaluationResult(
            status="success",
            project_id=request.project_id,
            risks=result.get("risks", []),
            overall_risk_score=result.get("overall_risk_score", 5),
            recommendations=result.get("recommendations", []),
            timestamp=time.time()
        )
    except Exception as e:
        logger.error(f"Error evaluating risks: {str(e)}")
        
        return PessimistErrorResult(
            status="error",
            message=f"Failed to evaluate risks: {str(e)}",
            project_id=request.project_id,
            tools=request.tools
        )
