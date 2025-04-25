#!/usr/bin/env python3
"""
Schema Breadcrumb Analyzer for Endpoint Repair
Analyzes schema files to extract endpoint structure information for repair.
"""

import os
import json
import re
import ast
from pathlib import Path
from collections import defaultdict

# Configuration
APP_DIR = "/home/ubuntu/personal-ai-agent/app"
SCHEMAS_DIR = os.path.join(APP_DIR, "schemas")
ROUTES_DIR = os.path.join(APP_DIR, "routes")
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
FINAL_VERIFICATION_FILE = "/home/ubuntu/personal-ai-agent/logs/final_endpoint_verification.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/schema_breadcrumbs_analysis.json"

def load_previous_verification():
    """Load previous endpoint verification results"""
    with open(FINAL_VERIFICATION_FILE, "r") as f:
        return json.load(f)

def extract_pydantic_models(file_path):
    """Extract Pydantic model definitions from a Python file"""
    models = []
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
        
        # Parse the Python file
        tree = ast.parse(content)
        
        # Find all class definitions that inherit from BaseModel or similar
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_pydantic_model = False
                
                # Check if the class inherits from BaseModel or similar
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id in ["BaseModel", "Schema"]:
                        is_pydantic_model = True
                    elif isinstance(base, ast.Attribute) and "Model" in base.attr:
                        is_pydantic_model = True
                
                if is_pydantic_model:
                    # Extract field definitions
                    fields = {}
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            field_name = item.target.id
                            
                            # Try to get the type annotation
                            if isinstance(item.annotation, ast.Name):
                                field_type = item.annotation.id
                            elif isinstance(item.annotation, ast.Subscript):
                                if isinstance(item.annotation.value, ast.Name):
                                    field_type = f"{item.annotation.value.id}[...]"
                                else:
                                    field_type = "Complex"
                            else:
                                field_type = "Unknown"
                            
                            fields[field_name] = field_type
                    
                    models.append({
                        "name": node.name,
                        "fields": fields
                    })
    
    except Exception as e:
        print(f"Error parsing {file_path}: {str(e)}")
    
    return models

def extract_route_info_from_schema(file_path):
    """Extract route information from schema file"""
    schema_name = os.path.basename(file_path).replace(".py", "")
    
    # Extract module name for potential route mapping
    module_name = schema_name.replace("_schema", "")
    
    # Guess potential route paths based on schema name
    potential_routes = []
    
    # Direct mapping (e.g., agent_schema.py -> /agent)
    base_path = f"/{module_name}"
    potential_routes.append(base_path)
    
    # Common operations
    operations = ["status", "create", "update", "delete", "list", "get", "search"]
    for op in operations:
        potential_routes.append(f"{base_path}/{op}")
    
    # Extract models from the schema file
    models = extract_pydantic_models(file_path)
    
    # Look for route path hints in the file content
    route_hints = []
    try:
        with open(file_path, "r") as f:
            content = f.read()
        
        # Look for strings that might be route paths
        path_pattern = r'["\']\/[a-zA-Z0-9_\-\/{}]+["\']'
        matches = re.findall(path_pattern, content)
        for match in matches:
            # Clean up the match
            path = match.strip('"\'')
            if path not in route_hints:
                route_hints.append(path)
    
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
    
    return {
        "schema_name": schema_name,
        "module_name": module_name,
        "file_path": file_path,
        "models": models,
        "potential_routes": potential_routes,
        "route_hints": route_hints
    }

def find_corresponding_route_file(module_name):
    """Find the corresponding route file for a module name"""
    # Check for exact match
    route_file = os.path.join(ROUTES_DIR, f"{module_name}.py")
    if os.path.exists(route_file):
        return route_file
    
    # Check for router match
    route_file = os.path.join(ROUTES_DIR, f"{module_name}_router.py")
    if os.path.exists(route_file):
        return route_file
    
    # Check for routes match
    route_file = os.path.join(ROUTES_DIR, f"{module_name}_routes.py")
    if os.path.exists(route_file):
        return route_file
    
    # Check for any file containing the module name
    for root, dirs, files in os.walk(ROUTES_DIR):
        for file in files:
            if module_name in file and file.endswith(".py"):
                return os.path.join(root, file)
    
    return None

def extract_route_definitions(route_file):
    """Extract route definitions from a route file"""
    routes = []
    
    try:
        with open(route_file, "r") as f:
            content = f.read()
        
        # Look for FastAPI route decorators
        decorator_pattern = r'@[a-zA-Z0-9_]+\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        matches = re.findall(decorator_pattern, content)
        for match in matches:
            routes.append(match)
    
    except Exception as e:
        print(f"Error reading {route_file}: {str(e)}")
    
    return routes

def map_schemas_to_routes():
    """Map schemas to routes and identify potential endpoint fixes"""
    schema_files = []
    for root, dirs, files in os.walk(SCHEMAS_DIR):
        for file in files:
            if file.endswith(".py"):
                schema_files.append(os.path.join(root, file))
    
    schema_route_map = {}
    for schema_file in schema_files:
        schema_info = extract_route_info_from_schema(schema_file)
        module_name = schema_info["module_name"]
        
        # Find corresponding route file
        route_file = find_corresponding_route_file(module_name)
        
        # Extract actual routes if route file exists
        actual_routes = []
        if route_file:
            actual_routes = extract_route_definitions(route_file)
        
        schema_route_map[schema_info["schema_name"]] = {
            "schema_info": schema_info,
            "route_file": route_file,
            "actual_routes": actual_routes
        }
    
    return schema_route_map

def analyze_non_operational_endpoints(verification_results, schema_route_map):
    """Analyze non-operational endpoints and identify potential fixes"""
    non_operational = []
    
    for endpoint in verification_results["results"]:
        if endpoint.get("status_code") not in [200, 422]:
            # Extract module name from route path
            path = endpoint["route_path"]
            parts = path.strip("/").split("/")
            if parts:
                module_name = parts[0]
                
                # Find matching schema
                matching_schemas = []
                for schema_name, schema_data in schema_route_map.items():
                    if schema_data["schema_info"]["module_name"] == module_name:
                        matching_schemas.append(schema_name)
                    elif module_name in schema_name:
                        matching_schemas.append(schema_name)
                
                non_operational.append({
                    "endpoint": endpoint,
                    "module_name": module_name,
                    "matching_schemas": matching_schemas
                })
            else:
                non_operational.append({
                    "endpoint": endpoint,
                    "module_name": "unknown",
                    "matching_schemas": []
                })
    
    return non_operational

def generate_endpoint_fix_recommendations(non_operational, schema_route_map):
    """Generate recommendations for fixing non-operational endpoints"""
    recommendations = []
    
    for endpoint in non_operational:
        route_path = endpoint["endpoint"]["route_path"]
        method = endpoint["endpoint"]["method"]
        status_code = endpoint["endpoint"]["status_code"]
        module_name = endpoint["module_name"]
        matching_schemas = endpoint["matching_schemas"]
        
        # Determine fix type based on status code
        if status_code == 404:
            fix_type = "missing_route"
        elif status_code == 405:
            fix_type = "method_not_allowed"
        elif status_code and status_code >= 500:
            fix_type = "server_error"
        else:
            fix_type = "unknown_error"
        
        # Find best matching schema
        best_schema = None
        if matching_schemas:
            best_schema = matching_schemas[0]
        
        # Generate recommendation
        recommendation = {
            "route_path": route_path,
            "method": method,
            "status_code": status_code,
            "module_name": module_name,
            "matching_schemas": matching_schemas,
            "best_schema": best_schema,
            "fix_type": fix_type,
            "priority": "low"
        }
        
        # Set priority based on module name
        if module_name in ["agent", "memory", "loop", "orchestrator", "hal", "forge"]:
            recommendation["priority"] = "high"
        elif module_name in ["health", "guardian", "historian", "nova", "sage"]:
            recommendation["priority"] = "medium"
        
        # Add schema information if available
        if best_schema and best_schema in schema_route_map:
            schema_info = schema_route_map[best_schema]["schema_info"]
            recommendation["schema_models"] = schema_info["models"]
            recommendation["potential_routes"] = schema_info["potential_routes"]
            recommendation["route_hints"] = schema_info["route_hints"]
        
        recommendations.append(recommendation)
    
    return recommendations

def main():
    """Main function to analyze schema breadcrumbs for endpoint repair"""
    print("Starting schema breadcrumb analysis...")
    
    # Load previous verification results
    verification_results = load_previous_verification()
    print(f"Loaded verification results with {verification_results['analysis']['total_endpoints']} endpoints")
    
    # Map schemas to routes
    schema_route_map = map_schemas_to_routes()
    print(f"Mapped {len(schema_route_map)} schemas to routes")
    
    # Analyze non-operational endpoints
    non_operational = analyze_non_operational_endpoints(verification_results, schema_route_map)
    print(f"Identified {len(non_operational)} non-operational endpoints")
    
    # Generate endpoint fix recommendations
    recommendations = generate_endpoint_fix_recommendations(non_operational, schema_route_map)
    
    # Sort recommendations by priority
    recommendations.sort(key=lambda x: 0 if x["priority"] == "high" else (1 if x["priority"] == "medium" else 2))
    
    # Count recommendations by priority
    high_priority = sum(1 for r in recommendations if r["priority"] == "high")
    medium_priority = sum(1 for r in recommendations if r["priority"] == "medium")
    low_priority = sum(1 for r in recommendations if r["priority"] == "low")
    
    print(f"Generated {len(recommendations)} fix recommendations:")
    print(f"  High priority: {high_priority}")
    print(f"  Medium priority: {medium_priority}")
    print(f"  Low priority: {low_priority}")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Save results to file
    output = {
        "schema_route_map": schema_route_map,
        "non_operational_endpoints": non_operational,
        "fix_recommendations": recommendations,
        "summary": {
            "total_schemas": len(schema_route_map),
            "non_operational_endpoints": len(non_operational),
            "fix_recommendations": len(recommendations),
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority
        }
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Schema breadcrumb analysis completed. Results saved to {OUTPUT_FILE}")
    
    return output

if __name__ == "__main__":
    main()
