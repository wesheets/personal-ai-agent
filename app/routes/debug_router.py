"""
Debug Router Module
fix/debug-status-endpoint-deployment

This module registers all debug-related routes with the FastAPI application.
"""

from fastapi import APIRouter
import logging

# Configure logging
logger = logging.getLogger("debug")

# Import the debug HAL schema router
from app.routes.debug_hal_schema import router as hal_schema_router
print("✅ Loaded debug_hal_schema_router")
logger.info("✅ Loaded debug_hal_schema_router")

# Try to import the debug status router
try:
    from app.routes.debug_status import router as status_router
    print("✅ Loaded debug_status_router")
    logger.info("✅ Loaded debug_status_router")
    status_router_loaded = True
except ImportError as e:
    print(f"⚠️ Could not load debug_status_router: {e}")
    logger.warning(f"⚠️ Could not load debug_status_router: {e}")
    status_router_loaded = False

# Create router
router = APIRouter(
    prefix="/debug",
    tags=["debug"],
    responses={404: {"description": "Not found"}}
)

# Include the HAL schema debug router
router.include_router(hal_schema_router, prefix="")
print("✅ Included debug_hal_schema_router")
logger.info("✅ Included debug_hal_schema_router")

# Include the debug status router if loaded
if status_router_loaded:
    router.include_router(status_router, prefix="")
    print("✅ Included debug_status_router")
    logger.info("✅ Included debug_status_router")
else:
    # Fallback implementation if debug_status router is not available
    @router.get("/status")
    async def get_status():
        # Return the status of the debug module
        return {"status": "degraded", "module": "debug", "message": "Using fallback implementation"}
    print("⚠️ Using fallback debug_status implementation")
    logger.warning("⚠️ Using fallback debug_status implementation")


This module registers all debug-related routes with the FastAPI application.
"""

from fastapi import APIRouter

# Import debug routes
from app.routes.debug_status import router as status_router
from app.routes.debug_hal_schema import router as hal_schema_router

# Create main debug router
router = APIRouter(
    prefix="/debug",
    tags=["debug"],
    responses={404: {"description": "Not found"}}
)

# Include all debug-related routers
router.include_router(status_router, prefix="")
router.include_router(hal_schema_router, prefix="")
main
