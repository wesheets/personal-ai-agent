"""
PESSIMIST Agent Routes

This module defines the routes for the PESSIMIST agent, which is responsible for
detecting bias, tracking bias tags over time, and identifying bias echo patterns.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
import time
import json
import asyncio

from app.schemas.pessimist_schema import (
    PessimistCheckRequest,
    PessimistCheckResult,
    PessimistErrorResult
)
from app.modules.pessimist_agent import pessimist_check

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/pessimist",
    tags=["pessimist"],
    responses={404: {"description": "Not found"}},
)

@router.post("/check", response_model=PessimistCheckResult)
async def check_bias(request: PessimistCheckRequest):
    """
    Analyze a loop summary for potential biases.
    
    This endpoint uses the PESSIMIST agent to detect bias, track bias tags over time,
    and identify bias echo patterns in loop summaries.
    """
    try:
        logger.info(f"Received pessimist check request for loop_id: {request.loop_id}")
        start_time = time.time()
        
        # Call the pessimist_check function from the pessimist_agent module
        result = await pessimist_check(request.loop_id, request.summary)
        
        # Add timestamp if not present
        if "timestamp" not in result:
            result["timestamp"] = time.time()
            
        # Log completion
        elapsed_time = time.time() - start_time
        logger.info(f"Completed pessimist check for loop_id: {request.loop_id} in {elapsed_time:.2f}s")
        
        return result
    except Exception as e:
        logger.error(f"Error in pessimist check: {str(e)}", exc_info=True)
        return PessimistErrorResult(
            status="error",
            message=f"Failed to perform pessimist check: {str(e)}",
            loop_id=request.loop_id,
            tools=request.tools
        )

@router.get("/health")
async def health_check():
    """
    Check the health of the PESSIMIST agent.
    """
    return {
        "status": "ok",
        "agent": "pessimist",
        "timestamp": time.time()
    }
