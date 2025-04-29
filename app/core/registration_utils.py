# app/core/registration_utils.py
import functools
import logging
from typing import List, Type

# Import the registry dictionary from the main registry file
from app.core.agent_registry import AGENT_REGISTRY
from app.core.agent_types import AgentCapability
from app.core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

def register(key: str, name: str, capabilities: List[AgentCapability]):
    """Decorator to register agent classes in the AGENT_REGISTRY."""
    def decorator(cls: Type[BaseAgent]):
        if not issubclass(cls, BaseAgent):
            raise TypeError("Registered class must be a subclass of BaseAgent")
        
        if key in AGENT_REGISTRY:
            logger.warning(f"Agent key ", key, " already exists. Overwriting registration.")

        # Basic validation for required schemas (can be enhanced)
        if not hasattr(cls, 'input_schema') or not hasattr(cls, 'output_schema'):
             logger.warning(f"Agent ", name, " (", key, ") is missing input_schema or output_schema definition.")

        AGENT_REGISTRY[key] = {
            "key": key,
            "name": name,
            "class": cls,
            "capabilities": capabilities,
            "input_schema": getattr(cls, 'input_schema', None),
            "output_schema": getattr(cls, 'output_schema', None),
            "description": cls.__doc__ or "No description provided."
        }
        logger.info(f"✅ Registered agent: ", name, " (", key, ")")
        
        @functools.wraps(cls)
        def wrapper(*args, **kwargs):
            return cls(*args, **kwargs)
        return wrapper
    return decorator

