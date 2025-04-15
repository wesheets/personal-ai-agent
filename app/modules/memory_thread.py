"""
Memory Thread Module

This module provides functionality to store and retrieve memory threads.

MODIFIED: Added enhanced logging for debugging memory thread issues
"""

import json
import datetime
import logging
import traceback
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Request

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

@router.post("/memory/thread")
async def add_memory_thread(memory_entry: Dict[str, Any], request: Request = None) -> Dict[str, Any]:
    """
    Add a memory entry to a thread.
    
    Args:
        memory_entry: Dictionary containing memory entry data
        request: Optional FastAPI request object for debugging
        
    Returns:
        Dict[str, Any]: Status and updated thread length
    """
    # Enhanced logging for debugging
    print(f"🔍 DEBUG: POST /memory/thread endpoint called")
    print(f"🔍 DEBUG: Received memory_entry: {json.dumps(memory_entry, indent=2)}")
    logger.info(f"DEBUG: POST /memory/thread endpoint called")
    
    if request:
        print(f"🔍 DEBUG: Request headers: {request.headers}")
        print(f"🔍 DEBUG: Request client: {request.client}")
    
    try:
        # Validate required fields
        required_fields = ["project_id", "chain_id", "agent", "role", "content", "step_type"]
        missing_fields = []
        for field in required_fields:
            if field not in memory_entry:
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            print(f"❌ ERROR: {error_msg}")
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate agent value
        valid_agents = ["hal", "ash", "nova"]
        if memory_entry["agent"] not in valid_agents:
            error_msg = f"Invalid agent value: {memory_entry['agent']}. Must be one of: {', '.join(valid_agents)}"
            print(f"❌ ERROR: {error_msg}")
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate step_type value
        valid_step_types = ["task", "summary", "reflection", "ui"]
        if memory_entry["step_type"] not in valid_step_types:
            error_msg = f"Invalid step_type value: {memory_entry['step_type']}. Must be one of: {', '.join(valid_step_types)}"
            print(f"❌ ERROR: {error_msg}")
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Add timestamp if not provided
        if "timestamp" not in memory_entry:
            memory_entry["timestamp"] = get_current_timestamp()
            print(f"🔍 DEBUG: Added timestamp: {memory_entry['timestamp']}")
        
        # Create the thread key
        thread_key = f"{memory_entry['project_id']}:{memory_entry['chain_id']}"
        print(f"🔍 DEBUG: Thread key: {thread_key}")
        
        # Create a new thread if it doesn't exist
        if thread_key not in THREAD_DB:
            print(f"🔍 DEBUG: Creating new thread for key: {thread_key}")
            THREAD_DB[thread_key] = []
        
        # Add the memory entry to the thread
        THREAD_DB[thread_key].append(memory_entry)
        print(f"🔍 DEBUG: Added entry to thread. New length: {len(THREAD_DB[thread_key])}")
        print(f"🔍 DEBUG: THREAD_DB now contains {len(THREAD_DB)} threads")
        
        # Return status and updated thread length
        result = {
            "status": "added",
            "thread_length": len(THREAD_DB[thread_key])
        }
        print(f"✅ SUCCESS: Memory entry added to thread: {result}")
        return result
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Log unexpected errors
        error_msg = f"Unexpected error in add_memory_thread: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        print(f"🔍 DEBUG: Exception traceback: {traceback.format_exc()}")
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
    # Enhanced logging for debugging
    print(f"🔍 DEBUG: GET /memory/thread/{project_id}/{chain_id} endpoint called")
    logger.info(f"DEBUG: GET /memory/thread/{project_id}/{chain_id} endpoint called")
    
    try:
        # Create the thread key
        thread_key = f"{project_id}:{chain_id}"
        print(f"🔍 DEBUG: Thread key: {thread_key}")
        
        # Check if thread exists
        if thread_key not in THREAD_DB:
            print(f"🔍 DEBUG: Thread not found for key: {thread_key}")
            print(f"🔍 DEBUG: Available thread keys: {list(THREAD_DB.keys())}")
            return []
        
        # Return the thread
        thread = THREAD_DB.get(thread_key, [])
        print(f"🔍 DEBUG: Found thread with {len(thread)} entries")
        return thread
    
    except Exception as e:
        # Log unexpected errors
        error_msg = f"Unexpected error in get_memory_thread: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        print(f"🔍 DEBUG: Exception traceback: {traceback.format_exc()}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

# Function to clear all threads (for testing purposes)
def clear_all_threads() -> None:
    """
    Clear all memory threads from the database.
    Used primarily for testing purposes.
    """
    print(f"🔍 DEBUG: Clearing all threads. Current count: {len(THREAD_DB)}")
    THREAD_DB.clear()
    print(f"🔍 DEBUG: All threads cleared. New count: {len(THREAD_DB)}")
