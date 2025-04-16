# Make the module importable
from fastapi import APIRouter

# Create a new router
router = APIRouter()

# Import the routes after router is defined to avoid circular imports
from app.api.agent.builder import router as builder_router
from app.api.agent.ops import router as ops_router
from app.api.agent.research import router as research_router
from app.api.agent.memory import router as memory_router
from app.api.agent.planner import router as planner_router

# Include all routes
router.include_router(builder_router)
router.include_router(ops_router)
router.include_router(research_router)
router.include_router(memory_router)
router.include_router(planner_router)
