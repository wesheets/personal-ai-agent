"""
NOVA Agent Routes

This module defines the routes for the NOVA agent, which is responsible for
UI component building in React/HTML.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
import time
import json

from app.schemas.nova_schema import (
    NovaUIRequest,
    NovaUIResult,
    NovaUIResultFallback
)
from app.agents.nova import nova_agent, run_nova_agent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/nova",
    tags=["nova"],
    responses={404: {"description": "Not found"}},
)

@router.post("/build-ui", response_model=NovaUIResult)
async def build_ui(request: NovaUIRequest):
    """
    Build UI components based on the provided task.
    
    This endpoint uses the NOVA agent to generate React/HTML UI components
    based on the provided task description.
    """
    try:
        logger.info(f"Received UI build request for project_id: {request.project_id}")
        start_time = time.time()
        
        # Run the NOVA agent
        result = nova_agent.run_agent(request)
        
        # Log completion
        elapsed_time = time.time() - start_time
        logger.info(f"Completed UI build for project_id: {request.project_id} in {elapsed_time:.2f}s")
        
        return result
    except Exception as e:
        logger.error(f"Error in build_ui: {str(e)}", exc_info=True)
        return NovaUIResultFallback(
            status="error",
            message=f"Failed to build UI components: {str(e)}",
            project_id=request.project_id,
            memory_tag=f"nova_ui_{request.project_id}"
        )

@router.post("/generate-component", response_model=NovaUIResult)
async def generate_component(request: NovaUIRequest):
    """
    Generate a specific UI component based on the provided task.
    
    This endpoint uses the NOVA agent to generate a specific React/HTML UI component
    based on the provided task description and component type.
    """
    try:
        logger.info(f"Received component generation request for project_id: {request.project_id}")
        start_time = time.time()
        
        # Run the NOVA agent
        result = nova_agent.run_agent(request)
        
        # Log completion
        elapsed_time = time.time() - start_time
        logger.info(f"Completed component generation for project_id: {request.project_id} in {elapsed_time:.2f}s")
        
        return result
    except Exception as e:
        logger.error(f"Error in generate_component: {str(e)}", exc_info=True)
        return NovaUIResultFallback(
            status="error",
            message=f"Failed to generate component: {str(e)}",
            project_id=request.project_id,
            memory_tag=f"nova_ui_{request.project_id}"
        )

@router.get("/health")
async def health_check():
    """
    Check the health of the NOVA agent.
    """
    return {
        "status": "ok",
        "agent": "nova",
        "timestamp": time.time()
    }
