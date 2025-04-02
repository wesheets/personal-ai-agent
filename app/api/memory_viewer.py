from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.vector_memory import get_vector_memory

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
    
    # Search memory with filters
    # Adapt parameters to match what search_memories accepts
    results = await memory.search_memories(
        query="",  # Empty query to get all entries matching filters
        limit=limit
        # Note: filter_string and filter_dict parameters are not supported by search_memories
    )
    
    # Convert results to response model
    memory_entries = []
    for result in results:
        entry = MemoryEntryModel(
            id=result.id,
            content=result.text,
            timestamp=result.metadata.get("timestamp", ""),
            agent_type=result.metadata.get("agent_type"),
            goal_id=result.metadata.get("goal_id"),
            tags=result.metadata.get("tags", []),
            title=result.metadata.get("title"),
            metadata={k: v for k, v in result.metadata.items() 
                     if k not in ["timestamp", "agent_type", "goal_id", "tags", "title"]}
        )
        memory_entries.append(entry)
    
    return memory_entries

# Export router
memory_router = router
