from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.vector_memory import get_vector_memory
import logging
from app.schemas.memory_schema import MemoryEntry

# Configure logging
logger = logging.getLogger("api")

# Define models for API responses - using MemoryEntry as base
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
            # Use the correct search_memories method instead of search
            results = await memory.search_memories(
                query="",  # Empty query to get all entries matching filters
                limit=limit
                # Note: search_memories doesn't support filter_string and filter_dict parameters
                # We'll need to filter the results after retrieval
            )
            
            # Apply filters manually if needed
            filtered_results = []
            for result in results:
                # Check if result matches our filters
                metadata = result.get("metadata", {}) or {}
                
                # Check goal_id filter
                if goal_id and metadata.get("goal_id") != goal_id:
                    continue
                
                # Check agent_type filter
                if agent_type and metadata.get("agent_type") != agent_type:
                    continue
                
                # Check timestamp filters
                timestamp = metadata.get("timestamp", "")
                if start_timestamp and timestamp < start_timestamp:
                    continue
                if end_timestamp and timestamp > end_timestamp:
                    continue
                
                filtered_results.append(result)
            
            results = filtered_results[:limit]  # Apply limit after filtering
            logger.info(f"Found {len(results)} memory entries after filtering")
        except Exception as e:
            logger.error(f"Error searching memory: {str(e)}")
            # Return empty results instead of failing
            return []
        
        # Convert results to response model
        memory_entries = []
        for result in results:
            try:
                # Handle potential attribute errors
                result_id = result.get("id", "unknown")
                result_text = result.get("content", "")
                result_metadata = result.get("metadata", {}) or {}
                
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
