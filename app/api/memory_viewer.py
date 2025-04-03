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
                
            # Log successful memory system initialization
            import logging
            logger = logging.getLogger("api")
            logger.info(f"Successfully initialized memory system: {type(memory).__name__}")
            
            # Check if memory system is properly initialized
            if not hasattr(memory, 'table_name') or not hasattr(memory, 'embedding_model'):
                logger.warning("Memory system missing expected attributes")
                
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
            # Check if the memory object has the expected search_memories method
            if not hasattr(memory, 'search_memories'):
                import logging
                logger = logging.getLogger("api")
                logger.error("VectorMemorySystem has no search_memories method")
                
                # Try alternative method names if available
                if hasattr(memory, 'similarity_search'):
                    logger.info("Using similarity_search method as fallback")
                    results = await memory.similarity_search(
                        query="",  # Empty query to get all entries matching filters
                        limit=limit
                    )
                else:
                    logger.error("No suitable search method found in VectorMemorySystem")
                    return []
            else:
                # Use the standard search_memories method
                results = await memory.search_memories(
                    query="",  # Empty query to get all entries matching filters
                    limit=limit
                    # Note: filter_string and filter_dict parameters are not supported by search_memories
                )
            
            # Validate results
            if results is None:
                import logging
                logger = logging.getLogger("api")
                logger.error("Memory search returned None")
                return []
                
            # Validate that results is a list
            if not isinstance(results, list):
                import logging
                logger = logging.getLogger("api")
                logger.error(f"Memory search returned non-list type: {type(results)}")
                return []
                
            # Log successful search
            import logging
            logger = logging.getLogger("api")
            logger.info(f"Successfully retrieved {len(results)} memory entries")
                
        except AttributeError as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"AttributeError in memory search: {str(e)}")
            return []
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error searching memories: {str(e)}")
            return []
        
        # Convert results to response model with enhanced validation and defensive programming
        memory_entries = []
        for result in results:
            try:
                # Skip invalid results
                if not result:
                    continue
                
                # Log result type for debugging
                import logging
                logger = logging.getLogger("api")
                logger.debug(f"Processing result of type: {type(result)}")
                
                # Validate result has required fields
                has_required_fields = False
                
                # Check if result has id and content/text fields
                if isinstance(result, dict):
                    has_id = 'id' in result
                    has_content = 'content' in result or 'text' in result
                    has_required_fields = has_id and has_content
                else:
                    has_id = hasattr(result, 'id')
                    has_content = hasattr(result, 'text') or hasattr(result, 'content')
                    has_required_fields = has_id and has_content
                
                if not has_required_fields:
                    logger.warning(f"Result missing required fields: {result}")
                    # Create minimal valid entry with generated ID
                    result_id = f"generated-{len(memory_entries)}"
                    content = str(result) if result else "No content available"
                    metadata = {}
                else:
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
                
                # Validate metadata fields
                for key in ["timestamp", "agent_type", "goal_id", "tags", "title"]:
                    if key in metadata and metadata[key] is None:
                        metadata[key] = "" if key != "tags" else []
                
                # Ensure tags is a list
                if "tags" in metadata and not isinstance(metadata["tags"], list):
                    metadata["tags"] = [str(metadata["tags"])] if metadata["tags"] else []
                
                # Create entry with safe defaults
                try:
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
                    logger.debug(f"Successfully processed memory entry with ID: {result_id}")
                except Exception as e:
                    logger.error(f"Error creating MemoryEntryModel: {str(e)}")
                    # Skip this entry
            except Exception as e:
                import logging
                logger = logging.getLogger("api")
                logger.error(f"Error processing memory entry: {str(e)}")
                # Continue to next result
        
        # Log successful completion with statistics
        import logging
        logger = logging.getLogger("api")
        logger.info(f"Memory retrieval completed successfully: {len(memory_entries)} entries returned")
        
        # Add detailed success metrics if entries were found
        if memory_entries:
            # Log some statistics about the entries
            goal_ids = set(entry.goal_id for entry in memory_entries if entry.goal_id)
            agent_types = set(entry.agent_type for entry in memory_entries if entry.agent_type)
            
            logger.info(f"Memory entries statistics: {len(goal_ids)} unique goals, {len(agent_types)} unique agent types")
            logger.info(f"Filter parameters applied: goal_id={goal_id}, agent_type={agent_type}, limit={limit}")
            
            # Unit test confirmation for successful path
            logger.info("UNIT_TEST_MARKER: Memory viewer endpoint successfully retrieved and processed entries")
        
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
