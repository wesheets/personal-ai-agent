"""
Review Task Endpoint

This module provides an API endpoint for the CriticAgent to review agent outputs.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

# Import CriticAgent
from app.modules.review.critic_agent import CriticAgent

# Configure logging
logger = logging.getLogger("modules.review.task")

# Create router
router = APIRouter()

# Create request model
class ReviewRequest(BaseModel):
    goal: str
    agent_outputs: Dict[str, str]

@router.post("/review/task")
async def review_task(request: ReviewRequest = Body(...)) -> Dict[str, Any]:
    """
    Review agent outputs using the CriticAgent.
    
    Args:
        request: ReviewRequest containing goal and agent outputs
        
    Returns:
        Dict containing scores and reflections
    """
    try:
        logger.info(f"Review task endpoint called with goal: {request.goal[:50]}...")
        
        # Create CriticAgent
        critic = CriticAgent()
        
        # Evaluate agent outputs
        result = critic.evaluate(request.goal, request.agent_outputs)
        
        # Check if evaluation was successful
        if result.get("status") == "error":
            logger.error(f"CriticAgent evaluation failed: {result.get('reflection')}")
            raise HTTPException(
                status_code=500,
                detail=f"CriticAgent evaluation failed: {result.get('reflection')}"
            )
        
        # Return result
        return result
    
    except Exception as e:
        logger.error(f"Error in review task endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing review request: {str(e)}"
        )
