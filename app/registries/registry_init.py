"""
Registry Initialization System
This module provides functions to automatically populate the Promethios registries.
"""
import os
import re
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel

from .module_registry import MODULE_REGISTRY, ModuleEntry
from .endpoint_registry import ENDPOINT_REGISTRY, EndpointEntry
from .schema_registry import SCHEMA_REGISTRY, SchemaEntry

def scan_modules(base_dir: str = None) -> List[ModuleEntry]:
    """Scan the codebase for modules and return a list of ModuleEntry objects.

    Args:
        base_dir: Base directory to scan (defaults to app directory)

    Returns:
        List of ModuleEntry objects
    """
    if base_dir is None:
        # Default to the app directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    module_dirs = [
        os.path.join(base_dir, "modules"),
        os.path.join(base_dir, "api"),
        os.path.join(base_dir, "utils"),
        os.path.join(base_dir, "routes")
    ]
    
    modules = []
    
    for directory in module_dirs:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, base_dir)
                        
                        try:
                            with open(file_path, "r") as f:
                                content = f.read()
                            
                            category = _determine_module_category(file_path, content)
                            status = _determine_module_status(content)
                            
                            modules.append(ModuleEntry(
                                name=rel_path,
                                category=category,
                                status=status
                            ))
                        except Exception as e:
                            print(f"Error processing {file_path}: {str(e)}")
    
    return sorted(modules, key=lambda x: x.name)

def _determine_module_category(file_path: str, content: str) -> str:
    """Determine the category of a module based on filename and content.

    Args:
        file_path: Path to the module file
        content: Content of the module file

    Returns:
        Category of the module
    """
    filename = os.path.basename(file_path)
    
    # Category mapping based on filename patterns
    category_patterns = {
        r"agent_": "Agent System",
        r"memory_": "Memory System",
        r"schema_": "Schema System",
        r"config_": "Configuration",
        r"util": "Utilities",
        r"helper": "Utilities",
        r"router": "Routing",
        r"route": "Routing",
        r"api_": "API",
        r"auth": "Authentication",
        r"db_": "Database",
        r"storage": "Storage",
        r"log": "Logging",
        r"monitor": "Monitoring",
        r"test": "Testing",
        r"validator": "Validation",
        r"middleware": "Middleware",
        r"plugin": "Plugins",
        r"integration": "Integrations",
        r"orchestrat": "Orchestration",
        r"reflect": "Reflection",
        r"drift": "Drift Monitoring",
        r"critic": "Critic System",
        r"ceo": "CEO System",
        r"cto": "CTO System",
        r"ash": "ASH System",
    }
    
    # Check for category in docstring
    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if docstring_match:
        docstring = docstring_match.group(1).lower()
        for keyword, category in category_patterns.items():
            if keyword.lower() in docstring:
                return category
    
    # Check filename patterns
    for pattern, category in category_patterns.items():
        if re.search(pattern, filename, re.IGNORECASE):
            return category
    
    # Default category
    return "Core System"

def _determine_module_status(content: str) -> str:
    """Determine the status of a module based on its content.

    Args:
        content: Content of the module file

    Returns:
        Status of the module (active, planned, or scaffolded)
    """
    # Check if the module has actual implementation or is just scaffolded
    if "pass" in content and len(content.strip().split("\n")) < 10:
        return "scaffolded"
    elif "TODO" in content or "FIXME" in content or "NotImplementedError" in content:
        return "planned"
    else:
        return "active"

def scan_endpoints(base_dir: str = None) -> List[EndpointEntry]:
    """Scan the codebase for endpoints and return a list of EndpointEntry objects.

    Args:
        base_dir: Base directory to scan (defaults to app directory)

    Returns:
        List of EndpointEntry objects
    """
    if base_dir is None:
        # Default to the app directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    endpoint_dirs = [
        os.path.join(base_dir, "routes"),
        os.path.join(base_dir, "modules")
    ]
    
    endpoints = []
    
    for directory in endpoint_dirs:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        file_path = os.path.join(root, file)
                        endpoints.extend(_extract_endpoints(file_path, base_dir))
    
    return sorted(endpoints, key=lambda x: x.path)

def _extract_endpoints(file_path: str, base_dir: str) -> List[EndpointEntry]:
    """Extract endpoints from a file.

    Args:
        file_path: Path to the file
        base_dir: Base directory for relative paths

    Returns:
        List of EndpointEntry objects
    """
    endpoints = []
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
        
        # Look for router definition
        router_match = re.search(r"router\s*=\s*APIRouter\(.*?\)", content, re.DOTALL)
        if not router_match:
            return []
        
        # Extract router prefix if any
        prefix = ""
        prefix_match = re.search(r"prefix\s*=\s*[\'\"](.*?)[\'\"]", router_match.group(0))
        if prefix_match:
            prefix = prefix_match.group(1)
            if not prefix.startswith("/"):
                prefix = "/" + prefix
        
        # Find all route decorators
        route_patterns = [
            r"@router\.(get|post|put|delete|patch)\s*\(\s*[\'\"](.*?)[\'\"]",
            r"@router\.route\s*\(\s*[\'\"](.*?)[\'\"].*?methods=\[[\'\"]*([A-Z]+)[\'\"]*"
        ]
        
        for pattern in route_patterns:
            for match in re.finditer(pattern, content):
                if len(match.groups()) == 2:
                    method, path = match.groups()
                    method = method.upper()
                else:
                    path, method = match.groups()
                
                if not path.startswith("/"):
                    path = "/" + path
                
                full_path = prefix + path
                
                # Find the function definition following this decorator
                func_name_match = re.search(r"def\s+([a-zA-Z0-9_]+)\s*\(", content[match.end():])
                if func_name_match:
                    func_name = func_name_match.group(1)
                    
                    # Try to find input and output schemas
                    input_schema = None
                    output_schema = None
                    
                    # Look for function parameters with type hints
                    func_def = content[match.end():match.end() + 500]  # Look at next 500 chars
                    param_match = re.search(r"\(\s*(.*?)\s*\)", func_def)
                    if param_match:
                        params = param_match.group(1)
                        # Look for Pydantic models in parameters
                        schema_matches = re.finditer(r"([a-zA-Z0-9_]+)\s*:\s*([a-zA-Z0-9_]+)", params)
                        for schema_match in schema_matches:
                            param_name, type_name = schema_match.groups()
                            if type_name not in ["str", "int", "float", "bool", "list", "dict", "Any", "Optional"]:
                                input_schema = type_name
                                break
                    
                    # Look for return type annotation
                    return_match = re.search(r"->\s*([a-zA-Z0-9_]+)", func_def)
                    if return_match:
                        output_schema = return_match.group(1)
                    
                    # Add endpoint to list
                    endpoints.append(EndpointEntry(
                        path=full_path,
                        method=method,
                        input_schema=input_schema,
                        output_schema=output_schema,
                        module=os.path.relpath(file_path, base_dir)
                    ))
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
    
    return endpoints

def scan_schemas(base_dir: str = None) -> List[SchemaEntry]:
    """Scan the codebase for schemas and return a list of SchemaEntry objects.

    Args:
        base_dir: Base directory to scan (defaults to app directory)

    Returns:
        List of SchemaEntry objects
    """
    if base_dir is None:
        # Default to the app directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    schema_dirs = [
        os.path.join(base_dir, "schemas"),
        base_dir
    ]
    
    schemas = []
    
    for directory in schema_dirs:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        file_path = os.path.join(root, file)
                        schemas.extend(_extract_schemas(file_path, base_dir))
    
    # Find usage for each schema
    module_dirs = [
        os.path.join(base_dir, "modules"),
        os.path.join(base_dir, "routes"),
        os.path.join(base_dir, "api")
    ]
    
    for schema in schemas:
        schema.used_by = _find_schema_usage(schema.name, module_dirs, base_dir)
    
    return sorted(schemas, key=lambda x: x.name)

def _extract_schemas(file_path: str, base_dir: str) -> List[SchemaEntry]:
    """Extract schemas from a file.

    Args:
        file_path: Path to the file
        base_dir: Base directory for relative paths

    Returns:
        List of SchemaEntry objects
    """
    schemas = []
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
        
        # Look for Pydantic model definitions
        class_patterns = [
            r"class\s+([a-zA-Z0-9_]+)\s*\(\s*BaseModel\s*\)",
            r"class\s+([a-zA-Z0-9_]+)\s*\(\s*Schema\s*\)",
            r"class\s+([a-zA-Z0-9_]+)\s*\(\s*[a-zA-Z0-9_]+Model\s*\)"
        ]
        
        for pattern in class_patterns:
            for match in re.finditer(pattern, content):
                schema_name = match.group(1)
                
                # Determine if schema is actively validated
                # Look for Field validations, validators, or type annotations
                schema_def = content[match.start():match.start() + 1000]  # Look at next 1000 chars
                has_validation = (
                    "Field(" in schema_def or 
                    "@validator" in schema_def or 
                    re.search(r":\s*(str|int|float|bool|List|Dict|Optional)", schema_def) is not None
                )
                
                status = "active" if has_validation else "scaffolded"
                
                # Add schema to list
                schemas.append(SchemaEntry(
                    name=schema_name,
                    file=os.path.relpath(file_path, base_dir),
                    status=status,
                    used_by=[]  # Will be populated later
                ))
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
    
    return schemas

def _find_schema_usage(schema_name: str, module_dirs: List[str], base_dir: str) -> List[str]:
    """Find where a schema is used.

    Args:
        schema_name: Name of the schema
        module_dirs: Directories to search
        base_dir: Base directory for relative paths

    Returns:
        List of module names that use the schema
    """
    used_by = []
    
    for directory in module_dirs:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        file_path = os.path.join(root, file)
                        
                        try:
                            with open(file_path, "r") as f:
                                content = f.read()
                            
                            # Look for imports or usage of the schema
                            if re.search(r"(from|import)\s+.*?" + schema_name + r"\b", content) or \
                               re.search(r"\b" + schema_name + r"\s*\(", content) or \
                               re.search(r":\s*" + schema_name + r"\b", content):
                                rel_path = os.path.relpath(file_path, base_dir)
                                used_by.append(rel_path)
                        
                        except Exception as e:
                            print(f"Error checking usage in {file_path}: {str(e)}")
    
    return used_by

def update_all_registries(base_dir: str = None) -> Dict[str, int]:
    """Update all registries with the latest data from the codebase.

    Args:
        base_dir: Base directory to scan (defaults to app directory)

    Returns:
        Dictionary with counts of modules, endpoints, and schemas
    """
    # Scan for modules, endpoints, and schemas
    modules = scan_modules(base_dir)
    endpoints = scan_endpoints(base_dir)
    schemas = scan_schemas(base_dir)
    
    # Update the registries
    MODULE_REGISTRY.modules = modules
    ENDPOINT_REGISTRY.endpoints = endpoints
    SCHEMA_REGISTRY.schemas = schemas
    
    return {
        "modules": len(modules),
        "endpoints": len(endpoints),
        "schemas": len(schemas)
    }
