from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.core.memory_manager import MemoryManager
from app.db.database import get_database

router = APIRouter()
memory_manager = MemoryManager()

class MemoryStoreRequest(BaseModel):
    input: str
    output: str
    metadata: Optional[Dict[str, Any]] = None

class MemoryQueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class MemoryItem(BaseModel):
    id: str
    input: str
    output: str
    metadata: Dict[str, Any]
    timestamp: str

class MemoryQueryResponse(BaseModel):
    results: List[MemoryItem]
    metadata: Dict[str, Any]

@router.post("/store", status_code=201)
async def store_memory(request: MemoryStoreRequest, db=Depends(get_database)):
    """
    Store an interaction in the memory system
    """
    try:
        memory_id = await memory_manager.store(
            input_text=request.input,
            output_text=request.output,
            metadata=request.metadata
        )
        
        return {"message": "Memory stored successfully", "memory_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing memory: {str(e)}")

@router.post("/query", response_model=MemoryQueryResponse)
async def query_memory(request: MemoryQueryRequest, db=Depends(get_database)):
    """
    Query the memory system for relevant past interactions
    """
    try:
        results = await memory_manager.query(
            query=request.query,
            limit=request.limit
        )
        
        return MemoryQueryResponse(
            results=results,
            metadata={
                "query": request.query,
                "limit": request.limit,
                "result_count": len(results)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying memory: {str(e)}")

@router.get("/item/{memory_id}", response_model=MemoryItem)
async def get_memory_item(memory_id: str, db=Depends(get_database)):
    """
    Get a specific memory item by ID
    """
    try:
        memory_item = await memory_manager.get_by_id(memory_id)
        
        if not memory_item:
            raise HTTPException(status_code=404, detail=f"Memory item with ID {memory_id} not found")
        
        return memory_item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory item: {str(e)}")

@router.delete("/item/{memory_id}", status_code=204)
async def delete_memory_item(memory_id: str, db=Depends(get_database)):
    """
    Delete a specific memory item by ID
    """
    try:
        success = await memory_manager.delete(memory_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Memory item with ID {memory_id} not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting memory item: {str(e)}")

@router.get("/stats", response_model=Dict[str, Any])
async def get_memory_stats(db=Depends(get_database)):
    """
    Get statistics about the memory system
    """
    try:
        # This is a placeholder for actual statistics
        # In a real implementation, this would query the database for statistics
        return {
            "total_memories": len(memory_manager.memories),
            "agent_counts": {
                "builder": sum(1 for m in memory_manager.memories if m.get("metadata", {}).get("agent") == "builder"),
                "ops": sum(1 for m in memory_manager.memories if m.get("metadata", {}).get("agent") == "ops"),
                "research": sum(1 for m in memory_manager.memories if m.get("metadata", {}).get("agent") == "research")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory stats: {str(e)}")
