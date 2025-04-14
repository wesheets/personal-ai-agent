"""
Orchestrator module initialization.

This module initializes the orchestrator package and exports the routers.
"""

from fastapi import APIRouter

# Import routers
from app.api.orchestrator.scope import router as scope_router

# Create package router
router = APIRouter()

# Include sub-routers
# This allows the main application to include just this router
# with the appropriate prefix
