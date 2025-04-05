from fastapi import FastAPI, APIRouter, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.routing import APIRoute
import os
import logging
import inspect
from dotenv import load_dotenv

from app.api.agent import router as agent_router
from app.api.memory import router as memory_router
from app.api.goals import goals_router
from app.api.memory_viewer import memory_router as memory_viewer_router
from app.api.control import control_router
from app.api.logs import logs_router
from app.api.delegate_route import router as delegate_router  # ✅ HAL ROUTER
from app.diagnostics.hal_route_debug import router as hal_debug_router

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

# CORS configuration
cors_allowed_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000,https://compassionate-compassion-production.up.railway.app,https://frontend-agent-ui-production.up.railway.app")
cors_allow_credentials = os.environ.get("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
allowed_origins = cors_allowed_origins.split(",")

# FastAPI app init
app = FastAPI(
    title="Enhanced AI Agent System",
    description="A personal AI agent system with vector memory, multi-model support, and configurable agent personalities",
    version="1.0.0"
)

# Route logger for debugging
@app.on_event("startup")
async def log_all_routes():
    print("🚀 Booting Enhanced AI Agent System...")
    print("📡 ROUTES REGISTERED ON STARTUP:")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"➡️ {route.path} [{', '.join(route.methods)}] from {inspect.getsourcefile(route.endpoint)}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Request headers: {request.headers}")
    if "delegate" in str(request.url) or "latest" in str(request.url) or "goals" in str(request.url):
        try:
            body = await request.body()
            if body:
                logger.info(f"Request body: {body.decode()}")
                request._body = body
        except Exception as e:
            logger.error(f"Error reading request body: {str(e)}")
    start_time = time.time()
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        logger.info(f"Process time: {time.time() - start_time:.4f}s")
        return response
    except Exception as e:
        logger.error(f"Error during request processing: {str(e)}")
        logger.error(f"Process time: {time.time() - start_time:.4f}s")
        raise

# Initialize providers
initialize_model_providers()

# System routes
system_router = APIRouter(prefix="/system", tags=["System"])

@system_router.get("/models")
async def get_models():
    models = get_available_models()
    return models

@system_router.get("/status")
async def get_system_status():
    try:
        prompt_manager = PromptManager()
        task_state_manager = get_task_state_manager()
        seeding_manager = get_seeding_manager()
        agents_seeded = await seeding_manager.seed_default_agents(prompt_manager)
        goals_seeded = await seeding_manager.seed_default_goals(task_state_manager)
        return {
            "status": "operational",
            "version": "1.0.0",
            "uptime": "N/A",
            "agents_count": len(prompt_manager.get_available_agents()),
            "goals_count": len(task_state_manager.goals),
            "tasks_count": len(task_state_manager.tasks),
            "seeding": {
                "agents_seeded": agents_seeded,
                "goals_seeded": goals_seeded
            }
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e), "version": "1.0.0"}

# Mount routers
app.include_router(agent_router, prefix="/agent", tags=["Agents"])
app.include_router(agent_router, prefix="/api/agent", tags=["API Agents"])
app.include_router(memory_router, prefix="/memory", tags=["Memory"])
app.include_router(goals_router, prefix="/api", tags=["Goals"])
app.include_router(memory_viewer_router, prefix="/api", tags=["Memory Viewer"])
app.include_router(control_router, prefix="/api", tags=["Control"])
app.include_router(logs_router, prefix="/api", tags=["Logs"])
app.include_router(system_router)
app.include_router(delegate_router, prefix="/api", tags=["HAL"])  # ✅ HAL ROUTE MOUNTED
app.include_router(hal_debug_router, prefix="/api", tags=["Diagnostics"])  # Diagnostic router for debugging routes

# Swagger docs route
@app.get("/api/docs", include_in_schema=False)
def overridden_swagger_docs():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Agent API Docs")

# Debug route
@app.post("/api/agent/delegate-debug")
async def delegate_debug(request: Request):
    body = await request.json()
    logger.info(f"🧠 Debug body received: {body}")
    return {"status": "success", "message": "Debug delegate endpoint response", "task_id": "debug-task-123"}

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    return Response(content="OK", media_type="text/plain")

# CORS preflight
@app.options("/{rest_of_path:path}")
async def options_handler(rest_of_path: str):
    return Response(
        content="",
        headers={
            "Access-Control-Allow-Origin": allowed_origins[0] if "," in cors_allowed_origins else cors_allowed_origins,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true" if cors_allow_credentials else "false",
            "Access-Control-Max-Age": "86400"
        }
    )

# Frontend fallback
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/dist")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Enhanced AI Agent System",
        "docs": "/api/docs",
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
