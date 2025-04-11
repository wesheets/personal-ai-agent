"""
Agent Fallback Module

This module provides functionality for agents to reroute tasks they cannot perform
due to skill mismatch, failure, or reflection-based decision. It allows agents to
delegate tasks to more suitable agents when they are unable to complete them.

Endpoint: /api/modules/agent/fallback
"""

import json
import os
import logging
import uuid
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import httpx
import asyncio

# Import memory-related functions
from app.modules.memory_writer import write_memory

# Configure logging
logger = logging.getLogger("api.modules.agent_fallback")

# Define the router
router = APIRouter()

# Define the models
class FallbackRequest(BaseModel):
    """Request model for the fallback endpoint"""
    agent_id: str
    task_id: str
    reason: str  # "missing_skills", "failed_task", "reflection_decision"
    suggested_agent: str
    notes: str
    project_id: Optional[str] = None

class FallbackResponse(BaseModel):
    """Response model for the fallback endpoint"""
    status: str = "rerouted"
    new_agent: str
    delegation_task_id: str
    memory_id: str

# Valid fallback reasons
VALID_FALLBACK_REASONS = ["missing_skills", "failed_task", "reflection_decision"]

def get_agent_info(agent_id: str) -> Dict[str, Any]:
    """
    Get information about a specific agent.
    
    Args:
        agent_id (str): The ID of the agent
        
    Returns:
        Dict[str, Any]: Information about the agent
        
    Raises:
        HTTPException: If the agent is not found
    """
    # Import agent registry functions
    try:
        from app.api.modules.agent import agent_registry, ensure_core_agents_exist
        
        # Ensure core agents exist before running
        ensure_core_agents_exist()
        
        # Check if agent exists
        if agent_id not in agent_registry:
            raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found")
        
        return agent_registry[agent_id]
    except ImportError:
        # Fallback to loading from manifest if agent registry import fails
        agent_manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                        "config", "agent_manifest.json")
        try:
            with open(agent_manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Check if agent_id has -agent suffix, if not add it
            full_agent_id = agent_id if agent_id.endswith("-agent") else f"{agent_id}-agent"
            
            if full_agent_id not in manifest:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found in manifest")
            
            return manifest[full_agent_id]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load agent information: {str(e)}")

async def delegate_task(from_agent: str, to_agent: str, task_id: str, notes: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Delegate a task from one agent to another using the delegate endpoint.
    
    Args:
        from_agent (str): The ID of the agent delegating the task
        to_agent (str): The ID of the agent receiving the task
        task_id (str): The ID of the task to delegate
        notes (str): Additional notes about the task
        project_id (Optional[str]): The project ID for context
        
    Returns:
        Dict[str, Any]: The delegation response
        
    Raises:
        HTTPException: If delegation fails
    """
    try:
        # Prepare the delegation request
        delegation_request = {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task": notes,
            "task_id": task_id,
            "project_id": project_id,
            "delegation_depth": 0  # Start with 0 as this is a new delegation chain
        }
        
        # Call the delegate endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/app/modules/delegate",  # Local endpoint
                json=delegation_request
            )
        
        # Check if delegation was successful
        if response.status_code != 200:
            error_detail = response.json().get("message", "Unknown error")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Delegation failed: {error_detail}"
            )
        
        return response.json()
    except httpx.RequestError as e:
        # Handle request errors
        raise HTTPException(
            status_code=500,
            detail=f"Delegation request failed: {str(e)}"
        )
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=500,
            detail=f"Delegation failed: {str(e)}"
        )

@router.post("/fallback", response_model=FallbackResponse)
async def fallback(request: FallbackRequest):
    """
    Reroute a task from one agent to another due to fallback trigger.
    
    Args:
        request (FallbackRequest): The fallback request
        
    Returns:
        FallbackResponse: The fallback response with new agent and task ID
        
    Raises:
        HTTPException: If required fields are missing, agents don't exist, or other errors occur
    """
    # Validate the request
    if not request.agent_id:
        raise HTTPException(status_code=422, detail="agent_id is required")
    
    if not request.task_id:
        raise HTTPException(status_code=422, detail="task_id is required")
    
    if not request.reason:
        raise HTTPException(status_code=422, detail="reason is required")
    
    if request.reason not in VALID_FALLBACK_REASONS:
        raise HTTPException(
            status_code=422, 
            detail=f"reason must be one of: {', '.join(VALID_FALLBACK_REASONS)}"
        )
    
    if not request.suggested_agent:
        raise HTTPException(status_code=422, detail="suggested_agent is required")
    
    # Verify that both agents exist
    source_agent_info = get_agent_info(request.agent_id)
    target_agent_info = get_agent_info(request.suggested_agent)
    
    # Format the fallback message
    source_agent = request.agent_id.upper()
    target_agent = request.suggested_agent.upper()
    
    fallback_message = f"{source_agent} is unable to complete task {request.task_id} due to {request.reason}. "
    fallback_message += f"Rerouting to {target_agent}. Notes: {request.notes}"
    
    # Generate tags based on fallback reason
    tags = ["fallback", f"reason:{request.reason}", f"to:{request.suggested_agent}"]
    
    # Write fallback memory for the source agent
    memory = write_memory(
        agent_id=request.agent_id,
        type="fallback",
        content=fallback_message,
        tags=tags,
        project_id=request.project_id,
        status="rerouted",
        task_id=request.task_id
    )
    
    # Generate a new task ID for the delegated task
    delegation_task_id = f"{request.task_id}-delegated"
    
    try:
        # Delegate the task to the suggested agent
        delegation_response = await delegate_task(
            from_agent=request.agent_id,
            to_agent=request.suggested_agent,
            task_id=delegation_task_id,
            notes=request.notes,
            project_id=request.project_id
        )
        
        # Log successful fallback
        logger.info(f"✅ Task {request.task_id} rerouted from {request.agent_id} to {request.suggested_agent}")
        
        # Return the response
        return FallbackResponse(
            status="rerouted",
            new_agent=request.suggested_agent,
            delegation_task_id=delegation_task_id,
            memory_id=memory["memory_id"]
        )
    except HTTPException as e:
        # If delegation fails, log the error and re-raise
        logger.error(f"❌ Fallback failed: {str(e.detail)}")
        
        # Update the memory to reflect the failure
        write_memory(
            agent_id=request.agent_id,
            type="fallback_error",
            content=f"Failed to reroute task {request.task_id} to {request.suggested_agent}: {str(e.detail)}",
            tags=["fallback", "error", f"reason:{request.reason}"],
            project_id=request.project_id,
            status="error",
            task_id=request.task_id
        )
        
        raise

# Add a print statement to confirm the route is defined
print("🧠 Route defined: /fallback -> fallback")
