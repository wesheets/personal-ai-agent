"""
Memory Recall Routes

This module defines the FastAPI routes for memory recall operations.
"""

from fastapi import APIRouter, HTTPException, Body, Query
from typing import Dict, Any, Optional

from app.modules.memory_recall import recall_memory
from app.schemas.memory_recall_schema import (
    MemoryRecallRequest,
    MemoryRecallResponse,
    MemoryRecallError,
    RecallMethod,
    RecallSortOrder
)

# Create router
router = APIRouter(
    prefix="/api/memory",
    tags=["memory"],
    responses={404: {"description": "Not found"}},
)

@router.post("/recall", response_model=MemoryRecallResponse)
async def recall_memory_endpoint(request: MemoryRecallRequest = Body(...)):
    """
    Recall memory entries based on the provided criteria.
    
    This endpoint allows searching memory using tags, keywords, semantic similarity, or temporal filters.
    
    Args:
        request: Memory recall request
        
    Returns:
        Memory recall response
    """
    try:
        result = recall_memory(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = MemoryRecallError(
            message=f"Error recalling memory: {str(e)}",
            query=request.query,
            method=request.method
        )
        return error_response

@router.get("/recall", response_model=MemoryRecallResponse)
async def recall_memory_get_endpoint(
    query: str,
    method: RecallMethod = RecallMethod.TAG,
    limit: int = 10,
    offset: int = 0,
    sort_order: RecallSortOrder = RecallSortOrder.NEWEST_FIRST,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    agent_filter: Optional[str] = None,
    loop_filter: Optional[str] = None
):
    """
    Recall memory entries based on the provided criteria using GET parameters.
    
    This endpoint allows searching memory using tags, keywords, semantic similarity, or temporal filters.
    
    Args:
        query: Query string for memory recall
        method: Method to use for memory recall
        limit: Maximum number of results to return
        offset: Offset for pagination
        sort_order: Sort order for results
        start_date: ISO timestamp for start date filter (inclusive)
        end_date: ISO timestamp for end date filter (inclusive)
        agent_filter: Filter results by agent ID
        loop_filter: Filter results by loop ID
        
    Returns:
        Memory recall response
    """
    try:
        request_data = {
            "query": query,
            "method": method,
            "limit": limit,
            "offset": offset,
            "sort_order": sort_order,
            "start_date": start_date,
            "end_date": end_date,
            "agent_filter": agent_filter,
            "loop_filter": loop_filter
        }
        
        result = recall_memory(request_data)
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = MemoryRecallError(
            message=f"Error recalling memory: {str(e)}",
            query=query,
            method=method
        )
        return error_response
