"""
Loop Routes Module

This module provides API routes for loop-related operations.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.models.loop import StartLoopRequest
from app.modules.loop import run_agent_from_loop

# Configure logging
logger = logging.getLogger("routes.loop")

# Create router
router = APIRouter()

@router.post("/start", response_model=Dict[str, Any])
async def start_loop(request: StartLoopRequest):
    """
    Start a loop execution for a project.
    
    This endpoint:
    1. Validates the project_id
    2. Calls the run_agent_from_loop function to execute the appropriate agent
    3. Returns the execution results
    
    Args:
        request: The StartLoopRequest containing project_id and optional parameters
        
    Returns:
        Dict containing the execution results
    """
    try:
        logger.info(f"Starting loop for project: {request.project_id}")
        
        # Call the run_agent_from_loop function
        result = run_agent_from_loop(request.project_id)
        
        # Check if the result indicates an error
        if result.get("status") == "error":
            logger.error(f"Loop execution failed: {result.get('message')}")
            return {
                "status": "error",
                "message": result.get("message", "Unknown error"),
                "project_id": request.project_id,
                "details": result
            }
            
        # Return successful result
        return {
            "status": "success",
            "message": "Loop execution started successfully",
            "project_id": request.project_id,
            "details": result
        }
        
    except Exception as e:
        logger.error(f"Error starting loop: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while starting the loop: {str(e)}"
        )

@router.get("/debug", response_model=Dict[str, Any])
async def debug_loop():
    """
    Debug endpoint to verify the loop routes are accessible.
    
    Returns:
        Dict containing debug information
    """
    return {
        "status": "success",
        "message": "Loop routes are accessible",
        "endpoints": [
            "/api/loop/start",
            "/api/loop/debug"
        ]
    }
