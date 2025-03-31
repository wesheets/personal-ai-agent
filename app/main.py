from fastapi import FastAPI, APIRouter, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from app.api.agent import router as agent_router
from app.api.memory import router as memory_router
from app.api.goals import goals_router
from app.api.memory_viewer import memory_router as memory_viewer_router
from app.api.control import control_router
from app.api.logs import logs_router
from app.providers import initialize_model_providers, get_available_models

# Load environment variables
load_dotenv()

# Get CORS configuration from environment variables
cors_allowed_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000,https://compassionate-compassion-production.up.railway.app,https://frontend-agent-ui-production.up.railway.app")
cors_allow_credentials = os.environ.get("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# Parse allowed origins
allowed_origins = cors_allowed_origins.split(",")

# Initialize the FastAPI app
app = FastAPI(
    title="Enhanced AI Agent System",
    description="A personal AI agent system with vector memory, multi-model support, and configurable agent personalities",
    version="1.0.0")

# Add CORS middleware with hardcoded configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-agent-ui-production.up.railway.app",
        "https://compassionate-compassion-production.up.railway.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # 24 hours in seconds
)

# Add enhanced middleware to log all requests and responses with detailed information
@app.middleware("http")
async def log_requests(request, call_next):
    import logging
    import time
    from app.core.logging_manager import get_logging_manager
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("api")
    logging_manager = get_logging_manager()
    
    # Log basic request details to console
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process the request
    start_time = time.time()
    error = None
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log basic response details to console
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Process time: {process_time:.4f}s")
        
        # Store detailed log entry
        try:
            await logging_manager.log_request(request, response, process_time, error)
        except Exception as log_error:
            logger.error(f"Error logging request: {str(log_error)}")
        
        return response
    except Exception as e:
        # Log any exceptions
        error = e
        process_time = time.time() - start_time
        logger.error(f"Error during request processing: {str(e)}")
        logger.error(f"Process time: {process_time:.4f}s")
        
        # Store detailed log entry with error
        try:
            await logging_manager.log_request(request, None, process_time, error)
        except Exception as log_error:
            logger.error(f"Error logging request with error: {str(log_error)}")
        raise
    finally:
        # Log detailed request/response to storage
        try:
            if 'response' in locals():
                await logging_manager.log_request_response(
                    request=request,
                    response=response,
                    process_time=process_time,
                    error=error
                )
        except Exception as log_error:
            logger.error(f"Error logging request/response: {str(log_error)}")

# Initialize model providers
initialize_model_providers()

# Create system router
system_router = APIRouter(prefix="/system", tags=["System"])

@system_router.get("/models")
async def get_models():
    """Get all available models"""
    return get_available_models()

# Include routers
app.include_router(agent_router, prefix="/agent", tags=["Agents"])
app.include_router(memory_router, prefix="/api/memory", tags=["Memory"])
app.include_router(system_router)

# Include new routers for UI integration
app.include_router(goals_router, prefix="/api", tags=["Goals"])
app.include_router(memory_viewer_router, prefix="/api", tags=["Memory Viewer"])
app.include_router(control_router, prefix="/api", tags=["Control"])
app.include_router(logs_router, prefix="/api/logs", tags=["Logs"])

# Health check endpoint for Railway
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Railway"""
    return Response(content="OK", media_type="text/plain")

# Add CORS preflight OPTIONS handler for all routes
@app.options("/{rest_of_path:path}")
async def options_handler(rest_of_path: str):
    return Response(
        content="",
        headers={
            "Access-Control-Allow-Origin": cors_allowed_origins.split(",")[0] if "," in cors_allowed_origins else cors_allowed_origins,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true" if cors_allow_credentials else "false",
            "Access-Control-Max-Age": "86400",  # 24 hours in seconds
        }
    )

# Serve frontend static files if they exist
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/dist")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Enhanced AI Agent System",
        "docs": "/docs",
        "agents": [
            "/agent/builder",
            "/agent/ops",
            "/agent/research",
            "/agent/memory"
        ],
        "memory": "/memory",
        "models": "/system/models",
        "ui": {
            "goals": "/api/goals",
            "task_state": "/api/task-state",
            "memory": "/api/memory",
            "control_mode": "/api/system/control-mode",
            "agent_status": "/api/agent/status"
        }
    }
