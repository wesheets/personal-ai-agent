"""
Agent Configuration Routes

This module defines the FastAPI routes for agent configuration.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

from app.modules.agent_config import set_agent_config, get_agent_config, delete_agent_config
from app.schemas.agent_config_schema import (
    AgentConfigRequest,
    AgentConfigResponse,
    AgentConfigError,
    AgentConfigGetRequest,
    AgentConfigGetResponse
)

# Create router
router = APIRouter(
    prefix="/api/agent",
    tags=["agent"],
    responses={404: {"description": "Not found"}},
)

@router.post("/config", response_model=AgentConfigResponse)
async def update_agent_config(request: AgentConfigRequest = Body(...)):
    """
    Update configuration for an agent.
    
    This endpoint allows setting permissions, tools, and fallback behaviors for an agent.
    
    Args:
        request: Agent configuration request
        
    Returns:
        Agent configuration response
    """
    try:
        result = set_agent_config(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = AgentConfigError(
            message=f"Error updating agent configuration: {str(e)}",
            agent_id=request.agent_id
        )
        return error_response

@router.get("/config/{agent_id}", response_model=AgentConfigGetResponse)
async def get_agent_configuration(agent_id: str):
    """
    Get configuration for an agent.
    
    This endpoint retrieves the current configuration for an agent.
    
    Args:
        agent_id: Unique identifier for the agent
        
    Returns:
        Agent configuration
    """
    try:
        result = get_agent_config(agent_id)
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = AgentConfigError(
            message=f"Error getting agent configuration: {str(e)}",
            agent_id=agent_id
        )
        return error_response

@router.delete("/config/{agent_id}", response_model=Dict[str, Any])
async def delete_agent_configuration(agent_id: str):
    """
    Delete configuration for an agent.
    
    This endpoint deletes the configuration for an agent.
    
    Args:
        agent_id: Unique identifier for the agent
        
    Returns:
        Deletion result
    """
    try:
        result = delete_agent_config(agent_id)
        
        # Check if the result is an error
        if "message" in result and "config_deleted" not in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = AgentConfigError(
            message=f"Error deleting agent configuration: {str(e)}",
            agent_id=agent_id
        )
        return error_response
