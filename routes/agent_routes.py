"""
Agent Routes Module

This module provides the API routes for agent execution.
It handles agent run requests and delegates them to the appropriate agent runner.

MODIFIED: Added debug logs to confirm agent_runner is being called
MODIFIED: Added fallback message for missing agents
MODIFIED: Enhanced error handling for agent execution
MODIFIED: Added detailed logging for agent run requests
MODIFIED: Added debug trap to diagnose AGENT_RUNNERS loading failure
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import logging
import traceback
import uuid
import json

# Debug trap to diagnose AGENT_RUNNERS loading failure
try:
    from app.modules.agent_runner import AGENT_RUNNERS
    print("✅ AGENT_RUNNERS loaded with keys:", list(AGENT_RUNNERS.keys()))
    AGENT_RUNNERS_AVAILABLE = True
except Exception as e:
    print("❌ Failed to import AGENT_RUNNERS:", e)
    AGENT_RUNNERS = {}
    AGENT_RUNNERS_AVAILABLE = False

# Configure logging
logger = logging.getLogger("routes.agent_routes")

router = APIRouter()

# Debug print to verify this file is loaded
print("✅ AGENT ROUTES LOADED")
if AGENT_RUNNERS_AVAILABLE:
    print(f"✅ Available agents in AGENT_RUNNERS: {list(AGENT_RUNNERS.keys())}")
else:
    print("⚠️ AGENT_RUNNERS not available, agent execution will fail")

@router.get("/ping")
def agent_ping():
    """
    Simple ping endpoint to verify the agent router is working.
    """
    return {"status": "Agent router recovered"}

@router.post("/run")
async def agent_run(request_data: dict):
    """
    Run an agent with the provided input.
    """
    try:
        # Extract request data
        agent_id = request_data.get("agent_id", "unknown").lower()
        project_id = request_data.get("project_id", f"project_{uuid.uuid4().hex[:8]}")
        task = request_data.get("task", "")
        tools = request_data.get("tools", [])

        # Debug logs to confirm agent_runner is being called
        logger.info(f"Agent run request received for agent_id={agent_id}, project_id={project_id}")
        print(f"🤖 Agent run request received for agent_id={agent_id}, project_id={project_id}")
        print(f"📋 Task: {task}")
        print(f"🧰 Tools: {tools}")
        
        # Runtime check for AGENT_RUNNERS
        print("🔍 Runtime AGENT_RUNNERS keys:", list(AGENT_RUNNERS.keys()))
        
        # Check if AGENT_RUNNERS is available
        if not AGENT_RUNNERS_AVAILABLE:
            error_msg = "AGENT_RUNNERS not available, cannot execute agent"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "agent": agent_id,
                "project_id": project_id,
                "fallback_message": "The agent system is currently unavailable. Please try again later."
            }
        
        print(f"🔍 Available agents: {list(AGENT_RUNNERS.keys())}")

        # Check if agent exists in AGENT_RUNNERS
        if agent_id not in AGENT_RUNNERS:
            logger.warning(f"Unknown agent_id: {agent_id}")
            print(f"⚠️ Unknown agent_id: {agent_id}")
            return {
                "status": "error",
                "message": f"Unknown agent: {agent_id}",
                "agent": agent_id,
                "project_id": project_id,
                "fallback_message": f"The requested agent '{agent_id}' is not available. Please try with one of these agents: {', '.join(AGENT_RUNNERS.keys())}"
            }

        # Get the agent runner function
        runner_func = AGENT_RUNNERS[agent_id]
        logger.info(f"Running {agent_id} agent with task: {task}")
        print(f"🏃 Running {agent_id} agent with task: {task}")

        # Execute the agent
        result = runner_func(task, project_id, tools)

        # Log success
        logger.info(f"Agent {agent_id} executed successfully")
        print(f"✅ Agent {agent_id} executed successfully")

        # Return success response
        return {
            "status": "success",
            "message": result.get("message", f"Agent {agent_id} executed successfully"),
            "agent": agent_id,
            "project_id": project_id,
            "task": task,
            "tools": tools,
            "output": result
        }

    except Exception as e:
        # Log error
        error_msg = f"Error running agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())

        # Return error response with fallback message
        return {
            "status": "error",
            "message": error_msg,
            "agent": request_data.get("agent_id", "unknown"),
            "project_id": request_data.get("project_id", "default"),
            "fallback_message": "An error occurred while executing the agent. Please try again later."
        }

@router.post("/loop")
async def agent_loop(request_data: dict):
    """
    Continue an agent conversation loop.
    """
    return {
        "status": "success",
        "message": "Agent loop request received",
        "agent": request_data.get("agent", "unknown"),
        "input": request_data.get("input", ""),
        "project_id": request_data.get("project_id", "default")
    }

@router.get("/list")
async def agent_list():
    """
    List all available agents.
    """
    if not AGENT_RUNNERS_AVAILABLE:
        return {
            "status": "error",
            "message": "AGENT_RUNNERS not available",
            "agents": [],
            "fallback_message": "The agent system is currently unavailable. Please try again later."
        }
    
    agents = list(AGENT_RUNNERS.keys())
    print(f"📋 Listing available agents: {agents}")
    return {
        "status": "success",
        "agents": agents,
        "message": "Agent list recovered"
    }

@router.post("/delegate")
async def agent_delegate(request_data: dict):
    """
    Delegate a task to an agent.
    """
    return {
        "status": "success",
        "message": "Task delegation request received",
        "agent": request_data.get("agent", "unknown"),
        "task": request_data.get("task", ""),
        "project_id": request_data.get("project_id", "default")
    }
