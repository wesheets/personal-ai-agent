"""
Debug Router Module

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
