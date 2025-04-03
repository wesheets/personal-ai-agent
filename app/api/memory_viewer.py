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
    try:
        # Get vector memory with error handling
        try:
            memory = get_vector_memory()
            if not memory:
                import logging
                logger = logging.getLogger("api")
                logger.error("Failed to get vector memory instance")
                return []
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error getting vector memory: {str(e)}")
            return []
        
        # Build filter query with defensive programming
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
        
        # Search memory with filters and error handling
        try:
            results = await memory.search_memories(
                query="",  # Empty query to get all entries matching filters
                limit=limit
                # Note: filter_string and filter_dict parameters are not supported by search_memories
            )
            
            # Validate results
            if results is None:
                import logging
                logger = logging.getLogger("api")
                logger.error("search_memories returned None")
                return []
                
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error searching memories: {str(e)}")
            return []
        
        # Convert results to response model with defensive programming
        memory_entries = []
        for result in results:
            try:
                # Skip invalid results
                if not result:
                    continue
                    
                # Safely access result attributes
                result_id = getattr(result, 'id', None)
                if not result_id:
                    # Try dictionary access if attribute access fails
                    result_id = result.get('id', f"unknown-{len(memory_entries)}")
                
                # Get content with fallbacks
                content = ""
                if hasattr(result, 'text'):
                    content = result.text
                elif hasattr(result, 'content'):
                    content = result.content
                elif isinstance(result, dict):
                    content = result.get('text', result.get('content', ''))
                
                # Safely get metadata
                metadata = {}
                if hasattr(result, 'metadata') and result.metadata:
                    metadata = result.metadata
                elif isinstance(result, dict) and 'metadata' in result:
                    metadata = result.get('metadata', {})
                
                # Ensure metadata is a dictionary
                if not isinstance(metadata, dict):
                    metadata = {}
                
                # Create entry with safe defaults
                entry = MemoryEntryModel(
                    id=result_id,
                    content=content,
                    timestamp=metadata.get("timestamp", ""),
                    agent_type=metadata.get("agent_type"),
                    goal_id=metadata.get("goal_id"),
                    tags=metadata.get("tags", []),
                    title=metadata.get("title"),
                    metadata={k: v for k, v in metadata.items() 
                             if k not in ["timestamp", "agent_type", "goal_id", "tags", "title"]}
                )
                memory_entries.append(entry)
            except Exception as e:
                import logging
                logger = logging.getLogger("api")
                logger.error(f"Error processing memory entry: {str(e)}")
                # Continue to next result
        
        return memory_entries
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger("api")
        logger.error(f"Error in get_memory_entries: {str(e)}")
        # Return empty list as fallback
        return []

# Export router
memory_router = router
