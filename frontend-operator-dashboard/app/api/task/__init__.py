"""
Task status tracking module for Promethios.

This module provides endpoints for logging and querying task execution status
as part of the System Lockdown Phase.
"""

from fastapi import APIRouter

router = APIRouter()

from .status import router as status_router
router.include_router(status_router)
