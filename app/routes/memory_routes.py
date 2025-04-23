"""
Memory Routes Module for app/routes directory

This module provides API routes for memory-related operations.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
import datetime
import logging

# Import memory operations
from app.api.modules.memory import read_memory, write_memory

# Configure logging
logger = logging.getLogger("app.routes.memory_routes")

router = APIRouter(tags=["memory"])

@router.get("/memory/ping")
def memory_ping():
    """
    Ping endpoint to verify memory routes are accessible.
    """
    logger.info("🔍 DEBUG: memory_ping endpoint called")
    return {"status": "Memory router operational", "timestamp": str(datetime.datetime.now())}

@router.post("/memory/write")
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
        # Convert request data to expected format for write_memory
        memory_data = {
            "agent_id": request_data.get("agent", "default"),
            "type": request_data.get("type", "note"),
            "content": request_data.get("content", ""),
            "tags": request_data.get("tags", []),
            "project_id": request_data.get("project_id", "default"),
            "chain_id": request_data.get("chain_id", "default"),
        }
        
        # Write to memory
        result = await write_memory(memory_data)
        
        return {
            "status": "success",
            "message": "Memory write request processed",
            "content": request_data.get("content", ""),
            "project_id": request_data.get("project_id", "default"),
            "chain_id": request_data.get("chain_id", "default"),
            "timestamp": str(datetime.datetime.now())
        }
    except Exception as e:
        logger.error(f"Error in memory_write_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to write memory: {str(e)}")

@router.get("/memory/read")
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
        # Get memory entries for the project
        entries = await read_memory(agent_id=project_id, memory_type="project")
        
        logger.info(f"✅ Successfully retrieved memory for project: {project_id}")
        return {
            "status": "success",
            "message": "Memory read successful",
            "project_id": project_id,
            "entries": [entries],
            "timestamp": str(datetime.datetime.now())
        }
    except Exception as e:
        logger.error(f"❌ Error reading memory for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to read memory: {str(e)}")
