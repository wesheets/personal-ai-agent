"""
Schema Utilities Module

This module provides utility functions for schema validation in the application.
It helps ensure that data structures conform to expected schemas, particularly
for project memory validation to prevent missing or malformed memory fields
from breaking agent logic.
"""

from typing import Dict, Any
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
