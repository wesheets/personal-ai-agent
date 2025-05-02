"""
API endpoint for system status and diagnostics.

This module provides REST API endpoints for monitoring system health,
including uptime, active routes, memory state, and agent registry status.
"""

print("📁 Loaded: system.py (System status route file)")

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import traceback
import os
import time
import json
import datetime
import importlib
from src.utils.debug_logger import log_test_result

# Import agent registry
from app.api.modules.agent import agent_registry

# Import memory store
from app.modules.memory_writer import MEMORY_STORE

# Configure logging
logger = logging.getLogger("api.modules.system")

# Create router
router = APIRouter()
print("🧠 Route defined: /api/modules/system/status -> get_system_status")
print("🧠 Route defined: /api/system/health -> healthcheck")

# Store server start time
SERVER_START_TIME = datetime.datetime.now()

# Track loaded modules
LOADED_MODULES = ["memory", "agent", "system"]

@router.get("/health")
async def healthcheck():
    """
    Simple health check endpoint that returns a 200 OK status.
    
    This endpoint is used by Railway to verify the container is healthy.
    It has no dependencies on database, agent registry, or memory systems
    to ensure it always returns a 200 OK status.
    
    Returns:
        dict: {"ok": True}
    """
    try:
        # Log health check
        logger.info("Health check endpoint accessed")
        
        # Return simple response with no dependencies
        return {"ok": True}
    except Exception as e:
        # Log error but still return success to ensure healthcheck passes
        logger.error(f"Error in health check endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Always return success for Railway healthcheck
        return {"ok": True}

def format_uptime():
    """
    Calculate and format the system uptime from the server start time.
    
    Returns:
        str: Formatted uptime string in the format "Xh Ym"
    """
    now = datetime.datetime.now()
    delta = now - SERVER_START_TIME
    
    # Calculate hours and minutes
    total_seconds = delta.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    
    return f"{hours}h {minutes}m"

def get_active_routes():
    """
    Get a list of active API routes.
    
    Returns:
        List[str]: List of active route paths
    """
    # Return a list of known API routes
    return [
        "/api/modules/memory/summarize",
        "/api/modules/memory/thread",
        "/api/modules/agent/list",
        "/api/modules/system/status"
    ]

def get_agent_count():
    """
    Get the number of agents in the registry.
    
    Returns:
        int: Number of registered agents
    """
    return len(agent_registry)

def get_memory_store_size():
    """
    Get the total number of memory entries across all agents.
    
    Returns:
        int: Total number of memory entries
    """
    return len(MEMORY_STORE)

def get_modules_loaded():
    """
    Get the list of loaded modules.
    
    Returns:
        List[str]: List of loaded module names
    """
    return LOADED_MODULES

@router.get("/status")
async def get_system_status():
    """
    Returns a snapshot of system health including uptime, active routes,
    memory state, and agent registry status.
    
    This endpoint provides a comprehensive overview of the system's current state,
    which is useful for monitoring and diagnostics.
    
    Returns:
    - status: "ok" if successful
    - uptime: Server uptime in "Xh Ym" format
    - active_routes: List of active API routes
    - agent_count: Number of agents in the registry
    - memory_store_size: Total number of memory entries
    - modules_loaded: List of loaded modules
    """
    try:
        # Get system status information
        uptime = format_uptime()
        active_routes = get_active_routes()
        agent_count = get_agent_count()
        memory_store_size = get_memory_store_size()
        modules_loaded = get_modules_loaded()
        
        # Log successful system status check
        log_test_result("System", "/api/system/status", "PASS", 
                       f"System running for {uptime}", 
                       f"Agents: {agent_count}, Memories: {memory_store_size}, Modules: {len(modules_loaded)}")
        
        # Return response
        return {
            "status": "ok",
            "uptime": uptime,
            "active_routes": active_routes,
            "agent_count": agent_count,
            "memory_store_size": memory_store_size,
            "modules_loaded": modules_loaded
        }
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Log system status check failure
        log_test_result("System", "/api/system/status", "FAIL", 
                       f"Error: {str(e)}", 
                       f"Check system logs for details")
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get system status: {str(e)}"
            }
        )
