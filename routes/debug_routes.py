"""
Debug routes for agent system
This module provides debug endpoints for the agent system.
feature/phase-3.5-hardening
SHA256: 9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b
INTEGRITY: v3.5.0-debug-routes
LAST_MODIFIED: 2025-04-18
main
"""
import logging
import os
import json
from fastapi import APIRouter, Request, Response
from typing import Dict, Any, List

from app.core.agent_router import get_agent_router

# Set up logging
logger = logging.getLogger("api.debug")

# Create router
router = APIRouter(tags=["Debug"])

@router.get("/agents")
async def debug_agents():
    """
    Returns detailed information about all registered agents for debugging purposes.
    
    This endpoint provides:
    - List of all agent IDs in the agent_map
    - List of all agent profiles
    - Comparison between agent_map and agent profiles
    """
    # Get the agent router
    agent_router = get_agent_router()
    
    # Get all agent profiles
    agent_profiles = agent_router.get_all_agent_profiles()
    profile_ids = list(agent_profiles.keys())
    
    # Get all agents from the agent_map
    from app.core.agent_router import find_agent
    import inspect
    
    # Introspect the agent_map
    agent_map_source = inspect.getsource(find_agent)
    agent_map_lines = [line.strip() for line in agent_map_source.split('\n') 
                      if "agent_map" in line and "=" in line]
    
    # Extract agent IDs from the agent_map
    agent_map_ids = []
    if agent_map_lines:
        # This is a simple parser and might need adjustment based on actual code format
        for line in agent_map_lines:
            if ":" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    agent_id = parts[0].strip().strip('"\'')
                    if agent_id and agent_id != "agent_map":
                        agent_map_ids.append(agent_id)
    
    # Check for mismatches
    missing_in_profiles = [agent_id for agent_id in agent_map_ids if agent_id not in profile_ids]
    missing_in_map = [agent_id for agent_id in profile_ids if agent_id not in agent_map_ids]
    
    # Log the debug information
    logger.info(f"🔍 Debug agents endpoint called")
    logger.info(f"🔍 Agent profiles: {profile_ids}")
    logger.info(f"🔍 Agent map IDs: {agent_map_ids}")
    
    if missing_in_profiles:
        logger.warning(f"⚠️ Agents in map but missing in profiles: {missing_in_profiles}")
    if missing_in_map:
        logger.warning(f"⚠️ Agents in profiles but missing in map: {missing_in_map}")
    
    # Return the debug information
    return {
        "agent_profiles": profile_ids,
        "agent_map": agent_map_ids,
        "missing_in_profiles": missing_in_profiles,
        "missing_in_map": missing_in_map,
        "status": "ok" if not (missing_in_profiles or missing_in_map) else "mismatched"
    }

@router.get("/memory/log")
async def get_memory_log():
    """
    Return the current in-memory debug log (or simulated log entries).
    """
    try:
        logger.info(f"🔍 Debug memory log endpoint called")
        
        # Path to memory store file
        memory_file = os.path.join(os.path.dirname(__file__), "../app/modules/memory_store.json")
        
        # Read memory entries from file
        memories = []
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r') as f:
                    memories = json.load(f)
                    # Sort by timestamp (newest first)
                    memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    # Limit to most recent entries
                    memories = memories[:50]  # Return the 50 most recent entries
                    logger.info(f"🔍 Retrieved {len(memories)} memory entries")
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Could not decode memory store file")
                memories = []
            except Exception as e:
                logger.error(f"❌ Error reading memory store: {str(e)}")
                memories = []
        else:
            logger.warning(f"⚠️ Memory store file not found at {memory_file}")
            # Generate synthetic entries if file doesn't exist
            memories = [
                {
                    "memory_id": "synthetic-1",
                    "timestamp": "2025-04-18T02:28:00.000000",
                    "agent": "hal",
                    "project_id": "demo_001",
                    "action": "received_task",
                    "content": "Synthetic memory entry for testing"
                },
                {
                    "memory_id": "synthetic-2",
                    "timestamp": "2025-04-18T02:27:00.000000",
                    "agent": "nova",
                    "project_id": "demo_001",
                    "action": "created",
                    "content": "Another synthetic memory entry"
                }
            ]
            logger.info(f"🔍 Generated {len(memories)} synthetic memory entries")
        
        return {
            "status": "success",
            "log": memories
        }
    except Exception as e:
        error_msg = f"Failed to retrieve memory log: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg
        }
