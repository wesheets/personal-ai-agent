"""
Update to main.py to register SAGE routes and Dashboard routes
"""

import os
import logging
import json
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")

# Create FastAPI app
app = FastAPI(
    title="Promethios API",
    description="API for the Promethios AI Agent System",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system manifest
try:
    from app.utils.manifest_manager import initialize_manifest, register_system_boot, register_loaded_routes
    
    # Initialize manifest at boot
    initialize_manifest()
    
    # Register system boot in manifest
    register_system_boot()
    
    print("✅ System manifest initialized")
    manifest_initialized = True
except ImportError as e:
    print(f"⚠️ Failed to initialize system manifest: {e}")
    manifest_initialized = False

# Setup dashboard static files
try:
    from app.utils.dashboard_setup import setup_dashboard_static_files
    setup_result = setup_dashboard_static_files()
    print(f"✅ Dashboard static files setup: {setup_result['message']}")
except ImportError as e:
    print(f"⚠️ Failed to setup dashboard static files: {e}")

# Mount static files directory
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    print("✅ Static files directory mounted")
except Exception as e:
    print(f"⚠️ Failed to mount static files directory: {e}")

# Track loaded routes
loaded_routes = []

# Import and include routes
# HAL routes
try:
    from app.routes.hal_routes import router as hal_router
    app.include_router(hal_router)
    loaded_routes.append("hal")
    print("✅ HAL routes loaded")
except ImportError as e:
    print(f"⚠️ Failed to load HAL routes: {e}")

# Orchestrator routes
try:
    from app.routes.orchestrator_routes import router as orchestrator_router
    app.include_router(orchestrator_router)
    loaded_routes.append("orchestrator")
    print("✅ Orchestrator routes loaded")
except ImportError as e:
    print(f"⚠️ Failed to load Orchestrator routes: {e}")

# SAGE routes - Hard-wired registration
try:
    from app.routes.sage_routes import router as sage_router
    app.include_router(sage_router)
    loaded_routes.append("sage")
    print("✅ SAGE routes loaded")
except ImportError as e:
    print(f"⚠️ Failed to load SAGE routes: {e}")

# Dashboard routes - Hard-wired registration
try:
    from app.routes.dashboard_routes import router as dashboard_router
    app.include_router(dashboard_router)
    loaded_routes.append("dashboard")
    print("✅ Dashboard routes loaded")
except ImportError as e:
    print(f"⚠️ Failed to load Dashboard routes: {e}")

# Loop routes
try:
    from app.routes.loop_routes import router as loop_router
    app.include_router(loop_router)
    loaded_routes.append("loop")
    print("✅ Loop routes loaded")
except ImportError as e:
    print(f"⚠️ Failed to load Loop routes: {e}")

# Critic routes
try:
    from app.routes.critic_routes import router as critic_router
    app.include_router(critic_router)
    loaded_routes.append("critic")
    print("✅ Critic routes loaded")
except ImportError as e:
    print(f"⚠️ Failed to load Critic routes: {e}")

# Drift routes
try:
    from app.routes.drift_routes import router as drift_router
    app.include_router(drift_router)
    loaded_routes.append("drift")
    print("✅ Drift routes loaded")
except ImportError as e:
    print(f"⚠️ Failed to load Drift routes: {e}")

# Output Policy routes
try:
    from app.routes.output_policy_routes import router as output_policy_router
    app.include_router(output_policy_router)
    loaded_routes.append("output_policy")
    print("✅ Output Policy routes loaded")
except ImportError as e:
    print(f"⚠️ Failed to load Output Policy routes: {e}")

# Register loaded routes in manifest
if manifest_initialized:
    try:
        register_loaded_routes(loaded_routes)
        print(f"✅ Registered {len(loaded_routes)} routes in manifest")
    except Exception as e:
        print(f"⚠️ Failed to register routes in manifest: {e}")

@app.get("/")
async def root():
    """Root endpoint that returns basic API information"""
    return {
        "name": "Promethios API",
        "version": "0.1.0",
        "status": "operational",
        "loaded_routes": loaded_routes,
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/dashboard")
async def dashboard_redirect():
    """Redirect to the dashboard frontend"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/dashboard/index.html")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to add processing time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
