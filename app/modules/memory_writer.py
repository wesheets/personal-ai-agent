"""
Memory writer module for writing and reading memory entries
"""
import logging
import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("app.modules.memory_writer")

# In-memory storage for testing
MEMORY_STORE = {}

async def write_memory(project_id: str, tag: str, value: Any) -> Dict[str, Any]:
    """
    Write a memory entry to the memory system.
    
    Args:
        project_id: The project identifier
        tag: The memory tag
        value: The memory value to store
            
    Returns:
        Dict containing status and memory entry details
    """
    try:
        logger.info(f"Writing memory for project: {project_id}, tag: {tag}")
        
        # Store in memory dictionary for testing
        if project_id not in MEMORY_STORE:
            MEMORY_STORE[project_id] = {}
        
        MEMORY_STORE[project_id][tag] = value
        
        # Return success response
        return {
            "status": "success",
            "message": "Memory write successful",
            "project_id": project_id,
            "tag": tag,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error writing memory: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to write memory: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }

async def read_memory(project_id: str, tag: str) -> Optional[Any]:
    """
    Read a memory entry from the memory system.
    
    Args:
        project_id: The project identifier
        tag: The memory tag
            
    Returns:
        The memory value if found, None otherwise
    """
    try:
        logger.info(f"Reading memory for project: {project_id}, tag: {tag}")
        
        # Read from memory dictionary for testing
        if project_id in MEMORY_STORE and tag in MEMORY_STORE[project_id]:
            return MEMORY_STORE[project_id][tag]
        
        logger.warning(f"Memory not found for project: {project_id}, tag: {tag}")
        return None
    except Exception as e:
        logger.error(f"Error reading memory: {str(e)}")
        return None
