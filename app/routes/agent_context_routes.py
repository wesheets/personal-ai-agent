"""
Agent Context Routes

This module defines the FastAPI routes for agent context.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional

from app.modules.agent_context import get_agent_context
from app.schemas.agent_context_schema import (
    AgentContextRequest,
    AgentContextResponse,
    AgentContextError
)

# Create router
router = APIRouter(
    prefix="/api/agent",
    tags=["agent"],
    responses={404: {"description": "Not found"}},
)

@router.post("/context", response_model=AgentContextResponse)
async def get_agent_context_endpoint(request: AgentContextRequest = Body(...)):
    """
    Get context information for an agent.
    
    This endpoint returns loop state, last agent, and memory usage information.
    
    Args:
        request: Agent context request
        
    Returns:
        Agent context response
    """
    try:
        result = get_agent_context(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = AgentContextError(
            message=f"Error getting agent context: {str(e)}",
            agent_id=request.agent_id,
            loop_id=request.loop_id
        )
        return error_response

@router.get("/context/{agent_id}", response_model=AgentContextResponse)
async def get_agent_context_by_id(
    agent_id: str,
    loop_id: Optional[str] = None,
    include_memory_stats: bool = True
):
    """
    Get context information for an agent by ID.
    
    This endpoint returns loop state, last agent, and memory usage information.
    
    Args:
        agent_id: Unique identifier for the agent
        loop_id: Optional loop ID to get context for
        include_memory_stats: Whether to include memory usage statistics
        
    Returns:
        Agent context response
    """
    try:
        request_data = {
            "agent_id": agent_id,
            "loop_id": loop_id,
            "include_memory_stats": include_memory_stats
        }
        
        result = get_agent_context(request_data)
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = AgentContextError(
            message=f"Error getting agent context: {str(e)}",
            agent_id=agent_id,
            loop_id=loop_id
        )
        return error_response
