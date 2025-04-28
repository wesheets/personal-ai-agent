"""
Memory Routes Module for app/routes directory

This module provides API routes for memory-related operations.
The implementation avoids top-level runtime logic and initializes
the memory engine inside each route handler.

# memory_tag: phase3.0_sprint1_core_cognitive_handler_activation
"""
from fastapi import APIRouter, Query, HTTPException, Path
from typing import Optional, Dict, Any
import datetime
import logging
import os
import uuid
import json
from app.schemas.memory.memory_add_schema import MemoryAddRequest, MemoryAddResponse
from app.schemas.memory.memory_get_key_schema import MemoryGetResponse

# Configure logging
logger = logging.getLogger("app.routes.memory_routes")

# Ensure logs directory exists
os.makedirs("/home/ubuntu/personal-ai-agent/logs", exist_ok=True)

# Create router
router = APIRouter(tags=["memory"])

@router.post("/add", response_model=MemoryAddResponse)
async def add_memory(request: MemoryAddRequest):
    """
    Add a simple key/value pair to memory.
    
    Args:
        request: MemoryAddRequest containing key and value to store
            
    Returns:
        MemoryAddResponse containing status and memory_id
    """
    logger.info(f"🔍 DEBUG: memory_add endpoint called with key: {request.key}")
    
    try:
        # In a real implementation, this would store the data in a database
        # For this minimal viable handler, we'll store it in a simple JSON file
        
        memory_file = "/home/ubuntu/personal-ai-agent/logs/simple_memory_store.json"
        
        # Generate a unique memory ID
        memory_id = str(uuid.uuid4())
        
        # Create memory entry
        memory_entry = {
            "memory_id": memory_id,
            "key": request.key,
            "value": request.value,
            "metadata": request.metadata,
            "timestamp": str(datetime.datetime.now())
        }
        
        # Check if memory file exists
        if os.path.exists(memory_file):
            # Read existing memory entries
            try:
                with open(memory_file, 'r') as f:
                    memory_store = json.load(f)
                    if not isinstance(memory_store, dict):
                        memory_store = {}
            except json.JSONDecodeError:
                memory_store = {}
        else:
            memory_store = {}
        
        # Add new memory entry
        memory_store[request.key] = memory_entry
        
        # Write updated memory store
        with open(memory_file, 'w') as f:
            json.dump(memory_store, f, indent=2)
        
        logger.info(f"✅ Successfully added memory with key: {request.key}")
        return MemoryAddResponse(
            memory_id=memory_id,
            status="success",
            key=request.key,
            metadata=request.metadata
        )
    except Exception as e:
        logger.error(f"❌ Error adding memory with key {request.key}: {str(e)}")
        
        # Log the error to memory_fallback.json
        try:
            log_file = "/home/ubuntu/personal-ai-agent/logs/memory_fallback.json"
            
            # Create log entry
            log_entry = {
                "timestamp": str(datetime.datetime.now()),
                "event": "route_error",
                "endpoint": "memory_add",
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
        
        raise HTTPException(status_code=500, detail=f"Failed to add memory: {str(e)}")

@router.get("/get/{key}", response_model=MemoryGetResponse)
async def get_memory(key: str = Path(..., description="Key to retrieve from memory")):
    """
    Retrieve a value from memory by key.
    
    Args:
        key: The key to retrieve
            
    Returns:
        MemoryGetResponse containing the retrieved value
    """
    logger.info(f"🔍 DEBUG: memory_get endpoint called with key: {key}")
    
    try:
        # In a real implementation, this would retrieve data from a database
        # For this minimal viable handler, we'll retrieve it from the simple JSON file
        
        memory_file = "/home/ubuntu/personal-ai-agent/logs/simple_memory_store.json"
        
        # Check if memory file exists
        if not os.path.exists(memory_file):
            raise HTTPException(status_code=404, detail=f"Memory key not found: {key}")
        
        # Read memory entries
        try:
            with open(memory_file, 'r') as f:
                memory_store = json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to read memory store")
        
        # Check if key exists
        if key not in memory_store:
            raise HTTPException(status_code=404, detail=f"Memory key not found: {key}")
        
        # Get memory entry
        memory_entry = memory_store[key]
        
        logger.info(f"✅ Successfully retrieved memory with key: {key}")
        return MemoryGetResponse(
            key=key,
            value=memory_entry["value"],
            memory_id=memory_entry["memory_id"],
            status="success",
            timestamp=memory_entry["timestamp"],
            metadata=memory_entry.get("metadata")
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving memory with key {key}: {str(e)}")
        
        # Log the error to memory_fallback.json
        try:
            log_file = "/home/ubuntu/personal-ai-agent/logs/memory_fallback.json"
            
            # Create log entry
            log_entry = {
                "timestamp": str(datetime.datetime.now()),
                "event": "route_error",
                "endpoint": "memory_get",
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
        
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memory: {str(e)}")

@router.get("/ping")
def memory_ping():
    """
    Ping endpoint to verify memory routes are accessible.
    """
    logger.info("🔍 DEBUG: memory_ping endpoint called")
    return {"status": "Memory router operational", "timestamp": str(datetime.datetime.now())}

@router.post("/write")
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

@router.get("/read")
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
