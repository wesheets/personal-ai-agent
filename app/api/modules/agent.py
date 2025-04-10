"""
API endpoint for the AgentRunner module.

This module provides REST API endpoints for executing agents in isolation,
and for creating and registering new agents dynamically.
"""

print("📁 Loaded: agent.py (AgentRunner route file)")

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import traceback
import os
import time
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger("api.modules.agent")

# Create router
router = APIRouter(prefix="/modules/agent", tags=["Agent Modules"])
print("🧠 Route defined: /api/modules/agent/run -> run_agent_endpoint")
print("🧠 Route defined: /api/modules/agent/create -> create_agent_endpoint")
print("🧠 Route defined: /api/modules/agent/list -> list_agents_endpoint")

# Initialize agent registry
agent_registry = {}

# Path for persistent storage
AGENTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "agents.json")

# Load existing agents if file exists
def load_agent_registry():
    global agent_registry
    try:
        if os.path.exists(AGENTS_FILE):
            with open(AGENTS_FILE, 'r') as f:
                agent_registry = json.load(f)
            print(f"📚 Loaded {len(agent_registry)} agents from registry")
    except Exception as e:
        print(f"⚠️ Error loading agent registry: {str(e)}")
        agent_registry = {}

# Save agent registry to file
def save_agent_registry():
    try:
        with open(AGENTS_FILE, 'w') as f:
            json.dump(agent_registry, f, indent=2)
        print(f"💾 Saved {len(agent_registry)} agents to registry")
    except Exception as e:
        print(f"⚠️ Error saving agent registry: {str(e)}")

# Load agents on module import
load_agent_registry()

# Pydantic model for agent creation request
class AgentCreateRequest(BaseModel):
    agent_id: str
    description: Optional[str] = None
    traits: Optional[List[str]] = []

@router.post("/create")
async def create_agent(agent: AgentCreateRequest):
    try:
        # Check if agent_id already exists
        if agent.agent_id in agent_registry:
            return JSONResponse(
                status_code=409,
                content={
                    "status": "error",
                    "message": f"Agent with ID '{agent.agent_id}' already exists"
                }
            )
        
        # Store the agent in registry
        agent_registry[agent.agent_id] = {
            "description": agent.description,
            "traits": agent.traits,
            "created_at": datetime.utcnow().isoformat(),
            "modules": ["memory"]  # Default module
        }
        
        # Save to disk
        save_agent_registry()
        
        # Return success response
        return {
            "status": "ok",
            "agent_id": agent.agent_id
        }
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to create agent: {str(e)}"
            }
        )

@router.get("/list")
async def list_agents():
    """
    Returns a list of all registered agents in the system.
    
    This endpoint retrieves all agents from the agent registry and returns them
    in a standardized format with agent_id, name, created_at, and modules fields.
    
    Returns:
    - status: "ok" if successful
    - agents: List of agent objects with metadata
    """
    try:
        # If registry is empty, add some sample agents for testing
        if not agent_registry:
            # Add sample agents for testing
            agent_registry["hal"] = {
                "description": "HAL is a general purpose assistant",
                "traits": ["helpful", "analytical", "logical"],
                "created_at": "2025-04-10T11:34:22Z",
                "modules": ["memory", "reflection", "loop"]
            }
            agent_registry["ash"] = {
                "description": "ASH is a specialized science assistant",
                "traits": ["scientific", "precise", "methodical"],
                "created_at": "2025-04-09T17:12:01Z",
                "modules": ["memory", "delegate"]
            }
            # Save to disk
            save_agent_registry()
        
        # Format agents for response
        agents_list = []
        for agent_id, agent_data in agent_registry.items():
            # Extract or set default values for required fields
            name = agent_data.get("name", agent_id.upper())
            created_at = agent_data.get("created_at", datetime.utcnow().isoformat())
            modules = agent_data.get("modules", ["memory"])
            
            # Create agent entry
            agent_entry = {
                "agent_id": agent_id,
                "name": name,
                "created_at": created_at,
                "modules": modules
            }
            agents_list.append(agent_entry)
        
        # Return response
        return {
            "status": "ok",
            "agents": agents_list
        }
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to list agents: {str(e)}"
            }
        )

# Temporarily commented out as per failsafe implementation requirements
"""
@router.post("/run")
async def run_agent_echo(request: Request):
    print("📣 AgentRunner echo route was hit!")
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "message": "AgentRunner route is working"
        }
    )
"""
