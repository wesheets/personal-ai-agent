from fastapi import APIRouter, Request
import logging
from fastapi.routing import APIRoute
import inspect
import time
import asyncio
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Debug"])
logger = logging.getLogger("api")

logger.info(f"🔍 Debug Routes module loaded from {__file__}")

@router.get("/debug/routes")
async def list_routes(request: Request):
    """List all registered routes in the application."""
    logger.info("🔍 Debug routes endpoint called")
    app = request.app
    routes_info = []
    
    for route in app.routes:
        if isinstance(route, APIRoute):
            try:
                source_file = inspect.getsourcefile(route.endpoint)
            except (TypeError, ValueError):
                source_file = "Unknown"
                
            routes_info.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route.endpoint, "__name__", "unknown"),
                "source": source_file
            })
    
    logger.info(f"🔍 Found {len(routes_info)} routes")
    return {"routes": routes_info}

@router.get("/debug/hal-status")
async def hal_status():
    """Check the status of the HAL delegate route."""
    logger.info("🔍 HAL status check endpoint called")
    try:
        from app.api.delegate_route import router as hal_router
        routes = [
            {"path": route.path, "methods": list(route.methods)}
            for route in hal_router.routes
        ]
        return {
            "status": "available",
            "routes": routes,
            "module_path": inspect.getsourcefile(hal_router),
            "route_count": len(hal_router.routes)
        }
    except Exception as e:
        logger.error(f"🔥 Error checking HAL status: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/debug/middleware-timing")
async def middleware_timing():
    """Monitor middleware timing and performance."""
    logger.info("🔍 Middleware timing endpoint called")
    return {
        "status": "active",
        "middleware": {
            "log_requests": {
                "body_read_timeout": "3.0 seconds",
                "request_timeout": "10.0 seconds",
                "status": "enabled"
            }
        },
        "monitoring": "Use X-Process-Time header in responses to track request processing time"
    }

@router.post("/debug/test-timeout")
async def test_timeout(request: Request, delay: float = 0):
    """Test endpoint that simulates a delay to test timeout handling."""
    logger.info(f"🔍 Test timeout endpoint called with delay={delay}")
    
    try:
        # Simulate processing delay
        if delay > 0:
            await asyncio.sleep(delay)
            
        # Read and return the request body
        body = await request.json()
        return {
            "status": "success",
            "message": f"Request processed after {delay} seconds",
            "received": body,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"🔥 Error in test timeout endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Error processing request",
                "error": str(e)
            }
        )
