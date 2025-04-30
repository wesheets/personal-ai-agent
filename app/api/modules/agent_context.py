"""
API endpoint for the Agent Context module.

This module provides REST API endpoints for retrieving a structured snapshot
of an agent's active projects, recent actions, loop state, and task list.
"""

print("📁 Loaded: agent_context.py (Agent Context route file)")

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import traceback
import requests
import json
from datetime import datetime

# Import agent registry and memory-related functions
from app.api.modules.agent import agent_registry, ensure_core_agents_exist
from app.modules.memory_writer import MEMORY_STORE

# Import context models
from app.api.modules.agent_context_models import (
    AgentContextRequest,
    AgentContextResponse,
    ProjectContext,
    TaskItem
)

# Configure logging
logger = logging.getLogger("api.modules.agent_context")

# Create router
router = APIRouter(prefix="/modules/agent/context", tags=["Agent Context"])
print("🧠 Route defined: /api/modules/agent/context -> get_agent_context")

@router.post("")
async def get_agent_context(request: Request):
    """
    Return a structured snapshot of an agent's active projects, recent actions, loop state, and task list.
    
    This endpoint retrieves data from the agent registry and memory store to provide
    a comprehensive view of an agent's context, including active projects, tasks,
    loop counts, and current state.
    
    Request body:
    - agent_id: ID of the agent to get context for
    
    Returns:
    - status: "ok" if successful
    - agent_id: ID of the agent
    - active_projects: List of project contexts with tasks and metadata
    - agent_state: Current state of the agent
    - last_active: Timestamp of the agent's last activity
    """
    try:
        # Parse request body
        body = await request.json()
        context_request = AgentContextRequest(**body)
        
        # Ensure core agents exist before retrieving context
        ensure_core_agents_exist()
        
        # Check if agent exists
        if context_request.agent_id not in agent_registry:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Agent with ID '{context_request.agent_id}' not found"
                }
            )
        
        # Get agent metadata from registry
        agent_data = agent_registry[context_request.agent_id]
        agent_state = agent_data.get("agent_state", "idle")
        last_active = agent_data.get("last_active", datetime.utcnow().isoformat())
        
        # Get all memories for this agent
        agent_memories = [m for m in MEMORY_STORE if m["agent_id"] == context_request.agent_id]
        
        # Group memories by project_id
        project_memories = {}
        for memory in agent_memories:
            if "project_id" in memory and memory["project_id"]:
                project_id = memory["project_id"]
                if project_id not in project_memories:
                    project_memories[project_id] = []
                project_memories[project_id].append(memory)
        
        # Process each project to build the context
        active_projects = []
        for project_id, memories in project_memories.items():
            # Sort memories by timestamp (newest first)
            memories.sort(key=lambda m: m["timestamp"], reverse=True)
            
            # Get the most recent action
            last_action = "unknown"
            if memories and "type" in memories[0]:
                memory_type = memories[0]["type"]
                if memory_type == "loop_snapshot":
                    last_action = "loop"
                elif memory_type == "delegation_log":
                    last_action = "delegate"
                elif memory_type == "agent_response":
                    last_action = "respond"
                else:
                    last_action = memory_type
            
            # Get the last active timestamp for this project
            project_last_active = memories[0]["timestamp"] if memories else last_active
            
            # Count loop snapshots
            loop_count = sum(1 for m in memories if m.get("type") == "loop_snapshot")
            
            # Extract tasks
            tasks = []
            for memory in memories:
                # Only consider memories that represent tasks
                if memory.get("task_type") in ["task", "delegated_task", "agent_task"]:
                    task_description = memory.get("content", "").split("\n")[0]  # First line as summary
                    if len(task_description) > 100:
                        task_description = task_description[:97] + "..."
                    
                    task_status = memory.get("status", "unknown")
                    
                    # Add task if not already in the list
                    task_item = TaskItem(task=task_description, status=task_status)
                    if task_item not in tasks:
                        tasks.append(task_item)
            
            # Create project context
            project_context = ProjectContext(
                project_id=project_id,
                last_action=last_action,
                loop_count=loop_count,
                last_active=project_last_active,
                tasks=tasks
            )
            
            active_projects.append(project_context)
        
        # Create response
        response = AgentContextResponse(
            status="ok",
            agent_id=context_request.agent_id,
            active_projects=active_projects,
            agent_state=agent_state,
            last_active=last_active
        )
        
        return response.dict()
    except Exception as e:
        logger.error(f"Error getting agent context: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get agent context: {str(e)}"
            }
        )
