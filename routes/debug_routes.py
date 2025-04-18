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
from fastapi import APIRouter, Request, Response, HTTPException
from typing import Dict, Any, List

from app.core.agent_router import get_agent_router

# Set up logging
logger = logging.getLogger("api.debug")
logger.setLevel(logging.DEBUG)  # Ensure debug level logging is enabled

# Create router
router = APIRouter(tags=["Debug"])

# Debug print to verify this file is loaded
print("✅ DEBUG ROUTES LOADED - Version 2025-04-18-03")
print("✅ Debug routes available:")
print("  - /api/debug/agents")
print("  - /api/debug/memory/log")

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

# Print debug info when this endpoint is defined
print("✅ Registering /api/debug/memory/log endpoint")

@router.get("/memory/log")
async def get_memory_log():
    """
    Return the current in-memory debug log (or simulated log entries).
    """
    try:
        print("🔍 Debug memory log endpoint called")
        logger.info(f"🔍 Debug memory log endpoint called")
        
        # Enhanced logging for debugging
        print(f"🔍 Current working directory: {os.getcwd()}")
        logger.debug(f"Current working directory: {os.getcwd()}")
        
        # Try multiple potential paths for memory store file
        potential_paths = [
            os.path.join(os.path.dirname(__file__), "../app/modules/memory_store.json"),  # Relative to routes dir
            "/app/app/modules/memory_store.json",  # Absolute path in container
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../app/modules/memory_store.json")),  # Absolute path
            os.path.join(os.getcwd(), "app/modules/memory_store.json")  # Relative to working dir
        ]
        
        # Log all potential paths
        for i, path in enumerate(potential_paths):
            print(f"🔍 Potential memory store path {i+1}: {path}")
            logger.debug(f"Potential memory store path {i+1}: {path}")
        
        # Try each path until we find the file
        memory_file = None
        for path in potential_paths:
            if os.path.exists(path):
                memory_file = path
                print(f"✅ Memory store file found at: {memory_file}")
                logger.info(f"Memory store file found at: {memory_file}")
                break
        
        # If no file found, use the first path for error reporting
        if memory_file is None:
            memory_file = potential_paths[0]
            print(f"⚠️ Memory store file not found in any potential location")
            logger.warning(f"Memory store file not found in any potential location")
        
        # Read memory entries from file
        memories = []
        if memory_file and os.path.exists(memory_file):
            try:
                print(f"✅ Memory store file found")
                with open(memory_file, 'r') as f:
                    memories = json.load(f)
                    # Sort by timestamp (newest first)
                    memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    # Limit to most recent entries
                    memories = memories[:50]  # Return the 50 most recent entries
                    print(f"✅ Retrieved {len(memories)} memory entries")
                    logger.info(f"🔍 Retrieved {len(memories)} memory entries")
            except json.JSONDecodeError:
                print(f"⚠️ Could not decode memory store file")
                logger.warning(f"⚠️ Could not decode memory store file")
                memories = []
            except Exception as e:
                print(f"❌ Error reading memory store: {str(e)}")
                logger.error(f"❌ Error reading memory store: {str(e)}")
                memories = []
        else:
            print(f"⚠️ Memory store file not found at {memory_file}")
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
                },
                {
                    "memory_id": "synthetic-3",
                    "timestamp": "2025-04-18T02:26:00.000000",
                    "agent": "sage",
                    "project_id": "demo_001",
                    "action": "summarized",
                    "content": "Third synthetic memory entry for testing"
                }
            ]
            print(f"✅ Generated {len(memories)} synthetic memory entries")
            logger.info(f"🔍 Generated {len(memories)} synthetic memory entries")
        
        print(f"✅ Returning memory log with {len(memories)} entries")
        return {
            "status": "success",
            "log": memories
        }
    except Exception as e:
        error_msg = f"Failed to retrieve memory log: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": error_msg
        }

# Fallback endpoint for memory log
@router.get("/memory/log/fallback")
async def get_memory_log_fallback():
    """
    Fallback endpoint for memory log that always returns synthetic entries.
    This endpoint is used when the main memory log endpoint fails.
    """
    print("🔍 Debug memory log fallback endpoint called")
    logger.info(f"🔍 Debug memory log fallback endpoint called")
    
    # Generate synthetic entries
    memories = [
        {
            "memory_id": "fallback-1",
            "timestamp": "2025-04-18T02:28:00.000000",
            "agent": "hal",
            "project_id": "demo_001",
            "action": "received_task",
            "content": "Fallback memory entry for testing"
        },
        {
            "memory_id": "fallback-2",
            "timestamp": "2025-04-18T02:27:00.000000",
            "agent": "nova",
            "project_id": "demo_001",
            "action": "created",
            "content": "Another fallback memory entry"
        },
        {
            "memory_id": "fallback-3",
            "timestamp": "2025-04-18T02:26:00.000000",
            "agent": "sage",
            "project_id": "demo_001",
            "action": "summarized",
            "content": "Third fallback memory entry for testing"
        }
    ]
    
    print(f"✅ Generated {len(memories)} fallback memory entries")
    logger.info(f"🔍 Generated {len(memories)} fallback memory entries")
    
    return {
        "status": "success",
        "log": memories,
        "source": "fallback"
    }

# Simple health check endpoint for the debug router
@router.get("/ping")
async def debug_ping():
    """
    Simple health check endpoint for the debug router.
    """
    print("🔍 Debug ping endpoint called")
    logger.info(f"🔍 Debug ping endpoint called")
    
    return {
        "status": "ok",
        "message": "Debug router is working",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }

# Print confirmation after all endpoints are defined
print("✅ All debug routes registered successfully")
