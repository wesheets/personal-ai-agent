"""
FORGE Routes Module

This module defines the routes for the FORGE agent, which acts as the deep system builder
in the Promethios architecture. It handles building system components, registering routes,
and managing project state.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Define schema classes for request and response
class ForgeBuildRequest(BaseModel):
    project_id: str = Field(..., description="The project identifier")
    loop_id: str = Field(..., description="The loop identifier") # Added loop_id for consistency
    blueprint: Optional[str] = Field(None, description="The blueprint to use")
    components: list = Field([], description="List of components to build")

class ForgeBuildResult(BaseModel):
    status: str
    message: str
    project_id: str
    loop_id: str
    components_built: list = []
    errors: Optional[Dict[str, str]] = None

# Import FORGE agent
try:
    # Assuming the agent logic is refactored or accessible
    from app.agents.forge_agent import ForgeAgent
    forge_agent_instance = ForgeAgent() # Instantiate if needed
    forge_agent_available = True
except ImportError:
    forge_agent_available = False
    logging.warning("⚠️ FORGE agent not available, routes will return errors")

# Configure logging
logger = logging.getLogger("app.routes.forge_routes")

# Create router
router = APIRouter(tags=["forge"])

# Corrected path to /build, assuming /api/forge prefix is added in main.py
@router.post("/build", response_model=ForgeBuildResult)
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

        if not forge_agent_available:
            raise HTTPException(
                status_code=503,
                detail="FORGE agent is not available"
            )

        # Prepare payload for the agent's execute method
        payload = {
            "project_id": request.project_id,
            "loop_id": request.loop_id,
            "task": "build_components", # Example task name
            "details": {
                "blueprint": request.blueprint,
                "components": request.components
            },
            "source_agent": "api_request"
        }

        # Run FORGE agent's execute method
        result_dict = await forge_agent_instance.execute(payload)

        # Adapt the agent's result to the ForgeBuildResult schema
        # This part depends heavily on the actual structure of result_dict
        return ForgeBuildResult(
            status=result_dict.get("status", "unknown"),
            message=result_dict.get("output", "Build process completed."),
            project_id=request.project_id,
            loop_id=request.loop_id,
            components_built=result_dict.get("components_built", request.components if result_dict.get("status") == "success" else []),
            errors=result_dict.get("errors")
        )

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions
        raise http_exc
    except Exception as e:
        logger.error(f"Error building system components: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error building system components: {str(e)}"
        )

