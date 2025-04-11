"""
Delegate module for delegating tasks between agents.

This module provides a dedicated endpoint for the /delegate functionality,
ensuring proper route registration and method handling.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import uuid
from datetime import datetime
import os
import json
import logging

# Import memory-related functions
from app.modules.memory_writer import write_memory

# Configure logging
logger = logging.getLogger("api.modules.delegate")

# Create router
router = APIRouter()
print("🧠 Route defined: /app/modules/delegate -> delegate_task")

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
print(f"🔒 Delegate module loaded system caps: max_delegation_depth={system_caps['max_delegation_depth']}")

class AgentDelegateRequest(BaseModel):
    from_agent: str
    to_agent: str
    task: str
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    memory_trace_id: Optional[str] = None
    delegation_depth: Optional[int] = 0  # Track delegation depth
    context: Optional[Dict[str, Any]] = None

@router.post("/")
async def delegate_task(request: Request):
    """
    Delegate a task from one agent to another.
    
    This endpoint handles task delegation between agents with depth tracking
    to prevent runaway delegation chains.
    
    Request body:
    - from_agent: ID of the agent delegating the task
    - to_agent: ID of the agent receiving the task
    - task: Description of the task to delegate
    - project_id: (Optional) Project ID for context
    - task_id: (Optional) UUID for task identification
    - memory_trace_id: (Optional) String for memory tracing
    - delegation_depth: (Optional) Current delegation depth
    - context: (Optional) Additional context for the task
    
    Returns:
    - status: "ok" if successful, "error" if error occurred
    - delegation_id: UUID for the delegation
    - to_agent: ID of the agent receiving the task
    - task_id: UUID for task identification
    - result_summary: Summary of the delegation result
    - feedback_required: Boolean indicating if feedback is required
    """
    try:
        # Parse request body
        body = await request.json()
        delegate_request = AgentDelegateRequest(**body)
        
        # Import agent registry functions
        from app.api.modules.agent import agent_registry, ensure_core_agents_exist
        
        # Ensure core agents exist before running
        ensure_core_agents_exist()
        
        # Check if agents exist
        if delegate_request.from_agent not in agent_registry:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Agent with ID '{delegate_request.from_agent}' not found"
                }
            )
            
        if delegate_request.to_agent not in agent_registry:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Agent with ID '{delegate_request.to_agent}' not found"
                }
            )
        
        # Get current delegation depth
        current_delegation_depth = delegate_request.delegation_depth if delegate_request.delegation_depth is not None else 0
        
        # Check if max_delegation_depth has been reached
        if current_delegation_depth >= system_caps["max_delegation_depth"]:
            # Log the failure to memory
            memory = write_memory(
                agent_id=delegate_request.from_agent,
                type="system_halt",
                content=f"Delegation depth exceeded: {current_delegation_depth} levels reached for delegation to {delegate_request.to_agent}",
                tags=["error", "delegation_limit", "system_halt"],
                project_id=delegate_request.project_id,
                status="error",
                task_type="delegate",
                task_id=delegate_request.task_id,
                memory_trace_id=delegate_request.memory_trace_id
            )
            
            # Return error response
            return JSONResponse(
                status_code=429,  # Too Many Requests
                content={
                    "status": "error",
                    "reason": "Delegation depth exceeded",
                    "delegation_depth": current_delegation_depth,
                    "agent_id": delegate_request.to_agent
                }
            )
        
        # Generate task_id if not provided
        if not delegate_request.task_id:
            delegate_request.task_id = str(uuid.uuid4())
            
        # Generate memory_trace_id if not provided
        if not delegate_request.memory_trace_id:
            delegate_request.memory_trace_id = str(uuid.uuid4())
            
        # Generate delegation_id for tracking
        delegation_id = str(uuid.uuid4())
        
        # Format the delegation message
        from_agent = delegate_request.from_agent.upper()
        to_agent = delegate_request.to_agent.upper()
        delegation_message = f"Received task from {from_agent}: {delegate_request.task}"
        
        # Write delegation memory for the receiving agent
        memory = write_memory(
            agent_id=delegate_request.to_agent,
            type="delegation_log",
            content=delegation_message,
            tags=[f"from:{delegate_request.from_agent}"],
            project_id=delegate_request.project_id,
            status="pending",
            task_type="delegation",
            task_id=delegate_request.task_id,
            memory_trace_id=delegate_request.memory_trace_id
        )
        
        # Write delegation memory for the delegating agent
        delegating_message = f"Delegated task to {to_agent}: {delegate_request.task}"
        from_memory = write_memory(
            agent_id=delegate_request.from_agent,
            type="delegation_log",
            content=delegating_message,
            tags=[f"to:{delegate_request.to_agent}"],
            project_id=delegate_request.project_id,
            status="delegated",
            task_type="delegation",
            task_id=delegate_request.task_id,
            memory_trace_id=delegate_request.memory_trace_id
        )
        
        # Update agent states
        agent_registry[delegate_request.from_agent]["agent_state"] = "delegating"
        agent_registry[delegate_request.from_agent]["last_active"] = datetime.utcnow().isoformat()
        
        agent_registry[delegate_request.to_agent]["agent_state"] = "assigned"
        agent_registry[delegate_request.to_agent]["last_active"] = datetime.utcnow().isoformat()
        
        from app.api.modules.agent import save_agent_registry
        save_agent_registry()
        
        # Return structured response
        return {
            "status": "ok",
            "delegation_id": delegation_id,
            "to_agent": delegate_request.to_agent,
            "task_id": delegate_request.task_id,
            "delegation_depth": current_delegation_depth + 1,  # Increment delegation depth
            "result_summary": "Agent accepted task.",
            "feedback_required": False
        }
    except HTTPException as e:
        logger.error(f"Delegation Engine error: {str(e.detail)}")
        return JSONResponse(status_code=e.status_code, content={
            "status": "error",
            "log": e.detail
        })
    except Exception as e:
        logger.error(f"Delegation Engine error: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "log": str(e)
        })
