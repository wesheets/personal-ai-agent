"""
Debug routes for agent system
This module provides debug endpoints for the agent system.
"""
import logging
from fastapi import APIRouter, Request, Response
from typing import Dict, Any, List

from app.core.agent_router import get_agent_router

# Set up logging
logger = logging.getLogger("api.debug")

# Create router
router = APIRouter(prefix="/api/debug", tags=["Debug"])

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
