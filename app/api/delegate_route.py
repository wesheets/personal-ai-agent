from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
import inspect
import time
import asyncio
from typing import Dict, Any

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

@router.post("/agent/delegate")
async def delegate(request: Request):
    try:
        # Log route execution with timing
        start_time = time.time()
        logger.info(f"🧠 HAL delegate route executed from {inspect.currentframe().f_code.co_filename}")
        
        # Parse request body with timeout
        try:
            body = await asyncio.wait_for(request.json(), timeout=2.0)
            body_time = time.time() - start_time
            logger.info(f"🧠 HAL received a task: {body} (parsed in {body_time:.4f}s)")
        except asyncio.TimeoutError:
            logger.error("🔥 HAL delegate timeout while parsing request body")
            return JSONResponse(status_code=408, content={
                "status": "error",
                "message": "Request body parsing timed out",
                "error": "Timeout while reading request body"
            })
        
        # Process the request with timeout
        try:
            response_data = await asyncio.wait_for(
                process_hal_request(body), 
                timeout=5.0
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
