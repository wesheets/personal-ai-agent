# app/core/registration_utils.py
import functools
import logging
from typing import List, Type

# Import the enhanced registry function
from app.core.agent_registry_enhanced import register_agent_with_contract
from app.core.agent_types import AgentCapability
from app.core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

def register(key: str, name: str, capabilities: List[AgentCapability]):
    """Decorator to register agent classes using the enhanced registry with contract enforcement."""
    def decorator(cls: Type[BaseAgent]):
        if not issubclass(cls, BaseAgent):
            raise TypeError("Registered class must be a subclass of BaseAgent")
        

        # Basic validation for required schemas (can be enhanced)
        if not hasattr(cls, 'input_schema') or not hasattr(cls, 'output_schema'):
             logger.warning(f"Agent ", name, " (", key, ") is missing input_schema or output_schema definition.")

        # Prepare agent data for enhanced registration
        agent_data = {
            "key": key,
            "name": name,
            "class": cls,
            "capabilities": capabilities,
            "input_schema": getattr(cls, 'input_schema', None),
            "output_schema": getattr(cls, 'output_schema', None),
            "description": cls.__doc__ or "No description provided."
        }
        
        # Call the enhanced registration function
        if not register_agent_with_contract(agent_id=key, agent_data=agent_data):
            logger.error(f"❌ Failed to register agent: {name} ({key}) using enhanced registry")
        # Note: The enhanced function handles its own logging on success/failure
        
        @functools.wraps(cls)
        def wrapper(*args, **kwargs):
            return cls(*args, **kwargs)
        return wrapper
    return decorator

