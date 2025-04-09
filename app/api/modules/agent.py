"""
API endpoint for the AgentRunner module.

This module provides a REST API endpoint for executing agents in isolation,
without relying on the central agent registry, UI, or delegate-stream system.

MODIFIED: Enhanced error handling and logging to prevent 502 errors
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import time
import traceback
import os

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
    
    MODIFIED: Enhanced error handling and logging to prevent 502 errors
    
    Args:
        request: AgentRunRequest containing agent_id and messages
        
    Returns:
        JSONResponse with the agent's response
    """
    # ADDED: Entry confirmation logging
    print("🔥 AgentRunner API endpoint invoked")
    logger.info("🔥 AgentRunner API endpoint invoked")
    
    start_time = time.time()
    
    # MODIFIED: Wrapped all logic in global try/except
    try:
        print(f"🔄 API request received for agent: {request.agent_id}")
        logger.info(f"Agent run request received for agent: {request.agent_id}")
        
        # Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔑 OpenAI API Key loaded in endpoint: {bool(api_key)}")
        
        # Validate request
        if not request.agent_id:
            error_msg = "Missing agent_id in request"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": error_msg
                }
            )
        
        if not request.messages:
            error_msg = "Missing messages in request"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": error_msg
                }
            )
        
        # Run the agent
        print(f"🏃 Calling run_agent for: {request.agent_id}")
        result = run_agent(request.agent_id, request.messages)
        
        # Check if result is already a JSONResponse (from error handling in run_agent)
        if isinstance(result, JSONResponse):
            print("⚠️ Received JSONResponse from run_agent, returning directly")
            logger.info("Received JSONResponse from run_agent, returning directly")
            return result
        
        # Check if agent execution was successful
        if result.get("status") == "error":
            error_msg = f"Agent execution failed: {result.get('response')}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return JSONResponse(
                status_code=500,
                content={
                    "agent_id": request.agent_id,
                    "response": result.get("response", "Unknown error"),
                    "status": "error",
                    "execution_time": time.time() - start_time
                }
            )
        
        # Log success
        print(f"✅ Agent execution successful for {request.agent_id} in {time.time() - start_time:.2f}s")
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
        print(f"❌ AgentRunner API failed: {str(e)}")
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
