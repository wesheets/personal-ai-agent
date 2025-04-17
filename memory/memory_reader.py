"""
Memory Reader Module

This module provides functionality to read memory entries for projects.
It serves as a centralized interface for retrieving memory data from
various sources and formats.

Created for Phase 6.2.1 Ground Control implementation.
"""

import logging
import datetime
from typing import Dict, List, Any, Optional
import traceback

# Configure logging
logger = logging.getLogger("memory.memory_reader")

# Try to import memory_thread module for accessing thread data
try:
    from app.modules.memory_thread import THREAD_DB
    THREAD_DB_AVAILABLE = True
    logger.info("Successfully imported THREAD_DB from memory_thread")
except ImportError:
    try:
        from memory_thread import THREAD_DB
        THREAD_DB_AVAILABLE = True
        logger.info("Successfully imported THREAD_DB from alternative location")
    except ImportError:
        THREAD_DB_AVAILABLE = False
        THREAD_DB = {}
        logger.warning("Failed to import THREAD_DB, using empty dictionary")

def get_memory_for_project(project_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve memory entries for a specific project.
    
    This function aggregates memory entries from all chains/threads
    associated with the given project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        List of memory entries for the project
    """
    try:
        logger.info(f"Retrieving memory entries for project: {project_id}")
        
        # Initialize empty list for memory entries
        memory_entries = []
        
        # Check if THREAD_DB is available
        if THREAD_DB_AVAILABLE:
            # Iterate through all thread keys in THREAD_DB
            for thread_key in THREAD_DB:
                # Check if thread key belongs to the project
                if thread_key.startswith(f"{project_id}::") or thread_key.startswith(f"{project_id}:"):
                    # Add thread entries to memory entries
                    memory_entries.extend(THREAD_DB[thread_key])
                    logger.info(f"Added {len(THREAD_DB[thread_key])} entries from thread {thread_key}")
        else:
            # If THREAD_DB is not available, return sample data
            logger.warning(f"THREAD_DB not available, returning sample data for project {project_id}")
            memory_entries = [
                {
                    "memory_id": f"sample-{i}",
                    "agent": "system" if i % 3 == 0 else ("hal" if i % 3 == 1 else "nova"),
                    "role": "assistant",
                    "content": f"Sample memory entry {i} for project {project_id}",
                    "step_type": "thinking" if i % 2 == 0 else "action",
                    "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=i)).isoformat(),
                    "project_id": project_id,
                    "chain_id": "main"
                }
                for i in range(1, 11)
            ]
        
        # Sort memory entries by timestamp (newest first)
        memory_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        logger.info(f"Retrieved {len(memory_entries)} memory entries for project {project_id}")
        return memory_entries
    
    except Exception as e:
        logger.error(f"Error retrieving memory for project {project_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return empty list in case of error
        return []

def get_memory_thread_for_project(project_id: str, chain_id: str = "main") -> List[Dict[str, Any]]:
    """
    Retrieve memory entries for a specific project and chain.
    
    This function retrieves memory entries from a specific thread/chain
    associated with the given project.
    
    Args:
        project_id: The project identifier
        chain_id: The chain identifier (defaults to "main")
        
    Returns:
        List of memory entries for the project and chain
    """
    try:
        logger.info(f"Retrieving memory thread for project: {project_id}, chain: {chain_id}")
        
        # Initialize empty list for memory entries
        memory_entries = []
        
        # Check if THREAD_DB is available
        if THREAD_DB_AVAILABLE:
            # Construct thread key
            thread_key = f"{project_id}::{chain_id}"
            thread_key_alt = f"{project_id}:{chain_id}"
            
            # Check if thread exists in THREAD_DB
            if thread_key in THREAD_DB:
                memory_entries = THREAD_DB[thread_key]
                logger.info(f"Retrieved {len(memory_entries)} entries from thread {thread_key}")
            elif thread_key_alt in THREAD_DB:
                memory_entries = THREAD_DB[thread_key_alt]
                logger.info(f"Retrieved {len(memory_entries)} entries from thread {thread_key_alt}")
            else:
                logger.warning(f"No thread found for key {thread_key} or {thread_key_alt}")
        else:
            # If THREAD_DB is not available, return sample data
            logger.warning(f"THREAD_DB not available, returning sample data for project {project_id}, chain {chain_id}")
            memory_entries = [
                {
                    "memory_id": f"sample-{i}",
                    "agent": "system" if i % 3 == 0 else ("hal" if i % 3 == 1 else "nova"),
                    "role": "assistant",
                    "content": f"Sample memory entry {i} for project {project_id}, chain {chain_id}",
                    "step_type": "thinking" if i % 2 == 0 else "action",
                    "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=i)).isoformat(),
                    "project_id": project_id,
                    "chain_id": chain_id
                }
                for i in range(1, 6)
            ]
        
        # Sort memory entries by timestamp (newest first)
        memory_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        logger.info(f"Retrieved {len(memory_entries)} memory entries for project {project_id}, chain {chain_id}")
        return memory_entries
    
    except Exception as e:
        logger.error(f"Error retrieving memory thread for project {project_id}, chain {chain_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return empty list in case of error
        return []

def get_latest_memory_for_project(project_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve the latest memory entries for a specific project.
    
    This function retrieves the most recent memory entries across all
    chains/threads associated with the given project.
    
    Args:
        project_id: The project identifier
        limit: Maximum number of entries to return (defaults to 5)
        
    Returns:
        List of the latest memory entries for the project
    """
    try:
        logger.info(f"Retrieving latest {limit} memory entries for project: {project_id}")
        
        # Get all memory entries for the project
        all_entries = get_memory_for_project(project_id)
        
        # Return the latest entries up to the limit
        latest_entries = all_entries[:limit]
        
        logger.info(f"Retrieved {len(latest_entries)} latest memory entries for project {project_id}")
        return latest_entries
    
    except Exception as e:
        logger.error(f"Error retrieving latest memory for project {project_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return empty list in case of error
        return []
