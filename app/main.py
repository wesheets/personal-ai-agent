from fastapi import FastAPI, APIRouter, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
from app.api.agent import router as agent_router
from app.api.memory import router as memory_router
from app.api.goals import goals_router
from app.api.memory_viewer import memory_router as memory_viewer_router
from app.api.control import control_router
from app.api.logs import logs_router
from app.providers import initialize_model_providers, get_available_models
from app.core.seeding import get_seeding_manager
from app.core.prompt_manager import PromptManager
from app.core.task_state_manager import get_task_state_manager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app/logs/api.log', mode='a')
    ]
)
logger = logging.getLogger("api")

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

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Keep wildcard for local development
        "http://localhost:5173",
        "https://personal-ai-agent-production.up.railway.app",
        "https://personal-ai-agent-git-manus-ui-restore-ted-sheets-projects.vercel.app",
        # "https://*.vercel.app"  # Temporary during testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add middleware to log healthcheck requests with timestamp
@app.middleware("http")
async def log_healthcheck_requests(request: Request, call_next):
    if request.url.path == "/health":
        timestamp = datetime.utcnow()
        logger.info(f"[HEALTHCHECK] Request received at {timestamp}")
        print(f"[HEALTHCHECK] Request received at {timestamp}")
    return await call_next(request)

# Add middleware to log all requests and responses for debugging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import logging
    import time
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("api")
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url}")
    print(f"Request: {request.method} {request.url}")
    logger.info(f"Request headers: {request.headers}")
    
    # Log request body for debugging task delegation issues
    if "delegate" in str(request.url) or "latest" in str(request.url) or "goals" in str(request.url):
        try:
            body = await request.body()
            if body:
                body_str = body.decode()
                logger.info(f"Request body: {body_str}")
                print(f"Request body in middleware: {body_str}")
                # Store body for later use (FastAPI consumes the body)
                request._body = body
        except Exception as e:
            logger.error(f"Error reading request body: {str(e)}")
            print(f"Error reading request body: {str(e)}")
    
    # Process the request
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(f"Response status: {response.status_code}")
        print(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        logger.info(f"Process time: {process_time:.4f}s")
        
        return response
    except Exception as e:
        # Log any exceptions
        process_time = time.time() - start_time
        logger.error(f"Error during request processing: {str(e)}")
        print(f"❌ Error during request processing: {str(e)}")
        logger.error(f"Process time: {process_time:.4f}s")
        raise

# Initialize model providers
initialize_model_providers()

# Create system router
system_router = APIRouter(prefix="/system", tags=["System"])

@system_router.get("/models")
async def get_models():
    """Get all available models"""
    logger.info("Getting available models")
    models = get_available_models()
    logger.info(f"Found {len(models)} available models")
    return models

@system_router.get("/status")
async def get_system_status():
    """Get system status"""
    logger.info("Getting system status")
    try:
        # Check if we need to seed data
        prompt_manager = PromptManager()
        task_state_manager = get_task_state_manager()
        seeding_manager = get_seeding_manager()
        
        # Seed agents and goals if needed
        agents_seeded = await seeding_manager.seed_default_agents(prompt_manager)
        goals_seeded = await seeding_manager.seed_default_goals(task_state_manager)
        
        status = {
            "status": "operational",
            "version": "1.0.0",
            "uptime": "N/A",  # Would be calculated in a real implementation
            "agents_count": len(prompt_manager.get_available_agents()),
            "goals_count": len(task_state_manager.goals),
            "tasks_count": len(task_state_manager.tasks),
            "seeding": {
                "agents_seeded": agents_seeded,
                "goals_seeded": goals_seeded
            }
        }
        logger.info(f"System status: {status}")
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e),
            "version": "1.0.0"
        }

# Health check endpoint for Railway
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Railway"""
    logger.info("Health check requested")
    print("[HEALTH] Health check requested")
    return {"status": "ok"}

# Add CORS preflight OPTIONS handler for all routes
@app.options("/{rest_of_path:path}")
async def options_handler(rest_of_path: str):
    logger.info(f"CORS preflight request for path: /{rest_of_path}")
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
    logger.info("Root endpoint accessed")
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
            "agent_status": "/api/agent/status",
            "logs": "/api/logs/latest"
        }
    }

# Run the application with uvicorn when this script is executed directly
if __name__ == "__main__":
    import uvicorn
    print("[MAIN] Starting uvicorn server on port 8080")
    logger.info("[MAIN] Starting uvicorn server on port 8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
