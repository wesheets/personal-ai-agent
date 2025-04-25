"""
Memory Routes Module for routes directory
This module provides API routes for memory-related operations.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
import datetime
import logging
import sys
import os

# Add app directory to path to fix imports
sys.path.append(os.path.join(os.getcwd(), 'app'))

# Import memory operations from app directory
from app.api.modules.memory import read_memory, write_memory

# Configure logging
logger = logging.getLogger("routes.memory_routes")

router = APIRouter(tags=["memory"])

@router.get("/memory/ping")
def memory_ping():
    """
    Ping endpoint to verify memory routes are accessible.
    """
    logger.info("🔍 DEBUG: memory_ping endpoint called")
    return {"status": "Memory router operational", "timestamp": str(datetime.datetime.now())}

@router.post("/memory/write")
async def memory_write(request_data: dict):
    """
    Write content to memory.
    
    Args:
        request_data: Dictionary containing memory entry data
    
    Returns:
        Dictionary with operation status
    """
    try:
        result = write_memory(
            content=request_data.get("content", ""),
            metadata=request_data.get("metadata", {}),
            tags=request_data.get("tags", []),
            project_id=request_data.get("project_id", "default")
        )
        return {"status": "success", "message": "Memory written successfully", "id": result.get("id", "")}
    except Exception as e:
        logger.error(f"Error writing memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to write memory: {str(e)}")

@router.get("/memory/read")
async def memory_read(
    project_id: str = Query("default", description="Project identifier"),
    limit: int = Query(10, description="Maximum number of entries to return"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """
    Read memory entries.
    
    Args:
        project_id: Project identifier
        limit: Maximum number of entries to return
        tag: Optional tag to filter by
    
    Returns:
        List of memory entries
    """
    try:
        filters = {}
        if tag:
            filters["tags"] = tag
            
        result = read_memory(
            project_id=project_id,
            limit=limit,
            filters=filters
        )
        return {"status": "success", "entries": result}
    except Exception as e:
        logger.error(f"Error reading memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to read memory: {str(e)}")

@router.get("/memory/thread")
async def memory_thread(
    project_id: str = Query("default", description="Project identifier"),
    thread_id: Optional[str] = Query(None, description="Thread identifier")
):
    """
    Get memory thread.
    
    Args:
        project_id: Project identifier
        thread_id: Thread identifier
    
    Returns:
        Memory thread entries
    """
    try:
        result = read_memory(
            project_id=project_id,
            filters={"thread_id": thread_id} if thread_id else {},
            sort_by="timestamp"
        )
        return {"status": "success", "thread": result}
    except Exception as e:
        logger.error(f"Error retrieving memory thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memory thread: {str(e)}")
