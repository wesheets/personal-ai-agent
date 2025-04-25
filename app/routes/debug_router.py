from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
import logging

# Import the debug HAL schema router
from app.routes.debug_hal_schema import router as hal_schema_router

# Configure logging
logger = logging.getLogger("debug")

# Create router
router = APIRouter(tags=["debug"])

# Include the HAL schema debug router
router.include_router(hal_schema_router)

@router.get("/debug/status")
async def get_status():
    # Return the status of the debug module
    return {"status": "operational", "module": "debug"}
