"""
Historian Routes Module

This module defines the API routes for the historian agent operations.

Includes:
- /historian/log endpoint for logging belief drift
- Fallback schema support for request validation
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.schemas.historian_schema import (
    HistorianDriftRequest, 
    HistorianDriftResult,
    validate_historian_drift_request
)
from app.agents.historian_agent import analyze_loop_summary

# Create router
router = APIRouter()
logger = logging.getLogger("api")

@router.post("/api/historian/log", response_model=HistorianDriftResult)
async def log_belief_drift(request: Dict[str, Any] = Body(...)):
    """
    Log belief drift and alignment scores.
    
    This endpoint analyzes loop summaries to detect belief drift and
    injects historian alerts into memory.
    
    Args:
        request: Dictionary containing the request data
        
    Returns:
        HistorianDriftResult: Result of the belief drift analysis
    """
    try:
        # Validate request with fallback support
        validated_request = validate_historian_drift_request(request)
        
        # Extract parameters
        loop_id = validated_request.loop_id
        loop_summary = validated_request.loop_summary
        recent_loops = validated_request.recent_loops
        beliefs = validated_request.beliefs
        memory = validated_request.memory
        
        # Set memory tag if provided, otherwise use default
        memory_tag = validated_request.memory_tag
        if not memory_tag:
            memory_tag = f"historian_belief_log_{loop_id}"
        
        # Log request
        logger.info(f"🧠 Historian agent processing belief drift for loop: {loop_id}")
        
        # Call historian agent to analyze loop summary
        updated_memory = analyze_loop_summary(
            loop_id=loop_id,
            loop_summary=loop_summary,
            recent_loops=recent_loops,
            beliefs=beliefs,
            memory=memory
        )
        
        # Extract the latest historian alert
        historian_alerts = updated_memory.get("historian_alerts", [])
        latest_alert = historian_alerts[-1] if historian_alerts else None
        
        if not latest_alert:
            raise HTTPException(status_code=500, detail="Failed to generate historian alert")
        
        # Create result
        result = HistorianDriftResult(
            updated_memory=updated_memory,
            alignment_score=latest_alert.get("loop_belief_alignment_score", 0.0),
            missing_beliefs=latest_alert.get("missing_beliefs", []),
            suggestion=latest_alert.get("suggestion", ""),
            alert=latest_alert
        )
        
        # Log success
        logger.info(f"✅ Historian agent successfully processed belief drift for loop: {loop_id}")
        
        return result
    
    except Exception as e:
        # Log error
        logger.error(f"❌ Error in historian agent: {str(e)}")
        
        # Raise HTTP exception
        raise HTTPException(
            status_code=500,
            detail=f"Error processing historian request: {str(e)}"
        )
