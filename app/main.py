"""
Main application module for the Promethios API.

This module initializes the FastAPI application and includes all routes.
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import os
import json

# Import routers
from app.routes.core_routes import router as core_router
from app.routes.loop_routes import router as loop_router
from app.routes.agent_routes import router as agent_router
from app.routes.persona_routes import router as persona_router
from app.routes.debug_routes import router as debug_router
from app.routes.orchestrator_routes import router as orchestrator_router
from app.routes.reflection_routes import router as reflection_router
from app.routes.trust_routes import router as trust_router
from app.routes.self_routes import router as self_router

# Import memory module
from app.memory.project_memory import PROJECT_MEMORY

# Create FastAPI app
app = FastAPI(
    title="Promethios API",
    description="API for the Promethios cognitive system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers
app.include_router(core_router)
app.include_router(loop_router, prefix="/api")
app.include_router(agent_router)
app.include_router(persona_router)
app.include_router(debug_router)
app.include_router(orchestrator_router)
app.include_router(reflection_router)
app.include_router(trust_router)
app.include_router(self_router, prefix="/self")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Promethios API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Schema injection test endpoint
@app.get("/schema-injection-test")
async def schema_injection_test():
    """
    Test endpoint for schema injection.
    """
    return {
        "schema_loaded": True,
        "memory_initialized": PROJECT_MEMORY is not None,
        "routes_registered": [
            "core_routes",
            "loop_routes",
            "agent_routes",
            "persona_routes",
            "debug_routes",
            "orchestrator_routes",
            "reflection_routes",
            "trust_routes"
        ]
    }

# Diagnostics router check endpoint
@app.get("/diagnostics/router-check")
async def router_diagnostics():
    """
    Diagnostics endpoint to check router registration.
    """
    return {
        "routers": [
            {"name": "core_router", "status": "registered"},
            {"name": "loop_router", "status": "registered"},
            {"name": "agent_router", "status": "registered"},
            {"name": "persona_router", "status": "registered"},
            {"name": "debug_router", "status": "registered"},
            {"name": "orchestrator_router", "status": "registered"},
            {"name": "reflection_router", "status": "registered"},
            {"name": "trust_router", "status": "registered"}
        ],
        "status": "ok"
    }
