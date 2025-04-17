from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import logging
import traceback
import uuid
import json

# Import agent runner module
from app.modules.agent_runner import AGENT_RUNNERS

# Configure logging
logger = logging.getLogger("routes.agent_routes")

router = APIRouter()

@router.get("/agent/ping")
def agent_ping():
    """
    Simple ping endpoint to verify the agent router is working.
    """
    return {"status": "Agent router recovered"}

@router.post("/agent/run")
async def agent_run(request_data: dict):
    """
    Run an agent with the provided input.
    
    This endpoint maps the agent_id to the appropriate runner function
    and executes it with the provided task, project_id, and tools.
    
    Args:
        request_data: Dictionary containing agent_id, project_id, task, and tools
        
    Returns:
        Dict containing the agent's response
    """
    try:
        # Extract request data
        agent_id = request_data.get("agent_id", "unknown").lower()
        project_id = request_data.get("project_id", f"project_{uuid.uuid4().hex[:8]}")
        task = request_data.get("task", "")
        tools = request_data.get("tools", [])
        
        # Log request
        logger.info(f"Agent run request received for agent_id={agent_id}, project_id={project_id}")
        print(f"🤖 Agent run request received for agent_id={agent_id}, project_id={project_id}")
        print(f"📋 Task: {task}")
        print(f"🧰 Tools: {tools}")
        
        # Check if agent_id is valid
        if agent_id not in AGENT_RUNNERS:
            logger.warning(f"Unknown agent_id: {agent_id}")
            print(f"⚠️ Unknown agent_id: {agent_id}")
            
            return {
                "status": "error",
                "message": f"Unknown agent: {agent_id}",
                "agent": agent_id,
                "project_id": project_id
            }
        
        # Get runner function for agent_id
        runner_func = AGENT_RUNNERS[agent_id]
        
        # Run agent
        logger.info(f"Running {agent_id} agent with task: {task}")
        print(f"🏃 Running {agent_id} agent with task: {task}")
        
        result = runner_func(task, project_id, tools)
        
        # Log success
        logger.info(f"Agent {agent_id} executed successfully")
        print(f"✅ Agent {agent_id} executed successfully")
        
        # Return result with entire result object as output
        return {
            "status": "success",
            "message": result.get("message", f"Agent {agent_id} executed successfully"),
            "agent": agent_id,
            "project_id": project_id,
            "task": task,
            "tools": tools,
            "output": result  # Use entire result object instead of just files_created
        }
    
    except Exception as e:
        # Log error
        error_msg = f"Error running agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        # Return error response
        return {
            "status": "error",
            "message": error_msg,
            "agent": request_data.get("agent_id", "unknown"),
            "project_id": request_data.get("project_id", "default")
        }

@router.post("/agent/loop")
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

@router.get("/agent/list")
async def agent_list():
    """
    List all available agents.
    """
    # Get list of agents from AGENT_RUNNERS mapping
    agents = list(AGENT_RUNNERS.keys())
    
    return {
        "status": "success",
        "agents": agents,
        "message": "Agent list recovered"
    }

@router.post("/agent/delegate")
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
