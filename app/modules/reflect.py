"""
Reflect module for generating agent reflections.

This module provides a dedicated endpoint for the /reflect functionality,
ensuring proper route registration and method handling.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import logging

# Import memory-related functions
from app.modules.memory_writer import write_memory, memory_store, generate_reflection

# Configure logging
logger = logging.getLogger("api.modules.reflect")

# Create router
router = APIRouter()

# Path for system caps configuration
SYSTEM_CAPS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "system_caps.json")

# Load system caps configuration
def load_system_caps():
    try:
        if os.path.exists(SYSTEM_CAPS_FILE):
            with open(SYSTEM_CAPS_FILE, 'r') as f:
                return json.load(f)
        else:
            print(f"⚠️ System caps file not found at {SYSTEM_CAPS_FILE}, using default caps")
            return {
                "max_loops_per_task": 3,
                "max_delegation_depth": 2
            }
    except Exception as e:
        print(f"⚠️ Error loading system caps: {str(e)}")
        return {
            "max_loops_per_task": 3,
            "max_delegation_depth": 2
        }

# Load system caps
system_caps = load_system_caps()
print(f"🔒 Reflect module loaded system caps: max_loops_per_task={system_caps['max_loops_per_task']}")

class ReflectionRequest(BaseModel):
    agent_id: str
    goal: str
    context: Optional[Dict] = None
    task_id: str
    project_id: str
    memory_trace_id: str
    type: Optional[str] = "memory"
    limit: int = 5
    loop_count: Optional[int] = 0  # Track number of loops for this task

@router.post("/")
async def reflect(request: Request):
    """
    Generate a reflection based on agent memories and store it with SDK-compliant metadata.
    
    This endpoint complies with Promethios_Module_Contract_v1.0.0 by:
    - Validating required input fields (agent_id, goal, task_id, project_id, memory_trace_id)
    - Returning a structured response with all required fields
    - Writing memory with memory_type="reflection" and all trace fields
    - Providing proper logging for failures or validation errors
    
    Request body:
    - agent_id: ID of the agent to generate reflection for (required)
    - goal: Purpose of the reflection (required)
    - context: Optional additional context for reflection
    - task_id: Task identifier for tracing (required)
    - project_id: Project identifier for context (required)
    - memory_trace_id: Memory trace identifier for linking (required)
    - type: Memory type to reflect on (optional, defaults to "memory")
    - limit: Maximum number of memories to consider (optional, defaults to 5)
    - loop_count: Number of loops already executed for this task (optional, defaults to 0)
    
    Returns:
    - status: "success" if successful, "failure" if error occurred
    - reflection: Generated reflection text
    - task_id: Task identifier (echoed from request)
    - project_id: Project identifier (echoed from request)
    - memory_trace_id: Memory trace identifier (echoed from request)
    - agent_id: Agent identifier (echoed from request)
    """
    try:
        # Parse request body
        body = await request.json()
        reflection_request = ReflectionRequest(**body)
        
        # Check if this reflection is part of a loop and enforce loop cap
        current_loop_count = reflection_request.loop_count if reflection_request.loop_count is not None else 0
        
        # Check if max_loops_per_task has been reached
        if current_loop_count >= system_caps["max_loops_per_task"]:
            # Log the failure to memory
            memory = write_memory(
                agent_id=reflection_request.agent_id,
                type="system_halt",
                content=f"Reflection loop limit exceeded: {current_loop_count} loops reached for task {reflection_request.task_id}",
                tags=["error", "loop_limit", "system_halt", "reflection"],
                project_id=reflection_request.project_id,
                status="error",
                task_id=reflection_request.task_id,
                memory_trace_id=reflection_request.memory_trace_id
            )
            
            # Return error response
            return JSONResponse(
                status_code=429,  # Too Many Requests
                content={
                    "status": "error",
                    "reason": "Loop limit exceeded",
                    "loop_count": current_loop_count,
                    "task_id": reflection_request.task_id,
                    "project_id": reflection_request.project_id,
                    "memory_trace_id": reflection_request.memory_trace_id,
                    "agent_id": reflection_request.agent_id
                }
            )
        
        # Get recent memories using similar logic to /read endpoint
        filtered_memories = [m for m in memory_store if m["agent_id"] == reflection_request.agent_id]
        
        # Apply type filter if type is provided
        if reflection_request.type:
            filtered_memories = [m for m in filtered_memories if m["type"] == reflection_request.type]
        
        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit
        filtered_memories = filtered_memories[:reflection_request.limit]
        
        # Generate reflection
        reflection_text = generate_reflection(filtered_memories)
        
        # Write reflection as a new memory with all trace fields
        memory = write_memory(
            agent_id=reflection_request.agent_id,
            type="reflection",
            content=reflection_text,
            tags=["reflection", f"based_on_{reflection_request.type}", "sdk_compliant"],
            project_id=reflection_request.project_id,
            task_id=reflection_request.task_id,
            memory_trace_id=reflection_request.memory_trace_id,
            status="completed"
        )
        
        # Log successful reflection generation
        logger.info(f"✅ Reflection generated for agent {reflection_request.agent_id} with task_id {reflection_request.task_id}")
        
        # Return SDK-compliant structured response
        return {
            "status": "success",
            "reflection": reflection_text,
            "task_id": reflection_request.task_id,
            "project_id": reflection_request.project_id,
            "memory_trace_id": reflection_request.memory_trace_id,
            "agent_id": reflection_request.agent_id,
            "loop_count": current_loop_count + 1  # Increment loop count
        }
    except Exception as e:
        logger.error(f"Error generating reflection: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "failure",
                "error": str(e),
                "task_id": reflection_request.task_id if hasattr(reflection_request, 'task_id') else "unknown",
                "project_id": reflection_request.project_id if hasattr(reflection_request, 'project_id') else "unknown",
                "memory_trace_id": reflection_request.memory_trace_id if hasattr(reflection_request, 'memory_trace_id') else "unknown",
                "agent_id": reflection_request.agent_id if hasattr(reflection_request, 'agent_id') else "unknown"
            }
        )
