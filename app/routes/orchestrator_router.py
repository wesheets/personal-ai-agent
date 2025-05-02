"""
Orchestrator Router Module

This module provides a router for orchestrator-related endpoints.
"""
from fastapi import APIRouter
import logging

# Configure logging
logger = logging.getLogger("app.routes.orchestrator_router")

# Create router
router = APIRouter(tags=["orchestrator"])

# Import orchestrator routes
try:
    from app.routes.orchestrator_routes import router as orchestrator_routes_router
    router.include_router(orchestrator_routes_router)
    logger.info("✅ Loaded orchestrator routes")
except Exception as e:
    logger.error(f"❌ Failed to load orchestrator routes: {str(e)}")
    
    # Fallback endpoint
    @router.get("/api/orchestrator/status")
    async def orchestrator_status_fallback():
        """
        Fallback status endpoint for orchestrator.
        """
        return {
            "status": "degraded",
            "message": "Orchestrator running in fallback mode due to loading errors",
            "error": str(e)
        }
