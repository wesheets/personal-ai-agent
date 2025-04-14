"""
Projects module for Promethios.

This module provides endpoints for creating and querying project containers
as part of the System Lockdown Phase.
"""

from fastapi import APIRouter

router = APIRouter()

from .projects import router as projects_router
router.include_router(projects_router)
