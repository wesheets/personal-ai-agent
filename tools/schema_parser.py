#!/usr/bin/env python3
"""
Schema Parser for Promethios System Resurrection
Identifies all schema definitions and their potential route module matches.
"""

import os
import json
import re
from pathlib import Path

# Configuration
SCHEMAS_DIR = "/home/ubuntu/personal-ai-agent/app/schemas"
ROUTES_DIR = "/home/ubuntu/personal-ai-agent/app/routes"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/schema_route_mapping.json"

def get_schema_files():
    """Get all schema files in the schemas directory and subdirectories"""
    schema_files = []
    
    # Walk through schemas directory and subdirectories
    for root, dirs, files in os.walk(SCHEMAS_DIR):
        for file in files:
            if file.endswith("_schema.py") or file.endswith(".schema.json") or file == "memory.py" or file == "loop_trace.py":
                schema_path = os.path.join(root, file)
                schema_name = file.replace(".py", "").replace(".schema.json", "")
                
                schema_files.append({
                    "name": schema_name,
                    "path": schema_path,
                    "type": "json" if file.endswith(".json") else "python"
                })
    
    return schema_files

def find_potential_route_modules(schema_name):
    """Find potential route modules for a schema"""
    potential_modules = []
    
    # Extract base name without _schema suffix
    base_name = schema_name.replace("_schema", "")
    
    # Look for matching route modules
    for file in os.listdir(ROUTES_DIR):
        if file.endswith(".py"):
            # Direct match (e.g., forge_schema.py -> forge_routes.py)
            if file.startswith(f"{base_name}_routes") or file.startswith(f"{base_name}_router"):
                module_path = os.path.join(ROUTES_DIR, file)
                potential_modules.append({
                    "name": file.replace(".py", ""),
                    "path": module_path,
                    "match_type": "direct"
                })
            # Partial match (check file content for schema import)
            else:
                module_path = os.path.join(ROUTES_DIR, file)
                try:
                    with open(module_path, "r") as f:
                        content = f.read()
                        if f"import {schema_name}" in content or f"from app.schemas.{schema_name} import" in content:
                            potential_modules.append({
                                "name": file.replace(".py", ""),
                                "path": module_path,
                                "match_type": "import"
                            })
                except:
                    pass
    
    return potential_modules

def check_router_definition(module_path):
    """Check if a route module has a router definition"""
    try:
        with open(module_path, "r") as f:
            content = f.read()
            has_router = "router = APIRouter" in content
            
            # Find path operations
            path_operations = []
            for method in ["get", "post", "put", "delete", "patch"]:
                pattern = rf'@router\.{method}\([\'"]([^\'"]+)[\'"]'
                matches = re.findall(pattern, content)
                for match in matches:
                    path_operations.append({
                        "method": method.upper(),
                        "path": match
                    })
            
            return {
                "has_router": has_router,
                "path_operations": path_operations
            }
    except:
        return {
            "has_router": False,
            "path_operations": []
        }

def main():
    """Main function to parse schemas and find route modules"""
    print("Starting schema parsing...")
    
    # Get all schema files
    schema_files = get_schema_files()
    print(f"Found {len(schema_files)} schema files")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Analyze each schema
    schema_route_mapping = []
    
    for schema in schema_files:
        print(f"Analyzing schema: {schema['name']}")
        
        # Find potential route modules
        potential_modules = find_potential_route_modules(schema['name'])
        
        # Check router definition for each potential module
        modules_with_routers = []
        for module in potential_modules:
            router_info = check_router_definition(module['path'])
            if router_info["has_router"]:
                module["has_router"] = True
                module["path_operations"] = router_info["path_operations"]
                modules_with_routers.append(module)
            else:
                module["has_router"] = False
                module["path_operations"] = []
        
        # Add to mapping
        schema_route_mapping.append({
            "schema_name": schema['name'],
            "schema_path": schema['path'],
            "schema_type": schema['type'],
            "potential_route_modules": potential_modules,
            "modules_with_routers": modules_with_routers
        })
    
    # Save results to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(schema_route_mapping, f, indent=2)
    
    print(f"Schema parsing completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    total_schemas = len(schema_route_mapping)
    schemas_with_modules = sum(1 for schema in schema_route_mapping if schema["potential_route_modules"])
    schemas_with_routers = sum(1 for schema in schema_route_mapping if schema["modules_with_routers"])
    
    print("\nSchema Parsing Summary:")
    print(f"Total Schemas: {total_schemas}")
    print(f"Schemas with Potential Route Modules: {schemas_with_modules}/{total_schemas} ({schemas_with_modules/total_schemas*100:.1f}%)")
    print(f"Schemas with Router Definitions: {schemas_with_routers}/{total_schemas} ({schemas_with_routers/total_schemas*100:.1f}%)")
    
    return schema_route_mapping

if __name__ == "__main__":
    main()
