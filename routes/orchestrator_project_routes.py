"""
Orchestrator to Project Start Redirect

This module adds a redirect from /api/project/start to the existing implementation
in /routes/project_routes.py.
"""

from fastapi import APIRouter, Request, HTTPException
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger("routes.orchestrator_project_routes")

# Create router
router = APIRouter(tags=["orchestrator"])

@router.post("/project/start")
async def project_start_redirect(request: Request):
    """
    Redirect endpoint for /api/project/start to the implementation in project_routes.py.
    
    This endpoint provides compatibility for clients expecting the project start endpoint
    at /api/project/start instead of directly accessing project_routes.
    
    Args:
        request: The request containing project parameters
            
    Returns:
        Dict containing the project start status and details
    """
    try:
        # Log the redirect
        logger.info("🔄 Redirecting /api/project/start to project_routes implementation")
        
        # Parse the request body
        body = await request.json()
        
        # Import the project_start function from project_routes
        try:
            from routes.project_routes import project_start
            
            # Call the implementation
            result = await project_start(body)
            
            # Return the result
            return result
        except ImportError as e:
            logger.error(f"❌ Error importing project_start from project_routes: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error redirecting to project_start: {str(e)}"
            )
    except Exception as e:
        logger.error(f"❌ Error in project_start_redirect: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in project_start_redirect: {str(e)}"
        )
