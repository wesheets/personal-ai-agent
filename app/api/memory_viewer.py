from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.vector_memory import get_vector_memory
import logging

# Configure logging
logger = logging.getLogger("api")

# Define models for API responses
class MemoryEntryModel(BaseModel):
    id: str
    content: str
    timestamp: str
    agent_type: Optional[str] = None
    goal_id: Optional[str] = None
    tags: Optional[List[str]] = None
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Create router
router = APIRouter()

@router.get("/memory", response_model=List[MemoryEntryModel])
@router.post("/memory", response_model=List[MemoryEntryModel])
async def get_memory_entries(
    goal_id: Optional[str] = Query(None, description="Filter by goal ID"),
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    start_timestamp: Optional[str] = Query(None, description="Filter by start timestamp"),
    end_timestamp: Optional[str] = Query(None, description="Filter by end timestamp"),
    limit: int = Query(50, description="Maximum number of entries to return")
):
    """
    Get memory entries with optional filtering
    """
    try:
        logger.info(f"Getting memory entries with filters: goal_id={goal_id}, agent_type={agent_type}, limit={limit}")
        memory = get_vector_memory()
        
        # Build filter query
        filter_params = {}
        if goal_id:
            filter_params["goal_id"] = goal_id
        if agent_type:
            filter_params["agent_type"] = agent_type
        
        # Add timestamp filters if provided
        timestamp_filters = []
        if start_timestamp:
            timestamp_filters.append(f"timestamp >= '{start_timestamp}'")
        if end_timestamp:
            timestamp_filters.append(f"timestamp <= '{end_timestamp}'")
        
        # Search memory with filters - wrapped in try/except
        try:
            # Check if search is async or sync method
            if hasattr(memory, "search_async"):
                # Use async method if available
                results = await memory.search_async(
                    query="",  # Empty query to get all entries matching filters
                    filter_string=" AND ".join(timestamp_filters) if timestamp_filters else None,
                    filter_dict=filter_params if filter_params else None,
                    limit=limit
                )
            else:
                # Fall back to sync method
                results = memory.search(
                    query="",  # Empty query to get all entries matching filters
                    filter_string=" AND ".join(timestamp_filters) if timestamp_filters else None,
                    filter_dict=filter_params if filter_params else None,
                    limit=limit
                )
            
            logger.info(f"Found {len(results)} memory entries")
        except Exception as e:
            logger.error(f"Error searching memory: {str(e)}")
            # Return empty results instead of failing
            return []
        
        # Convert results to response model
        memory_entries = []
        for result in results:
            try:
                # Handle potential attribute errors
                result_id = getattr(result, "id", "unknown")
                result_text = getattr(result, "text", "")
                result_metadata = getattr(result, "metadata", {}) or {}
                
                entry = MemoryEntryModel(
                    id=result_id,
                    content=result_text,
                    timestamp=result_metadata.get("timestamp", ""),
                    agent_type=result_metadata.get("agent_type"),
                    goal_id=result_metadata.get("goal_id"),
                    tags=result_metadata.get("tags", []),
                    title=result_metadata.get("title"),
                    metadata={k: v for k, v in result_metadata.items() 
                             if k not in ["timestamp", "agent_type", "goal_id", "tags", "title"]}
                )
                memory_entries.append(entry)
            except Exception as e:
                logger.error(f"Error processing memory entry: {str(e)}")
                # Continue processing other entries
                continue
        
        return memory_entries
    except Exception as e:
        logger.error(f"Unexpected error in get_memory_entries: {str(e)}")
        # Return empty list instead of throwing 500
        return []

# Export router
memory_router = router
