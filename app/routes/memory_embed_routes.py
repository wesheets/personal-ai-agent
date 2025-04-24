"""
Memory Embed Routes

This module defines the FastAPI routes for memory embedding operations.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

from app.modules.memory_embed import embed_memory, embed_memory_batch
from app.schemas.memory_embed_schema import (
    MemoryEmbedRequest,
    MemoryEmbedResponse,
    MemoryEmbedError,
    MemoryEmbedBatchRequest,
    MemoryEmbedBatchResponse
)

# Create router
router = APIRouter(
    prefix="/api/memory",
    tags=["memory"],
    responses={404: {"description": "Not found"}},
)

@router.post("/embed", response_model=MemoryEmbedResponse)
async def embed_memory_endpoint(request: MemoryEmbedRequest = Body(...)):
    """
    Embed content for vector-based retrieval.
    
    This endpoint creates vector embeddings for content to enable semantic search.
    
    Args:
        request: Memory embed request
        
    Returns:
        Memory embed response
    """
    try:
        result = embed_memory(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = MemoryEmbedError(
            message=f"Error embedding memory: {str(e)}",
            model=request.model
        )
        return error_response

@router.post("/embed/batch", response_model=MemoryEmbedBatchResponse)
async def embed_memory_batch_endpoint(request: MemoryEmbedBatchRequest = Body(...)):
    """
    Embed multiple content items for vector-based retrieval.
    
    This endpoint creates vector embeddings for multiple content items in a single request.
    
    Args:
        request: Memory embed batch request
        
    Returns:
        Memory embed batch response
    """
    try:
        result = embed_memory_batch(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = {
            "results": [],
            "errors": [{"message": f"Error embedding memory batch: {str(e)}"}],
            "total_items": len(request.items),
            "successful_items": 0,
            "timestamp": None,  # Will be set by Pydantic
            "version": "1.0.0"
        }
        return error_response
