from fastapi import APIRouter, Request
import logging
from fastapi.routing import APIRoute
import inspect

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
