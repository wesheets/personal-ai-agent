from fastapi import FastAPI
import logging

# Import routers
from app.routes import loop_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")

app = FastAPI(
    title="Personal AI Agent - Rebuilt Cognition",
    description="Rebuilt core components based on Batch 12.2 directive.",
    version="12.2.0"
)

# Include routers
app.include_router(loop_routes.router, prefix="/api/loop", tags=["Loop Execution"])

@app.get("/healthz", tags=["System"])
async def health_check():
    return {"status": "ok"}

logger.info("✅ FastAPI application initialized.")
logger.info("✅ Loop routes loaded.")

