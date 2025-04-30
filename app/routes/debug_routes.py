from fastapi import APIRouter
import logging

# Configure logging
logger = logging.getLogger("app.routes.debug_routes")

router = APIRouter()

@router.get("/status", tags=["Debug"])
async def get_debug_status():
    """Returns a simple status message for debugging purposes."""
    logger.info("GET /debug/status requested.")
    return {"status": "ok", "message": "Debug endpoint active."}

logger.info("✅ Debug routes initialized.")

