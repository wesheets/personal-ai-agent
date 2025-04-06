from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.core.vector_memory import VectorMemorySystem
from app.db.supabase_manager import get_supabase_client

router = APIRouter()
memory_system = VectorMemorySystem()

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
        memory_id, warning = await memory_system.store_memory(
            content=request.content,
            metadata=request.metadata,
            priority=request.priority
        )
        
        response = {"message": "Memory added successfully", "memory_id": memory_id}
        
        # Add warning to response if present
        if warning:
            response["warning"] = warning
            
        return response
    except Exception as e:
        # Instead of raising an exception, log and return a graceful response
        import logging
        logger = logging.getLogger("memory_api")
        logger.error(f"[MEMORY FAILSAFE] Error in add_memory endpoint: {str(e)}")
        
        # Try to store without embedding as last resort
        try:
            # Add a note about the error to metadata
            metadata = request.metadata or {}
            metadata["error_note"] = f"Stored without embedding due to error: {str(e)}"
            
            # Store directly in database without embedding
            from app.db.supabase_manager import SupabaseManager
            manager = SupabaseManager()
            result = await manager.insert_record(
                table=memory_system.table_name,
                data={
                    "content": request.content,
                    "metadata": metadata,
                    "embedding": None,
                    "priority": request.priority
                }
            )
            
            return {
                "message": "Memory added with limitations",
                "memory_id": result["id"],
                "warning": "Memory stored without embedding due to backend error."
            }
        except Exception as inner_e:
            # If even the fallback fails, return a meaningful error but don't crash
            logger.error(f"[MEMORY FAILSAFE] Fallback storage also failed: {str(inner_e)}")
            return {
                "message": "Memory operation partially completed",
                "warning": "Unable to store memory properly due to backend errors."
            }

@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(
    request: MemorySearchRequest,
    supabase_client = Depends(get_supabase_client)
):
    """
    Search for memories similar to the query
    """
    try:
        results, warning = await memory_system.search_memories(
            query=request.query,
            limit=request.limit,
            priority_only=request.priority_only
        )
        
        response = MemorySearchResponse(
            results=results,
            metadata={
                "query": request.query,
                "limit": request.limit,
                "priority_only": request.priority_only,
                "result_count": len(results)
            }
        )
        
        # Add warning to response if present
        if warning:
            response.metadata["warning"] = warning
            
        return response
    except Exception as e:
        # Instead of raising an exception, return a graceful fallback response
        import logging
        logger = logging.getLogger("memory_api")
        logger.error(f"[MEMORY FAILSAFE] Error in search_memories endpoint: {str(e)}")
        
        # Get fallback memories
        from app.core.memory_api_quota_guard import get_quota_guard
        quota_guard = get_quota_guard()
        fallback_memories = quota_guard.get_fallback_memories(request.limit)
        
        return MemorySearchResponse(
            results=fallback_memories,
            metadata={
                "query": request.query,
                "limit": request.limit,
                "priority_only": request.priority_only,
                "result_count": len(fallback_memories),
                "warning": f"Memory search failed: {str(e)}"
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
        memory = await memory_system.get_memory_by_id(memory_id)
        
        if not memory:
            raise HTTPException(status_code=404, detail=f"Memory with ID {memory_id} not found")
        
        return memory
    except HTTPException:
        raise
    except Exception as e:
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
        from app.db.supabase_manager import SupabaseManager
        
        manager = SupabaseManager()
        db_info = await manager.get_database_info()
        
        # Check if OpenAI embeddings are working
        try:
            from app.core.memory_api_quota_guard import get_quota_guard
            quota_guard = get_quota_guard()
            test_embedding, warning = quota_guard.get_embedding_safe("test")
            
            if test_embedding is None:
                return {
                    "status": "degraded",
                    "database": db_info,
                    "embedding_model": "text-embedding-ada-002",
                    "embedding_status": "unavailable",
                    "warning": warning
                }
            else:
                return {
                    "status": "operational",
                    "database": db_info,
                    "embedding_model": "text-embedding-ada-002",
                    "embedding_status": "available"
                }
        except Exception as e:
            return {
                "status": "degraded",
                "database": db_info,
                "embedding_model": "text-embedding-ada-002",
                "embedding_status": "error",
                "warning": f"Error checking embedding status: {str(e)}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "warning": "Memory system status check failed"
        }
