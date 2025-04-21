"""
Main Application Module

This module serves as the entry point for the Promethios API.
It initializes all required components and starts the server.
"""

import os
import sys
import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html

# Configure enhanced logging
logging.basicConfig(
    level=logging.DEBUG,  # Enhanced to DEBUG level for more detailed logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")

# Log system information for debugging
logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Environment variables: {', '.join([f'{k}={v}' for k, v in os.environ.items() if not k.startswith('_')])}")

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

# Dictionary to track router registration status
registered_routers = {}

# Import routers with explicit error handling
try:
    logger.info("Importing core_router...")
    from app.routes.core_routes import router as core_router
    registered_routers["core_router"] = "imported"
except Exception as e:
    logger.error(f"Error importing core_router: {str(e)}")
    logger.error(traceback.format_exc())
    registered_routers["core_router"] = f"import_error: {str(e)}"

try:
    logger.info("Importing loop_router...")
    from app.routes.loop_routes import router as loop_router
    registered_routers["loop_router"] = "imported"
except Exception as e:
    logger.error(f"Error importing loop_router: {str(e)}")
    logger.error(traceback.format_exc())
    registered_routers["loop_router"] = f"import_error: {str(e)}"

try:
    logger.info("Importing agent_router...")
    from app.routes.agent_routes import router as agent_router
    registered_routers["agent_router"] = "imported"
except Exception as e:
    logger.error(f"Error importing agent_router: {str(e)}")
    logger.error(traceback.format_exc())
    registered_routers["agent_router"] = f"import_error: {str(e)}"

try:
    logger.info("Importing persona_router...")
    from app.routes.persona_routes import router as persona_router
    registered_routers["persona_router"] = "imported"
except Exception as e:
    logger.error(f"Error importing persona_router: {str(e)}")
    logger.error(traceback.format_exc())
    registered_routers["persona_router"] = f"import_error: {str(e)}"

try:
    logger.info("Importing debug_routes...")
    from app.routes import debug_routes
    registered_routers["debug_routes"] = "imported"
except Exception as e:
    logger.error(f"Error importing debug_routes: {str(e)}")
    logger.error(traceback.format_exc())
    registered_routers["debug_routes"] = f"import_error: {str(e)}"

# Create a test fallback router for diagnostics
from fastapi import APIRouter
test_router = APIRouter()

@test_router.get("/diagnostics/router-check")
async def router_diagnostics():
    """
    Diagnostic endpoint to check router registration status.
    """
    # Include router registration in response
    return {
        "test_route_status": "running",
        "registered_routers": registered_routers,
        "python_info": {
            "version": sys.version,
            "path": sys.path,
            "cwd": os.getcwd(),
        },
        "app_info": {
            "routes_count": len(app.routes),
            "middleware_count": len(app.middleware),
        }
    }

# Include routers with explicit error handling and logging
logger.info("Registering routers...")

# Include test router first to ensure it's available
try:
    logger.info("Including test_router...")
    app.include_router(test_router)
    registered_routers["test_router"] = "registered"
    logger.info("test_router successfully registered")
except Exception as e:
    logger.error(f"Error including test_router: {str(e)}")
    logger.error(traceback.format_exc())
    registered_routers["test_router"] = f"registration_error: {str(e)}"

# Include core router
if "core_router" in registered_routers and registered_routers["core_router"] == "imported":
    try:
        logger.info("Including core_router...")
        app.include_router(core_router)
        registered_routers["core_router"] = "registered"
        logger.info("core_router successfully registered")
    except Exception as e:
        logger.error(f"Error including core_router: {str(e)}")
        logger.error(traceback.format_exc())
        registered_routers["core_router"] = f"registration_error: {str(e)}"

# Include loop router
if "loop_router" in registered_routers and registered_routers["loop_router"] == "imported":
    try:
        logger.info("Including loop_router...")
        app.include_router(loop_router)
        registered_routers["loop_router"] = "registered"
        logger.info("loop_router successfully registered")
    except Exception as e:
        logger.error(f"Error including loop_router: {str(e)}")
        logger.error(traceback.format_exc())
        registered_routers["loop_router"] = f"registration_error: {str(e)}"

# Include agent router
if "agent_router" in registered_routers and registered_routers["agent_router"] == "imported":
    try:
        logger.info("Including agent_router...")
        app.include_router(agent_router)
        registered_routers["agent_router"] = "registered"
        logger.info("agent_router successfully registered")
    except Exception as e:
        logger.error(f"Error including agent_router: {str(e)}")
        logger.error(traceback.format_exc())
        registered_routers["agent_router"] = f"registration_error: {str(e)}"

# Include persona router
if "persona_router" in registered_routers and registered_routers["persona_router"] == "imported":
    try:
        logger.info("Including persona_router...")
        app.include_router(persona_router)
        registered_routers["persona_router"] = "registered"
        logger.info("persona_router successfully registered")
    except Exception as e:
        logger.error(f"Error including persona_router: {str(e)}")
        logger.error(traceback.format_exc())
        registered_routers["persona_router"] = f"registration_error: {str(e)}"

# Include debug routes
if "debug_routes" in registered_routers and registered_routers["debug_routes"] == "imported":
    try:
        logger.info("Including debug_routes.router...")
        app.include_router(debug_routes.router)
        registered_routers["debug_routes"] = "registered"
        logger.info("debug_routes.router successfully registered")
    except Exception as e:
        logger.error(f"Error including debug_routes.router: {str(e)}")
        logger.error(traceback.format_exc())
        registered_routers["debug_routes"] = f"registration_error: {str(e)}"

# Schema injection test route
@app.get("/schema-injection-test")
async def schema_injection_test():
    """
    Test endpoint to validate if memory schemas are reachable.
    """
    schemas_status = {}
    
    # Test memory schema imports
    try:
        from app.memory.project_memory import PROJECT_MEMORY
        schemas_status["project_memory"] = "accessible"
    except Exception as e:
        schemas_status["project_memory"] = f"error: {str(e)}"
    
    # Test model registration
    try:
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            name: str
            value: int
        
        schemas_status["model_registration"] = "working"
    except Exception as e:
        schemas_status["model_registration"] = f"error: {str(e)}"
    
    return {
        "test_route_status": "running",
        "registered_routers": registered_routers,
        "schemas_status": schemas_status
    }

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
        "health": "/health",
        "diagnostics": "/diagnostics/router-check"
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
    error_details = {
        "exception_type": type(exc).__name__,
        "exception_str": str(exc),
        "traceback": traceback.format_exc()
    }
    
    logger.error(f"Unhandled exception: {error_details['exception_type']}: {error_details['exception_str']}")
    logger.error(error_details['traceback'])
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": f"An unexpected error occurred: {str(exc)}",
            "path": request.url.path,
            "error_details": error_details
        }
    )

# Log all registered routes for debugging
logger.info("All routes registered. Listing all application routes:")
for route in app.routes:
    logger.info(f"Route: {route.path}, Methods: {route.methods}")

# Run the application if executed directly
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting application server...")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
