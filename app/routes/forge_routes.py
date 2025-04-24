"""
FORGE Routes Module

This module defines the routes for the FORGE agent, which acts as the deep system builder
in the Promethios architecture. It handles building system components, registering routes,
and managing project state.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

# Import schemas
from app.schemas.forge_schema import ForgeBuildRequest, ForgeBuildResult

# Import FORGE agent
from app.agents.forge_agent import run_forge_agent

# Configure logging
logger = logging.getLogger("app.routes.forge_routes")

# Create router
router = APIRouter(tags=["forge"])

@router.post("/forge/build", response_model=ForgeBuildResult)
async def build_system_components(request: ForgeBuildRequest):
    """
    Build system components using the FORGE agent.
    
    Args:
        request: The build request containing project_id, loop_id, and components to build
        
    Returns:
        ForgeBuildResult containing the results of the build operation
    """
    try:
        logger.info(f"Received build request for project {request.project_id}, loop {request.loop_id}")
        
        # Run FORGE agent
        result = await run_forge_agent(request.dict())
        
        # Return result
        return result
    except Exception as e:
        logger.error(f"Error building system components: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error building system components: {str(e)}")
