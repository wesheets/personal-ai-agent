"""
API endpoint for the AgentRunner module.

This module provides a REST API endpoint for executing agents in isolation,
without relying on the central agent registry, UI, or delegate-stream system.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import time
import traceback

from app.modules.agent_runner import run_agent

# Configure logging
logger = logging.getLogger("api.modules.agent")

# Create router
router = APIRouter(prefix="/modules/agent", tags=["Agent Modules"])

# Define request model
class AgentRunRequest(BaseModel):
    agent_id: str
    messages: List[Dict[str, Any]]

@router.post("/run")
async def agent_run(request: AgentRunRequest):
    """
    Run an agent with the provided messages.
    
    This endpoint allows executing agent cognition in isolation,
    without relying on the central agent registry, UI, or delegate-stream system.
    
    Args:
        request: AgentRunRequest containing agent_id and messages
        
    Returns:
        JSONResponse with the agent's response
    """
    start_time = time.time()
    logger.info(f"Agent run request received for agent: {request.agent_id}")
    
    try:
        # Validate request
        if not request.agent_id:
            logger.error("Missing agent_id in request")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Missing agent_id in request"
                }
            )
        
        if not request.messages:
            logger.error("Missing messages in request")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Missing messages in request"
                }
            )
        
        # Run the agent
        result = run_agent(request.agent_id, request.messages)
        
        # Check if agent execution was successful
        if result.get("status") == "error":
            logger.error(f"Agent execution failed: {result.get('response')}")
            return JSONResponse(
                status_code=400,
                content={
                    "agent_id": request.agent_id,
                    "response": result.get("response", "Unknown error"),
                    "status": "error",
                    "execution_time": time.time() - start_time
                }
            )
        
        # Log success
        logger.info(f"Agent execution successful for {request.agent_id} in {time.time() - start_time:.2f}s")
        
        # Return successful response
        return JSONResponse(
            content={
                "agent_id": request.agent_id,
                "response": result.get("response", ""),
                "status": "ok",
                "execution_time": time.time() - start_time,
                "usage": result.get("usage", {})
            }
        )
    
    except Exception as e:
        # Handle any unexpected errors
        error_msg = f"Error processing agent run request: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "agent_id": request.agent_id if hasattr(request, "agent_id") else "unknown",
                "response": error_msg,
                "status": "error",
                "execution_time": time.time() - start_time
            }
        )
