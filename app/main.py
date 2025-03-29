from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.api.agent import router as agent_router
from app.api.memory import router as memory_router
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
    allow_origins=["*"],
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
        "models": "/system/models"
    }
