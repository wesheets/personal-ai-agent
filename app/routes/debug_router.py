"""
Debug Router Module

This module registers all debug-related routes with the FastAPI application.
"""

from fastapi import APIRouter
import logging
import os

# Configure logging
logger = logging.getLogger("debug")

# File existence check trap
if os.path.exists("/app/routes/status_debug.py"):
    print("🧠 status_debug.py file exists at runtime.")
    logger.info("🧠 status_debug.py file exists at runtime.")
else:
    print("🧠 status_debug.py file NOT found at runtime.")
    logger.warning("🧠 status_debug.py file NOT found at runtime.")

# Also check the local path
if os.path.exists("app/routes/status_debug.py"):
    print("🧠 status_debug.py file exists at local path.")
    logger.info("🧠 status_debug.py file exists at local path.")
else:
    print("🧠 status_debug.py file NOT found at local path.")
    logger.warning("🧠 status_debug.py file NOT found at local path.")

# Import the debug HAL schema router
from app.routes.debug_hal_schema import router as hal_schema_router
print("✅ Loaded debug_hal_schema_router")
logger.info("✅ Loaded debug_hal_schema_router")

# Try to import the debug status router
try:
    from app.routes.status_debug import router as status_router
    print("✅ Loaded status_debug_router")
    logger.info("✅ Loaded status_debug_router")
    status_router_loaded = True
except ImportError as e:
    print(f"⚠️ Could not load status_debug_router: {e}")
    logger.warning(f"⚠️ Could not load status_debug_router: {e}")
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
    print("✅ Included status_debug_router")
    logger.info("✅ Included status_debug_router")
else:
    # Fallback implementation if debug_status router is not available
    @router.get("/status")
    async def get_status():
        # Return the status of the debug module
        return {"status": "degraded", "module": "debug", "message": "Using fallback implementation"}
    print("⚠️ Using fallback debug_status implementation")
    logger.warning("⚠️ Using fallback debug_status implementation")
