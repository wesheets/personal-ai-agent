"""
CRITIC Review Routes
This module defines the routes for the CRITIC agent's review functionality.
"""
import logging
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.schemas.critic_schema import (
    CriticReviewRequest,
    CriticReviewResult,
    CriticErrorResult
)
from app.modules.critic.review import review_agent_outputs

# Configure logging
logger = logging.getLogger("app.routes.critic_review_routes")

# Create router
router = APIRouter(
    prefix="/api/critic",
    tags=["critic"],
    responses={404: {"description": "Not found"}}
)

@router.post("/review", response_model=CriticReviewResult)
async def review_endpoint(request: CriticReviewRequest = Body(...)):
    """
    Review agent outputs using the CRITIC agent.
    
    This endpoint analyzes outputs from other agents and provides feedback,
    scores, and recommendations for improvement.
    
    Args:
        request: The review request containing loop_id, agent, and output to review
        
    Returns:
        CriticReviewResult containing the results of the review
    """
    try:
        logger.info(f"Received review request for loop {request.loop_id}, agent {request.agent}")
        
        # Call the review module
        review_result = await review_agent_outputs(request.dict())
        
        # Convert to CriticReviewResult format
        result = CriticReviewResult(
            status="success",
            loop_id=request.loop_id,
            reflection=review_result.get("reflection"),
            scores={
                "technical_accuracy": review_result.get("scores", {}).get("logic", 7),
                "ux_clarity": review_result.get("scores", {}).get("ux", 7),
                "visual_design": review_result.get("scores", {}).get("visual", 7),
                "monetization_strategy": review_result.get("scores", {}).get("monetization", 7)
            },
            rejection=review_result.get("retry_needed", False),
            rejection_reason=review_result.get("reflection") if review_result.get("retry_needed", False) else None,
            timestamp=datetime.utcnow().timestamp(),
            usage=None  # We don't have usage metrics in this implementation
        )
        
        return result
    except Exception as e:
        logger.error(f"Error reviewing agent outputs: {str(e)}")
        
        # Return error result
        error_result = CriticErrorResult(
            status="error",
            message=f"Error reviewing agent outputs: {str(e)}",
            task="review",
            tools=request.tools,
            project_id=request.project_id,
            loop_id=request.loop_id
        )
        
        return error_result
