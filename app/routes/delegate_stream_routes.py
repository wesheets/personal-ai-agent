"""
Delegate Stream Routes

This module defines the FastAPI routes for creating and managing delegate streams.
"""

from fastapi import APIRouter, HTTPException, Body, Query, Path, WebSocket, WebSocketDisconnect
from typing import Dict, Any, Optional

from app.modules.delegate_stream import create_stream, get_stream_status, close_stream
from app.schemas.delegate_stream_schema import (
    StreamRequest,
    StreamResponse,
    StreamError,
    StreamStatusRequest,
    StreamStatusResponse,
    StreamCloseRequest,
    StreamCloseResponse,
    StreamType,
    StreamPriority
)

# Create router
router = APIRouter(
    prefix="/api/delegate/stream",
    tags=["delegate_stream"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=StreamResponse)
async def create_stream_endpoint(request: StreamRequest = Body(...)):
    """
    Create a delegate stream based on the provided parameters.
    
    This endpoint initiates a stream for the specified target and type.
    
    Args:
        request: Stream request
        
    Returns:
        Stream response with stream ID and connection details
    """
    try:
        result = create_stream(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = StreamError(
            message=f"Error creating stream: {str(e)}",
            stream_type=request.stream_type,
            target_id=request.target_id
        )
        return error_response

@router.get("/status/{stream_id}", response_model=StreamStatusResponse)
async def get_stream_status_endpoint(
    stream_id: str = Path(..., description="Unique identifier for the stream")
):
    """
    Get the status of a stream.
    
    This endpoint returns the current status, events streamed, and details of a stream.
    
    Args:
        stream_id: Unique identifier for the stream
        
    Returns:
        Stream status response
    """
    try:
        request_data = {"stream_id": stream_id}
        result = get_stream_status(request_data)
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=404 if "not found" in result["message"].lower() else 400,
                detail=result["message"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stream status: {str(e)}"
        )

@router.post("/status", response_model=StreamStatusResponse)
async def check_stream_status_endpoint(request: StreamStatusRequest = Body(...)):
    """
    Check the status of a stream using POST.
    
    This endpoint returns the current status, events streamed, and details of a stream.
    
    Args:
        request: Stream status request
        
    Returns:
        Stream status response
    """
    try:
        result = get_stream_status(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=404 if "not found" in result["message"].lower() else 400,
                detail=result["message"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_response = StreamError(
            message=f"Error checking stream status: {str(e)}"
        )
        return error_response

@router.post("/close", response_model=StreamCloseResponse)
async def close_stream_endpoint(request: StreamCloseRequest = Body(...)):
    """
    Close a stream.
    
    This endpoint closes a previously created stream.
    
    Args:
        request: Stream close request
        
    Returns:
        Stream close response
    """
    try:
        result = close_stream(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=404 if "not found" in result["message"].lower() else 400,
                detail=result["message"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_response = StreamError(
            message=f"Error closing stream: {str(e)}"
        )
        return error_response

@router.websocket("/ws/{stream_id}")
async def websocket_endpoint(websocket: WebSocket, stream_id: str):
    """
    WebSocket endpoint for connecting to a stream.
    
    This endpoint allows clients to connect to a stream and receive events in real-time.
    
    Args:
        websocket: WebSocket connection
        stream_id: Unique identifier for the stream
    """
    from app.modules.delegate_stream import handle_stream_connection
    
    await websocket.accept()
    try:
        await handle_stream_connection(websocket, f"/streams/{stream_id}")
    except WebSocketDisconnect:
        pass
