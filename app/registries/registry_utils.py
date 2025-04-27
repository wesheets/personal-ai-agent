"""
Registry Utilities
This module provides utility functions for working with the Promethios registries.
"""
from typing import List, Dict, Optional, Any, Union
from .module_registry import MODULE_REGISTRY, ModuleEntry
from .endpoint_registry import ENDPOINT_REGISTRY, EndpointEntry
from .schema_registry import SCHEMA_REGISTRY, SchemaEntry

def find_module(module_name: str) -> Optional[ModuleEntry]:
    """Find a module by name.

    Args:
        module_name: Name of the module to find

    Returns:
        ModuleEntry if found, None otherwise
    """
    for module in MODULE_REGISTRY.modules:
        if module.name == module_name:
            return module
    return None

def find_modules_by_category(category: str) -> List[ModuleEntry]:
    """Find all modules in a specific category.

    Args:
        category: Category to filter by

    Returns:
        List of ModuleEntry objects in the specified category
    """
    return [module for module in MODULE_REGISTRY.modules if module.category == category]

def find_endpoint(path: str, method: str) -> Optional[EndpointEntry]:
    """Find an endpoint by path and method.

    Args:
        path: Path of the endpoint
        method: HTTP method of the endpoint

    Returns:
        EndpointEntry if found, None otherwise
    """
    for endpoint in ENDPOINT_REGISTRY.endpoints:
        if endpoint.path == path and endpoint.method == method:
            return endpoint
    return None

def find_endpoints_by_module(module_name: str) -> List[EndpointEntry]:
    """Find all endpoints in a specific module.

    Args:
        module_name: Name of the module

    Returns:
        List of EndpointEntry objects in the specified module
    """
    return [endpoint for endpoint in ENDPOINT_REGISTRY.endpoints if endpoint.module == module_name]

def find_schema(schema_name: str) -> Optional[SchemaEntry]:
    """Find a schema by name.

    Args:
        schema_name: Name of the schema to find

    Returns:
        SchemaEntry if found, None otherwise
    """
    for schema in SCHEMA_REGISTRY.schemas:
        if schema.name == schema_name:
            return schema
    return None

def find_schemas_by_module(module_name: str) -> List[SchemaEntry]:
    """Find all schemas used by a specific module.

    Args:
        module_name: Name of the module

    Returns:
        List of SchemaEntry objects used by the specified module
    """
    return [schema for schema in SCHEMA_REGISTRY.schemas if module_name in schema.used_by]

def get_system_stats() -> Dict[str, Any]:
    """Get statistics about the Promethios system.

    Returns:
        Dictionary with system statistics
    """
    active_modules = sum(1 for module in MODULE_REGISTRY.modules if module.status == "active")
    planned_modules = sum(1 for module in MODULE_REGISTRY.modules if module.status == "planned")
    scaffolded_modules = sum(1 for module in MODULE_REGISTRY.modules if module.status == "scaffolded")
    
    active_schemas = sum(1 for schema in SCHEMA_REGISTRY.schemas if schema.status == "active")
    scaffolded_schemas = sum(1 for schema in SCHEMA_REGISTRY.schemas if schema.status == "scaffolded")
    
    return {
        "total_modules": len(MODULE_REGISTRY.modules),
        "active_modules": active_modules,
        "planned_modules": planned_modules,
        "scaffolded_modules": scaffolded_modules,
        "total_endpoints": len(ENDPOINT_REGISTRY.endpoints),
        "total_schemas": len(SCHEMA_REGISTRY.schemas),
        "active_schemas": active_schemas,
        "scaffolded_schemas": scaffolded_schemas,
        "module_categories": list(set(module.category for module in MODULE_REGISTRY.modules))
    }
