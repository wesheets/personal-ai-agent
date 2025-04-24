"""
SAGE Agent Routes

This module defines the API routes for the SAGE agent,
including the review endpoint for manual SAGE review.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

# Import schemas
from app.schemas.sage_schema import SageReviewRequest, SageReviewResult

# Import SAGE agent functions
try:
    from app.agents.sage import review_loop_summary, run_sage_agent
    sage_available = True
except ImportError:
    sage_available = False
    logging.warning("⚠️ SAGE agent not available, routes will return errors")

# Create router
router = APIRouter(
    prefix="/sage",
    tags=["sage"],
    responses={404: {"description": "Not found"}},
)

@router.post("/review", response_model=SageReviewResult)
async def sage_review(request: SageReviewRequest):
    """
    Endpoint for manual SAGE review of loop summaries.
    
    This endpoint allows manual invocation of the SAGE agent to review
    a loop summary and extract key beliefs with confidence scores.
    
    Args:
        request: SageReviewRequest containing loop_id and summary_text
        
    Returns:
        SageReviewResult containing belief scores and reflection
    """
    if not sage_available:
        raise HTTPException(
            status_code=503,
            detail="SAGE agent is not available"
        )
    
    try:
        # Call SAGE review function
        result = await review_loop_summary(request.loop_id, request.summary_text)
        
        # Check for error status
        if isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Unknown error in SAGE review")
            )
        
        return result
    
    except Exception as e:
        logging.error(f"Error in SAGE review endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in SAGE review: {str(e)}"
        )

@router.post("/run")
async def run_sage(project_id: str, task: str = None):
    """
    Run the SAGE agent for a given project.
    
    This endpoint maintains backward compatibility with the original
    SAGE agent functionality.
    
    Args:
        project_id: The project identifier
        task: Optional task to execute
        
    Returns:
        Dict containing the execution result
    """
    if not sage_available:
        raise HTTPException(
            status_code=503,
            detail="SAGE agent is not available"
        )
    
    try:
        # Call original SAGE function
        result = run_sage_agent(project_id, task)
        
        return result
    
    except Exception as e:
        logging.error(f"Error running SAGE agent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running SAGE agent: {str(e)}"
        )
