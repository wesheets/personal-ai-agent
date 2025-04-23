from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
# Fix import path to point to the correct location of memory_reader.py
from memory.memory_reader import get_memory_for_project, get_memory_thread_for_project
import datetime
import logging

# Configure logging
logger = logging.getLogger("memory_routes")

router = APIRouter()


@router.get("/memory/ping")
def memory_ping():
    print("🔍 DEBUG: memory_ping endpoint called")
    return {"status": "Memory router recovered", "timestamp": str(datetime.datetime.now())}


@router.post("/memory/write")
async def memory_write(request_data: dict):
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
    print(f"🔍 DEBUG: memory_write endpoint called with project_id: {request_data.get('project_id', 'default')}")
    return {
        "status": "success",
        "message": "Memory write request received",
        "content": request_data.get("content", ""),
        "project_id": request_data.get("project_id", "default"),
        "chain_id": request_data.get("chain_id", "default"),
        "timestamp": str(datetime.datetime.now())
    }


@router.get("/memory/read")
async def memory_read(project_id: str = Query(..., description="Project identifier")):
    """
    Read content from memory.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing memory entries for the specified project
    """
    logger.info(f"🔍 DEBUG: memory_read endpoint called with project_id: {project_id}")
    print(f"🔍 DEBUG: memory_read endpoint called with project_id: {project_id}")
    try:
        # Get memory entries for the project
        entries = get_memory_for_project(project_id)
        
        logger.info(f"✅ Successfully retrieved {len(entries)} memory entries for project: {project_id}")
        return {
            "status": "success",
            "message": "Memory read successful",
            "project_id": project_id,
            "entries": entries,
            "timestamp": str(datetime.datetime.now())
        }
    except Exception as e:
        logger.error(f"❌ Error reading memory for project {project_id}: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to read memory: {str(e)}",
            "project_id": project_id,
            "entries": [],
            "timestamp": str(datetime.datetime.now())
        }


@router.post("/memory/summarize")
async def memory_summarize(request_data: dict):
    """
    Summarize a memory thread.
    
    Args:
        request_data: Dictionary containing summarization parameters
            - project_id: The project identifier
            - summary_type: The type of summary to generate
            - limit: Optional maximum number of entries to summarize
            
    Returns:
        Dict containing the generated summary
    """
    logger.info(f"🔍 DEBUG: memory_summarize endpoint called with project_id: {request_data.get('project_id', 'default')}")
    print(f"🔍 DEBUG: memory_summarize endpoint called with project_id: {request_data.get('project_id', 'default')}")
    return {
        "status": "success",
        "message": "Memory summarize request received",
        "project_id": request_data.get("project_id", "default"),
        "chain_id": request_data.get("chain_id", "default"),
        "summary": "This is a placeholder summary of the memory thread.",
        "timestamp": str(datetime.datetime.now())
    }


@router.post("/memory/thread")
async def memory_thread_post(request_data: dict):
    """
    Get a memory thread via POST method.
    """
    logger.info(f"🔍 DEBUG: memory_thread_post endpoint called with project_id: {request_data.get('project_id', 'default')}")
    print(f"🔍 DEBUG: memory_thread_post endpoint called with project_id: {request_data.get('project_id', 'default')}")
    return {
        "status": "success",
        "message": "Memory thread request received",
        "project_id": request_data.get("project_id", "default"),
        "chain_id": request_data.get("chain_id", "default"),
        "thread": [
            {"timestamp": "2025-04-17T01:56:00", "content": "Example memory entry 1"},
            {"timestamp": "2025-04-17T01:56:30", "content": "Example memory entry 2"},
            {"timestamp": "2025-04-17T01:57:00", "content": "Example memory entry 3"},
        ],
        "timestamp": str(datetime.datetime.now())
    }


@router.get("/memory/thread")
async def memory_thread_get(
    project_id: str = Query(..., description="Project identifier")
):
    """
    Get a memory thread via GET method.

    Args:
        project_id: The project identifier

    Returns:
        Dict containing thread entries for the specified project
    """
    logger.info(f"🔍 DEBUG: memory_thread_get endpoint called with project_id: {project_id}")
    print(f"🔍 DEBUG: memory_thread_get endpoint called with project_id: {project_id}")
    try:
        # Get memory thread for the project
        thread = get_memory_thread_for_project(project_id)
        
        logger.info(f"✅ Successfully retrieved memory thread with {len(thread)} entries for project: {project_id}")
        return {
            "status": "success", 
            "project_id": project_id, 
            "thread": thread,
            "timestamp": str(datetime.datetime.now())
        }
    except Exception as e:
        logger.error(f"❌ Error getting memory thread for project {project_id}: {str(e)}")
        return {
            "status": "error", 
            "message": f"Failed to get memory thread: {str(e)}",
            "timestamp": str(datetime.datetime.now())
        }
