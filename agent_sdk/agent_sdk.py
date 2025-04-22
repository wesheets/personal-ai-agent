"""
Agent SDK Module

This module provides a standardized interface for creating and registering agents
in the Promethios system. It ensures all agents follow the same structure and
are properly registered in the plugin system.
"""

import json
import os
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime

class Agent:
    """
    Base class for all agents in the Promethios system.
    
    This class provides a standardized interface for creating agents with
    proper registration, schema validation, and memory integration.
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        tools: List[str],
        permissions: List[str],
        description: str = "",
        version: str = "1.0.0",
        status: str = "active",
        tone_profile: Optional[Dict[str, str]] = None,
        schema_path: Optional[str] = None
    ):
        """
        Initialize a new agent.
        
        Args:
            name (str): Unique identifier for the agent
            role (str): Human-readable description of the agent's role
            tools (List[str]): List of tools the agent can use
            permissions (List[str]): List of permissions the agent has
            description (str, optional): Detailed description of the agent
            version (str, optional): Version of the agent
            status (str, optional): Status of the agent (active, experimental)
            tone_profile (Dict[str, str], optional): Tone profile for the agent
            schema_path (str, optional): Path to the agent's output schema
        """
        self.name = name
        self.role = role
        self.tools = tools
        self.permissions = permissions
        self.description = description
        self.version = version
        self.status = status
        self.tone_profile = tone_profile or {
            "style": "neutral",
            "emotion": "neutral",
            "vibe": "professional",
            "persona": f"{role} specialist"
        }
        self.schema_path = schema_path
        self.registered = False
        self.trust_score = 1.0
        self.last_active = ""
        
        # Register the agent
        self.register()
    
    def register(self) -> bool:
        """
        Register the agent with the plugin system.
        
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            from app.modules.agent_registry import register_agent
            
            # Create handler function that will be called by the plugin system
            def handler_fn(*args, **kwargs):
                return self.execute(*args, **kwargs)
            
            # Register the agent
            register_agent(self.name, handler_fn)
            self.registered = True
            
            # Update agent manifest
            self._update_agent_manifest()
            
            return True
        except Exception as e:
            print(f"Failed to register agent {self.name}: {str(e)}")
            return False
    
    def _update_agent_manifest(self) -> None:
        """
        Update the agent manifest with this agent's information.
        """
        try:
            manifest_path = os.path.join("config", "agent_manifest.json")
            
            # Create manifest if it doesn't exist
            if not os.path.exists(manifest_path):
                os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
                with open(manifest_path, "w") as f:
                    json.dump({}, f, indent=2)
            
            # Read existing manifest
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            
            # Update manifest with this agent's information
            manifest[self.name] = {
                "version": self.version,
                "description": self.description,
                "status": self.status,
                "entrypoint": f"app/agents/{self.name.lower().replace('-', '_')}.py",
                "tone_profile": self.tone_profile,
                "skills": self.tools
            }
            
            # Write updated manifest
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
        except Exception as e:
            print(f"Failed to update agent manifest for {self.name}: {str(e)}")
    
    def validate_schema(self, output: Dict[str, Any]) -> bool:
        """
        Validate the agent's output against its schema.
        
        Args:
            output (Dict[str, Any]): The output to validate
            
        Returns:
            bool: True if validation was successful, False otherwise
        """
        if not self.schema_path:
            # No schema to validate against
            return True
        
        try:
            import jsonschema
            
            # Read schema
            with open(self.schema_path, "r") as f:
                schema = json.load(f)
            
            # Validate output against schema
            jsonschema.validate(output, schema)
            return True
        except Exception as e:
            print(f"Schema validation failed for {self.name}: {str(e)}")
            return False
    
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        This method should be overridden by subclasses.
        
        Returns:
            Dict[str, Any]: The agent's output
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def update_memory(self, memory: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update memory with the agent's output.
        
        Args:
            memory (Dict[str, Any]): The current memory state
            output (Dict[str, Any]): The agent's output
            
        Returns:
            Dict[str, Any]: The updated memory state
        """
        # Validate output against schema
        if not self.validate_schema(output):
            raise ValueError(f"Output from {self.name} failed schema validation")
        
        # Update memory with output
        if self.name not in memory:
            memory[self.name] = []
        
        # Add timestamp to output
        output["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Add output to memory
        memory[self.name].append(output)
        
        return memory
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the agent
        """
        return {
            "name": self.name,
            "role": self.role,
            "tools": self.tools,
            "permissions": self.permissions,
            "description": self.description,
            "version": self.version,
            "status": self.status,
            "tone_profile": self.tone_profile,
            "schema_path": self.schema_path,
            "registered": self.registered,
            "trust_score": self.trust_score,
            "last_active": self.last_active
        }

def register_legacy_agent(
    name: str,
    handler_fn: Callable,
    tools: List[str],
    permissions: List[str],
    description: str = "",
    version: str = "1.0.0",
    status: str = "active",
    tone_profile: Optional[Dict[str, str]] = None,
    schema_path: Optional[str] = None
) -> Agent:
    """
    Register a legacy agent function with the plugin system.
    
    This function creates an Agent instance that wraps the legacy handler function.
    
    Args:
        name (str): Unique identifier for the agent
        handler_fn (Callable): The legacy handler function
        tools (List[str]): List of tools the agent can use
        permissions (List[str]): List of permissions the agent has
        description (str, optional): Detailed description of the agent
        version (str, optional): Version of the agent
        status (str, optional): Status of the agent (active, experimental)
        tone_profile (Dict[str, str], optional): Tone profile for the agent
        schema_path (str, optional): Path to the agent's output schema
        
    Returns:
        Agent: The created Agent instance
    """
    class LegacyAgent(Agent):
        def execute(self, *args, **kwargs):
            return handler_fn(*args, **kwargs)
    
    return LegacyAgent(
        name=name,
        role=description or f"{name} agent",
        tools=tools,
        permissions=permissions,
        description=description,
        version=version,
        status=status,
        tone_profile=tone_profile,
        schema_path=schema_path
    )

def validate_schema(output: Dict[str, Any], schema_path: str) -> bool:
    """
    Validate output against a schema.
    
    This is a standalone function for use in legacy code.
    
    Args:
        output (Dict[str, Any]): The output to validate
        schema_path (str): Path to the schema file
        
    Returns:
        bool: True if validation was successful, False otherwise
    """
    try:
        import jsonschema
        
        # Read schema
        with open(schema_path, "r") as f:
            schema = json.load(f)
        
        # Validate output against schema
        jsonschema.validate(output, schema)
        return True
    except Exception as e:
        print(f"Schema validation failed: {str(e)}")
        return False
