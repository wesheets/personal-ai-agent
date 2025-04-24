"""
Memory read/write utility functions for HAL agent.

This module provides functions to read from and write to the memory system,
specifically designed for use with the HAL agent's code generation capabilities.
"""

import aiohttp
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("hal_memory")

async def read_memory(agent_id: str, memory_type: str, tag: str) -> str:
    """
    Read a memory value from the memory API.
    
    Parameters:
    - agent_id: The agent identifier
    - memory_type: The type of memory (e.g., 'loop')
    - tag: The memory tag to read
    
    Returns:
    - The memory value as a string
    """
    try:
        # Use internal API call to avoid network overhead
        from app.memory.project_memory import PROJECT_MEMORY
        
        # Try to read directly from memory system
        if PROJECT_MEMORY:
            memory_value = PROJECT_MEMORY.read_memory(
                agent_id=agent_id,
                memory_type=memory_type,
                tag=tag
            )
            if memory_value:
                logger.info(f"✅ Successfully read memory: {tag} for agent {agent_id}")
                return memory_value
        
        # Fallback to API call if direct access fails
        async with aiohttp.ClientSession() as session:
            url = f"http://localhost:8000/api/memory/read?agent_id={agent_id}&memory_type={memory_type}&tag={tag}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Successfully read memory via API: {tag}")
                    return data.get("value", "")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to read memory: {error_text}")
                    return ""
    except Exception as e:
        logger.error(f"❌ Error reading memory: {str(e)}")
        return ""

async def write_memory(agent_id: str, memory_type: str, tag: str, value: str) -> bool:
    """
    Write a memory value to the memory API.
    
    Parameters:
    - agent_id: The agent identifier
    - memory_type: The type of memory (e.g., 'loop')
    - tag: The memory tag to write
    - value: The value to write
    
    Returns:
    - True if successful, False otherwise
    """
    try:
        # Use internal API call to avoid network overhead
        from app.memory.project_memory import PROJECT_MEMORY
        
        # Try to write directly to memory system
        if PROJECT_MEMORY:
            PROJECT_MEMORY.write_memory(
                agent_id=agent_id,
                memory_type=memory_type,
                tag=tag,
                value=value
            )
            logger.info(f"✅ Successfully wrote memory: {tag} for agent {agent_id}")
            return True
        
        # Fallback to API call if direct access fails
        async with aiohttp.ClientSession() as session:
            url = "http://localhost:8000/api/memory/write"
            payload = {
                "agent_id": agent_id,
                "memory_type": memory_type,
                "tag": tag,
                "value": value
            }
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"✅ Successfully wrote memory via API: {tag}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to write memory: {error_text}")
                    return False
    except Exception as e:
        logger.error(f"❌ Error writing memory: {str(e)}")
        return False
