"""
CTO Agent Routes

This module defines the routes for the CTO agent, which is responsible for
auditing project memory, validating schema compliance, and identifying potential issues.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
import time
import json

from app.schemas.cto_schema import (
    CTOAuditRequest,
    CTOAuditResult,
    CTOErrorResult
)
from app.agents.cto_agent import cto_agent, run_cto_agent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/cto",
    tags=["cto"],
    responses={404: {"description": "Not found"}},
)

@router.post("/audit", response_model=CTOAuditResult)
async def audit_project(request: CTOAuditRequest):
    """
    Audit a project for memory compliance and schema validation.
    
    This endpoint uses the CTO agent to audit project memory, validate schema compliance,
    and identify potential issues in the system.
    """
    try:
        logger.info(f"Received audit request for project_id: {request.project_id}")
        start_time = time.time()
        
        # Run the CTO agent
        result = cto_agent.run_agent(request)
        
        # Log completion
        elapsed_time = time.time() - start_time
        logger.info(f"Completed audit for project_id: {request.project_id} in {elapsed_time:.2f}s")
        
        return result
    except Exception as e:
        logger.error(f"Error in audit_project: {str(e)}", exc_info=True)
        return CTOErrorResult(
            status="error",
            message=f"Failed to audit project: {str(e)}",
            project_id=request.project_id
        )

@router.get("/health")
async def health_check():
    """
    Check the health of the CTO agent.
    """
    return {
        "status": "ok",
        "agent": "cto",
        "timestamp": time.time()
    }
