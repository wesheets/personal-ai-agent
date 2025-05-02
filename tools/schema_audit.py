#!/usr/bin/env python3
"""
Schema Audit Tool for Personal AI Agent Backend
Examines schema files and their connections to routes and agents.
"""

import json
import os
import sys
import re
from pathlib import Path

# Configuration
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/schema_audit_report.json"
SCHEMAS_DIR = "/home/ubuntu/personal-ai-agent/app/schemas"
ROUTES_DIR = "/home/ubuntu/personal-ai-agent/app/routes"
AGENT_CONTRACTS_PATH = "/home/ubuntu/personal-ai-agent/app/contracts/agent_contracts.json"

def get_schema_files():
    """Get all schema files in the schemas directory"""
    schema_files = []
    
    # Get Python schema files
    for filename in os.listdir(SCHEMAS_DIR):
        if filename.endswith("_schema.py") or filename == "memory.py" or filename == "loop_trace.py":
            schema_path = os.path.join(SCHEMAS_DIR, filename)
            schema_name = filename.replace(".py", "")
            schema_files.append({
                "name": schema_name,
                "path": schema_path,
                "file_present": True
            })
    
    # Get JSON schema files
    for filename in os.listdir(SCHEMAS_DIR):
        if filename.endswith(".schema.json"):
            schema_path = os.path.join(SCHEMAS_DIR, filename)
            schema_name = filename.replace(".schema.json", "")
            schema_files.append({
                "name": schema_name,
                "path": schema_path,
                "file_present": True
            })
    
    return schema_files

def check_schema_bound_to_routes(schema_name):
    """Check if schema is bound to any routes"""
    bound_routes = []
    
    # Check if routes directory exists
    if not os.path.exists(ROUTES_DIR):
        return bound_routes
    
    # Search for schema name in route files
    for filename in os.listdir(ROUTES_DIR):
        if filename.endswith(".py"):
            route_path = os.path.join(ROUTES_DIR, filename)
            
            with open(route_path, "r") as f:
                content = f.read()
                
                # Look for imports of this schema
                if f"import {schema_name}" in content or f"from app.schemas.{schema_name} import" in content:
                    # Look for route definitions using this schema
                    route_matches = re.findall(r'@router\.(?:get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]', content)
                    
                    for route in route_matches:
                        if route not in bound_routes:
                            bound_routes.append(route)
    
    return bound_routes

def check_schema_bound_to_agents(schema_name):
    """Check if schema is bound to any agents"""
    bound_agents = []
    
    # Check if agent contracts file exists
    if not os.path.exists(AGENT_CONTRACTS_PATH):
        return bound_agents
    
    # Load agent contracts
    with open(AGENT_CONTRACTS_PATH, "r") as f:
        contracts = json.load(f)
    
    # Check each agent contract for this schema
    for agent_id, contract in contracts.items():
        input_schema = contract.get("accepted_input_schema", "")
        output_schema = contract.get("expected_output_schema", "")
        
        # Convert schema name to match format in contracts
        schema_check = schema_name.replace("_schema", "")
        
        if schema_check.lower() in input_schema.lower() or schema_check.lower() in output_schema.lower():
            bound_agents.append(agent_id)
    
    return bound_agents

def validate_pydantic_schema(schema_path):
    """Check if schema is a valid Pydantic schema"""
    try:
        with open(schema_path, "r") as f:
            content = f.read()
            
            # Check if file imports Pydantic and defines a model
            has_pydantic = "from pydantic import" in content
            has_basemodel = "BaseModel" in content
            
            return has_pydantic and has_basemodel
    except:
        return False

def main():
    """Main function to run the schema audit"""
    print("Starting schema audit...")
    
    # Get all schema files
    schema_files = get_schema_files()
    print(f"Found {len(schema_files)} schema files")
    
    # Analyze each schema
    audit_results = []
    
    for schema in schema_files:
        print(f"Analyzing schema: {schema['name']}")
        
        # Check if schema is bound to routes
        bound_routes = check_schema_bound_to_routes(schema['name'])
        
        # Check if schema is bound to agents
        bound_agents = check_schema_bound_to_agents(schema['name'])
        
        # Validate Pydantic schema
        validated = False
        if schema['path'].endswith('.py'):
            validated = validate_pydantic_schema(schema['path'])
        
        # Add to audit results
        audit_results.append({
            "schema_name": schema['name'],
            "file_present": schema['file_present'],
            "bound_to_route": bound_routes if bound_routes else "None",
            "bound_to_agent": bound_agents if bound_agents else "None",
            "validated_pydantic": validated
        })
    
    # Save results to file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f"Schema audit completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    total_schemas = len(audit_results)
    files_present = sum(1 for schema in audit_results if schema["file_present"])
    bound_to_routes = sum(1 for schema in audit_results if schema["bound_to_route"] != "None")
    bound_to_agents = sum(1 for schema in audit_results if schema["bound_to_agent"] != "None")
    validated = sum(1 for schema in audit_results if schema["validated_pydantic"])
    
    print("\nSchema Audit Summary:")
    print(f"Total Schemas: {total_schemas}")
    print(f"Files Present: {files_present}/{total_schemas} ({files_present/total_schemas*100:.1f}%)")
    print(f"Bound to Routes: {bound_to_routes}/{total_schemas} ({bound_to_routes/total_schemas*100:.1f}%)")
    print(f"Bound to Agents: {bound_to_agents}/{total_schemas} ({bound_to_agents/total_schemas*100:.1f}%)")
    print(f"Validated Pydantic: {validated}/{total_schemas} ({validated/total_schemas*100:.1f}%)")
    
    return audit_results

if __name__ == "__main__":
    main()
