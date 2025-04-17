"""
System Routes Module

This module provides API routes for system-level operations.
"""

from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import traceback

# Import SAGE agent
try:
    from app.modules.agent_runner import run_sage_agent
    SAGE_AGENT_AVAILABLE = True
except ImportError:
    SAGE_AGENT_AVAILABLE = False
    print("❌ SAGE agent import failed")

# Configure logging
logger = logging.getLogger("app.routes.system_routes")

router = APIRouter()

@router.get("/ping")
def system_ping():
    """
    Simple ping endpoint to check if the system routes are working.
    
    Returns:
        Dict with status message
    """
    return {"status": "System routes operational"}

@router.post("/summary")
async def generate_system_summary(
    request: Request,
    project_id: str = Query(..., description="Project ID to generate summary for")
):
    """
    Generate a system-wide summary for a project using the SAGE agent.
    
    This endpoint is called by the agent loop autonomy system when a project
    completes (max loops reached or status complete).
    
    Args:
        request: The request object
        project_id: The project ID to generate summary for
        
    Returns:
        Dict containing the summary
    """
    try:
        logger.info(f"Generating system summary for project {project_id}")
        
        # Check if SAGE agent is available
        if not SAGE_AGENT_AVAILABLE:
            error_msg = "SAGE agent not available"
            logger.error(error_msg)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
            )
        
        # Run SAGE agent to generate summary
        sage_result = run_sage_agent(project_id)
        
        # Check if SAGE execution was successful
        if sage_result.get("status") == "error":
            error_msg = f"SAGE agent execution failed: {sage_result.get('message')}"
            logger.error(error_msg)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
            )
        
        # Return summary
        logger.info(f"System summary generated for project {project_id}")
        return {
            "status": "success",
            "message": "System summary generated",
            "project_id": project_id,
            "summary": sage_result.get("summary", "No summary available")
        }
    except Exception as e:
        error_msg = f"Error generating system summary: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": error_msg,
                "project_id": project_id
            }
        )
