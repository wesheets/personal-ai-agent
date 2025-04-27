"""
Registry Usage Examples
This module provides examples of how to use the Promethios Registry System.
"""
import os
from typing import List, Dict, Any

# Import registry components
from app.registries import (
    MODULE_REGISTRY, ENDPOINT_REGISTRY, SCHEMA_REGISTRY,
    find_module, find_modules_by_category,
    find_endpoint, find_endpoints_by_module,
    find_schema, find_schemas_by_module,
    get_system_stats, update_all_registries
)

def example_basic_registry_access():
    """Example of basic registry access."""
    print("=== Basic Registry Access ===")
    
    # Access module registry
    print(f"Total modules: {len(MODULE_REGISTRY.modules)}")
    if MODULE_REGISTRY.modules:
        print(f"First module: {MODULE_REGISTRY.modules[0].name} ({MODULE_REGISTRY.modules[0].category})")
    
    # Access endpoint registry
    print(f"Total endpoints: {len(ENDPOINT_REGISTRY.endpoints)}")
    if ENDPOINT_REGISTRY.endpoints:
        print(f"First endpoint: {ENDPOINT_REGISTRY.endpoints[0].method} {ENDPOINT_REGISTRY.endpoints[0].path}")
    
    # Access schema registry
    print(f"Total schemas: {len(SCHEMA_REGISTRY.schemas)}")
    if SCHEMA_REGISTRY.schemas:
        print(f"First schema: {SCHEMA_REGISTRY.schemas[0].name} in {SCHEMA_REGISTRY.schemas[0].file}")

def example_find_module():
    """Example of finding a module."""
    print("\n=== Finding Modules ===")
    
    # Find a specific module
    module_name = "modules/agent_runner.py"
    module = find_module(module_name)
    if module:
        print(f"Found module {module.name} in category {module.category} with status {module.status}")
    else:
        print(f"Module {module_name} not found")
    
    # Find modules by category
    category = "Agent System"
    modules = find_modules_by_category(category)
    print(f"Found {len(modules)} modules in category {category}")
    for i, module in enumerate(modules[:3]):  # Show first 3
        print(f"  {i+1}. {module.name}")
    if len(modules) > 3:
        print(f"  ... and {len(modules) - 3} more")

def example_find_endpoint():
    """Example of finding an endpoint."""
    print("\n=== Finding Endpoints ===")
    
    # Find a specific endpoint
    path = "/api/agent/analyze-prompt"
    method = "POST"
    endpoint = find_endpoint(path, method)
    if endpoint:
        print(f"Found endpoint {endpoint.method} {endpoint.path}")
        print(f"  Input schema: {endpoint.input_schema or 'None'}")
        print(f"  Output schema: {endpoint.output_schema or 'None'}")
        print(f"  Defined in: {endpoint.module}")
    else:
        print(f"Endpoint {method} {path} not found")
    
    # Find endpoints by module
    module_name = "routes/agent_routes.py"
    endpoints = find_endpoints_by_module(module_name)
    print(f"Found {len(endpoints)} endpoints in module {module_name}")
    for i, endpoint in enumerate(endpoints[:3]):  # Show first 3
        print(f"  {i+1}. {endpoint.method} {endpoint.path}")
    if len(endpoints) > 3:
        print(f"  ... and {len(endpoints) - 3} more")

def example_find_schema():
    """Example of finding a schema."""
    print("\n=== Finding Schemas ===")
    
    # Find a specific schema
    schema_name = "AgentConfig"
    schema = find_schema(schema_name)
    if schema:
        print(f"Found schema {schema.name} in {schema.file}")
        print(f"  Status: {schema.status}")
        print(f"  Used by {len(schema.used_by)} modules")
        for i, module in enumerate(schema.used_by[:3]):  # Show first 3
            print(f"    {i+1}. {module}")
        if len(schema.used_by) > 3:
            print(f"    ... and {len(schema.used_by) - 3} more")
    else:
        print(f"Schema {schema_name} not found")
    
    # Find schemas used by a module
    module_name = "routes/agent_routes.py"
    schemas = find_schemas_by_module(module_name)
    print(f"Found {len(schemas)} schemas used by module {module_name}")
    for i, schema in enumerate(schemas[:3]):  # Show first 3
        print(f"  {i+1}. {schema.name}")
    if len(schemas) > 3:
        print(f"  ... and {len(schemas) - 3} more")

def example_system_stats():
    """Example of getting system statistics."""
    print("\n=== System Statistics ===")
    
    stats = get_system_stats()
    print(f"Total modules: {stats['total_modules']}")
    print(f"  Active: {stats['active_modules']}")
    print(f"  Planned: {stats['planned_modules']}")
    print(f"  Scaffolded: {stats['scaffolded_modules']}")
    print(f"Total endpoints: {stats['total_endpoints']}")
    print(f"Total schemas: {stats['total_schemas']}")
    print(f"  Active: {stats['active_schemas']}")
    print(f"  Scaffolded: {stats['scaffolded_schemas']}")
    print("Module categories:")
    for i, category in enumerate(sorted(stats['module_categories'])):
        print(f"  {i+1}. {category}")

def example_update_registries():
    """Example of updating the registries."""
    print("\n=== Updating Registries ===")
    
    # This would normally update all registries
    # For this example, we'll just print what would happen
    print("Updating all registries...")
    print("This would scan the codebase for modules, endpoints, and schemas")
    print("and update the registries with the latest data.")
    
    # Uncomment to actually update the registries
    # result = update_all_registries()
    # print(f"Updated {result['modules']} modules, {result['endpoints']} endpoints, and {result['schemas']} schemas")

def example_custom_query():
    """Example of a custom query using the registries."""
    print("\n=== Custom Query: Find Endpoints Without Schemas ===")
    
    # Find all endpoints that don't have input schemas
    endpoints_without_schemas = [
        endpoint for endpoint in ENDPOINT_REGISTRY.endpoints
        if endpoint.input_schema is None and endpoint.method != "GET"
    ]
    
    print(f"Found {len(endpoints_without_schemas)} POST/PUT/DELETE endpoints without input schemas")
    for i, endpoint in enumerate(endpoints_without_schemas[:5]):  # Show first 5
        print(f"  {i+1}. {endpoint.method} {endpoint.path} in {endpoint.module}")
    if len(endpoints_without_schemas) > 5:
        print(f"  ... and {len(endpoints_without_schemas) - 5} more")

def run_all_examples():
    """Run all examples."""
    example_basic_registry_access()
    example_find_module()
    example_find_endpoint()
    example_find_schema()
    example_system_stats()
    example_update_registries()
    example_custom_query()

if __name__ == "__main__":
    run_all_examples()
