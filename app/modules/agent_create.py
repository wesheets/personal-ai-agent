"""
Agent Creation Module

This module provides functionality for creating new agents based on suggestions
from the /scope endpoint, completing the workflow loop:
scope → detect gap → suggest agent → create agent → present

Endpoint: /agent/create
"""

import json
import os
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Define the router
router = APIRouter()

# Define the models
class ToneProfile(BaseModel):
    style: str
    emotion: str
    vibe: str
    persona: str

class AgentCreateRequest(BaseModel):
    agent_name: str
    skills: List[str]
    tone_profile: ToneProfile
    description: str

class AgentCreateResponse(BaseModel):
    status: str
    agent_id: str
    message: str

# Path to the agent manifest file
AGENT_MANIFEST_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 "config", "agent_manifest.json")

def load_agent_manifest() -> Dict[str, Any]:
    """
    Load the agent manifest from the JSON file.
    
    Returns:
        Dict[str, Any]: The agent manifest as a dictionary
    """
    try:
        with open(AGENT_MANIFEST_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load agent manifest: {str(e)}")

def save_agent_manifest(manifest: Dict[str, Any]) -> None:
    """
    Save the agent manifest to the JSON file.
    
    Args:
        manifest (Dict[str, Any]): The agent manifest to save
    """
    try:
        with open(AGENT_MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save agent manifest: {str(e)}")

def agent_exists(agent_name: str) -> bool:
    """
    Check if an agent with the given name already exists.
    
    Args:
        agent_name (str): The name of the agent to check
        
    Returns:
        bool: True if the agent exists, False otherwise
    """
    manifest = load_agent_manifest()
    
    # Check if agent_name has -agent suffix, if not add it
    full_agent_id = agent_name if agent_name.endswith("-agent") else f"{agent_name}-agent"
    
    return full_agent_id in manifest

def create_agent_entry(request: AgentCreateRequest) -> Dict[str, Any]:
    """
    Create a new agent entry based on the request.
    
    Args:
        request (AgentCreateRequest): The agent creation request
        
    Returns:
        Dict[str, Any]: The new agent entry
    """
    # Format the agent name (ensure it has -agent suffix)
    agent_name = request.agent_name
    full_agent_id = agent_name if agent_name.endswith("-agent") else f"{agent_name}-agent"
    
    # Generate the entrypoint path based on agent name
    base_name = agent_name.replace("-agent", "")
    entrypoint = f"app/agents/{base_name}_agent.py"
    
    # Create the agent entry
    agent_entry = {
        "version": "0.1.0",  # Start with initial version
        "description": request.description,
        "status": "experimental",  # New agents start as experimental
        "entrypoint": entrypoint,
        "tone_profile": {
            "style": request.tone_profile.style,
            "emotion": request.tone_profile.emotion,
            "vibe": request.tone_profile.vibe,
            "persona": request.tone_profile.persona
        },
        "skills": request.skills
    }
    
    return agent_entry

@router.post("/agent/create", response_model=AgentCreateResponse)
async def create_agent(request: AgentCreateRequest):
    """
    Create a new agent based on the request.
    
    Args:
        request (AgentCreateRequest): The agent creation request
        
    Returns:
        AgentCreateResponse: The response indicating success or failure
        
    Raises:
        HTTPException: If the agent already exists or other errors occur
    """
    # Validate the request
    if not request.agent_name:
        raise HTTPException(status_code=422, detail="agent_name is required")
    
    if not request.skills or len(request.skills) == 0:
        raise HTTPException(status_code=422, detail="At least one skill is required")
    
    # Check if the agent already exists
    if agent_exists(request.agent_name):
        return {
            "status": "error",
            "agent_id": request.agent_name,
            "message": f"Agent '{request.agent_name}' already exists."
        }
    
    # Create the agent entry
    agent_entry = create_agent_entry(request)
    
    # Load the manifest
    manifest = load_agent_manifest()
    
    # Format the agent name (ensure it has -agent suffix)
    full_agent_id = request.agent_name if request.agent_name.endswith("-agent") else f"{request.agent_name}-agent"
    
    # Add the new agent to the manifest
    manifest[full_agent_id] = agent_entry
    
    # Save the updated manifest
    save_agent_manifest(manifest)
    
    # Return success response
    return {
        "status": "success",
        "agent_id": request.agent_name,
        "message": f"Agent {request.agent_name} successfully created and registered."
    }
