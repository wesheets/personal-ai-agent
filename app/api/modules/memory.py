"""
Memory Module with SQLite Backend and In-Memory Store

This module provides memory-related functionality for agents, including:
- Writing memories to SQLite database and in-memory store
- Reading memories with flexible filtering
- Generating reflections based on memories
- Summarizing memories

The module uses both a SQLite database for persistent storage across deployments
and an in-memory store for immediate access within the same runtime.
"""

from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import json
import logging
import uuid
import asyncio

# Import the SQLite memory database
from app.db.memory_db import memory_db

# Configure logging
logger = logging.getLogger("api.modules.memory")

# Path for system caps configuration
SYSTEM_CAPS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "system_caps.json")

# Initialize global memory_store for in-memory access
memory_store = []

# Load system caps configuration
def load_system_caps():
    try:
        if os.path.exists(SYSTEM_CAPS_FILE):
            with open(SYSTEM_CAPS_FILE, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"⚠️ System caps file not found at {SYSTEM_CAPS_FILE}, using default caps")
            return {
                "max_loops_per_task": 3,
                "max_delegation_depth": 2
            }
    except Exception as e:
        logger.error(f"⚠️ Error loading system caps: {str(e)}")
        return {
            "max_loops_per_task": 3,
            "max_delegation_depth": 2
        }

# Load system caps
system_caps = load_system_caps()
logger.info(f"🔒 Memory module loaded system caps: max_loops_per_task={system_caps['max_loops_per_task']}, max_delegation_depth={system_caps['max_delegation_depth']}")

class MemoryEntry(BaseModel):
    agent_id: str
    memory_type: str
    content: str
    tags: List[str] = []
    project_id: Optional[str] = None
    status: Optional[str] = None
    task_type: Optional[str] = None

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
    
class SummarizeRequest(BaseModel):
    agent_id: str
    goal: str
    task_id: str
    project_id: str
    memory_trace_id: str
    context: Optional[List[Dict]] = None
    type: Optional[str] = None
    limit: int = 10

class ThreadRequest(BaseModel):
    agent_id: str
    limit: Optional[int] = 100
    project_id: Optional[str] = None

class SearchRequest(BaseModel):
    agent_id: str
    query: str
    role: Optional[str] = None
    memory_type: Optional[str] = None
    limit: Optional[int] = 25
    project_id: Optional[str] = None

router = APIRouter()

def write_memory(agent_id: str, type: str, content: str, tags: list, project_id: Optional[str] = None, 
                status: Optional[str] = None, task_type: Optional[str] = None, task_id: Optional[str] = None, 
                memory_trace_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Write a memory to both the SQLite database and in-memory store
    
    Args:
        agent_id: ID of the agent
        type: Type of memory
        content: Content of the memory
        tags: List of tags
        project_id: Optional project ID
        status: Optional status
        task_type: Optional task type
        task_id: Optional task ID
        memory_trace_id: Optional memory trace ID
        
    Returns:
        The memory with its memory_id
    """
    try:
        # Explicitly declare memory_store as global to prevent shadowing
        global memory_store
        
        # Get agent tone profile (placeholder - would need to be implemented)
        agent_tone = None  # get_agent_tone_profile(agent_id)
        
        # Create memory object
        memory = {
            "memory_id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "type": type,
            "content": content,
            "tags": tags,
            "timestamp": datetime.utcnow().isoformat(),
            "project_id": project_id,
            "status": status,
            "task_type": task_type,
            "task_id": task_id,
            "memory_trace_id": memory_trace_id
        }
        
        # Add agent tone if available
        if agent_tone:
            memory["agent_tone"] = agent_tone
            logger.info(f"🎭 Added tone profile for {agent_id}")
        
        # Write to SQLite database
        memory = memory_db.write_memory(memory)
        
        # Add diagnostic logging as requested
        print(f"🧠 [WRITE_MEMORY] memory_id: {memory['memory_id']}")
        print(f"🧠 [WRITE_MEMORY] Appending to store.")
        
        # IMPORTANT: Add to in-memory store for immediate access
        memory_store.append(memory)
        
        print(f"🧠 [WRITE_MEMORY] Store now has {len(memory_store)} entries.")
        
        # Keep existing debug logging for backward compatibility
        print(f"[WRITE] Appending to memory_store: {memory['memory_id']}")
        print(f"[WRITE] Store now has {len(memory_store)} memories")
        print(f"[WRITE] Memory store IDs: {[m['memory_id'] for m in memory_store]}")
        
        logger.info(f"🧠 Memory added to in-memory store, current count: {len(memory_store)}")
        
        # Also store in shared memory layer (placeholder - would need to be implemented)
        try:
            # Import here to avoid circular imports
            from app.core.shared_memory import get_shared_memory
            
            # Create async function to store in shared memory
            async def store_in_shared_memory():
                shared_memory = get_shared_memory()
                
                # Include agent_tone in metadata if available
                metadata = {
                    "agent_name": agent_id,
                    "type": type,
                    "memory_id": memory["memory_id"]
                }
                
                if agent_tone:
                    metadata["agent_tone"] = agent_tone
                
                await shared_memory.store_memory(
                    content=content,
                    metadata=metadata,
                    scope="agent",
                    agent_name=agent_id,
                    topics=tags
                )
            
            # Run the async function in a new event loop if we're not in an async context
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're in an async context, create a task
                    asyncio.create_task(store_in_shared_memory())
                else:
                    # We're not in an async context, run in a new loop
                    asyncio.run(store_in_shared_memory())
            except RuntimeError:
                # No event loop, run in a new one
                asyncio.run(store_in_shared_memory())
                
            logger.info(f"🧠 Memory also stored in shared memory layer for {agent_id}")
        except Exception as e:
            logger.warning(f"⚠️ Error storing in shared memory: {str(e)}")
        
        logger.info(f"🧠 Memory written for {agent_id}: {memory['memory_id']}")
        return memory
    except Exception as e:
        logger.error(f"❌ Error writing memory: {str(e)}")
        raise

def generate_reflection(memories: List[Dict]) -> str:
    """
    Generate a reflection based on a list of memories.
    This is a placeholder implementation that will be AI-powered later.
    
    Args:
        memories: List of memory dictionaries to reflect on
        
    Returns:
        A reflection string based on the memories
    """
    if not memories:
        return "No relevant memories to reflect on."
    
    return f"I have processed {len(memories)} memories. A pattern is forming..."

@router.post("/write")
async def memory_write(request: Request):
    try:
        body = await request.json()
        memory_entry = MemoryEntry(**body)
        
        memory = write_memory(
            agent_id=memory_entry.agent_id,
            type=memory_entry.memory_type,  # Pass memory_type to type parameter
            content=memory_entry.content,
            tags=memory_entry.tags,
            project_id=memory_entry.project_id,
            status=memory_entry.status,
            task_type=memory_entry.task_type
        )
        
        # Debug: Print all memory_ids in memory_store
        global memory_store
        memory_ids = [m["memory_id"] for m in memory_store]
        logger.info(f"🔍 DEBUG: memory_store contains {len(memory_ids)} memories: {memory_ids}")
        
        return JSONResponse(status_code=200, content={"status": "ok", "memory_id": memory["memory_id"]})
    except Exception as e:
        logger.error(f"❌ MemoryWriter error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.get("/read")
async def read_memory(
    agent_id: Optional[str] = None,
    type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: Optional[int] = 10,
    since: Optional[str] = None,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    memory_id: Optional[str] = None  # Added memory_id parameter
):
    """
    Read memories with flexible filtering options.
    
    This endpoint retrieves memories with optional filtering by agent_id, type, tag,
    timestamp, project_id, task_id, thread_id, and memory_id. Any combination of filters can be used.
    
    Parameters:
    - agent_id: (Optional) ID of the agent whose memories to retrieve
    - type: (Optional) Filter by memory type
    - tag: (Optional) Filter by tag
    - limit: (Optional) Maximum number of memories to return, default is 10
    - since: (Optional) ISO 8601 timestamp to filter memories after a specific time
    - project_id: (Optional) Filter by project context
    - task_id: (Optional) Filter by specific task
    - thread_id: (Optional) Filter by conversation thread
    - memory_id: (Optional) Retrieve a specific memory by its ID
    
    Returns:
    - status: "ok" if successful
    - memories: List of memory entries sorted by timestamp (newest first)
    """
    try:
        # Explicitly declare memory_store as global to prevent shadowing
        global memory_store
        
        # Enhanced debug logging to verify memory_store contents at read time
        print(f"[READ] Current memory store: {[m['memory_id'] for m in memory_store]}")
        
        # Debug: Print all memory_ids in memory_store
        memory_ids = [m["memory_id"] for m in memory_store]
        logger.info(f"🔍 DEBUG: memory_store contains {len(memory_ids)} memories: {memory_ids}")
        
        # If memory_id is provided, first check in-memory store for immediate access
        if memory_id:
            # Add diagnostic logging as requested
            print(f"🔍 [READ] Looking for memory_id: {memory_id}")
            print(f"🔍 [READ] memory_store: {[m['memory_id'] for m in memory_store]}")
            
            # Keep existing debug logging for backward compatibility
            print(f"[READ] Looking for memory_id: {memory_id}")
            
            # Check in-memory store first
            for memory in memory_store:
                if memory["memory_id"] == memory_id:
                    print(f"[READ] Memory found in memory_store: {memory_id}")
                    logger.info(f"✅ Memory found in memory_store: {memory_id}")
                    return {
                        "status": "ok",
                        "memories": [memory]
                    }
            
            # If not found in memory_store, try SQLite database
            print(f"📦 [READ] Memory not in memory_store. Checking DB...")
            print(f"[READ] Memory not found in memory_store, checking database: {memory_id}")
            logger.info(f"⚠️ Memory not found in memory_store, checking database: {memory_id}")
            memory = memory_db.read_memory_by_id(memory_id)
            print(f"📦 [READ] DB result: {memory}")
            
            if memory:
                # Add to memory_store for future in-memory access
                memory_store.append(memory)
                print(f"[READ] Memory found in database and added to memory_store: {memory_id}")
                print(f"[READ] Updated memory store: {[m['memory_id'] for m in memory_store]}")
                logger.info(f"✅ Memory found in database and added to memory_store: {memory_id}")
                return {
                    "status": "ok",
                    "memories": [memory]
                }
            else:
                print(f"[READ] Memory not found in memory_store or database: {memory_id}")
                logger.error(f"❌ Memory not found in memory_store or database: {memory_id}")
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": "error",
                        "message": f"Memory with ID {memory_id} not found"
                    }
                )
        
        # Otherwise, use flexible filtering
        memories = memory_db.read_memories(
            agent_id=agent_id,
            memory_type=type,
            tag=tag,
            limit=limit,
            since=since,
            project_id=project_id,
            task_id=task_id,
            thread_id=thread_id
        )
        
        return {
            "status": "ok",
            "memories": memories
        }
    except HTTPException as e:
        logger.error(f"❌ MemoryReader error: {str(e.detail)}")
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})
    except Exception as e:
        logger.error(f"❌ MemoryReader error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.post("/reflect")
async def reflect_on_memories(request: Request):
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
        
        # Get recent memories using the SQLite database
        memories = memory_db.read_memories(
            agent_id=reflection_request.agent_id,
            memory_type=reflection_request.type,
            limit=reflection_request.limit
        )
        
        # Generate reflection
        reflection_text = generate_reflection(memories)
        
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
            "loop_count": current_loop_count + 1  # Increment loop count in response
        }
    except Exception as e:
        # Log error details
        logger.error(f"❌ Reflection Engine error: {str(e)}")
        
        # Return SDK-compliant error response
        return JSONResponse(status_code=500, content={
            "status": "failure",
            "reflection": f"Error generating reflection: {str(e)}",
            "task_id": body.get("task_id", "unknown"),
            "project_id": body.get("project_id", "unknown"),
            "memory_trace_id": body.get("memory_trace_id", "unknown"),
            "agent_id": body.get("agent_id", "unknown")
        })

@router.post("/summarize")
async def summarize_memories_endpoint(request: Request):
    """
    Summarize recent memories for an agent into a coherent natural language summary.
    
    This endpoint complies with Promethios_Module_Contract_v1.0.0 by:
    - Validating required input fields (agent_id, goal, task_id, project_id, memory_trace_id)
    - Returning a structured response with all required fields
    - Writing memory with memory_type="summary" and all trace fields
    - Providing proper logging for failures or validation errors
    
    Request body:
    - agent_id: ID of the agent to generate summary for (required)
    - goal: Purpose of the summary (required)
    - task_id: Task identifier for tracing (required)
    - project_id: Project identifier for context (required)
    - memory_trace_id: Memory trace identifier for linking (required)
    - context: Optional list of memory or raw notes
    - type: Memory type to summarize (optional)
    - limit: Maximum number of memories to consider (optional, defaults to 10)
    
    Returns:
    - status: "success" if successful, "failure" if error occurred
    - summary: Generated summary text
    - task_id: Task identifier (echoed from request)
    - project_id: Project identifier (echoed from request)
    - memory_trace_id: Memory trace identifier (echoed from request)
    - agent_id: Agent identifier (echoed from request)
    """
    try:
        # Parse request body
        body = await request.json()
        summarize_request = SummarizeRequest(**body)
        
        # Get memories to summarize
        memories = []
        
        # If context is provided, use it directly
        if summarize_request.context:
            memories = summarize_request.context
        else:
            # Otherwise, fetch memories from the database
            memories = memory_db.read_memories(
                agent_id=summarize_request.agent_id,
                memory_type=summarize_request.type,
                limit=summarize_request.limit
            )
        
        # Generate summary
        summary_text = summarize_memories(memories)
        
        # Write summary as a new memory with all trace fields
        memory = write_memory(
            agent_id=summarize_request.agent_id,
            type="summary",
            content=summary_text,
            tags=["summary", "sdk_compliant"],
            project_id=summarize_request.project_id,
            task_id=summarize_request.task_id,
            memory_trace_id=summarize_request.memory_trace_id,
            status="completed"
        )
        
        # Log successful summary generation
        logger.info(f"✅ Summary generated for agent {summarize_request.agent_id} with task_id {summarize_request.task_id}")
        
        # Return SDK-compliant structured response
        return {
            "status": "success",
            "summary": summary_text,
            "task_id": summarize_request.task_id,
            "project_id": summarize_request.project_id,
            "memory_trace_id": summarize_request.memory_trace_id,
            "agent_id": summarize_request.agent_id
        }
    except Exception as e:
        # Log error details
        logger.error(f"❌ Summary Engine error: {str(e)}")
        
        # Return SDK-compliant error response
        return JSONResponse(status_code=500, content={
            "status": "failure",
            "summary": f"Error generating summary: {str(e)}",
            "task_id": body.get("task_id", "unknown"),
            "project_id": body.get("project_id", "unknown"),
            "memory_trace_id": body.get("memory_trace_id", "unknown"),
            "agent_id": body.get("agent_id", "unknown")
        })

# Import missing dependencies
from app.modules.memory_summarizer import summarize_memories
