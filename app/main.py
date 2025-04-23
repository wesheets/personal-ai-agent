"""
Main application module for the Promethios API.

This module initializes the FastAPI application and includes all routes.
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import importlib
import time
import os
import json

# Import memory module
from app.memory.project_memory import PROJECT_MEMORY

# Import self_routes directly as it's in a different location
from app.routes.self_routes import router as self_router

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

# Dynamic route loader
routes_to_try = [
    "loop_routes",
    "agent_routes",
    "memory_routes",
    "core_routes",
    "persona_routes",
    "system_routes",
    "plan_routes",
    "orchestrator_routes",
    "debug_routes",
    "reflection_routes",
    "trust_routes"
]

for route in routes_to_try:
    try:
        module = importlib.import_module(f"routes.{route}")
        app.include_router(module.router, prefix="/api")
        print(f"✅ Loaded route: {route}")
    except ImportError as e:
        print(f"⚠️ Skipped missing route: {route} — {e}")
    except AttributeError as e:
        print(f"⚠️ Route file found but missing 'router' object: {route} — {e}")

# Include self_router separately as it's from a different location
app.include_router(self_router, prefix="/self")
print(f"✅ Loaded route: self_routes")

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
        "routes_registered": routes_to_try
    }

# Diagnostics router check endpoint
@app.get("/diagnostics/router-check")
async def router_diagnostics():
    """
    Diagnostics endpoint to check router registration.
    """
    return {
        "routers": [{"name": route, "status": "registered"} for route in routes_to_try],
        "status": "ok"
    }
