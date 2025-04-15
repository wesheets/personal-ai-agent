# /app/modules/memory_thread.py

import json
import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException

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
async def add_memory_thread(memory_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a memory entry to a thread.
    
    Args:
        memory_entry: Dictionary containing memory entry data
        
    Returns:
        Dict[str, Any]: Status and updated thread length
    """
    # Validate required fields
    required_fields = ["project_id", "chain_id", "agent", "role", "content", "step_type"]
    for field in required_fields:
        if field not in memory_entry:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Validate agent value
    valid_agents = ["hal", "ash", "nova"]
    if memory_entry["agent"] not in valid_agents:
        raise HTTPException(status_code=400, detail=f"Invalid agent value. Must be one of: {', '.join(valid_agents)}")
    
    # Validate step_type value
    valid_step_types = ["task", "summary", "reflection", "ui"]
    if memory_entry["step_type"] not in valid_step_types:
        raise HTTPException(status_code=400, detail=f"Invalid step_type value. Must be one of: {', '.join(valid_step_types)}")
    
    # Add timestamp if not provided
    if "timestamp" not in memory_entry:
        memory_entry["timestamp"] = get_current_timestamp()
    
    # Create the thread key
    thread_key = f"{memory_entry['project_id']}:{memory_entry['chain_id']}"
    
    # Create a new thread if it doesn't exist
    if thread_key not in THREAD_DB:
        THREAD_DB[thread_key] = []
    
    # Add the memory entry to the thread
    THREAD_DB[thread_key].append(memory_entry)
    
    # Return status and updated thread length
    return {
        "status": "added",
        "thread_length": len(THREAD_DB[thread_key])
    }

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
    # Create the thread key
    thread_key = f"{project_id}:{chain_id}"
    
    # Return the thread if it exists, otherwise return an empty list
    return THREAD_DB.get(thread_key, [])

# Function to clear all threads (for testing purposes)
def clear_all_threads() -> None:
    """
    Clear all memory threads from the database.
    Used primarily for testing purposes.
    """
    THREAD_DB.clear()
