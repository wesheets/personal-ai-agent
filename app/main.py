"""
Main Application Module

This module serves as the entry point for the application.
It initializes all required components and starts the server.

MODIFIED: Added agent registry initialization
MODIFIED: Added loop router registration
"""

import os
import sys
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")

# Create FastAPI app
app = FastAPI(title="Personal AI Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and initialize agent registry
from app.modules.agent_registry import list_agents
from app.modules.register_all_agents import register_all_agents

# Register all agents
register_all_agents()
print("✅ Registered agents:", list_agents())

# Import routers
from routes.agent_routes import router as agent_router
from routes.system_routes import router as system_router
from routes.project_routes import router as project_router
from routes.orchestrator_routes import router as orchestrator_router
from routes.debug_routes import router as debug_router
from routes.loop_routes import router as loop_router

# Include routers
app.include_router(agent_router, prefix="/api/agent", tags=["agent"])
app.include_router(system_router, prefix="/api/system", tags=["system"])
app.include_router(project_router, prefix="/api/project", tags=["project"])
app.include_router(orchestrator_router, prefix="/api/orchestrator", tags=["orchestrator"])
app.include_router(debug_router, prefix="/api/debug", tags=["debug"])
app.include_router(loop_router, prefix="/api/loop", tags=["loop"])

@app.get("/")
async def root():
    """
    Root endpoint that returns basic API information.
    """
    return {
        "name": "Personal AI Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/agent",
            "/api/system",
            "/api/project",
            "/api/orchestrator",
            "/api/debug",
            "/api/loop"
        ]
    }

@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for all unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": f"An unexpected error occurred: {str(exc)}",
            "path": request.url.path
        }
    )

# Run the application if executed directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
