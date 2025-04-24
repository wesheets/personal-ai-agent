"""
Agent Configuration Module

This module implements the functionality for agent configuration management.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Configure logging
logger = logging.getLogger("agent_config")

# In-memory storage for agent configurations
# In a production environment, this would be stored in a database
_agent_configs: Dict[str, Dict[str, Any]] = {}

def set_agent_config(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set configuration for an agent.
    
    Args:
        config_data: Agent configuration data
        
    Returns:
        Dictionary containing the configuration result
    """
    try:
        agent_id = config_data.get("agent_id")
        if not agent_id:
            raise ValueError("Missing agent_id in configuration data")
        
        # Store the configuration
        _agent_configs[agent_id] = {
            "permissions": config_data.get("permissions", []),
            "fallback_behavior": config_data.get("fallback_behavior"),
            "memory_access_level": config_data.get("memory_access_level", "standard"),
            "custom_settings": config_data.get("custom_settings", {}),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Log the configuration update to memory
        _log_config_update(agent_id, config_data)
        
        # Return the result
        return {
            "agent_id": agent_id,
            "config_updated": True,
            "permissions_count": len(config_data.get("permissions", [])),
            "memory_access_level": config_data.get("memory_access_level", "standard"),
            "fallback_configured": config_data.get("fallback_behavior") is not None,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error setting agent configuration: {str(e)}")
        return {
            "message": f"Failed to update agent configuration: {str(e)}",
            "agent_id": config_data.get("agent_id"),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def get_agent_config(agent_id: str) -> Dict[str, Any]:
    """
    Get configuration for an agent.
    
    Args:
        agent_id: Unique identifier for the agent
        
    Returns:
        Dictionary containing the agent configuration
    """
    try:
        if not agent_id:
            raise ValueError("Missing agent_id")
        
        # Get the configuration
        config = _agent_configs.get(agent_id)
        if not config:
            # Return default configuration if not found
            return {
                "agent_id": agent_id,
                "permissions": [],
                "fallback_behavior": None,
                "memory_access_level": "standard",
                "custom_settings": {},
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Return the configuration
        return {
            "agent_id": agent_id,
            "permissions": config.get("permissions", []),
            "fallback_behavior": config.get("fallback_behavior"),
            "memory_access_level": config.get("memory_access_level", "standard"),
            "custom_settings": config.get("custom_settings", {}),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error getting agent configuration: {str(e)}")
        return {
            "message": f"Failed to get agent configuration: {str(e)}",
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def delete_agent_config(agent_id: str) -> Dict[str, Any]:
    """
    Delete configuration for an agent.
    
    Args:
        agent_id: Unique identifier for the agent
        
    Returns:
        Dictionary containing the deletion result
    """
    try:
        if not agent_id:
            raise ValueError("Missing agent_id")
        
        # Check if the configuration exists
        if agent_id not in _agent_configs:
            return {
                "agent_id": agent_id,
                "config_deleted": False,
                "message": "Configuration not found",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Delete the configuration
        del _agent_configs[agent_id]
        
        # Log the configuration deletion to memory
        _log_config_deletion(agent_id)
        
        # Return the result
        return {
            "agent_id": agent_id,
            "config_deleted": True,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error deleting agent configuration: {str(e)}")
        return {
            "message": f"Failed to delete agent configuration: {str(e)}",
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def _log_config_update(agent_id: str, config_data: Dict[str, Any]) -> None:
    """
    Log configuration update to memory.
    
    Args:
        agent_id: Unique identifier for the agent
        config_data: Agent configuration data
    """
    try:
        # In a real implementation, this would write to a memory service
        log_entry = {
            "agent_id": agent_id,
            "operation": "config_update",
            "timestamp": datetime.utcnow().isoformat(),
            "permissions_count": len(config_data.get("permissions", [])),
            "memory_access_level": config_data.get("memory_access_level", "standard"),
            "fallback_configured": config_data.get("fallback_behavior") is not None,
            "custom_settings_keys": list(config_data.get("custom_settings", {}).keys())
        }
        
        # Log to console for demonstration
        logger.info(f"Agent config update logged: {json.dumps(log_entry)}")
        print(f"Logged to memory: agent_config_update_{agent_id}")
    
    except Exception as e:
        logger.error(f"Error logging configuration update: {str(e)}")

def _log_config_deletion(agent_id: str) -> None:
    """
    Log configuration deletion to memory.
    
    Args:
        agent_id: Unique identifier for the agent
    """
    try:
        # In a real implementation, this would write to a memory service
        log_entry = {
            "agent_id": agent_id,
            "operation": "config_deletion",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log to console for demonstration
        logger.info(f"Agent config deletion logged: {json.dumps(log_entry)}")
        print(f"Logged to memory: agent_config_delete_{agent_id}")
    
    except Exception as e:
        logger.error(f"Error logging configuration deletion: {str(e)}")
