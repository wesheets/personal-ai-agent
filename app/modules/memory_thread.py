"""
Memory Thread Module

This module provides functionality to store and retrieve memory threads.

MODIFIED: Added enhanced logging for debugging memory thread issues
MODIFIED: Fixed thread key format to use double colons
MODIFIED: Added support for batch memory operations via ThreadRequest
MODIFIED: Updated to use schema models from app.schemas.memory
"""

import json
import datetime
import logging
import traceback
from typing import Dict, List, Any, Optional, Union
from fastapi import APIRouter, HTTPException, Request

# Import schema models
from app.schemas.memory import ThreadRequest, MemoryItem, StepType

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

@router.post("/thread")
async def add_memory_thread(request: Union[ThreadRequest, Dict[str, Any]], request_obj: Request = None) -> Dict[str, Any]:
    """
    Add memory entries to a thread. Supports both single entries and batch operations.
    
    Args:
        request: Either a ThreadRequest model for batch operations or a dictionary for single entries
        request_obj: Optional FastAPI request object for debugging
        
    Returns:
        Dict[str, Any]: Status and updated thread length
    """
    # Check if this is a batch request (ThreadRequest model) or a single entry (dict)
    is_batch = isinstance(request, ThreadRequest)
    
    if is_batch:
        # Process batch request
        project_id = request.project_id
        chain_id = request.chain_id
        agent_id = request.agent_id
        memories = request.memories
        
        # Enhanced logging for batch operations
        logger.info(f"📝 Memory Thread: Received batch write request with project_id={project_id}, chain_id={chain_id}")
        logger.info(f"📝 Memory Thread: Batch contains {len(memories)} memory entries from agent_id={agent_id}")
        print(f"🔍 DEBUG: POST /memory/thread endpoint called with batch request")
        print(f"🔍 DEBUG: Received batch request with {len(memories)} memories")
        
        # Create the thread key with double colons
        thread_key = f"{project_id}::{chain_id}"
        print(f"🔍 DEBUG: Thread key: {thread_key}")
        logger.info(f"📝 Memory Thread: Using thread key: {thread_key}")
        
        # Create a new thread if it doesn't exist
        if thread_key not in THREAD_DB:
            print(f"🔍 DEBUG: Creating new thread for key: {thread_key}")
            logger.info(f"📝 Memory Thread: Creating new thread for key: {thread_key}")
            THREAD_DB[thread_key] = []
        
        # Add each memory entry to the thread
        for memory in memories:
            memory_entry = {
                "project_id": project_id,
                "chain_id": chain_id,
                "agent": memory.agent,
                "role": memory.role,
                "content": memory.content,
                "step_type": memory.step_type,
                "timestamp": get_current_timestamp()
            }
            THREAD_DB[thread_key].append(memory_entry)
        
        print(f"🔍 DEBUG: Added {len(memories)} entries to thread. New length: {len(THREAD_DB[thread_key])}")
        logger.info(f"📝 Memory Thread: Added {len(memories)} entries to thread. New length: {len(THREAD_DB[thread_key])}")
        logger.info(f"📝 Memory Thread: Stored {len(memories)} memories under key {thread_key}")
        
        # Return status and updated thread length
        result = {
            "status": "added",
            "thread_length": len(THREAD_DB[thread_key])
        }
        print(f"✅ SUCCESS: Batch memory entries added to thread: {result}")
        logger.info(f"📝 Memory Thread: Successfully added batch memory entries to thread: {result}")
        return result
    
    else:
        # Process single entry (legacy support)
        memory_entry = request
        
        # Enhanced logging for debugging
        logger.info(f"📝 Memory Thread: Received write request with project_id={memory_entry.get('project_id')}, chain_id={memory_entry.get('chain_id')}")
        logger.info(f"📝 Memory Thread: Content type={memory_entry.get('type')}, agent={memory_entry.get('agent')}")
        logger.debug(f"📝 Memory Thread: Full payload={memory_entry}")
        
        print(f"🔍 DEBUG: POST /memory/thread endpoint called with single entry")
        print(f"🔍 DEBUG: Received memory_entry: {json.dumps(memory_entry, indent=2)}")
        
        if request_obj:
            print(f"🔍 DEBUG: Request headers: {request_obj.headers}")
            print(f"🔍 DEBUG: Request client: {request_obj.client}")
        
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
                logger.error(f"📝 Memory Thread: Error - {error_msg}")
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Validate agent value
            valid_agents = ["hal", "ash", "nova"]
            if memory_entry["agent"] not in valid_agents:
                error_msg = f"Invalid agent value: {memory_entry['agent']}. Must be one of: {', '.join(valid_agents)}"
                print(f"❌ ERROR: {error_msg}")
                logger.error(f"📝 Memory Thread: Error - {error_msg}")
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Validate step_type value using the expanded StepType enum
            valid_step_types = [step_type.value for step_type in StepType]
            if memory_entry["step_type"] not in valid_step_types:
                error_msg = f"Invalid step_type value: {memory_entry['step_type']}. Must be one of: {', '.join(valid_step_types)}"
                print(f"❌ ERROR: {error_msg}")
                logger.error(f"📝 Memory Thread: Error - {error_msg}")
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Add timestamp if not provided
            if "timestamp" not in memory_entry:
                memory_entry["timestamp"] = get_current_timestamp()
                print(f"🔍 DEBUG: Added timestamp: {memory_entry['timestamp']}")
                logger.debug(f"📝 Memory Thread: Added timestamp: {memory_entry['timestamp']}")
            
            # Create the thread key with double colons
            thread_key = f"{memory_entry['project_id']}::{memory_entry['chain_id']}"
            print(f"🔍 DEBUG: Thread key: {thread_key}")
            logger.info(f"📝 Memory Thread: Using thread key: {thread_key}")
            
            # Create a new thread if it doesn't exist
            if thread_key not in THREAD_DB:
                print(f"🔍 DEBUG: Creating new thread for key: {thread_key}")
                logger.info(f"📝 Memory Thread: Creating new thread for key: {thread_key}")
                THREAD_DB[thread_key] = []
            
            # Add the memory entry to the thread
            THREAD_DB[thread_key].append(memory_entry)
            print(f"🔍 DEBUG: Added entry to thread. New length: {len(THREAD_DB[thread_key])}")
            logger.info(f"📝 Memory Thread: Added entry to thread. New length: {len(THREAD_DB[thread_key])}")
            print(f"🔍 DEBUG: THREAD_DB now contains {len(THREAD_DB)} threads")
            logger.info(f"📝 Memory Thread: THREAD_DB now contains {len(THREAD_DB)} threads")
            
            # Add additional logging for thread updates
            logger.info(f"📝 Thread updated: {thread_key} now has {len(THREAD_DB[thread_key])} entries")
            
            # Return status and updated thread length
            result = {
                "status": "added",
                "thread_length": len(THREAD_DB[thread_key])
            }
            print(f"✅ SUCCESS: Memory entry added to thread: {result}")
            logger.info(f"📝 Memory Thread: Successfully added memory entry to thread: {result}")
            return result
        
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        
        except Exception as e:
            # Log unexpected errors
            error_msg = f"Unexpected error in add_memory_thread: {str(e)}"
            print(f"❌ ERROR: {error_msg}")
            print(f"🔍 DEBUG: Exception traceback: {traceback.format_exc()}")
            logger.error(f"📝 Memory Thread: Unexpected error: {error_msg}")
            logger.error(f"📝 Memory Thread: Exception traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=error_msg)

@router.get("/thread/{project_id}/{chain_id}")
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
    logger.info(f"📝 Memory Thread: Received read request for project_id={project_id}, chain_id={chain_id}")
    print(f"🔍 DEBUG: GET /memory/thread/{project_id}/{chain_id} endpoint called")
    
    try:
        # Create the thread key with double colons
        thread_key = f"{project_id}::{chain_id}"
        print(f"🔍 DEBUG: Thread key: {thread_key}")
        logger.info(f"📝 Memory Thread: Using thread key: {thread_key}")
        
        # Check if thread exists
        if thread_key not in THREAD_DB:
            print(f"🔍 DEBUG: Thread not found for key: {thread_key}")
            logger.info(f"📝 Memory Thread: Thread not found for key: {thread_key}")
            print(f"🔍 DEBUG: Available thread keys: {list(THREAD_DB.keys())}")
            logger.debug(f"📝 Memory Thread: Available thread keys: {list(THREAD_DB.keys())}")
            return []
        
        # Return the thread
        thread = THREAD_DB.get(thread_key, [])
        print(f"🔍 DEBUG: Found thread with {len(thread)} entries")
        logger.info(f"📝 Memory Thread: Found thread with {len(thread)} entries")
        return thread
    
    except Exception as e:
        # Log unexpected errors
        error_msg = f"Unexpected error in get_memory_thread: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        print(f"🔍 DEBUG: Exception traceback: {traceback.format_exc()}")
        logger.error(f"📝 Memory Thread: Unexpected error: {error_msg}")
        logger.error(f"📝 Memory Thread: Exception traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

# Function to clear all threads (for testing purposes)
def clear_all_threads() -> None:
    """
    Clear all memory threads from the database.
    Used primarily for testing purposes.
    """
    print(f"🔍 DEBUG: Clearing all threads. Current count: {len(THREAD_DB)}")
    logger.info(f"📝 Memory Thread: Clearing all threads. Current count: {len(THREAD_DB)}")
    THREAD_DB.clear()
    print(f"🔍 DEBUG: All threads cleared. New count: {len(THREAD_DB)}")
    logger.info(f"📝 Memory Thread: All threads cleared. New count: {len(THREAD_DB)}")
