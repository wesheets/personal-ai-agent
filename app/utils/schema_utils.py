"""
Schema Utilities Module

This module provides utility functions for schema validation in the application.
It helps ensure that data structures conform to expected schemas, particularly
for project memory validation to prevent missing or malformed memory fields
from breaking agent logic, API request validation to prevent invalid requests,
agent role validation to ensure proper execution order, and loop structure validation
to ensure loop integrity.
"""

from typing import Dict, Any, List
from app.schema_registry import SCHEMA_REGISTRY

def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, str]:
    """
    Validates data against a schema definition.
    
    Args:
        data: The data to validate
        schema: The schema to validate against, with keys as field names and values as expected types
        
    Returns:
        Dictionary of validation errors, where keys are field names and values are error messages.
        Empty dictionary means validation passed.
    """
    errors = {}
    for key, expected_type in schema.items():
        if key not in data:
            errors[key] = "Missing"
        elif not isinstance(data[key], expected_type):
            errors[key] = f"Expected {expected_type.__name__}, got {type(data[key]).__name__}"
    return errors

def validate_project_memory(project_id: str, memory_store: Dict[str, Any]) -> Dict[str, str]:
    """
    Validates project memory against the expected schema.
    
    Args:
        project_id: The ID of the project to validate
        memory_store: The memory store containing project memories
        
    Returns:
        Dictionary of validation errors, where keys are field names and values are error messages.
        Empty dictionary means validation passed.
    """
    project_memory = memory_store.get(project_id, {})
    memory_schema = SCHEMA_REGISTRY["memory"]["project"]
    return validate_schema(project_memory, memory_schema)

def validate_api_request(path: str, method: str, payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Validates an API request against the expected schema.
    
    Args:
        path: The API endpoint path (e.g., "/api/agent/run")
        method: The HTTP method (e.g., "POST", "GET")
        payload: The request payload to validate
        
    Returns:
        Dictionary of validation errors, where keys are field names and values are error messages.
        Empty dictionary means validation passed.
    """
    from app.schema_registry import SCHEMA_REGISTRY
    api_def = SCHEMA_REGISTRY.get("api", {}).get(path)
    
    if not api_def:
        return {"error": "Path not found in schema"}
    
    if api_def["method"].lower() != method.lower():
        return {"error": f"Invalid method: expected {api_def['method']}"}
    
    return validate_schema(payload, api_def.get("input", {}))

def get_agent_schema(agent_name: str) -> dict:
    """
    Retrieves the schema definition for a specific agent.
    
    Args:
        agent_name: The name of the agent (e.g., "hal", "nova")
        
    Returns:
        Dictionary containing the agent's schema definition, or empty dict if not found
    """
    from app.schema_registry import SCHEMA_REGISTRY
    return SCHEMA_REGISTRY.get("agents", {}).get(agent_name, {})

def validate_agent_action(agent_name: str, project_memory: dict) -> Dict[str, str]:
    """
    Validates if an agent can be executed based on its dependencies.
    
    Args:
        agent_name: The name of the agent to validate
        project_memory: The project memory containing completed steps
        
    Returns:
        Dictionary of validation errors, where keys are dependency names and values are error messages.
        Empty dictionary means the agent can be executed.
    """
    schema = get_agent_schema(agent_name)
    errors = {}

    for dep in schema.get("dependencies", []):
        if dep not in project_memory.get("completed_steps", []):
            errors[dep] = f"Required dependency '{dep}' not completed"
    
    return errors

def get_loop_schema() -> dict:
    """
    Retrieves the schema definition for loop structure.
    
    Returns:
        Dictionary containing the loop structure schema definition
    """
    from app.schema_registry import SCHEMA_REGISTRY
    return SCHEMA_REGISTRY.get("loop", {})

def validate_loop_state(project_id: str, memory_store: dict) -> Dict[str, Any]:
    """
    Validates the loop state for a project against the expected schema.
    
    Args:
        project_id: The ID of the project to validate
        memory_store: The memory store containing project memories
        
    Returns:
        Dictionary of validation errors, where keys are error types and values are error details.
        Empty dictionary means the loop state is valid.
    """
    memory = memory_store.get(project_id, {})
    loop_schema = get_loop_schema()
    errors = {}

    # Validate required agents completed
    required = set(loop_schema.get("required_agents", []))
    completed = set(memory.get("completed_steps", []))
    missing = required - completed
    if missing:
        errors["missing_agents"] = list(missing)

    # Validate loop exit conditions
    if memory.get("loop_count", 0) >= loop_schema.get("max_loops", 5):
        errors["loop_depth_exceeded"] = f"{memory.get('loop_count')} >= {loop_schema['max_loops']}"
    
    if memory.get("loop_complete", False):
        errors["loop_marked_complete"] = "Loop is already marked complete"

    return errors
