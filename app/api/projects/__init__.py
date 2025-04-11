"""
Projects module for Promethios.

This module provides endpoints for creating and querying project containers
as part of the System Lockdown Phase.
"""

from fastapi import APIRouter

router = APIRouter()

from . import projects
