"""
Memory writer module for writing and reading memory entries

This module provides functions for writing and reading memory entries,
with support for different agent types and memory categories.
"""
import logging
import datetime
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger("app.modules.memory_writer")

# In-memory storage for testing
MEMORY_STORE = {}

async def write_memory(
    agent_id: str,
    memory_type: str,
    tag: str,
    value: Any,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Write a memory entry to the memory system.
    
    Args:
        agent_id: The agent identifier
        memory_type: Type of memory (e.g., "loop", "state", "reflection")
        tag: The memory tag
        value: The memory value to store
        project_id: Optional project identifier
            
    Returns:
        Dict containing status and memory entry details
    """
    try:
        logger.info(f"Writing memory for agent: {agent_id}, type: {memory_type}, tag: {tag}")
        
        # Use agent_id as key if project_id not provided
        store_key = project_id if project_id else agent_id
        
        # Store in memory dictionary for testing
        if store_key not in MEMORY_STORE:
            MEMORY_STORE[store_key] = {}
            
        if memory_type not in MEMORY_STORE[store_key]:
            MEMORY_STORE[store_key][memory_type] = {}
            
        MEMORY_STORE[store_key][memory_type][tag] = value
        
        # Return success response
        return {
            "status": "success",
            "message": "Memory write successful",
            "agent_id": agent_id,
            "memory_type": memory_type,
            "tag": tag,
            "project_id": project_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error writing memory: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to write memory: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }

async def read_memory(
    agent_id: str,
    memory_type: str,
    tag: str,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Read a memory entry from the memory system.
    
    Args:
        agent_id: The agent identifier
        memory_type: Type of memory (e.g., "loop", "state", "reflection")
        tag: The memory tag
        project_id: Optional project identifier
            
    Returns:
        Dict containing status and memory value if found
    """
    try:
        logger.info(f"Reading memory for agent: {agent_id}, type: {memory_type}, tag: {tag}")
        
        # Use agent_id as key if project_id not provided
        store_key = project_id if project_id else agent_id
        
        # Read from memory dictionary for testing
        if (store_key in MEMORY_STORE and 
            memory_type in MEMORY_STORE[store_key] and 
            tag in MEMORY_STORE[store_key][memory_type]):
            
            return {
                "status": "success",
                "value": MEMORY_STORE[store_key][memory_type][tag],
                "agent_id": agent_id,
                "memory_type": memory_type,
                "tag": tag,
                "project_id": project_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        logger.warning(f"Memory not found for agent: {agent_id}, type: {memory_type}, tag: {tag}")
        return {
            "status": "not_found",
            "message": "Memory entry not found",
            "agent_id": agent_id,
            "memory_type": memory_type,
            "tag": tag,
            "project_id": project_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error reading memory: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to read memory: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }

async def list_memories(
    agent_id: str,
    memory_type: str,
    tag_prefix: Optional[str] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List memory entries matching the specified criteria.
    
    Args:
        agent_id: The agent identifier
        memory_type: Type of memory (e.g., "loop", "state", "reflection")
        tag_prefix: Optional prefix to filter tags
        project_id: Optional project identifier
            
    Returns:
        Dict containing status and list of matching memory entries
    """
    try:
        logger.info(f"Listing memories for agent: {agent_id}, type: {memory_type}")
        
        # Use agent_id as key if project_id not provided
        store_key = project_id if project_id else agent_id
        
        # Initialize empty result
        memories = []
        
        # Check if the store key and memory type exist
        if (store_key in MEMORY_STORE and 
            memory_type in MEMORY_STORE[store_key]):
            
            # Get all tags for this memory type
            tags = MEMORY_STORE[store_key][memory_type].keys()
            
            # Filter by tag prefix if specified
            if tag_prefix:
                tags = [tag for tag in tags if tag.startswith(tag_prefix)]
                
            # Build memory entries list
            for tag in tags:
                memories.append({
                    "agent_id": agent_id,
                    "memory_type": memory_type,
                    "tag": tag,
                    "project_id": project_id
                })
        
        return {
            "status": "success",
            "memories": memories,
            "count": len(memories),
            "agent_id": agent_id,
            "memory_type": memory_type,
            "tag_prefix": tag_prefix,
            "project_id": project_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing memories: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to list memories: {str(e)}",
            "memories": [],
            "count": 0,
            "timestamp": datetime.datetime.now().isoformat()
        }
