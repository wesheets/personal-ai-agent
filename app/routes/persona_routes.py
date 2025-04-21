"""
Persona Routes Module

This module defines the persona-related routes for the Promethios API.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List

router = APIRouter(tags=["persona"])

@router.post("/persona/switch")
async def switch_persona(data: Dict[str, Any]):
    """
    Change active mode.
    """
    persona = data.get("persona")
    loop_id = data.get("loop_id")
    reason = data.get("reason")
    
    if not persona or not loop_id:
        raise HTTPException(status_code=400, detail="persona and loop_id are required")
    
    # Validate persona
    valid_personas = ["SAGE", "ARCHITECT", "RESEARCHER", "RITUALIST", "INVENTOR"]
    if persona not in valid_personas:
        raise HTTPException(status_code=400, detail=f"Invalid persona. Must be one of: {', '.join(valid_personas)}")
    
    # This would normally switch the persona
    # For now, return a success response
    return {
        "status": "success",
        "previous_persona": "SAGE",  # Mock previous persona
        "new_persona": persona,
        "loop_id": loop_id,
        "reason": reason,
        "timestamp": "2025-04-21T12:30:00Z"
    }

@router.get("/persona/current")
async def get_current_persona():
    """
    Return current orchestrator_persona.
    """
    # This would normally retrieve the current persona from memory
    # For now, return a mock response
    return {
        "persona": "SAGE",
        "active_since": "2025-04-21T10:00:00Z",
        "description": "The SAGE persona focuses on wisdom, balance, and holistic thinking.",
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
