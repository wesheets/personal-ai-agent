"""
API endpoint for the AgentRunner module.

This module provides a REST API endpoint for executing agents in isolation,
without relying on the central agent registry, UI, or delegate-stream system.

MODIFIED: Replaced with inline execution debug logging to diagnose 502 errors
"""

print("📁 Loaded: agent.py (AgentRunner route file)")

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
import traceback
import os
import time

# Configure logging
logger = logging.getLogger("api.modules.agent")

# Create router
router = APIRouter(prefix="/modules/agent", tags=["Agent Modules"])
print("🧠 Route defined: /api/modules/agent/run -> run_agent_endpoint")

@router.post("/api/modules/agent/run")
async def run_agent_echo(request: Request):
    print("📣 AgentRunner echo route was hit!")
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "message": "AgentRunner route is working"
        }
    )
