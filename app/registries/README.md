# Promethios Registry System

This document provides an overview of the Promethios Registry System, which is designed to track and organize modules, endpoints, and schemas across the codebase.

## Overview

The Registry System consists of three main components:

1. **Module Registry** - Tracks all modules in the system
2. **Endpoint Registry** - Tracks all FastAPI endpoints in the system
3. **Schema Registry** - Tracks all Pydantic schemas used in the system

Each registry is implemented as a Pydantic model for validation and type safety, ensuring that all registry entries follow a consistent structure.

## Registry Components

### Module Registry

The Module Registry tracks all Python modules in the system, categorizing them and tracking their implementation status.

```python
# Example Module Registry Entry
ModuleEntry(
    name="modules/agent_runner.py",
    category="Agent System",
    status="active"
)
```

Fields:
- `name`: Path to the module file relative to the app directory
- `category`: Category of the module (e.g., "Agent System", "Utilities", "Routing")
- `status`: Implementation status ("active", "planned", or "scaffolded")

### Endpoint Registry

The Endpoint Registry tracks all FastAPI endpoints in the system, including their HTTP methods, paths, and associated schemas.

```python
# Example Endpoint Registry Entry
EndpointEntry(
    path="/api/agent/analyze-prompt",
    method="POST",
    input_schema="PromptAnalysisRequest",
    output_schema="PromptAnalysisResponse",
    module="routes/agent_routes.py"
)
```

Fields:
- `path`: URL path of the endpoint
- `method`: HTTP method (GET, POST, PUT, DELETE, etc.)
- `input_schema`: Name of the input schema (if any)
- `output_schema`: Name of the output schema (if any)
- `module`: Path to the module file that defines the endpoint

### Schema Registry

The Schema Registry tracks all Pydantic schemas in the system, including their implementation status and usage.

```python
# Example Schema Registry Entry
SchemaEntry(
    name="PromptAnalysisRequest",
    file="schemas/agent_schema.py",
    status="active",
    used_by=["routes/agent_routes.py", "modules/agent_runner.py"]
)
```

Fields:
- `name`: Name of the schema class
- `file`: Path to the file that defines the schema
- `status`: Implementation status ("active" or "scaffolded")
- `used_by`: List of modules that use this schema

## Using the Registry System

### Importing the Registries

```python
from app.registries import MODULE_REGISTRY, ENDPOINT_REGISTRY, SCHEMA_REGISTRY
```

### Accessing Registry Data

```python
# Get all modules
all_modules = MODULE_REGISTRY.modules

# Get all endpoints
all_endpoints = ENDPOINT_REGISTRY.endpoints

# Get all schemas
all_schemas = SCHEMA_REGISTRY.schemas
```

### Using Registry Utilities

The registry system includes utility functions to help you work with the registries:

```python
from app.registries import (
    find_module, find_modules_by_category,
    find_endpoint, find_endpoints_by_module,
    find_schema, find_schemas_by_module,
    get_system_stats
)

# Find a specific module
agent_runner = find_module("modules/agent_runner.py")

# Find all modules in a category
agent_modules = find_modules_by_category("Agent System")

# Find a specific endpoint
endpoint = find_endpoint("/api/agent/analyze-prompt", "POST")

# Find all endpoints in a module
agent_endpoints = find_endpoints_by_module("routes/agent_routes.py")

# Find a specific schema
schema = find_schema("PromptAnalysisRequest")

# Find all schemas used by a module
module_schemas = find_schemas_by_module("routes/agent_routes.py")

# Get system statistics
stats = get_system_stats()
```

### Updating the Registries

The registry system includes functions to scan the codebase and update the registries:

```python
from app.registries import update_all_registries

# Update all registries
result = update_all_registries()
print(f"Updated {result['modules']} modules, {result['endpoints']} endpoints, and {result['schemas']} schemas")
```

You can also update individual registries:

```python
from app.registries import scan_modules, scan_endpoints, scan_schemas

# Update the module registry
MODULE_REGISTRY.modules = scan_modules()

# Update the endpoint registry
ENDPOINT_REGISTRY.endpoints = scan_endpoints()

# Update the schema registry
SCHEMA_REGISTRY.schemas = scan_schemas()
```

## Best Practices

1. **Keep Registries Updated**: Run `update_all_registries()` periodically to ensure the registries reflect the current state of the codebase.

2. **Use Registry Utilities**: Use the provided utility functions instead of directly accessing the registry data structures.

3. **Validate New Entries**: When manually adding entries to the registries, use the provided Pydantic models to ensure the entries are valid.

4. **Check for Consistency**: Use the registry system to check for consistency between modules, endpoints, and schemas.

## Implementation Details

The registry system is implemented in the following files:

- `app/registries/module_registry.py` - Module registry implementation
- `app/registries/endpoint_registry.py` - Endpoint registry implementation
- `app/registries/schema_registry.py` - Schema registry implementation
- `app/registries/registry_utils.py` - Utility functions for working with registries
- `app/registries/registry_init.py` - Functions for initializing and updating registries
- `app/registries/__init__.py` - Package initialization and exports

Each registry is implemented as a Pydantic model for validation and type safety, ensuring that all registry entries follow a consistent structure.
