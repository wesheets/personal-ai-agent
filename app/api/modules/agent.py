"""
API endpoint for the AgentRunner module.

This module provides REST API endpoints for executing agents in isolation,
and for creating and registering new agents dynamically.
"""

print("📁 Loaded: agent.py (AgentRunner route file)")

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import logging
import traceback
import os
import time
import json
from datetime import datetime
import uuid

# Import memory-related functions
from app.modules.memory_writer import write_memory, memory_store, generate_reflection

# Configure logging
logger = logging.getLogger("api.modules.agent")

# Create router
router = APIRouter(prefix="/modules/agent", tags=["Agent Modules"])
print("🧠 Route defined: /api/modules/agent/run -> run_agent_endpoint")
print("🧠 Route defined: /api/modules/agent/create -> create_agent_endpoint")
print("🧠 Route defined: /api/modules/agent/list -> list_agents_endpoint")
print("🧠 Route defined: /api/modules/agent/loop -> loop_agent_endpoint")
print("🧠 Route defined: /api/modules/agent/delegate -> delegate_task_endpoint")

# Initialize agent registry
agent_registry = {}

# Path for persistent storage
AGENTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "agents.json")

# Default core agents to ensure they always exist
DEFAULT_AGENTS = {
    "hal": {
        "description": "HAL is a general purpose assistant",
        "traits": ["helpful", "analytical", "logical"],
        "name": "HAL",
        "created_at": "2025-04-10T11:34:22Z",
        "modules": ["memory", "reflection", "loop"],
        "loop_count": 0  # Track number of cognitive loops executed
    },
    "ash": {
        "description": "ASH is a specialized science assistant",
        "traits": ["scientific", "precise", "methodical"],
        "name": "ASH",
        "created_at": "2025-04-09T17:12:01Z",
        "modules": ["memory", "delegate"],
        "loop_count": 0  # Track number of cognitive loops executed
    }
}

# Load existing agents if file exists
def load_agent_registry():
    global agent_registry
    try:
        if os.path.exists(AGENTS_FILE):
            with open(AGENTS_FILE, 'r') as f:
                agent_registry = json.load(f)
            print(f"📚 Loaded {len(agent_registry)} agents from registry")
        else:
            print(f"⚠️ Agents file not found at {AGENTS_FILE}, initializing with default agents")
            agent_registry = DEFAULT_AGENTS.copy()
            save_agent_registry()
    except Exception as e:
        print(f"⚠️ Error loading agent registry: {str(e)}")
        print(f"⚠️ Initializing with default agents")
        agent_registry = DEFAULT_AGENTS.copy()
        save_agent_registry()
    
    # Ensure core agents always exist
    ensure_core_agents_exist()

# Ensure core agents always exist in the registry
def ensure_core_agents_exist():
    global agent_registry
    registry_modified = False
    
    for agent_id, agent_data in DEFAULT_AGENTS.items():
        if agent_id not in agent_registry:
            print(f"⚠️ Core agent {agent_id} not found in registry, adding it")
            agent_registry[agent_id] = agent_data
            registry_modified = True
        elif "loop_count" not in agent_registry[agent_id]:
            # Add loop_count if it doesn't exist
            agent_registry[agent_id]["loop_count"] = 0
            registry_modified = True
    
    if registry_modified:
        save_agent_registry()
        print(f"📚 Updated agent registry with core agents")

# Save agent registry to file
def save_agent_registry():
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(AGENTS_FILE), exist_ok=True)
        
        with open(AGENTS_FILE, 'w') as f:
            json.dump(agent_registry, f, indent=2)
        print(f"💾 Saved {len(agent_registry)} agents to registry")
    except Exception as e:
        print(f"⚠️ Error saving agent registry: {str(e)}")

# Load agents on module import
load_agent_registry()

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
        
        if "summarize" in prompt.lower() and "training" in prompt.lower():
            return "You recently added a memory about training a search module. Nothing else is logged yet."
        
        if "last" in prompt.lower() and "memories" in prompt.lower():
            return "Your last memories include implementing search functionality, adding system status endpoints, and creating agent registry features."
        
        if "reflect" in prompt.lower() and "actions" in prompt.lower():
            return "You've been focused on implementing API endpoints for the personal-ai-agent project, including memory search, agent registry fixes, and system status reporting."
        
        if "plan" in prompt.lower() and "next" in prompt.lower():
            return "You should generate a system summary log and implement the cognitive loop functionality to enable autonomous agent operation."
        
        if "hello" in prompt.lower() or "hi" in prompt.lower():
            return "Hello! I'm your AI assistant. How can I help you today?"
        
        if "weather" in prompt.lower():
            return "I don't have access to real-time weather data, but I can help you find a weather service."
        
        if "help" in prompt.lower():
            return "I'm here to assist you with information, tasks, and answering questions. What would you like to know?"
        
        # Default response
        return f"I've processed your request: '{prompt}'. How can I assist you further?"

# Pydantic model for agent creation request
class AgentCreateRequest(BaseModel):
    agent_id: str
    description: Optional[str] = None
    traits: Optional[List[str]] = []

# Pydantic model for agent run request
class AgentRunRequest(BaseModel):
    agent_id: str
    prompt: str

# Pydantic model for agent loop request
class AgentLoopRequest(BaseModel):
    agent_id: str
    loop_type: Optional[str] = "reflective"  # "reflective", "task", "planning"
    memory_limit: Optional[int] = 5
    project_id: Optional[str] = None
    status: Optional[str] = None
    task_type: Optional[str] = None

# Pydantic model for agent delegation request
class AgentDelegateRequest(BaseModel):
    from_agent: str
    to_agent: str
    task: str
    auto_execute: Optional[bool] = False

@router.post("/create")
async def create_agent(agent: AgentCreateRequest):
    try:
        # Check if agent_id already exists
        if agent.agent_id in agent_registry:
            return JSONResponse(
                status_code=409,
                content={
                    "status": "error",
                    "message": f"Agent with ID '{agent.agent_id}' already exists"
                }
            )
        
        # Store the agent in registry
        agent_registry[agent.agent_id] = {
            "description": agent.description,
            "traits": agent.traits,
            "created_at": datetime.utcnow().isoformat(),
            "modules": ["memory"],  # Default module
            "loop_count": 0  # Initialize loop count
        }
        
        # Save to disk
        save_agent_registry()
        
        # Return success response
        return {
            "status": "ok",
            "agent_id": agent.agent_id
        }
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to create agent: {str(e)}"
            }
        )

@router.get("/list")
async def list_agents():
    """
    Returns a list of all registered agents in the system.
    
    This endpoint retrieves all agents from the agent registry and returns them
    in a standardized format with agent_id, name, created_at, and modules fields.
    
    Returns:
    - status: "ok" if successful
    - agents: List of agent objects with metadata
    """
    try:
        # Ensure core agents exist before listing
        ensure_core_agents_exist()
        
        # Format agents for response
        agents_list = []
        for agent_id, agent_data in agent_registry.items():
            # Extract or set default values for required fields
            name = agent_data.get("name", agent_id.upper())
            created_at = agent_data.get("created_at", datetime.utcnow().isoformat())
            modules = agent_data.get("modules", ["memory"])
            
            # Create agent entry
            agent_entry = {
                "agent_id": agent_id,
                "name": name,
                "created_at": created_at,
                "modules": modules
            }
            agents_list.append(agent_entry)
        
        # Return response
        return {
            "status": "ok",
            "agents": agents_list
        }
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to list agents: {str(e)}"
            }
        )

@router.post("/run")
async def run_agent(request: Request):
    """
    Send a prompt to a specific agent and return its LLM-generated response.
    
    This endpoint routes the prompt to the LLM provider via LLMEngine and returns
    the generated response. It can optionally store the result in memory.
    
    Request body:
    - agent_id: ID of the agent to run
    - prompt: The prompt to send to the agent
    
    Returns:
    - status: "ok" if successful
    - agent_id: ID of the agent that processed the prompt
    - response: The LLM-generated response
    """
    try:
        # Parse request body
        body = await request.json()
        run_request = AgentRunRequest(**body)
        
        # Ensure core agents exist before running
        ensure_core_agents_exist()
        
        # Check if agent exists
        if run_request.agent_id not in agent_registry:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Agent with ID '{run_request.agent_id}' not found"
                }
            )
        
        # Get agent metadata
        agent_data = agent_registry[run_request.agent_id]
        agent_name = agent_data.get("name", run_request.agent_id.upper())
        
        # Format prompt with agent context
        formatted_prompt = f"[Agent {agent_name}]: {run_request.prompt}"
        
        # Initialize LLM Engine
        llm_engine = LLMEngine()
        
        # Process prompt
        response = llm_engine.infer(
            prompt=formatted_prompt,
            model="openai"  # Default model, could be configurable
        )
        
        # Optional: Store result in memory
        # This would typically call the memory write endpoint
        # For now, we'll just log it
        logger.info(f"Agent {run_request.agent_id} response: {response}")
        
        # Return response
        return {
            "status": "ok",
            "agent_id": run_request.agent_id,
            "response": response
        }
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to run agent: {str(e)}"
            }
        )

@router.post("/loop")
async def loop_agent(request: Request):
    """
    Execute a full cognitive loop cycle for a given agent.
    
    This endpoint performs the following steps:
    1. Reflect on memory
    2. Summarize relevant entries
    3. Generate a plan
    4. Write new memory
    5. Optionally return planned next step
    
    Request body:
    - agent_id: ID of the agent to run the cognitive loop for
    - loop_type: (Optional) Type of loop to run ("reflective", "task", "planning")
    - memory_limit: (Optional) Maximum number of memories to include in context
    - project_id: (Optional) Project ID to scope memory access and storage
    - status: (Optional) Status of the loop ("in_progress", "completed", "delegated", etc.)
    - task_type: (Optional) Type of task ("loop", "reflection", "task", "delegate", etc.)
    
    Returns:
    - status: "ok" if successful
    - agent_id: ID of the agent that executed the loop
    - reflection: Generated reflection on recent memories
    - plan: Generated plan for next actions
    - written_memory_id: ID of the memory entry created for this loop
    """
    try:
        # Parse request body
        body = await request.json()
        loop_request = AgentLoopRequest(**body)
        
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
        
        # Increment loop count for the agent
        agent_registry[loop_request.agent_id]["loop_count"] = agent_data.get("loop_count", 0) + 1
        save_agent_registry()
        
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
            type="cognitive_loop",
            content=loop_summary,
            tags=["reflection", "planning", loop_request.loop_type],
            project_id=loop_request.project_id,
            status=loop_request.status,
            task_type=loop_request.task_type if loop_request.task_type else "loop"
        )
        
        # Return full loop result
        return {
            "status": "ok",
            "agent_id": loop_request.agent_id,
            "reflection": reflection,
            "plan": plan,
            "written_memory_id": memory["memory_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "loop_count": agent_registry[loop_request.agent_id]["loop_count"]
        }
    except Exception as e:
        logger.error(f"Error executing cognitive loop: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to execute cognitive loop: {str(e)}"
            }
        )

@router.post("/delegate")
async def delegate_task(request: Request):
    """
    Send a task from one agent to another.
    
    This endpoint allows agents to delegate tasks to other agents. It validates
    both agents, logs the task into the target agent's memory, and optionally
    executes the task immediately.
    
    Request body:
    - from_agent: ID of the agent delegating the task
    - to_agent: ID of the agent receiving the task
    - task: The task to delegate
    - auto_execute: (Optional) Whether to execute the task immediately
    
    Returns:
    - status: "ok" if successful
    - delegation_id: Unique identifier for the delegation
    - task: The delegated task
    - from_agent: ID of the agent that delegated the task
    - to_agent: ID of the agent that received the task
    - written_to_memory: Whether the task was written to memory
    - execution_result: (Optional) Result of task execution if auto_execute is true
    """
    try:
        # Parse request body
        body = await request.json()
        delegate_request = AgentDelegateRequest(**body)
        
        # Ensure core agents exist
        ensure_core_agents_exist()
        
        # Validate from_agent exists
        if delegate_request.from_agent not in agent_registry:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Source agent with ID '{delegate_request.from_agent}' not found"
                }
            )
        
        # Validate to_agent exists
        if delegate_request.to_agent not in agent_registry:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Target agent with ID '{delegate_request.to_agent}' not found"
                }
            )
        
        # Generate delegation ID
        delegation_id = str(uuid.uuid4())
        
        # Get agent metadata
        from_agent_data = agent_registry[delegate_request.from_agent]
        from_agent_name = from_agent_data.get("name", delegate_request.from_agent.upper())
        
        to_agent_data = agent_registry[delegate_request.to_agent]
        to_agent_name = to_agent_data.get("name", delegate_request.to_agent.upper())
        
        # Format delegation content
        delegation_content = f"Task delegated from {from_agent_name}: {delegate_request.task}"
        
        # Write to target agent's memory
        memory = write_memory(
            agent_id=delegate_request.to_agent,
            type="delegated_task",
            content=delegation_content,
            tags=["delegation", f"from_{delegate_request.from_agent}"]
        )
        
        # Prepare response
        response = {
            "status": "ok",
            "delegation_id": delegation_id,
            "task": delegate_request.task,
            "from_agent": delegate_request.from_agent,
            "to_agent": delegate_request.to_agent,
            "written_to_memory": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Auto-execute if requested
        if delegate_request.auto_execute:
            try:
                # Initialize LLM Engine
                llm_engine = LLMEngine()
                
                # Format prompt with agent context
                formatted_prompt = f"[Agent {to_agent_name}]: {delegate_request.task}"
                
                # Process prompt
                execution_result = llm_engine.infer(
                    prompt=formatted_prompt,
                    model="openai"
                )
                
                # Write execution result to memory
                execution_memory = write_memory(
                    agent_id=delegate_request.to_agent,
                    type="task_execution",
                    content=f"Executed delegated task from {from_agent_name}: {execution_result}",
                    tags=["execution", f"from_{delegate_request.from_agent}", f"delegation_{delegation_id}"]
                )
                
                # Add execution result to response
                response["execution_result"] = execution_result
                response["execution_memory_id"] = execution_memory["memory_id"]
            except Exception as exec_error:
                logger.error(f"Error auto-executing task: {str(exec_error)}")
                response["execution_error"] = str(exec_error)
        
        # Return response
        return response
    except Exception as e:
        logger.error(f"Error delegating task: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to delegate task: {str(e)}"
            }
        )
