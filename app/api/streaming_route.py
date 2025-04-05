from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
import logging
import inspect
import time
import asyncio
import json
from typing import Dict, Any, AsyncGenerator

router = APIRouter()
logger = logging.getLogger("api")

# Debug logging for route registration
logger.info(f"📡 Streaming Router module loaded from {__file__}")
logger.info(f"📡 Streaming Router object created: {router}")

# Streaming response generator
async def stream_response(request: Request) -> AsyncGenerator[bytes, None]:
    """
    Stream the response to avoid buffering the entire response in memory.
    This helps with large payloads and improves response time perception.
    """
    start_time = time.time()
    logger.info(f"🔄 Starting streaming response at {start_time}")
    
    # Stream the response header
    yield b'{"status":"streaming","message":"Processing request"}\n'
    
    # Get the request body
    try:
        # Use pre-parsed body from middleware if available
        if hasattr(request.state, "body"):
            body = request.state.body
        else:
            # Parse body directly if not pre-parsed
            raw_body = await request.body()
            body = json.loads(raw_body.decode())
        
        # Stream progress updates
        yield b'{"status":"progress","message":"Request body parsed successfully"}\n'
        await asyncio.sleep(0.1)  # Small delay to ensure client receives updates
        
        # Process the request (simulated)
        yield b'{"status":"progress","message":"Processing HAL request"}\n'
        await asyncio.sleep(0.1)
        
        # Stream the final response
        response_data = {
            "status": "success",
            "agent": "HAL9000",
            "message": "I'm sorry, Dave. I'm afraid I can't do that.",
            "received": body,
            "processing_time": time.time() - start_time
        }
        
        yield f'{json.dumps(response_data)}\n'.encode()
        logger.info(f"🔄 Streaming response completed in {time.time() - start_time:.4f}s")
        
    except Exception as e:
        # Stream error response
        error_data = {
            "status": "error",
            "message": "Error processing request",
            "error": str(e),
            "time": time.time() - start_time
        }
        yield f'{json.dumps(error_data)}\n'.encode()
        logger.error(f"🔥 Streaming error: {str(e)}")

@router.post("/agent/delegate-stream")
async def delegate_stream(request: Request):
    """
    Streaming version of the delegate endpoint.
    This endpoint streams the response back to the client, which helps with:
    1. Avoiding request timeouts by sending data incrementally
    2. Providing immediate feedback to the client
    3. Reducing memory usage for large responses
    """
    logger.info(f"🔄 Streaming HAL delegate route executed")
    
    return StreamingResponse(
        stream_response(request),
        media_type="application/x-ndjson"
    )
