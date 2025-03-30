# Make the module importable
# Create a router directly in the __init__.py file
from fastapi import APIRouter
from app.api.agent import router as agent_router_original

# Create a new router that includes all routes from the original
router = APIRouter()
router.include_router(agent_router_original)
