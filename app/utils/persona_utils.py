"""
Persona Utilities Module

This module provides utility functions for persona validation and management.
"""

from typing import Optional, List, Dict, Any
from app.memory.project_memory import get_project_memory, update_project_memory

# Define valid personas
VALID_PERSONAS = ["SAGE", "ARCHITECT", "RESEARCHER", "RITUALIST", "INVENTOR"]

def validate_persona(persona: str) -> bool:
    """
    Validate if a persona is in the allowed list.
    
    Args:
        persona: The persona to validate
        
    Returns:
        True if valid, False otherwise
    """
    return persona in VALID_PERSONAS

def get_persona_description(persona: str) -> str:
    """
    Get the description for a specific persona.
    
    Args:
        persona: The persona to get description for
        
    Returns:
        The persona description
    """
    persona_descriptions = {
        "SAGE": "The SAGE persona focuses on wisdom, balance, and holistic thinking.",
        "ARCHITECT": "The ARCHITECT persona focuses on structure, systems, and design thinking.",
        "RESEARCHER": "The RESEARCHER persona focuses on inquiry, analysis, and evidence-based reasoning.",
        "RITUALIST": "The RITUALIST persona focuses on process, tradition, and methodical approaches.",
        "INVENTOR": "The INVENTOR persona focuses on creativity, innovation, and novel solutions."
    }
    
    return persona_descriptions.get(persona, "No description available.")

def get_current_persona(loop_id: Optional[str] = None) -> str:
    """
    Get the current persona for a specific loop or the default.
    
    Args:
        loop_id: Optional loop ID to get persona for
        
    Returns:
        The current persona
    """
    default_persona = "SAGE"
    
    if not loop_id:
        return default_persona
    
    try:
        # Try to get the current persona from memory
        loop_trace = get_project_memory(loop_id)
        if "orchestrator_persona" in loop_trace:
            return loop_trace["orchestrator_persona"]
    except KeyError:
        # If loop doesn't exist in memory, use default
        pass
    
    return default_persona

def set_persona_for_loop(loop_id: str, persona: str, reason: str = "auto") -> bool:
    """
    Set the persona for a specific loop.
    
    Args:
        loop_id: The loop ID to set persona for
        persona: The persona to set
        reason: The reason for setting the persona
        
    Returns:
        True if successful, False otherwise
    """
    if not validate_persona(persona):
        return False
    
    try:
        update_project_memory(loop_id, "orchestrator_persona", persona)
        update_project_memory(loop_id, "persona_switch_reason", reason)
        return True
    except KeyError:
        # If loop doesn't exist in memory, create it
        try:
            update_project_memory(loop_id, "orchestrator_persona", persona)
            update_project_memory(loop_id, "persona_switch_reason", reason)
            return True
        except Exception:
            return False

def preload_persona_for_deep_loop(loop_id: str, rerun_depth: int) -> str:
    """
    Preload persona for a deep loop.
    
    If no persona is set and depth is "deep" (rerun_depth > 0),
    default to SAGE.
    
    Args:
        loop_id: The loop ID to preload persona for
        rerun_depth: The rerun depth of the loop
        
    Returns:
        The persona that was set
    """
    if rerun_depth <= 0:
        return get_current_persona(loop_id)
    
    # For deep loops, check if persona is already set
    current_persona = get_current_persona(loop_id)
    
    # If no persona is set for a deep loop, default to SAGE
    if current_persona is None:
        set_persona_for_loop(loop_id, "SAGE", "deep_loop_default")
        return "SAGE"
    
    return current_persona
