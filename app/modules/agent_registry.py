"""
Agent Registry Module

This module provides a centralized registry for all agents in the system.
It allows for plug-and-play architecture where agents can be registered
and accessed through a unified interface.
"""

from typing import Dict, Any, Callable, List, Optional

# The central agent registry dictionary
AGENT_REGISTRY = {}

def register_agent(agent_id: str, handler_fn: Callable) -> None:
    """
    Register an agent with the central registry.
    
    Args:
        agent_id: The unique identifier for the agent
        handler_fn: The function that handles agent execution
    """
    AGENT_REGISTRY[agent_id] = handler_fn
    print(f"✅ Registered agent: {agent_id}")

def get_registered_agent(agent_id: str) -> Optional[Callable]:
    """
    Get an agent handler function from the registry.
    
    Args:
        agent_id: The unique identifier for the agent
        
    Returns:
        The agent handler function, or None if not found
    """
    return AGENT_REGISTRY.get(agent_id)

def list_agents() -> List[str]:
    """
    List all registered agents.
    
    Returns:
        A list of agent identifiers
    """
    return list(AGENT_REGISTRY.keys())
