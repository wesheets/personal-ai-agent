"""
Central registry for agents, capabilities, and toolkits.
"""

import inspect
from enum import Enum
from typing import Callable, Dict, List, Type

# Agent Capabilities Enum
class AgentCapability(Enum):
    ARCHITECTURE = "architecture"
    MEMORY_WRITE = "memory_write"
    PLANNING = "planning"
    CODE_GENERATION = "code_generation"
    VALIDATION = "validation"
    FILE_READ = "file_read"
    RISK_ASSESSMENT = "risk_assessment" # Added for Pessimist Agent
    # Add more capabilities as needed

# Agent Registry
agent_registry: Dict[str, Dict] = {}

# Toolkit Registry (Placeholder for now)
toolkit_registry: Dict[str, Callable] = {}

def register(key: str, name: str, capabilities: List[AgentCapability]):
    """Decorator to register agents in the central registry."""
    def decorator(cls):
        if key in agent_registry:
            print(f"Warning: Agent key 	'{key}	' already registered. Overwriting.")
        
        agent_info = {
            "name": name,
            "class": cls,
            "capabilities": [cap.value for cap in capabilities],
            "signature": inspect.signature(cls.run) if hasattr(cls, 'run') else None # Store signature for validation
        }
        agent_registry[key] = agent_info
        print(f"Registered agent: {name} with key 	'{key}	'")
        return cls
    return decorator

def get_agent(key: str) -> Type | None:
    """Retrieve an agent class from the registry by key."""
    agent_info = agent_registry.get(key)
    return agent_info["class"] if agent_info else None

def list_agents() -> Dict[str, Dict]:
    """List all registered agents and their details."""
    return agent_registry

# Example of registering a toolkit function (if needed later)
# def register_tool(key: str):
#     def decorator(func):
#         if key in toolkit_registry:
#             print(f"Warning: Tool key 	'{key}	' already registered. Overwriting.")
#         toolkit_registry[key] = func
#         print(f"Registered tool: {key}")
#         return func
#     return decorator

