"""
Plan Module

This module provides endpoints for SaaS product planning and execution.
"""

from fastapi import APIRouter

# Import scope router
from app.modules.plan.scope import router as scope_router

# Create main router
router = APIRouter()

# Include scope router
router.include_router(scope_router, tags=["plan"])
