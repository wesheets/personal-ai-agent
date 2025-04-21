"""
Persona Routes Module

This module defines the persona-related routes for the Promethios API.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.memory.project_memory import update_project_memory, get_project_memory

# Define valid personas
VALID_PERSONAS = ["SAGE", "ARCHITECT", "RESEARCHER", "RITUALIST", "INVENTOR"]

router = APIRouter(tags=["persona"])

class PersonaSwitchRequest(BaseModel):
    """Request model for persona switch endpoint."""
    persona: str
    operator_id: str
    loop_id: str

@router.post("/persona/switch")
async def switch_persona(request: PersonaSwitchRequest):
    """
    Change active persona for a specific loop.
    
    This endpoint:
    1. Validates the persona against the allowed list
    2. Writes the persona state to memory
    3. Returns the previous and new persona information
    """
    # Validate persona against allowed list
    if request.persona not in VALID_PERSONAS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid persona. Must be one of: {', '.join(VALID_PERSONAS)}"
        )
    
    # Get current timestamp
    timestamp = datetime.utcnow().isoformat()
    
    # Get previous persona (if any)
    previous_persona = "SAGE"  # Default if not found
    try:
        # Try to get the current persona from memory
        loop_trace = get_project_memory(request.loop_id)
        if "orchestrator_persona" in loop_trace:
            previous_persona = loop_trace["orchestrator_persona"]
    except KeyError:
        # If loop doesn't exist in memory, use default
        pass
    
    # Write to memory
    persona_state = {
        "loop_id": request.loop_id,
        "orchestrator_persona": request.persona,
        "switched_by": "operator",
        "operator_id": request.operator_id,
        "timestamp": timestamp,
        "persona_switch_reason": "manual"
    }
    
    # Update memory with persona state
    try:
        update_project_memory(request.loop_id, "orchestrator_persona", request.persona)
        update_project_memory(request.loop_id, "persona_switch_timestamp", timestamp)
        update_project_memory(request.loop_id, "persona_switch_reason", "manual")
        update_project_memory(request.loop_id, "operator_id", request.operator_id)
    except KeyError:
        # If loop doesn't exist in memory, create it with persona state
        update_project_memory(request.loop_id, "orchestrator_persona", request.persona)
        update_project_memory(request.loop_id, "persona_switch_timestamp", timestamp)
        update_project_memory(request.loop_id, "persona_switch_reason", "manual")
        update_project_memory(request.loop_id, "operator_id", request.operator_id)
    
    # Return success response
    return {
        "status": "success",
        "previous_persona": previous_persona,
        "new_persona": request.persona,
        "loop_id": request.loop_id,
        "timestamp": timestamp,
        "switched_by": "operator",
        "operator_id": request.operator_id
    }

@router.get("/persona/current")
async def get_current_persona(loop_id: Optional[str] = None):
    """
    Return current orchestrator_persona for the specified loop or the system default.
    
    Args:
        loop_id: Optional loop ID to get persona for a specific loop
    """
    current_persona = "SAGE"  # Default persona
    active_since = datetime.utcnow().isoformat()
    
    if loop_id:
        try:
            # Try to get the current persona from memory for the specified loop
            loop_trace = get_project_memory(loop_id)
            if "orchestrator_persona" in loop_trace:
                current_persona = loop_trace["orchestrator_persona"]
            if "persona_switch_timestamp" in loop_trace:
                active_since = loop_trace["persona_switch_timestamp"]
        except KeyError:
            # If loop doesn't exist in memory, use default
            pass
    
    # Get persona description
    persona_descriptions = {
        "SAGE": "The SAGE persona focuses on wisdom, balance, and holistic thinking.",
        "ARCHITECT": "The ARCHITECT persona focuses on structure, systems, and design thinking.",
        "RESEARCHER": "The RESEARCHER persona focuses on inquiry, analysis, and evidence-based reasoning.",
        "RITUALIST": "The RITUALIST persona focuses on process, tradition, and methodical approaches.",
        "INVENTOR": "The INVENTOR persona focuses on creativity, innovation, and novel solutions."
    }
    
    description = persona_descriptions.get(current_persona, "No description available.")
    
    return {
        "current_persona": current_persona,
        "active_since": active_since,
        "description": description,
        "loop_id": loop_id,
        "status": "active"
    }

@router.get("/mode/trace")
async def get_mode_trace():
    """
    Trace of persona usage over loops.
    """
    # This would normally retrieve the mode trace from storage
    # For now, return a mock response
    return {
        "traces": [
            {
                "loop_id": "loop_001",
                "persona": "SAGE",
                "timestamp": "2025-04-21T10:00:00Z",
                "reason": "Initial mode"
            },
            {
                "loop_id": "loop_002",
                "persona": "RESEARCHER",
                "timestamp": "2025-04-21T10:30:00Z",
                "reason": "Complex research task detected"
            },
            {
                "loop_id": "loop_003",
                "persona": "SAGE",
                "timestamp": "2025-04-21T11:00:00Z",
                "reason": "Returning to balanced approach"
            }
        ],
        "current_persona": "SAGE",
        "status": "success"
    }
