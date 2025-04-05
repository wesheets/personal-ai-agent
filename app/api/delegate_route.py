from fastapi import APIRouter, Request, Body, Depends
from fastapi.responses import JSONResponse
import logging
import inspect
import time
import asyncio
import json
from typing import Dict, Any, Optional

router = APIRouter()
logger = logging.getLogger("api")

# Debug logging for route registration
logger.info(f"📡 HAL Router module loaded from {__file__}")
logger.info(f"📡 HAL Router object created: {router}")

# Performance tracking
async def process_hal_request(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process HAL request with performance tracking.
    This function simulates the actual processing that would happen in a real HAL implementation.
    """
    start_time = time.time()
    
    # Log the start of processing
    logger.info(f"🧠 HAL processing started at {start_time}")
    
    # Return standard HAL response
    response = {
        "status": "success",
        "agent": "HAL9000",
        "message": "I'm sorry, Dave. I'm afraid I can't do that.",
        "received": body,
        "processing_time": time.time() - start_time
    }
    
    logger.info(f"🧠 HAL processing completed in {response['processing_time']:.4f}s")
    return response

# Helper function to extract pre-parsed body from request state
async def get_request_body(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get the request body, either from pre-parsed state or by parsing it directly.
    This avoids double-parsing issues between middleware and route handler.
    """
    # Check if body was already parsed by middleware
    if hasattr(request.state, "body"):
        logger.info("🧠 Using pre-parsed body from request state")
        return request.state.body
    
    # If not pre-parsed, try to parse it directly with a longer timeout
    try:
        # Use raw body if available
        if hasattr(request, "_body") and request._body:
            logger.info("🧠 Using cached raw body")
            body_str = request._body.decode()
            return json.loads(body_str)
        
        # Last resort: parse directly with increased timeout
        logger.info("🧠 Parsing body directly with increased timeout")
        raw_body = await asyncio.wait_for(request.body(), timeout=8.0)
        body_str = raw_body.decode()
        return json.loads(body_str)
    except json.JSONDecodeError as e:
        logger.error(f"🔥 JSON decode error: {str(e)}")
        raise ValueError(f"Invalid JSON: {str(e)}")
    except asyncio.TimeoutError:
        logger.error("🔥 Timeout while parsing request body")
        raise TimeoutError("Request body parsing timed out")
    except Exception as e:
        logger.error(f"🔥 Error parsing request body: {str(e)}")
        raise ValueError(f"Error parsing request body: {str(e)}")

@router.post("/agent/delegate")
async def delegate(request: Request):
    try:
        # Log route execution with timing
        start_time = time.time()
        logger.info(f"🧠 HAL delegate route executed from {inspect.currentframe().f_code.co_filename}")
        
        # Parse request body with optimized approach
        try:
            body = await get_request_body(request)
            body_time = time.time() - start_time
            logger.info(f"🧠 HAL received a task (parsed in {body_time:.4f}s)")
        except TimeoutError:
            logger.error("🔥 HAL delegate timeout while parsing request body")
            return JSONResponse(status_code=408, content={
                "status": "error",
                "message": "Request body parsing timed out",
                "error": "Timeout while reading request body"
            })
        except ValueError as e:
            logger.error(f"🔥 HAL delegate error parsing request body: {str(e)}")
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": "Invalid request body",
                "error": str(e)
            })
        
        # Process the request with timeout
        try:
            response_data = await asyncio.wait_for(
                process_hal_request(body), 
                timeout=8.0  # Increased timeout for processing
            )
            
            # Add overall timing information
            total_time = time.time() - start_time
            response_data["total_time"] = total_time
            logger.info(f"🧠 HAL delegate total execution time: {total_time:.4f}s")
            
            return JSONResponse(content=response_data)
        except asyncio.TimeoutError:
            logger.error("🔥 HAL delegate timeout during request processing")
            return JSONResponse(status_code=504, content={
                "status": "error",
                "message": "HAL processing timed out",
                "error": "Timeout during request processing"
            })
            
    except Exception as e:
        # Log the error with timing information
        error_time = time.time() - start_time
        logger.error(f"🔥 HAL delegate error after {error_time:.4f}s: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "HAL encountered an unexpected failure.",
            "error": str(e)
        })
