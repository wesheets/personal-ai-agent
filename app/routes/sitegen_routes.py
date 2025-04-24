"""
SITEGEN Agent Routes

This module defines the routes for the SITEGEN agent, which is responsible for
planning commercial sites, analyzing zoning requirements, creating optimal layouts,
and evaluating market-fit for construction projects.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
import time
import json

from app.schemas.sitegen_schema import (
    SiteGenTaskRequest,
    SiteGenTaskResult,
    SiteGenErrorResult
)
from app.agents.sitegen_agent import sitegen_agent, handle_sitegen_task

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/sitegen",
    tags=["sitegen"],
    responses={404: {"description": "Not found"}},
)

@router.post("/plan", response_model=SiteGenTaskResult)
async def create_site_plan(request: SiteGenTaskRequest):
    """
    Create a site plan based on the provided requirements.
    
    This endpoint uses the SITEGEN agent to analyze zoning requirements,
    create optimal layouts, and evaluate market-fit for construction projects.
    """
    try:
        logger.info(f"Received site plan request: {request.task}")
        start_time = time.time()
        
        # Run the SITEGEN agent
        result = sitegen_agent.run_agent(request)
        
        # Log completion
        elapsed_time = time.time() - start_time
        logger.info(f"Completed site plan creation in {elapsed_time:.2f}s")
        
        return result
    except Exception as e:
        logger.error(f"Error in create_site_plan: {str(e)}", exc_info=True)
        return SiteGenErrorResult(
            status="error",
            message=f"Failed to create site plan: {str(e)}",
            task=request.task,
            project_id=request.project_id
        )

@router.post("/analyze", response_model=SiteGenTaskResult)
async def analyze_site_requirements(request: SiteGenTaskRequest):
    """
    Analyze site requirements and zoning regulations.
    
    This endpoint uses the SITEGEN agent to analyze site requirements
    and provide insights on zoning regulations and constraints.
    """
    try:
        logger.info(f"Received site analysis request: {request.task}")
        start_time = time.time()
        
        # Run the SITEGEN agent
        result = sitegen_agent.run_agent(request)
        
        # Log completion
        elapsed_time = time.time() - start_time
        logger.info(f"Completed site analysis in {elapsed_time:.2f}s")
        
        return result
    except Exception as e:
        logger.error(f"Error in analyze_site_requirements: {str(e)}", exc_info=True)
        return SiteGenErrorResult(
            status="error",
            message=f"Failed to analyze site requirements: {str(e)}",
            task=request.task,
            project_id=request.project_id
        )

@router.get("/health")
async def health_check():
    """
    Check the health of the SITEGEN agent.
    """
    return {
        "status": "ok",
        "agent": "sitegen",
        "timestamp": time.time()
    }
