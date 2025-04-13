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
from app.db.memory_db import memory_db, MemoryDB

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
            
            # Log the absolute database path
            logger.info(f"💾 DB PATH: {memory_db.get_path()}")
            
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
    goal_id: Optional[str] = None

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
                memory_trace_id: Optional[str] = None, metadata: Optional[Dict] = None, goal_id: Optional[str] = None) -> Dict[str, Any]:
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
        goal_id: Optional goal ID (stored at top level for efficient retrieval)
        
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
        
        # Add goal_id at top level if provided
        if goal_id:
            memory["goal_id"] = goal_id
            logger.info(f"🎯 Added top-level goal_id: {goal_id} for memory {memory['memory_id']}")
            
            # Also ensure it's in metadata for backward compatibility
            if metadata is None:
                memory["metadata"] = {"goal_id": goal_id}
            elif isinstance(metadata, dict) and "goal_id" not in metadata:
                memory["metadata"]["goal_id"] = goal_id
        
        # Extract goal_id from metadata if not provided directly but exists in metadata
        elif metadata and isinstance(metadata, dict) and "goal_id" in metadata:
            memory["goal_id"] = metadata["goal_id"]
            logger.info(f"🎯 Extracted goal_id from metadata: {metadata['goal_id']} for memory {memory['memory_id']}")
        
        # Add agent tone if available
        if agent_tone:
            memory["agent_tone"] = agent_tone
            logger.info(f"🎭 Added tone profile for {agent_id}")
        
        # Write to SQLite database using the singleton memory_db instance
        try:
            # First, ensure we have a fresh connection
            memory_db.close()  # Close any existing connection
            # Get a new connection
            conn = memory_db._get_connection()
            # Log the absolute database path
            logger.info(f"💾 DB PATH: Writing to {memory_db.get_path()}")
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
    - db_contents_after_write: List of memories retrieved immediately after write
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
        
        # Extract goal_id from request or metadata if present
        goal_id = request.goal_id
        if not goal_id and request.metadata and "goal_id" in request.metadata:
            goal_id = request.metadata["goal_id"]
        
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
            metadata=request.metadata,
            goal_id=goal_id
        )
        
        logger.info(f"✅ Memory written: {memory['memory_id']}")
        
        # Immediately read memories to verify persistence
        logger.info(f"🔍 Verifying persistence by immediately reading memories")
        
        # First, ensure we have a fresh connection
        try:
            memory_db.close()  # Close any existing connection
        except Exception as close_error:
            logger.warning(f"⚠️ Non-critical error during connection close: {str(close_error)}")
            pass
            
        # Get a new connection
        conn = memory_db._get_connection()
        
        # Read memories with the same goal_id if provided, otherwise read recent memories
        if goal_id:
            db_contents = memory_db.read_memories(goal_id=goal_id, limit=10)
            logger.info(f"📦 DB contents after write (filtered by goal_id={goal_id}): {[m.get('memory_id') for m in db_contents]}")
        else:
            db_contents = memory_db.read_memories(limit=10)
            logger.info(f"📦 DB contents after write: {[m.get('memory_id') for m in db_contents]}")
        
        # Check if our memory is in the results
        memory_found = False
        for m in db_contents:
            if m.get("memory_id") == memory["memory_id"]:
                memory_found = True
                logger.info(f"✅ PERSISTENCE VERIFIED: Memory {memory['memory_id']} found in database immediately after write")
                break
        
        if not memory_found:
            logger.warning(f"⚠️ PERSISTENCE ISSUE: Memory {memory['memory_id']} NOT found in database immediately after write")
        
        # Return the memory ID and verification results
        return JSONResponse(status_code=200, content={
            "status": "ok", 
            "memory_id": memory["memory_id"],
            "db_contents_after_write": [m.get("memory_id") for m in db_contents],
            "persistence_verified": memory_found
        })
    except Exception as e:
        logger.error(f"❌ Error writing memory: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error", 
            "message": str(e)
        })

@router.get("/read")
async def memory_read_endpoint(
    agent_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    since: Optional[str] = None,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    memory_trace_id: Optional[str] = None,
    goal_id: Optional[str] = None,
    limit: Optional[int] = 100
):
    """
    Read memories with flexible filtering options.
    
    This endpoint allows querying memories with various filters to retrieve
    specific subsets of memories for analysis, display, or processing.
    
    Parameters:
    - agent_id: Filter by agent ID (optional)
    - memory_type: Filter by memory type (optional)
    - since: Filter by timestamp (ISO 8601 format, optional)
    - project_id: Filter by project ID (optional)
    - task_id: Filter by task ID (optional)
    - memory_trace_id: Filter by memory trace ID (optional)
    - goal_id: Filter by goal ID (optional)
    - limit: Maximum number of memories to return (optional, default 100)
    
    Returns:
    - status: "ok" if successful
    - memories: List of memory entries matching the filters
    """
    try:
        logger.info(f"🧠 Reading memories with filters: agent_id={agent_id}, memory_type={memory_type}, goal_id={goal_id}")
        
        # Log the absolute database path
        logger.info(f"💾 DB PATH: Reading from {memory_db.get_path()}")
        
        # Ensure we have a fresh connection
        try:
            memory_db.close()  # Close any existing connection
        except Exception as close_error:
            logger.warning(f"⚠️ Non-critical error during connection close: {str(close_error)}")
            pass
            
        # Get a new connection
        conn = memory_db._get_connection()
        
        # Read memories with provided filters
        memories = memory_db.read_memories(
            agent_id=agent_id,
            memory_type=memory_type,
            since=since,
            project_id=project_id,
            task_id=task_id,
            thread_id=memory_trace_id,
            goal_id=goal_id,
            limit=limit
        )
        
        logger.info(f"✅ Retrieved {len(memories)} memories")
        return JSONResponse(status_code=200, content={
            "status": "ok", 
            "memories": memories
        })
    except Exception as e:
        logger.error(f"❌ Error reading memories: {str(e)}")
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
    limit: Optional[int] = 50,
    debug_mode: Optional[bool] = False
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
    - debug_mode: (Optional) If true, returns all memories without filtering, default is false
    
    Returns:
    - status: "ok" if successful
    - thread: List of memory entries sorted chronologically
    """
    # Updated implementation to use the singleton memory_db instance
    try:
        # Validate that at least one of goal_id, task_id, or memory_trace_id is provided
        if not debug_mode and not goal_id and not task_id and not memory_trace_id:
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
        
        # Use the singleton memory_db instance instead of creating a new one
        logger.info(f"✅ Using singleton memory_db instance for memory_thread request")
        
        # Log the absolute database path
        logger.info(f"💾 DB PATH: Reading from {memory_db.get_path()}")
        
        # Ensure we have a fresh connection
        try:
            memory_db.close()  # Close any existing connection
        except Exception as close_error:
            logger.warning(f"⚠️ Non-critical error during connection close: {str(close_error)}")
            pass
            
        # Get a new connection
        conn = memory_db._get_connection()
        
        # Read fresh memories directly from DB with a high limit
        all_memories = memory_db.read_memories(limit=1000)
        logger.info(f"Retrieved {len(all_memories)} memories from database")
        
        # In debug mode, skip filtering and use all memories
        if debug_mode:
            filtered_memories = [dict(m) for m in all_memories]
            logger.info(f"🔍 DEBUG MODE: Returning all {len(filtered_memories)} memories without filtering")
            
            # Add debug info for each memory
            for m in filtered_memories:
                logger.info(f"🔍 DEBUG: Memory ID: {m.get('memory_id')}, Type: {m.get('type')}, Goal ID: {m.get('goal_id')}")
                if m.get("metadata") and isinstance(m.get("metadata"), dict) and "goal_id" in m.get("metadata", {}):
                    logger.info(f"🔍 DEBUG: Memory {m.get('memory_id')} has goal_id in metadata: {m.get('metadata', {}).get('goal_id')}")
        else:
            # Filter memories based on provided criteria
            filtered_memories = []
            for m in all_memories:
                # Convert SQLite Row to dict if needed
                if not isinstance(m, dict):
                    m = dict(m)
                
                # Filter by goal_id if provided
                if goal_id:
                    goal_id_match = False
                    
                    # Check top-level goal_id
                    top_level_goal_id = m.get("goal_id")
                    if top_level_goal_id is not None:
                        logger.info(f"🔍 Comparing top-level goal_id: '{top_level_goal_id}' with filter: '{goal_id}'")
                        if str(top_level_goal_id).strip() == str(goal_id).strip():
                            goal_id_match = True
                            logger.info(f"✅ Match found on top-level goal_id for memory {m.get('memory_id')}")
                    
                    # If no match at top level, check metadata
                    if not goal_id_match and m.get("metadata"):
                        metadata = m.get("metadata")
                        if isinstance(metadata, str):
                            try:
                                metadata_dict = json.loads(metadata)
                                if metadata_dict.get("goal_id") == goal_id:
                                    goal_id_match = True
                                    logger.info(f"✅ Match found in metadata goal_id for memory {m.get('memory_id')}")
                            except:
                                pass
                        elif isinstance(metadata, dict) and metadata.get("goal_id") == goal_id:
                            goal_id_match = True
                            logger.info(f"✅ Match found in metadata goal_id for memory {m.get('memory_id')}")
                    
                    if not goal_id_match:
                        continue
                
                # Filter by task_id if provided
                if task_id and m.get("task_id") != task_id:
                    continue
                
                # Filter by memory_trace_id if provided
                if memory_trace_id and m.get("memory_trace_id") != memory_trace_id:
                    continue
                
                # Filter by user_id if provided (in tags)
                if user_id:
                    user_scope = f"user:{user_id}"
                    tags = m.get("tags", [])
                    if isinstance(tags, str):
                        try:
                            tags = json.loads(tags)
                        except:
                            tags = []
                    
                    if user_scope not in tags:
                        continue
                
                # Filter by agent_id if provided
                if agent_id and m.get("agent_id") != agent_id:
                    continue
                
                # Add to filtered memories if it passed all filters
                filtered_memories.append(m)
        
        # Sort memories by timestamp
        if order and order.lower() == "desc":
            filtered_memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        else:
            filtered_memories.sort(key=lambda x: x.get("timestamp", ""))
        
        # Apply limit if provided
        if limit and len(filtered_memories) > limit:
            filtered_memories = filtered_memories[:limit]
        
        logger.info(f"✅ Returning {len(filtered_memories)} memories in thread")
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "thread": filtered_memories
            }
        )
    except Exception as e:
        logger.error(f"❌ Error retrieving memory thread: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )

@router.post("/reflect")
async def memory_reflect_endpoint(request: ReflectionRequest):
    """
    Generate a reflection based on recent memories.
    
    This endpoint analyzes recent memories and generates a reflection
    that summarizes patterns, insights, or conclusions.
    
    Parameters:
    - agent_id: ID of the agent (required)
    - goal: Current goal or objective (required)
    - context: Additional context for reflection (optional)
    - task_id: ID of the current task (required)
    - project_id: ID of the current project (required)
    - memory_trace_id: ID for memory tracing (required)
    - type: Type of memories to reflect on (optional, default "memory")
    - limit: Maximum number of memories to consider (optional, default 5)
    - loop_count: Current loop count for this task (optional, default 0)
    
    Returns:
    - status: "ok" if successful
    - reflection: Generated reflection text
    - memories_used: List of memories used for reflection
    """
    try:
        logger.info(f"🧠 Generating reflection for {request.agent_id}")
        
        # Check if we've exceeded the maximum loops for this task
        if request.loop_count >= system_caps["max_loops_per_task"]:
            logger.warning(f"⚠️ Maximum loop count reached for task {request.task_id}")
            return JSONResponse(status_code=200, content={
                "status": "ok",
                "reflection": "I've reached my maximum reflection depth for this task. Let me proceed with what I know.",
                "memories_used": []
            })
        
        # Get relevant memories for reflection
        memories = memory_db.read_memories(
            agent_id=request.agent_id,
            memory_type=request.type,
            project_id=request.project_id,
            task_id=request.task_id,
            thread_id=request.memory_trace_id,
            limit=request.limit
        )
        
        # Generate reflection
        reflection = generate_reflection(memories)
        
        logger.info(f"✅ Generated reflection based on {len(memories)} memories")
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "reflection": reflection,
            "memories_used": memories
        })
    except Exception as e:
        logger.error(f"❌ Error generating reflection: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

@router.post("/summarize")
async def memory_summarize_endpoint(request: SummarizeRequest):
    """
    Summarize a collection of memories.
    
    This endpoint analyzes a set of memories and generates a concise summary
    that captures the key points and insights.
    
    Parameters:
    - agent_id: ID of the agent (required)
    - goal: Current goal or objective (required)
    - task_id: ID of the current task (required)
    - project_id: ID of the current project (required)
    - memory_trace_id: ID for memory tracing (required)
    - context: Additional context for summarization (optional)
    - type: Type of memories to summarize (optional)
    - limit: Maximum number of memories to consider (optional, default 10)
    
    Returns:
    - status: "ok" if successful
    - summary: Generated summary text
    - memories_used: List of memories used for summarization
    """
    try:
        logger.info(f"🧠 Generating summary for {request.agent_id}")
        
        # Get relevant memories for summarization
        memories = memory_db.read_memories(
            agent_id=request.agent_id,
            memory_type=request.type,
            project_id=request.project_id,
            task_id=request.task_id,
            thread_id=request.memory_trace_id,
            limit=request.limit
        )
        
        # Generate summary (placeholder implementation)
        if not memories:
            summary = "No relevant memories to summarize."
        else:
            summary = f"Summary of {len(memories)} memories: This task involved several steps..."
        
        logger.info(f"✅ Generated summary based on {len(memories)} memories")
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "summary": summary,
            "memories_used": memories
        })
    except Exception as e:
        logger.error(f"❌ Error generating summary: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

@router.post("/search")
async def memory_search_endpoint(request: SearchRequest):
    """
    Search memories using a query string.
    
    This endpoint allows searching memories using a query string,
    with optional filters for role, memory type, and project.
    
    Parameters:
    - agent_id: ID of the agent (required)
    - query: Search query string (required)
    - role: Filter by role (optional)
    - memory_type: Filter by memory type (optional)
    - limit: Maximum number of results (optional, default 25)
    - project_id: Filter by project ID (optional)
    
    Returns:
    - status: "ok" if successful
    - results: List of matching memories
    """
    try:
        logger.info(f"🧠 Searching memories for {request.agent_id} with query: {request.query}")
        
        # This is a placeholder implementation
        # In a real implementation, this would use full-text search or vector search
        
        # Get all memories for the agent
        memories = memory_db.read_memories(
            agent_id=request.agent_id,
            memory_type=request.memory_type,
            project_id=request.project_id,
            limit=1000  # Get a large number to search through
        )
        
        # Filter memories that contain the query string (case-insensitive)
        query_lower = request.query.lower()
        results = []
        for memory in memories:
            content = memory.get("content", "").lower()
            if query_lower in content:
                results.append(memory)
                if len(results) >= request.limit:
                    break
        
        logger.info(f"✅ Found {len(results)} memories matching query: {request.query}")
        return JSONResponse(status_code=200, content={
            "status": "ok",
            "results": results
        })
    except Exception as e:
        logger.error(f"❌ Error searching memories: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })
