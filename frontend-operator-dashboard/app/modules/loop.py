"""
Loop module for executing cognitive loops for agents.

This module provides a dedicated endpoint for the /loop functionality,
ensuring proper route registration and method handling.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import os
import json
import uuid
from datetime import datetime

# Import memory-related functions
from app.modules.memory_writer import write_memory
# Import task supervisor
from app.modules.task_supervisor import monitor_loop, halt_task

# Configure logging
logger = logging.getLogger("api.modules.loop")

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
print(f"🔒 Loop module loaded system caps: max_loops_per_task={system_caps['max_loops_per_task']}")

# Pydantic model for agent loop request
class AgentLoopRequest(BaseModel):
    agent_id: str
    loop_type: Optional[str] = "reflective"  # "reflective", "task", "planning"
    memory_limit: Optional[int] = 5
    project_id: Optional[str] = None
    status: Optional[str] = None
    task_type: Optional[str] = None
    task_id: Optional[str] = None
    memory_trace_id: Optional[str] = None
    max_cycles: Optional[int] = 1
    exit_conditions: Optional[List[str]] = []
    loop_count: Optional[int] = 0  # Track number of loops for this task

# Simple LLM Engine for agent execution
class LLMEngine:
    """
    A simple LLM Engine that processes prompts and returns responses.
    This is a mock implementation for the agent run endpoint.
    """
    
    @staticmethod
    def infer(prompt, model="default"):
        """
        Process a prompt and return a response.
        
        Args:
            prompt: The prompt to process
            model: The model to use for inference
            
        Returns:
            The generated response
        """
        logger.info(f"LLMEngine processing prompt with model: {model}")
        
        # In a real implementation, this would call an actual LLM API
        # For now, we'll generate simple responses based on the prompt
        
        if "reflect" in prompt.lower() and "actions" in prompt.lower():
            return "You've been focused on implementing API endpoints for the personal-ai-agent project, including memory search, agent registry fixes, and system status reporting."
        
        if "plan" in prompt.lower() and "next" in prompt.lower():
            return "You should generate a system summary log and implement the cognitive loop functionality to enable autonomous agent operation."
        
        # Default response
        return f"I've processed your request: '{prompt}'. How can I assist you further?"

# Helper function to load recent memories for an agent
def load_recent_memories(agent_id: str, memory_limit: int = 5, memory_type: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load recent memories for an agent, optionally filtered by type and project_id.
    
    Args:
        agent_id: ID of the agent whose memories to load
        memory_limit: Maximum number of memories to load
        memory_type: Optional type of memories to filter by
        project_id: Optional project_id to filter by
        
    Returns:
        List of memory dictionaries
    """
    from app.modules.memory_writer import memory_store
    
    # Filter memories by agent_id
    filtered_memories = [m for m in memory_store if m["agent_id"] == agent_id]
    
    # Apply type filter if provided
    if memory_type:
        filtered_memories = [m for m in filtered_memories if m["type"] == memory_type]
    
    # Apply project_id filter if provided
    if project_id:
        filtered_memories = [
            m for m in filtered_memories 
            if "project_id" in m and m["project_id"] == project_id
        ]
    
    # Sort by timestamp (newest first)
    filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
    
    # Apply limit
    if memory_limit and memory_limit > 0:
        filtered_memories = filtered_memories[:memory_limit]
    
    return filtered_memories

@router.post("/loop")
async def loop_agent(request: Request):
    """
    Execute a full cognitive loop cycle for a given agent.
    
    This endpoint performs the following steps:
    1. Reflect on memory
    2. Summarize relevant entries
    3. Generate a plan
    4. Write new memory
    5. Return structured result according to SDK Contract v1.0.0
    
    Request body:
    - agent_id: ID of the agent to run the cognitive loop for
    - loop_type: (Optional) Type of loop to run ("reflective", "task", "planning")
    - memory_limit: (Optional) Maximum number of memories to include in context
    - project_id: (Optional) Project ID to scope memory access and storage
    - status: (Optional) Status of the loop ("in_progress", "completed", "delegated", etc.)
    - task_type: (Optional) Type of task ("loop", "reflection", "task", "delegate", etc.)
    - task_id: (Optional) UUID for task identification
    - memory_trace_id: (Optional) String for memory tracing
    - max_cycles: (Optional) Maximum number of loop cycles to execute
    - exit_conditions: (Optional) Array of conditions that will terminate the loop
    - loop_count: (Optional) Number of loops already executed for this task
    
    Returns:
    - status: "success" | "error" | "incomplete"
    - loop_summary: String summarizing the loop
    - loop_result: String containing the result
    - cycle_number: Integer tracking loop count
    - memory_id: ID of the memory entry created for this loop
    - task_id: UUID for task identification
    - project_id: String for project scope
    - memory_trace_id: String for memory tracing
    """
    try:
        # Parse request body
        body = await request.json()
        loop_request = AgentLoopRequest(**body)
        
        # Import agent registry functions
        from app.api.modules.agent import agent_registry, ensure_core_agents_exist
        
        # Ensure core agents exist before running
        ensure_core_agents_exist()
        
        # Check if agent exists
        if loop_request.agent_id not in agent_registry:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Agent with ID '{loop_request.agent_id}' not found"
                }
            )
        
        # Get agent metadata
        agent_data = agent_registry[loop_request.agent_id]
        agent_name = agent_data.get("name", loop_request.agent_id.upper())
        
        # Get current loop count for this task
        current_loop_count = loop_request.loop_count if loop_request.loop_count is not None else 0
        
        # Use task supervisor to monitor loop count
        monitor_result = monitor_loop(
            task_id=loop_request.task_id if loop_request.task_id else str(uuid.uuid4()),
            loop_count=current_loop_count
        )
        
        # Check if task should be halted
        if monitor_result["status"] != "ok":
            # Return error response
            return JSONResponse(
                status_code=429,  # Too Many Requests
                content={
                    "status": "error",
                    "reason": monitor_result["reason"],
                    "loop_count": current_loop_count,
                    "task_id": loop_request.task_id if loop_request.task_id else "unknown",
                    "event": monitor_result["event"]
                }
            )
        
        # Update agent state to "looping" and last_active timestamp
        agent_registry[loop_request.agent_id]["agent_state"] = "looping"
        agent_registry[loop_request.agent_id]["last_active"] = datetime.utcnow().isoformat()
        
        # Increment loop count for the agent
        agent_registry[loop_request.agent_id]["loop_count"] = agent_data.get("loop_count", 0) + 1
        from app.api.modules.agent import save_agent_registry
        save_agent_registry()
        
        # Increment loop count for this task
        current_loop_count += 1
        
        # Check if max_cycles has been reached
        if loop_request.max_cycles and current_loop_count > loop_request.max_cycles:
            # Reset agent state to "idle" after loop completes
            agent_registry[loop_request.agent_id]["agent_state"] = "idle"
            save_agent_registry()
            
            return {
                "status": "incomplete",
                "loop_summary": "Maximum cycle count reached",
                "loop_result": "Loop terminated due to max_cycles limit",
                "cycle_number": current_loop_count,
                "memory_id": "",
                "task_id": loop_request.task_id if loop_request.task_id else str(uuid.uuid4()),
                "project_id": loop_request.project_id if loop_request.project_id else "",
                "memory_trace_id": loop_request.memory_trace_id if loop_request.memory_trace_id else ""
            }
        
        # Check for exit conditions (stub implementation for now)
        if loop_request.exit_conditions and len(loop_request.exit_conditions) > 0:
            # In a real implementation, we would check each condition against the current state
            # For now, we'll just log that exit conditions were provided
            logger.info(f"Exit conditions provided: {loop_request.exit_conditions}")
        
        # Load recent memories
        memory_limit = loop_request.memory_limit if loop_request.memory_limit is not None else 5
        
        # Apply project_id filter if provided
        project_id_filter = None
        if hasattr(loop_request, 'project_id') and loop_request.project_id:
            project_id_filter = loop_request.project_id
            
        recent_memories = load_recent_memories(
            agent_id=loop_request.agent_id,
            memory_limit=memory_limit,
            project_id=project_id_filter
        )
        
        # Format memories for reflection
        memory_entries = "\n".join([
            f"- {m['timestamp']}: {m['type']} - {m['content']}"
            for m in recent_memories
        ])
        
        # Initialize LLM Engine
        llm_engine = LLMEngine()
        
        # Generate reflection based on loop type
        reflection_prompt = f"Reflect on the agent's last {len(recent_memories)} actions: {memory_entries}"
        if loop_request.loop_type == "task":
            reflection_prompt = f"Analyze the current task status based on these recent actions: {memory_entries}"
        elif loop_request.loop_type == "planning":
            reflection_prompt = f"Evaluate progress on current goals based on these actions: {memory_entries}"
        
        reflection = llm_engine.infer(
            prompt=reflection_prompt,
            model="openai"
        )
        
        # Generate plan based on reflection
        plan_prompt = f"Based on this reflection: '{reflection}', what should the agent do next?"
        plan = llm_engine.infer(
            prompt=plan_prompt,
            model="openai"
        )
        
        # Write summary + plan into memory
        loop_summary = f"Reflection: {reflection}\n\nPlan: {plan}"
        memory = write_memory(
            agent_id=loop_request.agent_id,
            type="loop_snapshot",
            content=f"{agent_name} completed a loop: {reflection[:100]}... and planned {plan[:100]}...",
            tags=["reflection", "planning", loop_request.loop_type],
            project_id=loop_request.project_id,
            status=loop_request.status if loop_request.status else "success",
            task_type=loop_request.task_type if loop_request.task_type else "loop",
            task_id=loop_request.task_id,
            memory_trace_id=loop_request.memory_trace_id
        )
        
        # Return full loop result with structured format according to SDK Contract v1.0.0
        return_data = {
            "status": "success",
            "loop_summary": reflection,
            "loop_result": plan,
            "cycle_number": current_loop_count,
            "loop_count": current_loop_count,  # Include current loop count in response
            "memory_id": memory["memory_id"],
            "task_id": loop_request.task_id if loop_request.task_id else str(uuid.uuid4()),
            "project_id": loop_request.project_id if loop_request.project_id else "",
            "memory_trace_id": loop_request.memory_trace_id if loop_request.memory_trace_id else memory["memory_id"]
        }
        
        # Reset agent state to "idle" after loop completes
        agent_registry[loop_request.agent_id]["agent_state"] = "idle"
        save_agent_registry()
        
        return return_data
    except Exception as e:
        logger.error(f"Error executing cognitive loop: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to execute cognitive loop: {str(e)}"
            }
        )
