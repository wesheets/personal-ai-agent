"""
Agent SDK Module

This module provides the standardized interface for creating and registering agents
with proper schema validation and memory integration.
"""

import json
import logging
import os
import datetime
from typing import Dict, List, Any, Optional
import jsonschema

# Configure logging
logger = logging.getLogger("agent_sdk")

class Agent:
    """
    Base class for all agents in the Promethios system.
    
    This class provides standardized methods for agent registration,
    schema validation, and memory integration.
    """
    
    def __init__(self, 
                 name: str,
                 role: str,
                 tools: List[str],
                 permissions: List[str],
                 description: str,
                 version: str = "1.0.0",
                 status: str = "active",
                 tone_profile: Dict[str, str] = None,
                 schema_path: str = None,
                 trust_score: float = 0.8,
                 contract_version: str = "1.0.0"):
        """
        Initialize an agent with required configuration.
        
        Args:
            name: Unique identifier for the agent
            role: Role description for the agent
            tools: List of tools the agent can use
            permissions: List of permissions the agent has
            description: Detailed description of the agent's purpose
            version: Agent version
            status: Agent status (active, inactive, deprecated)
            tone_profile: Dictionary of tone settings for the agent
            schema_path: Path to the schema file for output validation
            trust_score: Trust score for the agent (0.0 to 1.0)
            contract_version: Version of the agent contract
        """
        self.name = name
        self.role = role
        self.tools = tools
        self.permissions = permissions
        self.description = description
        self.version = version
        self.status = status
        self.tone_profile = tone_profile or {}
        self.schema_path = schema_path
        self.trust_score = trust_score
        self.contract_version = contract_version
        self.schema = None
        
        # Load schema if provided
        if schema_path:
            self._load_schema()
        
        # Register the agent
        self._register()
    
    def _load_schema(self) -> None:
        """Load the schema from the specified path."""
        try:
            schema_file = os.path.join(os.getcwd(), self.schema_path)
            if os.path.exists(schema_file):
                with open(schema_file, 'r') as f:
                    self.schema = json.load(f)
                logger.info(f"Loaded schema from {schema_file}")
            else:
                logger.warning(f"Schema file not found: {schema_file}")
        except Exception as e:
            logger.error(f"Error loading schema: {str(e)}")
    
    def _register(self) -> None:
        """Register the agent with the system."""
        logger.info(f"Registering agent: {self.name}")
        # In a real implementation, this would register with a central registry
        print(f"🟢 Registered agent: {self.name} (role: {self.role})")
    
    def validate_schema(self, data: Dict[str, Any]) -> bool:
        """
        Validate data against the agent's schema.
        
        Args:
            data: Data to validate
            
        Returns:
            True if validation succeeds, False otherwise
        """
        if not self.schema:
            logger.warning(f"No schema loaded for agent {self.name}")
            return True
        
        try:
            jsonschema.validate(instance=data, schema=self.schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error during schema validation: {str(e)}")
            return False
    
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        This method should be overridden by subclasses.
        
        Returns:
            Result of the agent's execution
        """
        raise NotImplementedError("Subclasses must implement execute()")

# Function to validate schema without an agent instance
def validate_schema(data: Dict[str, Any], schema_path: str) -> bool:
    """
    Validate data against a schema.
    
    Args:
        data: Data to validate
        schema_path: Path to the schema file
        
    Returns:
        True if validation succeeds, False otherwise
    """
    try:
        schema_file = os.path.join(os.getcwd(), schema_path)
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                schema = json.load(f)
            
            jsonschema.validate(instance=data, schema=schema)
            return True
        else:
            logger.warning(f"Schema file not found: {schema_file}")
            return False
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Schema validation failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error during schema validation: {str(e)}")
        return False
