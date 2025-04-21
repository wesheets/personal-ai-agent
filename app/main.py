"""
Main Application Module

This module serves as the entry point for the Promethios API.
It initializes all required components and starts the server.
"""

import os
import sys
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")

# Create FastAPI app
app = FastAPI(
    title="Promethios API",
    description="API for the Promethios cognitive system",
    version="1.0.0",
    docs_url=None,  # We'll create a custom docs endpoint
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.routes.core_routes import router as core_router
from app.routes.loop_routes import router as loop_router
from app.routes.agent_routes import router as agent_router
from app.routes.persona_routes import router as persona_router
from app.routes import debug_routes

# Include routers with correct prefixes (no /api/ prefix)
app.include_router(core_router)
app.include_router(loop_router)
app.include_router(agent_router)
app.include_router(persona_router)
app.include_router(debug_routes.router)

# Custom docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Promethios API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/")
async def root():
    """
    Root endpoint that returns basic API information.
    """
    return {
        "name": "Promethios API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint that returns the API status.
    """
    return {"status": "ok"}

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
