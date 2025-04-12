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
import sqlite3

# Import the SQLite memory database
from app.db.memory_db import memory_db

# Configure logging
logger = logging.getLogger("api.modules.memory")

# Path for system caps configuration
SYSTEM_CAPS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "system_caps.json")

# Initialize global memory_store for in-memory access
memory_store = []

# Function to initialize memory_store from SQLite database
def initialize_memory_store():
    """
    Initialize the in-memory store from SQLite database on startup
    to ensure persistence across app restarts.
    """
    global memory_store
    try:
        # Clear the current memory_store to avoid duplicates
        memory_store.clear()
        
        try:
            # Ensure DB connection is open before attempting to read
            conn = memory_db._get_connection()
            
            # Get recent memories from SQLite database (limit to a reasonable number)
            recent_memories = memory_db.read_memories(limit=1000)
            
            # Add memories to in-memory store
            memory_store.extend(recent_memories)
            
            logger.info(f"✅ Initialized memory_store with {len(memory_store)} memories from SQLite database")
            print(f"🧠 [INIT] Loaded {len(memory_store)} memories from SQLite database into memory_store")
            print(f"🧠 [INIT] Memory IDs: {[m['memory_id'] for m in memory_store]}")
            
            return len(memory_store)
        except sqlite3.ProgrammingError as e:
            if "closed database" in str(e):
                logger.error(f"❌ Memory read failed: DB closed during initialization")
                print(f"❌ [INIT] Memory read failed: DB closed during initialization")
                return 0
            else:
                raise
    except Exception as e:
        logger.error(f"❌ Error initializing memory_store from SQLite: {str(e)}")
        print(f"❌ [INIT] Error loading memories from SQLite: {str(e)}")
        return 0

# Initialize memory_store on module import
initialized_count = initialize_memory_store()
logger.info(f"🧠 Memory module loaded with {initialized_count} memories from SQLite database")

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

class MemoryWriteRequest(BaseModel):
    agent_id: str
    user_id: Optional[str] = None
    memory_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    project_id: Optional[str] = None
    status: Optional[str] = None
    task_type: Optional[str] = None
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    memory_trace_id: Optional[str] = None

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
                memory_trace_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
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
        metadata: Optional metadata dictionary for additional structured data
        
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
            "memory_trace_id": memory_trace_id,
            "metadata": metadata
        }
        
        # Add agent tone if available
        if agent_tone:
            memory["agent_tone"] = agent_tone
            logger.info(f"🎭 Added tone profile for {agent_id}")
        
        # Write to SQLite database
        try:
            # First, ensure we have a fresh connection
            memory_db.close()  # Close any existing connection
            # Get a new connection
            conn = memory_db._get_connection()
            # Now attempt the write with the fresh connection
            memory = memory_db.write_memory(memory)
        except sqlite3.ProgrammingError as e:
            if "closed database" in str(e):
                logger.warning(f"⚠️ Reinitializing connection due to closed DB")
                print(f"⚠️ [WRITE_MEMORY] Reinitializing connection due to closed DB")
                # Force close and get a completely new connection
                try:
                    memory_db.close()
                except:
                    pass  # Ignore errors during close
                
                # Get a fresh connection and retry
                conn = memory_db._get_connection()
                memory = memory_db.write_memory(memory)
            else:
                raise
        
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
                
                # Include agent_tone and custom metadata if available
                shared_metadata = {
                    "agent_name": agent_id,
                    "type": type,
                    "memory_id": memory["memory_id"]
                }
                
                if agent_tone:
                    shared_metadata["agent_tone"] = agent_tone
                    
                # Include any custom metadata provided by the caller
                if metadata:
                    shared_metadata.update(metadata)
                
                await shared_memory.store_memory(
                    content=content,
                    metadata=shared_metadata,
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
async def memory_write_endpoint(request: MemoryWriteRequest):
    """
    Write a memory entry with full metadata and scope support.
    
    This endpoint allows agents, developers, or external systems to write structured 
    memories directly for debugging, manual inserts, admin overrides, or scripting.
    
    Parameters:
    - agent_id: ID of the agent (required)
    - user_id: ID of the user (optional, for scoping)
    - memory_type: Type of memory (required)
    - content: Content of the memory (required)
    - metadata: Additional structured data (optional)
    - tags: List of tags (optional)
    - project_id: Project context (optional)
    - status: Status of the memory (optional)
    - task_type: Type of task (optional)
    - task_id: ID of the task (optional)
    - session_id: ID of the session (optional)
    - memory_trace_id: ID for memory tracing (optional)
    
    Returns:
    - status: "ok" if successful
    - memory_id: ID of the created memory
    """
    try:
        logger.info(f"🧠 Writing memory for {request.agent_id}: type={request.memory_type}")
        
        # Create tags list, including user_id as a scope if provided
        tags = request.tags.copy() if request.tags else []
        
        # Add user scope tag if user_id is provided
        if request.user_id:
            user_scope = f"user:{request.user_id}"
            if user_scope not in tags:
                tags.append(user_scope)
        
        # Write memory with all provided parameters
        memory = write_memory(
            agent_id=request.agent_id,
            type=request.memory_type,
            content=request.content,
            tags=tags,
            project_id=request.project_id,
            status=request.status,
            task_type=request.task_type,
            task_id=request.task_id,
            memory_trace_id=request.memory_trace_id,
            metadata=request.metadata
        )
        
        logger.info(f"✅ Memory written: {memory['memory_id']}")
        return JSONResponse(status_code=200, content={
            "status": "ok", 
            "memory_id": memory["memory_id"]
        })
    except Exception as e:
        logger.error(f"❌ Error writing memory: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error", 
            "message": str(e)
        })

@router.get("/thread")
async def memory_thread(
    goal_id: Optional[str] = None,
    task_id: Optional[str] = None,
    memory_trace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    order: Optional[str] = "asc",
    limit: Optional[int] = 50
):
    """
    Retrieve a sequence of connected memory entries, logically threaded by shared context.
    
    This endpoint returns memories that are connected by goal_id, task_id, or memory_trace_id,
    allowing clients to view complete memory threads for specific tasks or goals.
    
    Parameters:
    - goal_id: (Optional) Filter memories by goal ID
    - task_id: (Optional) Filter memories by task ID
    - memory_trace_id: (Optional) Filter memories by memory trace ID
    - user_id: (Optional) Scope to a specific user
    - agent_id: (Optional) Scope to a specific agent
    - order: (Optional) Sort direction, "asc" or "desc", default is "asc"
    - limit: (Optional) Maximum number of memories to return, default is 50
    
    Returns:
    - status: "ok" if successful
    - thread: List of memory entries sorted chronologically
    """
    # PROM-247.8 Fix: Simplified implementation that reads directly from database
    # and bypasses memory_store completely to avoid desynchronization issues
    try:
        # Validate that at least one of goal_id, task_id, or memory_trace_id is provided
        if not goal_id and not task_id and not memory_trace_id:
            logger.error("Missing required filter: At least one of goal_id, task_id, or memory_trace_id is required")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "At least one of goal_id, task_id, or memory_trace_id is required"
                }
            )
        
        # Validate order parameter
        if order and order.lower() not in ["asc", "desc"]:
            logger.error(f"Invalid order parameter: {order}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Order parameter must be 'asc' or 'desc'"
                }
            )
        
        # Initialize memory_db to ensure fresh connection
        db = MemoryDB()
        logger.info(f"✅ Initialized fresh MemoryDB instance for memory_thread request")
        
        # Read fresh memories directly from DB with a high limit
        all_memories = db.read_memories(limit=1000)
        logger.info(f"Retrieved {len(all_memories)} memories from database")
        
        # Filter memories based on provided criteria
        filtered_memories = []
        for m in all_memories:
            # Convert SQLite Row to dict
            m = dict(m)
            
            # Filter by goal_id if provided
            if goal_id and not (
                str(m.get("goal_id", "")).strip() == str(goal_id).strip() or
                (m.get("metadata") and isinstance(m.get("metadata"), dict) and 
                 str(m.get("metadata", {}).get("goal_id", "")).strip() == str(goal_id).strip())
            ):
                continue
            
            # Filter by task_id if provided
            if task_id and str(m.get("task_id", "")).strip() != str(task_id).strip():
                continue
                
            # Filter by memory_trace_id if provided
            if memory_trace_id and str(m.get("memory_trace_id", "")).strip() != str(memory_trace_id).strip():
                continue
                
            # Filter by agent_id if provided
            if agent_id and str(m.get("agent_id", "")).strip() != str(agent_id).strip():
                continue
                
            # Filter by user_id if provided (using tags)
            if user_id:
                user_tag = f"user:{user_id}"
                if "tags" not in m or user_tag not in m["tags"]:
                    continue
            
            # If we got here, the memory passed all filters
            filtered_memories.append(m)
        
        logger.info(f"After filtering: found {len(filtered_memories)} matching memories")
        
        # Sort memories by timestamp
        if order and order.lower() == "asc":
            filtered_memories.sort(key=lambda m: m.get("timestamp", ""))
            logger.info("Sorted memories in ascending order")
        else:
            filtered_memories.sort(key=lambda m: m.get("timestamp", ""), reverse=True)
            logger.info("Sorted memories in descending order")
        
        # Apply limit
        if limit and limit > 0 and len(filtered_memories) > limit:
            filtered_memories = filtered_memories[:limit]
            logger.info(f"Limited results to {limit} memories")
        
        # Format memories for response
        thread = []
        for memory in filtered_memories:
            # Extract relevant fields for the response
            memory_entry = {
                "memory_type": memory.get("type"),
                "timestamp": memory.get("timestamp"),
                "content": memory.get("content"),
                "memory_id": memory.get("memory_id")
            }
            
            # Add task_id if present
            if memory.get("task_id"):
                memory_entry["task_id"] = memory.get("task_id")
            
            # Add goal_id if present at top level
            if memory.get("goal_id"):
                memory_entry["goal_id"] = memory.get("goal_id")
            # Or if present in metadata
            elif memory.get("metadata") and memory.get("metadata").get("goal_id"):
                memory_entry["goal_id"] = memory.get("metadata").get("goal_id")
            
            # Add result if present in metadata (for task_result type)
            if memory.get("type") == "task_result" and memory.get("metadata") and memory.get("metadata").get("result"):
                memory_entry["result"] = memory.get("metadata").get("result")
            
            # Add confidence_delta if present in metadata (for feedback_summary type)
            if memory.get("type") == "feedback_summary" and memory.get("metadata") and memory.get("metadata").get("confidence_delta"):
                memory_entry["confidence_delta"] = memory.get("metadata").get("confidence_delta")
            
            thread.append(memory_entry)
        
        logger.info(f"Returning {len(thread)} formatted memory entries")
        
        # Return the thread
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "thread": thread
            }
        )
    except Exception as e:
        logger.error(f"❌ Error retrieving memory thread: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to retrieve memory thread: {str(e)}"
            }
        )
    finally:
        # Always ensure connection is properly closed after request completes
        try:
            db.close()
            logger.info("✅ Database connection properly closed after memory_thread request")
        except Exception as close_error:
            logger.warning(f"⚠️ Non-critical error during final connection close: {str(close_error)}")
            pass

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
    memory_id: Optional[str] = None
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
                print(f"[READ] Memory found in database: {memory_id}")
                logger.info(f"✅ Memory found in database: {memory_id}")
                return {
                    "status": "ok",
                    "memories": [memory]
                }
            else:
                print(f"[READ] Memory not found: {memory_id}")
                logger.warning(f"⚠️ Memory not found: {memory_id}")
                return {
                    "status": "error",
                    "message": f"Memory not found: {memory_id}"
                }
        
        # Build filters for memory_db.read_memories
        filters = {}
        
        if agent_id:
            filters["agent_id"] = agent_id
        
        if type:
            filters["memory_type"] = type
        
        if since:
            filters["since"] = since
        
        if project_id:
            filters["project_id"] = project_id
        
        if task_id:
            filters["task_id"] = task_id
        
        if thread_id:
            filters["thread_id"] = thread_id
        
        if limit:
            filters["limit"] = limit
        
        # Query memories from database
        memories = memory_db.read_memories(**filters)
        
        # Additional filtering for tags (needs to be done after JSON parsing)
        if tag:
            memories = [m for m in memories if "tags" in m and tag in m["tags"]]
        
        # Log the results
        print(f"[READ] Retrieved {len(memories)} memories")
        logger.info(f"✅ Retrieved {len(memories)} memories")
        
        return {
            "status": "ok",
            "memories": memories
        }
    except Exception as e:
        logger.error(f"❌ Error reading memories: {str(e)}")
        return {
            "status": "error",
            "message": f"Error reading memories: {str(e)}"
        }

@router.post("/reflect")
async def memory_reflect_endpoint(request: ReflectionRequest):
    """
    Generate a reflection based on recent memories.
    
    This endpoint retrieves recent memories for the specified agent and generates
    a reflection based on those memories.
    
    Parameters:
    - agent_id: ID of the agent (required)
    - goal: Goal of the task (required)
    - context: Additional context for reflection (optional)
    - task_id: ID of the task (required)
    - project_id: Project context (required)
    - memory_trace_id: ID for memory tracing (required)
    - type: Type of reflection (optional, default is "memory")
    - limit: Maximum number of memories to consider (optional, default is 5)
    - loop_count: Number of loops for this task (optional, default is 0)
    
    Returns:
    - status: "ok" if successful
    - reflection: Generated reflection
    """
    try:
        logger.info(f"🧠 Generating reflection for {request.agent_id}")
        
        # Check if we've exceeded the maximum number of loops
        if request.loop_count >= system_caps["max_loops_per_task"]:
            logger.warning(f"⚠️ Maximum loop count reached for task {request.task_id}")
            return JSONResponse(status_code=200, content={
                "status": "ok",
                "reflection": "I've been reflecting on this task for a while. Let me try a different approach.",
                "loop_count": request.loop_count
            })
        
        # Get recent memories for the agent
        memories = memory_db.read_memories(
            agent_id=request.agent_id,
            project_id=request.project_id,
            task_id=request.task_id,
            limit=request.limit
        )
        
        # Generate reflection
        reflection = generate_reflection(memories)
        
        # Write reflection to memory
        memory = write_memory(
            agent_id=request.agent_id,
            type="reflection",
            content=reflection,
            tags=["reflection", f"task:{request.task_id}", f"project:{request.project_id}"],
            project_id=request.project_id,
            task_id=request.task_id,
            memory_trace_id=request.memory_trace_id,
            metadata={
                "goal": request.goal,
                "loop_count": request.loop_count + 1
            }
        )
        
        logger.info(f"✅ Reflection generated for {request.agent_id}")
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "reflection": reflection,
            "memory_id": memory["memory_id"],
            "loop_count": request.loop_count + 1
        })
    except Exception as e:
        logger.error(f"❌ Error generating reflection: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

@router.post("/memory/summarize")
async def memory_summarize_endpoint(request: SummarizeRequest):
    """
    Summarize memories for a specific task or goal.
    
    This endpoint retrieves memories for the specified agent and task, and generates
    a summary based on those memories.
    
    Parameters:
    - agent_id: ID of the agent (required)
    - goal: Goal of the task (required)
    - task_id: ID of the task (required)
    - project_id: Project context (required)
    - memory_trace_id: ID for memory tracing (required)
    - context: Additional context for summarization (optional)
    - type: Type of summary (optional)
    - limit: Maximum number of memories to consider (optional, default is 10)
    
    Returns:
    - status: "ok" if successful
    - summary: Generated summary
    """
    try:
        logger.info(f"🧠 Generating summary for {request.agent_id}")
        
        # Get memories for the agent and task
        memories = memory_db.read_memories(
            agent_id=request.agent_id,
            project_id=request.project_id,
            task_id=request.task_id,
            limit=request.limit
        )
        
        # Generate summary (placeholder implementation)
        if not memories:
            summary = "No memories to summarize."
        else:
            summary = f"Summary of {len(memories)} memories for task {request.task_id}."
        
        # Write summary to memory
        memory = write_memory(
            agent_id=request.agent_id,
            type="summary",
            content=summary,
            tags=["summary", f"task:{request.task_id}", f"project:{request.project_id}"],
            project_id=request.project_id,
            task_id=request.task_id,
            memory_trace_id=request.memory_trace_id,
            metadata={
                "goal": request.goal,
                "summary_type": request.type
            }
        )
        
        logger.info(f"✅ Summary generated for {request.agent_id}")
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "summary": summary,
            "memory_id": memory["memory_id"]
        })
    except Exception as e:
        logger.error(f"❌ Error generating summary: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

@router.get("/memory/recent")
async def memory_recent(
    agent_id: str,
    limit: Optional[int] = 10,
    memory_type: Optional[str] = None,
    project_id: Optional[str] = None
):
    """
    Get recent memories for an agent.
    
    This endpoint retrieves the most recent memories for the specified agent,
    with optional filtering by memory type and project.
    
    Parameters:
    - agent_id: ID of the agent (required)
    - limit: Maximum number of memories to return (optional, default is 10)
    - memory_type: Filter by memory type (optional)
    - project_id: Filter by project ID (optional)
    
    Returns:
    - status: "ok" if successful
    - memories: List of recent memories
    """
    try:
        logger.info(f"🧠 Getting recent memories for {agent_id}")
        
        # Build filters
        filters = {
            "agent_id": agent_id,
            "limit": limit
        }
        
        if memory_type:
            filters["memory_type"] = memory_type
        
        if project_id:
            filters["project_id"] = project_id
        
        # Query memories from database
        memories = memory_db.read_memories(**filters)
        
        logger.info(f"✅ Retrieved {len(memories)} recent memories for {agent_id}")
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "memories": memories
        })
    except Exception as e:
        logger.error(f"❌ Error getting recent memories: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

@router.post("/memory/search")
async def memory_search_endpoint(request: SearchRequest):
    """
    Search memories by content.
    
    This endpoint searches memories for the specified agent based on a query string.
    
    Parameters:
    - agent_id: ID of the agent (required)
    - query: Search query (required)
    - role: Filter by role (optional)
    - memory_type: Filter by memory type (optional)
    - limit: Maximum number of memories to return (optional, default is 25)
    - project_id: Filter by project ID (optional)
    
    Returns:
    - status: "ok" if successful
    - memories: List of matching memories
    """
    try:
        logger.info(f"🧠 Searching memories for {request.agent_id} with query: {request.query}")
        
        # Get all memories for the agent
        filters = {
            "agent_id": request.agent_id,
            "limit": 1000  # Get a large number to search through
        }
        
        if request.memory_type:
            filters["memory_type"] = request.memory_type
        
        if request.project_id:
            filters["project_id"] = request.project_id
        
        # Query memories from database
        memories = memory_db.read_memories(**filters)
        
        # Simple search implementation (case-insensitive substring match)
        query_lower = request.query.lower()
        matching_memories = []
        
        for memory in memories:
            if query_lower in memory.get("content", "").lower():
                matching_memories.append(memory)
                
                # Break if we've reached the limit
                if len(matching_memories) >= request.limit:
                    break
        
        logger.info(f"✅ Found {len(matching_memories)} matching memories for {request.agent_id}")
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "memories": matching_memories
        })
    except Exception as e:
        logger.error(f"❌ Error searching memories: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })
