"""
API endpoint for the AgentRunner module.

This module provides a REST API endpoint for executing agents in isolation,
without relying on the central agent registry, UI, or delegate-stream system.

MODIFIED: Replaced with inline execution debug logging to diagnose 502 errors
"""

print("📁 Loaded: agent.py (AgentRunner route file)")

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
import traceback
import os
import time

# Configure logging
logger = logging.getLogger("api.modules.agent")

# Create router
router = APIRouter(prefix="/modules/agent", tags=["Agent Modules"])
print("🧠 Route defined: /api/modules/agent/run -> run_agent_endpoint")

@router.post("/run")
async def run_agent_endpoint(request: Request):
    """
    Run an agent with the provided messages.
    
    MODIFIED: Replaced with inline execution debug logging to diagnose 502 errors
    
    Args:
        request: Request object containing the raw request data
        
    Returns:
        JSONResponse with the agent's response or error details
    """
    print("🔥 AgentRunner endpoint HIT")
    logger.info("🔥 AgentRunner endpoint HIT")
    
    start_time = time.time()
    
    try:
        # Parse request body
        body = await request.json()
        print("🧠 Parsed body:", body)
        logger.info(f"Parsed request body with {len(body.get('messages', []))} messages")
        
        # Check for required fields
        if 'messages' not in body:
            error_msg = "Missing 'messages' in request body"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": error_msg
                }
            )
        
        # Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔑 OpenAI API Key loaded: {bool(api_key)}")
        logger.info(f"OpenAI API Key available: {bool(api_key)}")
        
        if not api_key:
            error_msg = "OpenAI API key is not set in environment variables"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": error_msg
                }
            )
        
        # Import CoreForgeAgent directly
        try:
            print("🧠 Attempting to import CoreForgeAgent")
            from app.modules.agent_runner import CoreForgeAgent
            print("✅ Successfully imported CoreForgeAgent")
        except ImportError:
            try:
                print("⚠️ First import attempt failed, trying alternate import path")
                from app.core.forge import CoreForgeAgent
                print("✅ Successfully imported CoreForgeAgent from alternate path")
            except ImportError as e:
                error_msg = f"Failed to import CoreForgeAgent: {str(e)}"
                print(f"❌ {error_msg}")
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": error_msg
                    }
                )
        
        # Create agent instance
        print("🧠 Creating CoreForgeAgent instance")
        agent = CoreForgeAgent()
        print("✅ Successfully created CoreForgeAgent instance")
        
        # Run the agent
        print(f"🧠 Calling agent.run() with {len(body['messages'])} messages")
        output = agent.run(body["messages"])
        print("✅ CoreForgeAgent returned:", output)
        
        # Return successful response
        return JSONResponse(
            content={
                "agent_id": "Core.Forge",
                "response": output.get("content", ""),
                "status": "ok",
                "execution_time": time.time() - start_time,
                "usage": output.get("usage", {})
            }
        )
    
    except Exception as e:
        # Handle any unexpected errors
        error_msg = f"Error in AgentRunner endpoint: {str(e)}"
        print(f"❌ AgentRunner exception: {str(e)}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "agent_id": "Core.Forge"
            }
        )
