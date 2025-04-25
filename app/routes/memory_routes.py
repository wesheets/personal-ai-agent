"""
Memory Routes Module for app/routes directory

This module provides API routes for memory-related operations.
The implementation avoids top-level runtime logic and initializes
the memory engine inside each route handler.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
import datetime
import logging
import os

# Configure logging
logger = logging.getLogger("app.routes.memory_routes")

# Ensure logs directory exists
os.makedirs("/home/ubuntu/personal-ai-agent/logs", exist_ok=True)

# Create router
router = APIRouter(tags=["memory"])

@router.get("/api/memory/ping")
def memory_ping():
    """
    Ping endpoint to verify memory routes are accessible.
    """
    logger.info("🔍 DEBUG: memory_ping endpoint called")
    return {"status": "Memory router operational", "timestamp": str(datetime.datetime.now())}

@router.post("/api/memory/write")
async def memory_write_endpoint(request_data: dict):
    """
    Write content to memory.
    
    Args:
        request_data: Dictionary containing memory entry data
            - project_id: The project identifier
            - agent: The agent identifier
            - type: The memory entry type
            - content: The memory entry content
            - tags: Optional list of tags
            
    Returns:
        Dict containing status and memory entry details
    """
    logger.info(f"🔍 DEBUG: memory_write endpoint called with project_id: {request_data.get('project_id', 'default')}")
    
    try:
        # Initialize memory engine inside the route handler
        from app.api.modules.memory_engine import get_memory_engine
        memory_engine = get_memory_engine()
        
        # Convert request data to expected format for write_memory
        memory_data = {
            "agent_id": request_data.get("agent", "default"),
            "type": request_data.get("type", "note"),
            "content": request_data.get("content", ""),
            "tags": request_data.get("tags", []),
            "project_id": request_data.get("project_id", "default"),
            "chain_id": request_data.get("chain_id", "default"),
        }
        
        # Write to memory using the engine
        result = await memory_engine.write_memory(memory_data)
        
        return {
            "status": result.get("status", "success"),
            "message": result.get("message", "Memory write request processed"),
            "content": request_data.get("content", ""),
            "project_id": request_data.get("project_id", "default"),
            "chain_id": request_data.get("chain_id", "default"),
            "timestamp": str(datetime.datetime.now())
        }
    except Exception as e:
        logger.error(f"Error in memory_write_endpoint: {str(e)}")
        
        # Log the error to memory_fallback.json
        try:
            import json
            
            log_file = "/home/ubuntu/personal-ai-agent/logs/memory_fallback.json"
            
            # Create log entry
            log_entry = {
                "timestamp": str(datetime.datetime.now()),
                "event": "route_error",
                "endpoint": "memory_write",
                "error": str(e)
            }
            
            # Check if log file exists
            if os.path.exists(log_file):
                # Read existing logs
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = [logs]
                except json.JSONDecodeError:
                    logs = []
            else:
                logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Write updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as log_error:
            logger.error(f"Failed to log memory route error: {str(log_error)}")
        
        raise HTTPException(status_code=500, detail=f"Failed to write memory: {str(e)}")

@router.get("/api/memory/read")
async def memory_read_endpoint(project_id: str = Query(..., description="Project identifier")):
    """
    Read content from memory.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing memory entries for the specified project
    """
    logger.info(f"🔍 DEBUG: memory_read endpoint called with project_id: {project_id}")
    
    try:
        # Initialize memory engine inside the route handler
        from app.api.modules.memory_engine import get_memory_engine
        memory_engine = get_memory_engine()
        
        # Get memory entries for the project using the engine
        entries = await memory_engine.read_memory(agent_id=project_id, memory_type="project")
        
        logger.info(f"✅ Successfully retrieved memory for project: {project_id}")
        return {
            "status": entries.get("status", "success"),
            "message": entries.get("message", "Memory read successful"),
            "project_id": project_id,
            "entries": [entries],
            "timestamp": str(datetime.datetime.now())
        }
    except Exception as e:
        logger.error(f"❌ Error reading memory for project {project_id}: {str(e)}")
        
        # Log the error to memory_fallback.json
        try:
            import json
            
            log_file = "/home/ubuntu/personal-ai-agent/logs/memory_fallback.json"
            
            # Create log entry
            log_entry = {
                "timestamp": str(datetime.datetime.now()),
                "event": "route_error",
                "endpoint": "memory_read",
                "error": str(e)
            }
            
            # Check if log file exists
            if os.path.exists(log_file):
                # Read existing logs
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = [logs]
                except json.JSONDecodeError:
                    logs = []
            else:
                logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Write updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as log_error:
            logger.error(f"Failed to log memory route error: {str(log_error)}")
        
        raise HTTPException(status_code=500, detail=f"Failed to read memory: {str(e)}")
