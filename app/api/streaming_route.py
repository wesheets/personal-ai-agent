from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
import logging
import inspect
import time
import asyncio
import json
from typing import Dict, Any, AsyncGenerator, List

# Import AGENT_PERSONALITIES from delegate_route
from app.api.delegate_route import AGENT_PERSONALITIES

router = APIRouter()
logger = logging.getLogger("api")

# Debug logging for route registration
logger.info(f"📡 Streaming Router module loaded from {__file__}")
logger.info(f"📡 Streaming Router object created: {router}")

# Enhanced processing stages for more detailed progress updates
PROCESSING_STAGES = [
    {"status": "initializing", "message": "Initializing agent systems"},
    {"status": "analyzing", "message": "Analyzing request parameters"},
    {"status": "processing", "message": "Processing request data"},
    {"status": "thinking", "message": "Formulating response"},
    {"status": "finalizing", "message": "Finalizing agent response"}
]

# Streaming response generator with enhanced progress reporting
async def stream_response(request: Request) -> AsyncGenerator[bytes, None]:
    """
    Stream the response to avoid buffering the entire response in memory.
    This helps with large payloads and improves response time perception.
    Enhanced with detailed progress updates and better error handling.
    """
    start_time = time.time()
    logger.info(f"🔄 Starting streaming response at {start_time}")
    
    # Stream the response header with metadata
    yield json.dumps({
        "status": "streaming",
        "message": "Processing request",
        "timestamp": time.time(),
        "metadata": {
            "request_id": f"agent-{int(start_time)}",
            "stream_type": "ndjson"
        }
    }).encode() + b'\n'
    
    # Get the request body with enhanced error handling
    try:
        body = None
        body_parse_start = time.time()
        
        # Use pre-parsed body from middleware if available
        if hasattr(request.state, "body"):
            body = request.state.body
            logger.info("🔄 Using pre-parsed body from middleware")
        elif hasattr(request, "_body") and request._body:
            # Use cached raw body if available
            body_str = request._body.decode()
            body = json.loads(body_str)
            logger.info("🔄 Using cached raw body")
        else:
            # Parse body directly with timeout if not pre-parsed
            try:
                raw_body = await asyncio.wait_for(request.body(), timeout=15.0)
                body = json.loads(raw_body.decode())
                logger.info("🔄 Parsed body directly with timeout")
            except asyncio.TimeoutError:
                yield json.dumps({
                    "status": "error",
                    "message": "Request body parsing timed out",
                    "error": "Timeout while reading request body",
                    "time": time.time() - start_time
                }).encode() + b'\n'
                logger.error("🔥 Timeout while parsing request body")
                return
            except json.JSONDecodeError as e:
                yield json.dumps({
                    "status": "error",
                    "message": "Invalid JSON in request body",
                    "error": str(e),
                    "time": time.time() - start_time
                }).encode() + b'\n'
                logger.error(f"🔥 JSON decode error: {str(e)}")
                return
        
        # Stream body parsing success with timing
        body_parse_time = time.time() - body_parse_start
        yield json.dumps({
            "status": "progress",
            "stage": "body_parsed",
            "message": f"Request body parsed successfully in {body_parse_time:.4f}s",
            "timestamp": time.time(),
            "elapsed": time.time() - start_time
        }).encode() + b'\n'
        
        # Get agent_id from request body and look up personality
        agent_id = body.get("agent_id", "").lower() if body else ""
        personality = AGENT_PERSONALITIES.get(agent_id)
        
        # Log agent selection
        if personality:
            logger.info(f"🤖 Selected agent personality: {agent_id} ({personality['name']})")
        else:
            logger.warning(f"⚠️ Unknown agent_id requested: {agent_id}")
        
        # Process the request with detailed progress updates
        for i, stage in enumerate(PROCESSING_STAGES):
            # Calculate dynamic delay based on stage complexity
            # Earlier stages are faster, later stages take more time
            stage_delay = 0.2 * (i + 1)
            
            # Stream progress update for this stage
            yield json.dumps({
                "status": "progress",
                "stage": stage["status"],
                "message": stage["message"],
                "progress": (i + 1) / len(PROCESSING_STAGES) * 100,
                "timestamp": time.time(),
                "elapsed": time.time() - start_time
            }).encode() + b'\n'
            
            # Simulate processing with backpressure handling
            await asyncio.sleep(stage_delay)
        
        # Prepare the final response with enhanced metadata
        processing_time = time.time() - start_time
        
        # Use the appropriate personality response based on agent_id
        if personality:
            response_data = {
                "status": "success",
                "agent": personality["name"],
                "message": personality["message"],
                "tone": personality["tone"],
                "received": body,
                "processing": {
                    "total_time": processing_time,
                    "body_parse_time": body_parse_time,
                    "processing_time": processing_time - body_parse_time,
                    "stages_completed": len(PROCESSING_STAGES),
                    "timestamp": time.time()
                }
            }
        else:
            # Default response for unknown agent_id
            response_data = {
                "status": "success",
                "agent": agent_id or "unknown",
                "message": "No personality assigned. Executing generic protocol.",
                "tone": "neutral",
                "received": body,
                "processing": {
                    "total_time": processing_time,
                    "body_parse_time": body_parse_time,
                    "processing_time": processing_time - body_parse_time,
                    "stages_completed": len(PROCESSING_STAGES),
                    "timestamp": time.time()
                }
            }
        
        # Stream the final response
        yield json.dumps(response_data).encode() + b'\n'
        logger.info(f"🔄 Streaming response completed in {processing_time:.4f}s for agent: {agent_id}")
        
    except Exception as e:
        # Enhanced error response with detailed diagnostics
        error_time = time.time() - start_time
        error_data = {
            "status": "error",
            "message": "Error processing request",
            "error": str(e),
            "error_type": type(e).__name__,
            "diagnostics": {
                "time": error_time,
                "timestamp": time.time(),
                "request_path": str(request.url.path),
                "error_location": inspect.currentframe().f_code.co_name
            }
        }
        yield json.dumps(error_data).encode() + b'\n'
        logger.error(f"🔥 Streaming error after {error_time:.4f}s: {str(e)}")

@router.post("/agent/delegate-stream")
async def delegate_stream(request: Request):
    """
    Enhanced streaming version of the delegate endpoint.
    This endpoint streams the response back to the client, which helps with:
    1. Avoiding request timeouts by sending data incrementally
    2. Providing immediate feedback to the client
    3. Reducing memory usage for large responses
    4. Handling complex operations with detailed progress updates
    
    Supports multiple agent personalities based on agent_id parameter:
    - hal9000: HAL 9000 with calm tone
    - ash-xenomorph: Ash with clinical tone
    """
    logger.info(f"🔄 Streaming delegate route executed from {inspect.currentframe().f_code.co_filename}")
    
    # Return streaming response with enhanced headers
    return StreamingResponse(
        stream_response(request),
        media_type="application/x-ndjson",
        headers={
            "X-Streaming-Mode": "enabled",
            "X-Agent-Version": "1.0.0",
            "Cache-Control": "no-cache"
        }
    )
