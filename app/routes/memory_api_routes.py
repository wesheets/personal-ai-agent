from fastapi import APIRouter, Body, Query, HTTPException, Depends
from typing import List, Dict, Any, Optional
import datetime
import os
import logging

from app.schemas.memory_schema import (
    MemoryAddRequest,
    MemoryAddResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryEntry
)

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/memory", tags=["memory"])

@router.post("/add", response_model=MemoryAddResponse)
async def add_memory(request: MemoryAddRequest = Body(...)):
    """
    Add a new memory entry to the vector store.
    
    Args:
        request: The memory entry to add containing project_id, content, and optional metadata
        
    Returns:
        MemoryAddResponse containing the generated memory_id
    """
    try:
        logger.info(f"Adding memory for project {request.project_id}")
        
        # Validate required fields
        if not request.content or not request.content.strip():
            logger.warning("Invalid request: Missing or empty content field")
            return MemoryAddResponse(
                status="error",
                message="Invalid request: Content field is required and cannot be empty",
                memory_id=None,
                timestamp=str(datetime.datetime.now())
            )
        
        # Initialize memory engine
        from app.core.vector_memory import get_memory_engine
        memory_engine = get_memory_engine()
        
        # Add memory entry
        memory_id = await memory_engine.add_memory(
            project_id=request.project_id,
            content=request.content,
            metadata=request.metadata,
            tags=request.tags,
            agent_id=request.agent_id
        )
        
        logger.info(f"Successfully added memory with ID: {memory_id}")
        
        return MemoryAddResponse(
            status="success",
            message="Memory added successfully",
            memory_id=memory_id,
            timestamp=str(datetime.datetime.now())
        )
    except Exception as e:
        logger.error(f"Error adding memory: {str(e)}")
        
        # Log the error to memory_fallback.json
        try:
            import json
            
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
        
        # Return error response with 200 status code instead of raising exception
        return MemoryAddResponse(
            status="error",
            message=f"Failed to add memory: {str(e)}",
            memory_id=None,
            timestamp=str(datetime.datetime.now())
        )

@router.post("/search", response_model=MemorySearchResponse)
async def search_memory(request: MemorySearchRequest):
    """
    Search for memory entries in the vector store.
    
    Args:
        request: The memory search request containing project_id, query, and optional filters
        
    Returns:
        MemorySearchResponse containing the search results
    """
    try:
        logger.info(f"Searching memory for project {request.project_id} with query: {request.query}")
        
        # Validate required fields
        if not request.query or not request.query.strip():
            logger.warning("Invalid request: Missing or empty query field")
            return MemorySearchResponse(
                status="error",
                message="Invalid request: Query field is required and cannot be empty",
                results=[],
                count=0,
                timestamp=str(datetime.datetime.now())
            )
        
        # Initialize memory engine
        from app.core.vector_memory import get_memory_engine
        memory_engine = get_memory_engine()
        
        # Search memory entries
        results = await memory_engine.search_memory(
            project_id=request.project_id,
            query=request.query,
            limit=request.limit,
            tags=request.tags,
            agent_id=request.agent_id,
            threshold=request.threshold
        )
        
        logger.info(f"Found {len(results)} memory entries matching the query")
        
        return MemorySearchResponse(
            status="success",
            message="Memory search completed successfully",
            results=results,
            count=len(results),
            timestamp=str(datetime.datetime.now())
        )
    except Exception as e:
        logger.error(f"Error searching memory: {str(e)}")
        
        # Log the error to memory_fallback.json
        try:
            import json
            
            log_file = "/home/ubuntu/personal-ai-agent/logs/memory_fallback.json"
            
            # Create log entry
            log_entry = {
                "timestamp": str(datetime.datetime.now()),
                "event": "route_error",
                "endpoint": "memory_search",
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
        
        # Return error response with 200 status code instead of raising exception
        return MemorySearchResponse(
            status="error",
            message=f"Failed to search memory: {str(e)}",
            results=[],
            count=0,
            timestamp=str(datetime.datetime.now())
        )
