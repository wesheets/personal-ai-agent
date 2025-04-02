from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from app.api.agent import router as agent_router
from app.api.memory import router as memory_router
from app.api.goals import goals_router
from app.api.memory_viewer import memory_router as memory_viewer_router
from app.api.control import control_router
from app.providers import initialize_model_providers, get_available_models

# Load environment variables
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title="Enhanced AI Agent System",
    description="A personal AI agent system with vector memory, multi-model support, and configurable agent personalities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Keep wildcard for local development
        "https://personal-ai-agent-production.up.railway.app",
        # "https://*.vercel.app"  # Temporary during testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(memory_router, prefix="/memory", tags=["Memory"])
app.include_router(system_router)

# Include new routers for UI integration
app.include_router(goals_router, prefix="/api", tags=["Goals"])
app.include_router(memory_viewer_router, prefix="/api", tags=["Memory Viewer"])
app.include_router(control_router, prefix="/api", tags=["Control"])

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
