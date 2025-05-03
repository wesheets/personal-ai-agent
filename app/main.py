from fastapi import FastAPI
import logging

# Import routers
from app.routes import loop_routes
from app.routes import debug_routes

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
app.include_router(debug_routes.router, prefix="/debug", tags=["Debug"])

@app.get("/healthz", tags=["System"])
async def health_check():
    return {"status": "ok"}

logger.info("✅ FastAPI application initialized.")
logger.info("✅ Loop routes loaded.")
logger.info("✅ Debug routes loaded.")


from app.core.loop_controller import LoopController


# Placeholder for LoopController instantiation (Batch 15.31)
controller = LoopController()
logger.info("✅ LoopController scaffold instantiated (Placeholder).")


# Placeholder for LoopController invocation (Batch 15.31)
# controller.start_loop() # Commented out for safety in zero-drift phase
logger.info("ℹ️ LoopController.start_loop() placeholder invocation skipped (Zero-Drift Phase).")
