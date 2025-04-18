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

# Debug print to verify this file is loaded
print("✅ AGENT ROUTES LOADED")
print(f"✅ Available agents in AGENT_RUNNERS: {list(AGENT_RUNNERS.keys())}")

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
        agent_id = request_data.get("agent_id", "unknown").lower()
        project_id = request_data.get("project_id", f"project_{uuid.uuid4().hex[:8]}")
        task = request_data.get("task", "")
        tools = request_data.get("tools", [])

        logger.info(f"Agent run request received for agent_id={agent_id}, project_id={project_id}")
        print(f"🤖 Agent run request received for agent_id={agent_id}, project_id={project_id}")
        print(f"📋 Task: {task}")
        print(f"🧰 Tools: {tools}")
        print(f"🔍 Available agents: {list(AGENT_RUNNERS.keys())}")

        if agent_id not in AGENT_RUNNERS:
            logger.warning(f"Unknown agent_id: {agent_id}")
            print(f"⚠️ Unknown agent_id: {agent_id}")
            return {
                "status": "error",
                "message": f"Unknown agent: {agent_id}",
                "agent": agent_id,
                "project_id": project_id
            }

        runner_func = AGENT_RUNNERS[agent_id]
        logger.info(f"Running {agent_id} agent with task: {task}")
        print(f"🏃 Running {agent_id} agent with task: {task}")

        result = runner_func(task, project_id, tools)

        logger.info(f"Agent {agent_id} executed successfully")
        print(f"✅ Agent {agent_id} executed successfully")

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
        error_msg = f"Error running agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())

        return {
            "status": "error",
            "message": error_msg,
            "agent": request_data.get("agent_id", "unknown"),
            "project_id": request_data.get("project_id", "default")
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
