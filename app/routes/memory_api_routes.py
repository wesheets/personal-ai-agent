"""
Memory API Routes Module
This module defines the routes for memory operations in the application.
Includes:
- /api/memory/add for adding new memory entries
- /api/memory/search for searching existing memory entries
"""
import logging
import datetime
import os
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel

# Import schemas
from app.schemas.memory import MemoryItem, ThreadRequest, SummarizationRequest

# Configure logging
logger = logging.getLogger("app.routes.memory_api_routes")

# Create router with API prefix
router = APIRouter(
    prefix="/api/memory",
    tags=["memory"],
    responses={404: {"description": "Not found"}}
)

class MemoryAddRequest(BaseModel):
    """
    Schema for memory add request.
    """
    project_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    agent_id: Optional[str] = "system"

class MemoryAddResponse(BaseModel):
    """
    Schema for memory add response.
    """
    status: str
    message: str
    memory_id: str
    timestamp: str

class MemorySearchRequest(BaseModel):
    """
    Schema for memory search request.
    """
    project_id: str
    query: str
    limit: Optional[int] = 10
    tags: Optional[List[str]] = []
    agent_id: Optional[str] = None
    threshold: Optional[float] = 0.7

class MemorySearchResponse(BaseModel):
    """
    Schema for memory search response.
    """
    status: str
    message: str
    results: List[Dict[str, Any]]
    count: int
    timestamp: str

@router.post("/add", response_model=MemoryAddResponse)
async def add_memory(request: MemoryAddRequest):
    """
    Add a new memory entry to the vector store.
    
    Args:
        request: The memory add request containing project_id, content, and optional metadata
        
    Returns:
        MemoryAddResponse containing the status and memory_id
    """
    try:
        logger.info(f"Adding memory for project {request.project_id}")
        
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
        
        raise HTTPException(status_code=500, detail=f"Failed to add memory: {str(e)}")

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
        
        raise HTTPException(status_code=500, detail=f"Failed to search memory: {str(e)}")
