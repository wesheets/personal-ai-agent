"""
Agent Routes Module

This module provides the API routes for agent execution.
It handles agent run requests and delegates them to the appropriate agent runner.

MODIFIED: Added debug logs to confirm agent_runner is being called
MODIFIED: Added fallback message for missing agents
MODIFIED: Enhanced error handling for agent execution
MODIFIED: Added detailed logging for agent run requests
MODIFIED: Added debug trap to diagnose AGENT_RUNNERS loading failure
MODIFIED: Updated /agent/loop endpoint to use run_agent_from_loop function
MODIFIED: Refactored to use unified agent registry instead of AGENT_RUNNERS
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
import traceback
import uuid
import json

# Import the agent registry instead of AGENT_RUNNERS
from app.modules.agent_registry import get_registered_agent, list_agents

# Import the run_agent_from_loop function
from app.modules.loop import run_agent_from_loop

# Configure logging
logger = logging.getLogger("routes.agent_routes")

router = APIRouter()

# Debug print to verify this file is loaded
print("✅ AGENT ROUTES LOADED")
print(f"✅ Available agents: {list_agents()}")

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
        
        # Runtime check for available agents
        print(f"🔍 Available agents: {list_agents()}")

        # Get the agent handler function from the registry
        agent_fn = get_registered_agent(agent_id)
        
        # Check if agent exists in registry
        if not agent_fn:
            logger.warning(f"Unknown agent_id: {agent_id}")
            print(f"⚠️ Unknown agent_id: {agent_id}")
            return {
                "status": "error",
                "message": f"Unknown agent: {agent_id}",
                "agent": agent_id,
                "project_id": project_id,
                "fallback_message": f"The requested agent '{agent_id}' is not available. Please try with one of these agents: {', '.join(list_agents())}"
            }

        # Log agent execution
        logger.info(f"Running {agent_id} agent with task: {task}")
        print(f"🏃 Running {agent_id} agent with task: {task}")

        # Execute the agent
        result = agent_fn(task, project_id, tools)

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
async def agent_loop(request_data: dict = None, project_id: str = Query(None)):
    """
    Automatically trigger the appropriate agent based on project memory.
    
    This endpoint:
    1. Gets the project state from system status
    2. Extracts the next recommended step
    3. Determines which agent to run
    4. Triggers the appropriate agent
    
    Args:
        request_data: Optional request body that may contain project_id
        project_id: Project ID (can be provided as query parameter)
        
    Returns:
        Dict containing the execution results
    """
    try:
        # Extract project_id from either query parameter or request body
        effective_project_id = project_id
        if not effective_project_id and request_data:
            effective_project_id = request_data.get("project_id")
            
        # Validate project_id
        if not effective_project_id:
            error_msg = "Missing project_id in both query and body"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "fallback_message": "Project ID is required to run the agent loop."
            }
            
        logger.info(f"Agent loop request received for project_id={effective_project_id}")
        print(f"🔄 Agent loop request received for project_id={effective_project_id}")
        
        # Call run_agent_from_loop function
        result = run_agent_from_loop(effective_project_id)
        
        # Return the result
        return result
        
    except Exception as e:
        # Log error
        error_msg = f"Error in agent loop: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        # Return error response
        return {
            "status": "error",
            "message": error_msg,
            "project_id": effective_project_id if 'effective_project_id' in locals() else None,
            "fallback_message": "An error occurred while executing the agent loop. Please try again later."
        }

@router.get("/list")
async def agent_list():
    """
    List all available agents.
    """
    agents = list_agents()
    if not agents:
        return {
            "status": "error",
            "message": "No agents registered",
            "agents": [],
            "fallback_message": "The agent system is currently unavailable. Please try again later."
        }
    
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
