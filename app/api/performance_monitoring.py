import logging
import time
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Performance"])
logger = logging.getLogger("api")

logger.info(f"🔍 Performance Monitoring module loaded")

@router.get("/debug/performance")
async def get_performance_metrics():
    """Get current performance metrics for the application."""
    return {
        "status": "active",
        "metrics": {
            "hal_route": {
                "request_body_timeout": "2.0 seconds",
                "processing_timeout": "5.0 seconds",
                "middleware_timeout": "10.0 seconds"
            },
            "monitoring": "Active with detailed timing logs"
        }
    }

@router.post("/debug/simulate-load")
async def simulate_load(request: Request, delay: float = 0):
    """
    Test endpoint that simulates processing load with configurable delay.
    
    Args:
        delay: Artificial delay in seconds to simulate processing time
    """
    start_time = time.time()
    logger.info(f"🔍 Load simulation started with delay={delay}s")
    
    try:
        # Parse request body
        body = await request.json()
        
        # Simulate processing delay
        if delay > 0:
            # Use non-blocking sleep
            await asyncio.sleep(delay)
        
        # Calculate metrics
        process_time = time.time() - start_time
        
        return {
            "status": "success",
            "metrics": {
                "requested_delay": delay,
                "actual_process_time": process_time,
                "timestamp": time.time()
            },
            "request": body
        }
    except Exception as e:
        logger.error(f"🔥 Error in load simulation: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Error in load simulation",
                "error": str(e),
                "process_time": time.time() - start_time
            }
        )
