"""
Agent Modules API Module

This module provides API endpoints for agent operations including listing agents.
"""

print("📁 Loaded: agent.py (AgentRunner route file)")

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
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

# Import schemas
from app.schemas.agent.agent_list_schema import AgentListResponse

# Configure logging
logger = logging.getLogger("api.modules.agent")

# Create router
router = APIRouter(prefix="/modules/agent", tags=["Agent Modules"])
print("🧠 Route defined: /api/modules/agent/run -> run_agent_endpoint")
print("🧠 Route defined: /api/modules/agent/create -> create_agent_endpoint")
print("🧠 Route defined: /api/modules/agent/list -> list_agents_endpoint")
print("🧠 Route defined: /api/modules/agent/loop -> loop_agent_endpoint")
# REMOVED: Conflicting delegate route
# print("🧠 Route defined: /api/modules/agent/delegate -> delegate_task_endpoint")

# Initialize agent registry
agent_registry = {}

# Path for persistent storage
AGENTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "agents.json")

# Path for system caps configuration
SYSTEM_CAPS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "system_caps.json")

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
print(f"🔒 Loaded system caps: max_loops_per_task={system_caps['max_loops_per_task']}, max_delegation_depth={system_caps['max_delegation_depth']}")

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
    """
    Agent run request model compliant with Promethios SDK Contract v1.0.0
    
    This model defines the schema for agent run requests, including task identification,
    project context, memory tracing, and structured input/output specifications.
    """
    agent_id: str
    task_id: str  # UUID for task identification
    project_id: str  # String for project scope
    memory_trace_id: Optional[str] = None  # String for memory tracing
    objective: str  # String describing the task objective
    input_data: Dict[str, Any] = Field(default_factory=dict)  # Object containing input data
    expected_output_type: Optional[str] = None  # String specifying expected output format

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

# Pydantic model for agent delegation request
class AgentDelegateRequest(BaseModel):
    from_agent: str
    to_agent: str
    task: str
    auto_execute: Optional[bool] = False
    delegation_depth: Optional[int] = 0  # Track delegation depth

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

@router.get("/list", response_model=AgentListResponse)
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
        return AgentListResponse(
            status="ok",
            agents=agents_list
        )
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
    Send a task to a specific agent and return a structured response compliant with Promethios SDK Contract v1.0.0.
    
    This endpoint processes structured task payloads, routes them to the LLM provider via LLMEngine,
    and returns standardized responses with proper metadata. Results are logged to memory for traceability.
    
    Request body:
    - agent_id: ID of the agent to run
    - task_id: UUID for task identification
    - project_id: String for project scope
    - memory_trace_id: (Optional) String for memory tracing
    - objective: String describing the task objective
    - input_data: Object containing input data
    - expected_output_type: (Optional) String specifying expected output format
    
    Returns:
    - status: "success" | "error" | "incomplete"
    - log: String describing the processing result
    - output: Object containing result_text and other fields
    - task_id: UUID for task identification
    - project_id: String for project scope
    - memory_trace_id: String for memory tracing
    - contract_version: String indicating SDK contract version
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
                    "log": f"Agent with ID '{run_request.agent_id}' not found",
                    "task_id": run_request.task_id,
                    "project_id": run_request.project_id,
                    "memory_trace_id": run_request.memory_trace_id,
                    "contract_version": "v1.0.0"
                }
            )
        
        # Get agent metadata
        agent_data = agent_registry[run_request.agent_id]
        agent_name = agent_data.get("name", run_request.agent_id.upper())
        
        # Update agent state to "responding" and last_active timestamp
        agent_registry[run_request.agent_id]["agent_state"] = "responding"
        agent_registry[run_request.agent_id]["last_active"] = datetime.utcnow().isoformat()
        save_agent_registry()
        
        # Format prompt with agent context and objective
        formatted_prompt = f"[Agent {agent_name}]: {run_request.objective}"
        
        # Add input data to prompt if available
        if run_request.input_data:
            formatted_prompt += f"\n\nInput Data: {json.dumps(run_request.input_data, indent=2)}"
        
        # Process the prompt with LLMEngine
        start_time = time.time()
        response_text = LLMEngine.infer(formatted_prompt)
        process_time = time.time() - start_time
        
        # Update agent state to "idle" and last_active timestamp
        agent_registry[run_request.agent_id]["agent_state"] = "idle"
        agent_registry[run_request.agent_id]["last_active"] = datetime.utcnow().isoformat()
        save_agent_registry()
        
        # Write memory for the agent
        memory = write_memory(
            agent_id=run_request.agent_id,
            type="task_execution",
            content=f"Objective: {run_request.objective}\n\nResponse: {response_text}",
            tags=["task", "execution"],
            project_id=run_request.project_id,
            status="completed",
            task_type="run",
            task_id=run_request.task_id,
            memory_trace_id=run_request.memory_trace_id
        )
        
        # Return structured response
        return {
            "status": "success",
            "log": f"Agent {agent_name} processed task in {process_time:.2f}s",
            "output": {
                "result_text": response_text,
                "format": "text",
                "processing_time": process_time
            },
            "task_id": run_request.task_id,
            "project_id": run_request.project_id,
            "memory_trace_id": run_request.memory_trace_id or memory["memory_id"],
            "contract_version": "v1.0.0"
        }
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "log": f"Failed to run agent: {str(e)}",
                "task_id": body.get("task_id", "unknown"),
                "project_id": body.get("project_id", "unknown"),
                "memory_trace_id": body.get("memory_trace_id", "unknown"),
                "contract_version": "v1.0.0"
            }
        )

@router.post("/loop")
async def loop_agent(request: Request):
    """
    Execute a cognitive loop for an agent.
    
    This endpoint processes loop requests, executes the specified loop type,
    and returns structured responses with loop results and metadata.
    
    Request body:
    - agent_id: ID of the agent to loop
    - loop_type: Type of loop to execute (reflective, task, planning)
    - memory_limit: Maximum number of memories to include in context
    - project_id: (Optional) Project ID for context
    - task_id: (Optional) UUID for task identification
    - memory_trace_id: (Optional) String for memory tracing
    - max_cycles: (Optional) Maximum number of loop cycles to execute
    - exit_conditions: (Optional) List of conditions that will exit the loop
    
    Returns:
    - status: "ok" if successful, "error" if error occurred
    - loop_id: UUID for the loop
    - loop_type: Type of loop executed
    - loop_cycles: Number of cycles executed
    - loop_result: Result of the loop execution
    - loop_summary: Summary of the loop execution
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
        
        # Get current loop count for this task
        current_loop_count = loop_request.loop_count if loop_request.loop_count is not None else 0
        
        # Check if max_loops_per_task has been reached
        if current_loop_count >= system_caps["max_loops_per_task"]:
            # Log the failure to memory
            memory = write_memory(
                agent_id=loop_request.agent_id,
                type="system_halt",
                content=f"Loop limit exceeded: {current_loop_count} loops reached for task {loop_request.task_id}",
                tags=["error", "loop_limit", "system_halt"],
                project_id=loop_request.project_id,
                status="error",
                task_type="loop",
                task_id=loop_request.task_id,
                memory_trace_id=loop_request.memory_trace_id
            )
            
            # Return error response
            return JSONResponse(
                status_code=429,  # Too Many Requests
                content={
                    "status": "error",
                    "reason": "Loop limit exceeded",
                    "loop_count": current_loop_count,
                    "task_id": loop_request.task_id
                }
            )
        
        # Generate loop_id for tracking
        loop_id = str(uuid.uuid4())
        
        # Generate task_id if not provided
        if not loop_request.task_id:
            loop_request.task_id = str(uuid.uuid4())
            
        # Generate memory_trace_id if not provided
        if not loop_request.memory_trace_id:
            loop_request.memory_trace_id = str(uuid.uuid4())
        
        # Get agent metadata
        agent_data = agent_registry[loop_request.agent_id]
        agent_name = agent_data.get("name", loop_request.agent_id.upper())
        
        # Update agent state to "looping" and last_active timestamp
        agent_registry[loop_request.agent_id]["agent_state"] = "looping"
        agent_registry[loop_request.agent_id]["last_active"] = datetime.utcnow().isoformat()
        
        # Increment loop count for this agent
        agent_registry[loop_request.agent_id]["loop_count"] = agent_registry[loop_request.agent_id].get("loop_count", 0) + 1
        save_agent_registry()
        
        # Load recent memories for context
        recent_memories = load_recent_memories(
            agent_id=loop_request.agent_id,
            memory_limit=loop_request.memory_limit,
            memory_type=None,  # Include all memory types
            project_id=loop_request.project_id
        )
        
        # Format memories for context
        memory_context = ""
        for memory in recent_memories:
            memory_context += f"[{memory['type']}] {memory['content']}\n\n"
        
        # Execute loop based on type
        loop_result = ""
        loop_summary = ""
        
        if loop_request.loop_type == "reflective":
            # Generate reflection based on recent memories
            reflection = generate_reflection(
                agent_id=loop_request.agent_id,
                memory_limit=loop_request.memory_limit,
                project_id=loop_request.project_id
            )
            
            loop_result = reflection["content"]
            loop_summary = "Generated reflection based on recent memories"
            
            # Write memory for the reflection
            write_memory(
                agent_id=loop_request.agent_id,
                type="reflection",
                content=loop_result,
                tags=["loop", "reflection"],
                project_id=loop_request.project_id,
                status="completed",
                task_type="loop",
                task_id=loop_request.task_id,
                memory_trace_id=loop_request.memory_trace_id
            )
        elif loop_request.loop_type == "task":
            # Format prompt for task-based loop
            task_prompt = f"[Agent {agent_name}] Execute the following task based on your recent memories and knowledge:\n\n"
            
            if memory_context:
                task_prompt += f"Recent memories:\n{memory_context}\n\n"
            
            task_prompt += "Task: Generate a plan for implementing a new feature in the personal-ai-agent project."
            
            # Process the prompt with LLMEngine
            loop_result = LLMEngine.infer(task_prompt)
            loop_summary = "Executed task-based loop"
            
            # Write memory for the task execution
            write_memory(
                agent_id=loop_request.agent_id,
                type="task_execution",
                content=loop_result,
                tags=["loop", "task"],
                project_id=loop_request.project_id,
                status="completed",
                task_type="loop",
                task_id=loop_request.task_id,
                memory_trace_id=loop_request.memory_trace_id
            )
        elif loop_request.loop_type == "planning":
            # Format prompt for planning loop
            planning_prompt = f"[Agent {agent_name}] Generate a plan based on your recent memories and knowledge:\n\n"
            
            if memory_context:
                planning_prompt += f"Recent memories:\n{memory_context}\n\n"
            
            planning_prompt += "Task: Create a detailed plan for the next development sprint."
            
            # Process the prompt with LLMEngine
            loop_result = LLMEngine.infer(planning_prompt)
            loop_summary = "Generated planning loop"
            
            # Write memory for the planning
            write_memory(
                agent_id=loop_request.agent_id,
                type="planning",
                content=loop_result,
                tags=["loop", "planning"],
                project_id=loop_request.project_id,
                status="completed",
                task_type="loop",
                task_id=loop_request.task_id,
                memory_trace_id=loop_request.memory_trace_id
            )
        else:
            loop_result = "Unknown loop type"
            loop_summary = f"Attempted to execute unknown loop type: {loop_request.loop_type}"
        
        # Update agent state to "idle" and last_active timestamp
        agent_registry[loop_request.agent_id]["agent_state"] = "idle"
        agent_registry[loop_request.agent_id]["last_active"] = datetime.utcnow().isoformat()
        save_agent_registry()
        
        # Return structured response
        return {
            "status": "ok",
            "loop_id": loop_id,
            "loop_type": loop_request.loop_type,
            "loop_cycles": 1,
            "loop_count": current_loop_count + 1,  # Increment loop count
            "loop_result": loop_result,
            "loop_summary": loop_summary
        }
    except Exception as e:
        logger.error(f"Error executing loop: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to execute loop: {str(e)}"
            }
        )

# REMOVED: Conflicting delegate route
# @router.post("/delegate")
# async def delegate_task(request: Request):
#     """
#     Delegate a task from one agent to another.
#     
#     This endpoint handles task delegation between agents, including memory logging
#     and optional auto-execution of the delegated task.
#     
#     Request body
