"""
OBSERVER Agent Routes

This module defines the routes for the OBSERVER agent, which is responsible for
journaling system behavior, tracking anomalies, and documenting agent reflections.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
import time
import json

from app.schemas.observer_schema import (
    ObserverTaskRequest,
    ObserverTaskResult,
    ObserverErrorResult
)
from app.agents.observer_agent import observer_agent, handle_observer_task

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/observer",
    tags=["observer"],
    responses={404: {"description": "Not found"}},
)

@router.post("/journal", response_model=ObserverTaskResult)
async def create_journal(request: ObserverTaskRequest):
    """
    Create a journal entry for system observations.
    
    This endpoint uses the OBSERVER agent to create a journal entry documenting
    system behavior, anomalies, and agent reflections.
    """
    try:
        logger.info(f"Received journal request for date: {request.date}")
        start_time = time.time()
        
        # Ensure task is set to journal
        request.task = "journal"
        
        # Run the OBSERVER agent
        result = observer_agent.run_agent(request)
        
        # Log completion
        elapsed_time = time.time() - start_time
        logger.info(f"Completed journal creation for date: {request.date} in {elapsed_time:.2f}s")
        
        return result
    except Exception as e:
        logger.error(f"Error in create_journal: {str(e)}", exc_info=True)
        return ObserverErrorResult(
            status="error",
            message=f"Failed to create journal entry: {str(e)}",
            task="journal"
        )

@router.post("/observe", response_model=ObserverTaskResult)
async def observe_system(request: ObserverTaskRequest):
    """
    Observe system behavior and record findings.
    
    This endpoint uses the OBSERVER agent to observe system behavior and record
    findings about anomalies, loops, and other patterns.
    """
    try:
        logger.info(f"Received observation request for date: {request.date}")
        start_time = time.time()
        
        # Ensure task is set to observe
        request.task = "observe"
        
        # Run the OBSERVER agent
        result = observer_agent.run_agent(request)
        
        # Log completion
        elapsed_time = time.time() - start_time
        logger.info(f"Completed system observation for date: {request.date} in {elapsed_time:.2f}s")
        
        return result
    except Exception as e:
        logger.error(f"Error in observe_system: {str(e)}", exc_info=True)
        return ObserverErrorResult(
            status="error",
            message=f"Failed to observe system: {str(e)}",
            task="observe"
        )

@router.get("/health")
async def health_check():
    """
    Check the health of the OBSERVER agent.
    """
    return {
        "status": "ok",
        "agent": "observer",
        "timestamp": time.time()
    }
