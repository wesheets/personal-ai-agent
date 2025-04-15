"""
Memory Thread Module

This module provides functionality to store and retrieve memory threads.

MODIFIED: Added support for batched thread writing and expanded step types
"""

import json
import datetime
import logging
import traceback
from typing import Dict, List, Any, Optional, Union
from fastapi import APIRouter, HTTPException, Request, Body

# Import schemas
from app.schemas.memory import StepType, ThreadRequest, MemoryItem

# Configure logging
logger = logging.getLogger("modules.memory_thread")

# In-memory database to store memory threads
THREAD_DB: Dict[str, List[Dict[str, Any]]] = {}

# Create router for memory thread endpoints
router = APIRouter()

def get_current_timestamp() -> str:
    """
    Get the current timestamp in ISO format.
    
    Returns:
        str: Current timestamp in ISO format
    """
    return datetime.datetime.now().isoformat() + "Z"

@router.post("/api/memory/thread")
async def thread_memory(request: Union[ThreadRequest, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Add multiple memory entries to a thread in a single call.
    
    Args:
        request: ThreadRequest containing project_id, chain_id, agent_id, and memories
               or a dictionary with the same structure
        
    Returns:
        Dict[str, Any]: Status and updated thread length
    """
    # Enhanced logging for debugging
    logger.info(f"📝 Memory Thread: Batch endpoint called")
    
    try:
        # Convert dict to ThreadRequest if needed
        if isinstance(request, dict):
            # Extract required fields
            project_id = request.get("project_id")
            chain_id = request.get("chain_id")
            agent_id = request.get("agent_id")
            memories = request.get("memories", [])
            
            if not project_id or not chain_id or not agent_id or not memories:
                error_msg = "Missing required fields in request"
                logger.error(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)
                
            logger.info(f"📝 Memory Thread: Processing dictionary with {len(memories)} memories")
        else:
            # Use the ThreadRequest object directly
            project_id = request.project_id
            chain_id = request.chain_id
            agent_id = request.agent_id
            memories = request.memories
            logger.info(f"📝 Memory Thread: Processing ThreadRequest with {len(memories)} memories")
        
        # Create the thread key
        thread_key = f"{project_id}::{chain_id}"
        
        # Create a new thread if it doesn't exist
        if thread_key not in THREAD_DB:
            THREAD_DB[thread_key] = []
        
        # Add each memory entry to the thread
        memory_ids = []
        for memory in memories:
            # Handle both dict and MemoryItem objects
            if isinstance(memory, dict):
                agent = memory.get("agent")
                role = memory.get("role")
                content = memory.get("content")
                step_type = memory.get("step_type")
            else:
                agent = memory.agent
                role = memory.role
                content = memory.content
                step_type = memory.step_type
            
            # Generate a unique memory ID
            memory_id = f"mem-{datetime.datetime.now().timestamp()}-{len(THREAD_DB[thread_key])}"
            memory_ids.append(memory_id)
            
            # Add the memory to the thread
            THREAD_DB[thread_key].append({
                "memory_id": memory_id,
                "agent": agent,
                "role": role,
                "content": content,
                "step_type": step_type,
                "timestamp": get_current_timestamp(),
                "project_id": project_id,
                "chain_id": chain_id
            })
        
        logger.info(f"📝 Memory Thread: Stored {len(memories)} memories under key {thread_key}")
        
        # Return status and updated thread length
        return {
            "status": "added",
            "thread_length": len(THREAD_DB[thread_key]),
            "memory_ids": memory_ids
        }
    
    except Exception as e:
        # Log unexpected errors
        error_msg = f"Unexpected error in thread_memory: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/memory/thread")
async def add_memory_thread(memory_entry: Dict[str, Any], request: Request = None) -> Dict[str, Any]:
    """
    Add a single memory entry to a thread (legacy endpoint).
    
    Args:
        memory_entry: Dictionary containing memory entry data
        request: Optional FastAPI request object for debugging
        
    Returns:
        Dict[str, Any]: Status and updated thread length
    """
    # Enhanced logging for debugging
    logger.info(f"DEBUG: Legacy POST /memory/thread endpoint called")
    
    try:
        # Validate required fields
        required_fields = ["project_id", "chain_id", "agent", "role", "content", "step_type"]
        missing_fields = []
        for field in required_fields:
            if field not in memory_entry:
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate agent value
        valid_agents = ["hal", "ash", "nova", "critic", "orchestrator"]
        if memory_entry["agent"] not in valid_agents:
            logger.warning(f"Non-standard agent value: {memory_entry['agent']}. Proceeding anyway.")
        
        # Validate step_type value and convert to enum if possible
        try:
            step_type = StepType(memory_entry["step_type"])
            memory_entry["step_type"] = step_type
        except ValueError:
            error_msg = f"Invalid step_type value: {memory_entry['step_type']}. Must be one of: {', '.join([t.value for t in StepType])}"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Add timestamp if not provided
        if "timestamp" not in memory_entry:
            memory_entry["timestamp"] = get_current_timestamp()
        
        # Create the thread key
        thread_key = f"{memory_entry['project_id']}::{memory_entry['chain_id']}"
        
        # Create a new thread if it doesn't exist
        if thread_key not in THREAD_DB:
            THREAD_DB[thread_key] = []
        
        # Generate a unique memory ID
        memory_id = f"mem-{datetime.datetime.now().timestamp()}-{len(THREAD_DB[thread_key])}"
        memory_entry["memory_id"] = memory_id
        
        # Add the memory entry to the thread
        THREAD_DB[thread_key].append(memory_entry)
        
        # Return status and updated thread length
        result = {
            "status": "added",
            "thread_length": len(THREAD_DB[thread_key]),
            "memory_id": memory_id
        }
        return result
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Log unexpected errors
        error_msg = f"Unexpected error in add_memory_thread: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/memory/thread/{project_id}/{chain_id}")
async def get_memory_thread(project_id: str, chain_id: str) -> List[Dict[str, Any]]:
    """
    Get the memory thread for a specific project and chain.
    
    Args:
        project_id: Project identifier
        chain_id: Chain identifier
        
    Returns:
        List[Dict[str, Any]]: List of memory entries in the thread
    """
    logger.info(f"DEBUG: GET /memory/thread/{project_id}/{chain_id} endpoint called")
    
    try:
        # Try both separator formats for backward compatibility
        thread_key = f"{project_id}::{chain_id}"
        thread_key_alt = f"{project_id}:{chain_id}"
        
        # Check if thread exists with either key format
        if thread_key in THREAD_DB:
            thread = THREAD_DB[thread_key]
        elif thread_key_alt in THREAD_DB:
            thread = THREAD_DB[thread_key_alt]
        else:
            return []
        
        # Return the thread
        return thread
    
    except Exception as e:
        # Log unexpected errors
        error_msg = f"Unexpected error in get_memory_thread: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

# Function to clear all threads (for testing purposes)
def clear_all_threads() -> None:
    """
    Clear all memory threads from the database.
    Used primarily for testing purposes.
    """
    logger.debug(f"Clearing all threads. Current count: {len(THREAD_DB)}")
    THREAD_DB.clear()
    logger.debug(f"All threads cleared. New count: {len(THREAD_DB)}")
