"""
Memory read/write utility functions for HAL agent.

This module provides functions to read from and write to the memory system,
specifically designed for use with the HAL agent's code generation capabilities.
"""

import os
import aiohttp
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("hal_memory")

# Configure base URL for memory service
BASE_URL = os.getenv("MEMORY_SERVICE_URL", "https://web-production-2639.up.railway.app")
logger.info(f"🔌 Memory service configured with base URL: {BASE_URL}")

async def read_memory(agent_id: str, memory_type: str, tag: str, project_id: str = "default") -> str:
    """
    Read a memory value from the memory API.
    
    Parameters:
    - agent_id: The agent identifier
    - memory_type: The type of memory (e.g., 'loop')
    - tag: The memory tag to read
    - project_id: The project identifier (needed to avoid 422 errors)
    
    Returns:
    - The memory value as a string
    """
    try:
        # Use internal API call to avoid network overhead
        try:
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
        except ImportError:
            logger.info("⚠️ Direct memory access not available, using API fallback")
        
        # Fallback to API call if direct access fails
        async with aiohttp.ClientSession() as session:
            read_url = f"{BASE_URL}/api/memory/read"
            
            # Include project_id in params to avoid 422 errors
            params = {
                "project_id": project_id,  # ✅ Needed to avoid 422
                "agent_id": agent_id,
                "memory_type": memory_type,
                "tag": tag
            }
            
            logger.info(f"🔍 Reading memory from: {read_url} with params: {params}")
            
            async with session.get(read_url, params=params) as response:
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

async def write_memory(agent_id: str, memory_type: str, tag: str, value: str, project_id: str = "default") -> bool:
    """
    Write a memory value to the memory API.
    
    Parameters:
    - agent_id: The agent identifier
    - memory_type: The type of memory (e.g., 'loop')
    - tag: The memory tag to write
    - value: The value to write
    - project_id: The project identifier (needed to avoid 422 errors)
    
    Returns:
    - True if successful, False otherwise
    """
    try:
        # Use internal API call to avoid network overhead
        try:
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
        except ImportError:
            logger.info("⚠️ Direct memory access not available, using API fallback")
        
        # Fallback to API call if direct access fails
        async with aiohttp.ClientSession() as session:
            write_url = f"{BASE_URL}/api/memory/write"
            logger.info(f"💾 Writing memory to: {write_url}")
            
            payload = {
                "project_id": project_id,  # ✅ Needed to avoid 422
                "agent_id": agent_id,
                "memory_type": memory_type,
                "tag": tag,
                "value": value
            }
            async with session.post(write_url, json=payload) as response:
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
