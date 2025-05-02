"""
Minimal HAL routes module

This module provides a minimal implementation of HAL routes for the application.
It is used as a fallback when the actual HAL routes module cannot be loaded.
"""
from fastapi import APIRouter, HTTPException, Body
import datetime
from typing import Dict, Any

# Create router
router = APIRouter(tags=["hal"])

@router.get("/health")
async def hal_health_check():
    """
    Basic health check endpoint for HAL.
    """
    return {
        "status": "operational",
        "message": "HAL is operational (minimal implementation)",
        "timestamp": str(datetime.datetime.now())
    }

@router.get("/status")
async def hal_status():
    """
    Status endpoint for HAL.
    """
    return {
        "status": "operational",
        "mode": "minimal",
        "message": "HAL is running in minimal mode",
        "timestamp": str(datetime.datetime.now())
    }

@router.post("/generate")
async def hal_generate(prompt: str = ""):
    """
    Minimal implementation of HAL generation endpoint.
    """
    return {
        "status": "success",
        "response": f"HAL minimal implementation received: {prompt}",
        "timestamp": str(datetime.datetime.now())
    }

# Added /api/agent/run endpoint for Batch 1 cleanup
@router.post("/run") # Assuming prefix /api/agent is added in main.py
async def agent_run(payload: Dict[str, Any] = Body(...)):
    """
    Run an agent task (minimal implementation).

    Args:
        payload: Dictionary containing agent run parameters
            - agent_id: The agent identifier (e.g., "hal")
            - project_id: The project identifier
            - goal: The task goal
            - additional_context: Optional additional context

    Returns:
        Dict containing the agent run status and details
    """
    agent_id = payload.get("agent_id")
    project_id = payload.get("project_id")
    goal = payload.get("goal")

    if not agent_id or not project_id or not goal:
        raise HTTPException(status_code=422, detail="agent_id, project_id, and goal are required")

    # Minimal implementation - just acknowledges the request
    # In a full implementation, this would invoke the actual agent logic
    print(f"🧪 Agent run triggered for agent {agent_id}, project {project_id}")
    return {
        "status": "success",
        "message": f"Agent {agent_id} run initiated for project {project_id} (minimal implementation)",
        "project_id": project_id,
        "agent_id": agent_id,
        "goal": goal,
        "timestamp": str(datetime.datetime.now())
    }

