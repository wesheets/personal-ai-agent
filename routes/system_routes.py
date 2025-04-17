"""
System Routes Module

This module provides API routes for system-level operations.
"""

from fastapi import APIRouter, Query, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import traceback
import datetime

# Import SAGE agent
try:
    from app.modules.agent_runner import run_sage_agent
    SAGE_AGENT_AVAILABLE = True
except ImportError:
    SAGE_AGENT_AVAILABLE = False
    print("❌ SAGE agent import failed")

# Import project_state module for status endpoint
try:
    from app.modules.project_state import read_project_state
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    print("❌ Project state module import failed")

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

@router.get("/status")
def get_system_status(project_id: str = Query(..., description="Project ID to get status for")):
    """
    Get the current system status for a project.
    
    This endpoint returns the current project state including loop count,
    status, and other relevant information.
    
    Args:
        project_id: The project ID to get status for
        
    Returns:
        Dict containing the project state
    """
    try:
        logger.info(f"Getting system status for project {project_id}")
        print(f"🔍 Getting system status for project {project_id}")
        
        # Check if project_state module is available
        if not PROJECT_STATE_AVAILABLE:
            error_msg = "Project state module not available"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
            )
        
        # Read project state
        project_state = read_project_state(project_id)
        
        # Check if project state exists
        if not project_state:
            error_msg = f"Project state not found for project {project_id}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
            )
        
        # Return project state
        logger.info(f"System status retrieved for project {project_id}")
        print(f"✅ System status retrieved for project {project_id}")
        return {
            "status": "success",
            "message": "System status retrieved",
            "project_id": project_id,
            "project_state": project_state
        }
    except Exception as e:
        error_msg = f"Error getting system status: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "error_details": traceback.format_exc()
            }
        )

@router.post("/summary")
async def generate_system_summary(
    request: Request,
    project_id: Optional[str] = Query(None, description="Project ID to generate summary for"),
    request_body: Optional[Dict[str, Any]] = Body(None)
):
    """
    Generate a system-wide summary for a project using the SAGE agent.
    
    This endpoint is called by the agent loop autonomy system when a project
    completes (max loops reached or status complete).
    
    Args:
        request: The request object
        project_id: The project ID to generate summary for (can be provided as query parameter)
        request_body: Optional JSON body that may contain project_id
        
    Returns:
        Dict containing the summary
    """
    # Extract project_id from either query parameter or request body
    effective_project_id = project_id or (request_body or {}).get("project_id")
    
    # Add debug logging
    print(f"[SYSTEM SUMMARY] project_id resolved to: {effective_project_id}")
    logger.info(f"[SYSTEM SUMMARY] project_id resolved to: {effective_project_id}")
    
    # Validate that project_id is provided
    if not effective_project_id:
        logger.error("[SYSTEM SUMMARY] Missing project_id in both query and body")
        raise HTTPException(status_code=400, detail="project_id is required")
    
    try:
        logger.info(f"Generating system summary for project {effective_project_id}")
        
        # Check if SAGE agent is available
        if not SAGE_AGENT_AVAILABLE:
            error_msg = "SAGE agent not available"
            logger.error(error_msg)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": error_msg,
                    "project_id": effective_project_id
                }
            )
        
        # Run SAGE agent to generate summary
        sage_result = run_sage_agent(effective_project_id)
        
        # Check if SAGE execution was successful
        if sage_result.get("status") == "error":
            error_msg = f"SAGE agent execution failed: {sage_result.get('message')}"
            logger.error(error_msg)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": error_msg,
                    "project_id": effective_project_id
                }
            )
        
        # Return summary
        logger.info(f"System summary generated for project {effective_project_id}")
        return {
            "status": "success",
            "message": "System summary generated",
            "project_id": effective_project_id,
            "summary": sage_result.get("summary", "No summary available"),
            "timestamp": datetime.datetime.now().isoformat()
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
                "project_id": effective_project_id
            }
        )
