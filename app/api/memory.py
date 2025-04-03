from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.core.vector_memory import VectorMemorySystem
from app.db.supabase_manager import get_supabase_client

router = APIRouter()
memory_system = VectorMemorySystem()  # Initialize but will use dependency injection for clients

class MemoryAddRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    priority: Optional[bool] = False

class MemorySearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    priority_only: Optional[bool] = False

class MemoryResponse(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    similarity: Optional[float] = None
    priority: bool
    created_at: str

class MemorySearchResponse(BaseModel):
    results: List[MemoryResponse]
    metadata: Dict[str, Any]

class MemoryUpdatePriorityRequest(BaseModel):
    priority: bool

@router.post("/add", status_code=201)
async def add_memory(
    request: MemoryAddRequest,
    background_tasks: BackgroundTasks,
    supabase_client = Depends(get_supabase_client)
):
    """
    Add a new memory to the vector memory system
    """
    try:
        # Validate request parameters
        if not request:
            import logging
            logger = logging.getLogger("api")
            logger.error("Invalid request: request object is None")
            raise HTTPException(status_code=400, detail="Invalid request")
            
        # Ensure content exists and is a string
        content = getattr(request, 'content', None)
        if not content or not isinstance(content, str):
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Invalid content: {content}")
            raise HTTPException(status_code=400, detail="Content is required and must be a string")
            
        # Ensure metadata is a dictionary if provided
        metadata = getattr(request, 'metadata', None)
        if metadata is not None and not isinstance(metadata, dict):
            metadata = {}
            
        # Ensure priority is a boolean
        priority = bool(getattr(request, 'priority', False))
        
        # Store memory with error handling
        try:
            memory_id = await memory_system.store_memory(
                content=content,
                metadata=metadata,
                priority=priority
            )
            
            if not memory_id:
                raise ValueError("Failed to get valid memory_id from store_memory")
                
            return {"message": "Memory added successfully", "memory_id": memory_id}
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error in memory_system.store_memory: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error adding memory: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger("api")
        logger.error(f"Unexpected error in add_memory endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding memory: {str(e)}")

@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(
    request: MemorySearchRequest,
    supabase_client = Depends(get_supabase_client)
):
    """
    Search for memories similar to the query
    """
    try:
        # Validate request parameters
        query = request.query if request.query else ""
        limit = max(1, min(100, request.limit if request.limit is not None else 5))  # Ensure limit is between 1 and 100
        priority_only = bool(request.priority_only)
        
        # Search memories with error handling
        try:
            results = await memory_system.search_memories(
                query=query,
                limit=limit,
                priority_only=priority_only
            )
            
            # Validate results
            if results is None:
                results = []
                
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error in memory_system.search_memories: {str(e)}")
            results = []
        
        # Process results with defensive programming
        processed_results = []
        for result in results:
            try:
                # Skip invalid results
                if not result:
                    continue
                    
                # Process result and add to list
                processed_results.append(result)
            except Exception as e:
                import logging
                logger = logging.getLogger("api")
                logger.error(f"Error processing search result: {str(e)}")
                # Continue to next result
        
        # Return response with safe values
        return MemorySearchResponse(
            results=processed_results,
            metadata={
                "query": query,
                "limit": limit,
                "priority_only": priority_only,
                "result_count": len(processed_results)
            }
        )
    except Exception as e:
        # Log error and return empty response instead of 500 error
        import logging
        logger = logging.getLogger("api")
        logger.error(f"Error in search_memories endpoint: {str(e)}")
        
        return MemorySearchResponse(
            results=[],
            metadata={
                "query": getattr(request, "query", ""),
                "limit": getattr(request, "limit", 5),
                "priority_only": getattr(request, "priority_only", False),
                "result_count": 0,
                "error": str(e)
            }
        )

@router.get("/get/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    supabase_client = Depends(get_supabase_client)
):
    """
    Get a specific memory by ID
    """
    try:
        # Validate memory_id
        if not memory_id or not isinstance(memory_id, str):
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Invalid memory_id: {memory_id}")
            raise HTTPException(status_code=400, detail="Invalid memory ID")
            
        # Get memory with error handling
        try:
            memory = await memory_system.get_memory_by_id(memory_id)
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error in memory_system.get_memory_by_id: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving memory: {str(e)}")
        
        # Check if memory exists
        if not memory:
            raise HTTPException(status_code=404, detail=f"Memory with ID {memory_id} not found")
        
        # Validate memory structure before returning
        try:
            # Ensure required fields exist
            if not hasattr(memory, 'id') and not isinstance(memory, dict):
                raise ValueError("Memory object missing required 'id' field")
                
            # Return memory object
            return memory
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error validating memory structure: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Invalid memory structure: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger("api")
        logger.error(f"Unexpected error in get_memory endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving memory: {str(e)}")

@router.patch("/priority/{memory_id}")
async def update_memory_priority(
    memory_id: str,
    request: MemoryUpdatePriorityRequest,
    supabase_client = Depends(get_supabase_client)
):
    """
    Update the priority flag of a memory
    """
    try:
        success = await memory_system.update_memory_priority(memory_id, request.priority)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Memory with ID {memory_id} not found")
        
        return {"message": f"Memory priority updated to {request.priority}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating memory priority: {str(e)}")

@router.delete("/delete/{memory_id}")
async def delete_memory(
    memory_id: str,
    supabase_client = Depends(get_supabase_client)
):
    """
    Delete a memory by ID
    """
    try:
        success = await memory_system.delete_memory(memory_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Memory with ID {memory_id} not found")
        
        return {"message": "Memory deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting memory: {str(e)}")

@router.get("/status")
async def get_memory_status(
    supabase_client = Depends(get_supabase_client)
):
    """
    Get status information about the memory system
    """
    try:
        # Import with error handling
        try:
            from app.db.supabase_manager import SupabaseManager
        except ImportError as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error importing SupabaseManager: {str(e)}")
            return {
                "status": "error",
                "error": f"Import error: {str(e)}",
                "embedding_model": getattr(memory_system, "embedding_model", "unknown")
            }
        
        # Create manager with error handling
        try:
            manager = SupabaseManager()
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error creating SupabaseManager: {str(e)}")
            return {
                "status": "error",
                "error": f"Manager initialization error: {str(e)}",
                "embedding_model": getattr(memory_system, "embedding_model", "unknown")
            }
        
        # Get database info with error handling
        try:
            db_info = await manager.get_database_info()
        except Exception as e:
            import logging
            logger = logging.getLogger("api")
            logger.error(f"Error getting database info: {str(e)}")
            db_info = {"error": str(e)}
        
        # Return status with safe attribute access
        return {
            "status": "operational",
            "database": db_info,
            "embedding_model": getattr(memory_system, "embedding_model", "unknown")
        }
    except Exception as e:
        # Log error but still return a valid response
        import logging
        logger = logging.getLogger("api")
        logger.error(f"Unexpected error in get_memory_status: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "embedding_model": getattr(memory_system, "embedding_model", "unknown") if memory_system else "unknown"
        }
