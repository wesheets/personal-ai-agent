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
        memory_id = await memory_system.store_memory(
            content=request.content,
            metadata=request.metadata,
            priority=request.priority
        )
        
        return {"message": "Memory added successfully", "memory_id": memory_id}
    except Exception as e:
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
        results = await memory_system.search_memories(
            query=request.query,
            limit=request.limit,
            priority_only=request.priority_only
        )
        
        return MemorySearchResponse(
            results=results,
            metadata={
                "query": request.query,
                "limit": request.limit,
                "priority_only": request.priority_only,
                "result_count": len(results)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching memories: {str(e)}")

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
        
        return {
            "status": "operational",
            "database": db_info,
            "embedding_model": memory_system.embedding_model
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
