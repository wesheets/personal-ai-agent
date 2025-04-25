#!/usr/bin/env python3
"""
Module Audit Tool for Personal AI Agent Backend
Examines routes and modules to verify registration and live status.
"""

import json
import os
import sys
import re
from pathlib import Path

# Configuration
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/module_audit_report.json"
ROUTES_DIR = "/home/ubuntu/personal-ai-agent/app/routes"
MODULES_DIR = "/home/ubuntu/personal-ai-agent/app/modules"
MAIN_APP_PATH = "/home/ubuntu/personal-ai-agent/app/main.py"

def get_route_modules():
    """Get all route modules in the routes directory"""
    route_modules = []
    
    # Check if routes directory exists
    if not os.path.exists(ROUTES_DIR):
        return route_modules
    
    # Get all route files
    for filename in os.listdir(ROUTES_DIR):
        if filename.endswith("_routes.py") or filename.endswith("_router.py"):
            module_path = os.path.join(ROUTES_DIR, filename)
            module_name = filename.replace(".py", "")
            
            # Determine purpose from file content
            purpose = "Unknown"
            try:
                with open(module_path, "r") as f:
                    content = f.read()
                    # Look for docstring or comments
                    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                    if docstring_match:
                        purpose_lines = docstring_match.group(1).strip().split('\n')
                        if purpose_lines:
                            purpose = purpose_lines[0].strip()
                    # If no docstring, look for router definition
                    elif "router = APIRouter" in content:
                        prefix_match = re.search(r'prefix=[\'"]([^\'"]+)[\'"]', content)
                        if prefix_match:
                            purpose = f"Router for {prefix_match.group(1)} endpoints"
            except:
                pass
            
            route_modules.append({
                "module_name": module_name,
                "path": module_path,
                "purpose": purpose
            })
    
    return route_modules

def check_router_registered(module_name):
    """Check if router is registered in main.py"""
    # Check if main.py exists
    if not os.path.exists(MAIN_APP_PATH):
        return False
    
    # Look for router import and inclusion
    try:
        with open(MAIN_APP_PATH, "r") as f:
            content = f.read()
            
            # Check for import
            import_pattern = rf'from app.routes.{module_name} import'
            if re.search(import_pattern, content):
                # Check for app.include_router
                include_pattern = rf'app.include_router\([^)]*{module_name.replace("_router", "").replace("_routes", "")}[^)]*\)'
                if re.search(include_pattern, content):
                    return True
            
            # Alternative check for direct router import
            router_name = module_name.replace("_routes", "").replace("_router", "")
            alt_import_pattern = rf'from app.routes.{module_name} import {router_name}_router'
            if re.search(alt_import_pattern, content):
                alt_include_pattern = rf'app.include_router\({router_name}_router[^)]*\)'
                if re.search(alt_include_pattern, content):
                    return True
    except:
        pass
    
    return False

def check_live_on_backend(module_name, route_audit_data):
    """Check if module endpoints are live on backend based on route audit data"""
    # Extract router name from module name
    router_name = module_name.replace("_routes", "").replace("_router", "")
    
    # Look for routes with this router name in the path
    for route in route_audit_data:
        route_path = route["route_path"]
        if f"/{router_name}/" in route_path or route_path == f"/{router_name}":
            if route["status"] == "200 OK":
                return True
    
    return False

def main():
    """Main function to run the module audit"""
    print("Starting module audit...")
    
    # Load route audit data if available
    route_audit_data = []
    route_audit_path = "/home/ubuntu/personal-ai-agent/logs/live_endpoint_audit_report.json"
    if os.path.exists(route_audit_path):
        with open(route_audit_path, "r") as f:
            route_audit_data = json.load(f)
            print(f"Loaded route audit data with {len(route_audit_data)} routes")
    
    # Get all route modules
    route_modules = get_route_modules()
    print(f"Found {len(route_modules)} route modules")
    
    # Analyze each module
    audit_results = []
    
    for module in route_modules:
        print(f"Analyzing module: {module['module_name']}")
        
        # Check if router is registered in main.py
        router_registered = check_router_registered(module['module_name'])
        
        # Check if module endpoints are live on backend
        live_on_backend = check_live_on_backend(module['module_name'], route_audit_data)
        
        # Add to audit results
        audit_results.append({
            "module_name": module['module_name'],
            "router_registered": router_registered,
            "live_on_backend": live_on_backend,
            "purpose": module['purpose']
        })
    
    # Save results to file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f"Module audit completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    total_modules = len(audit_results)
    registered_routers = sum(1 for module in audit_results if module["router_registered"])
    live_modules = sum(1 for module in audit_results if module["live_on_backend"])
    
    print("\nModule Audit Summary:")
    print(f"Total Modules: {total_modules}")
    print(f"Registered Routers: {registered_routers}/{total_modules} ({registered_routers/total_modules*100:.1f}%)")
    print(f"Live on Backend: {live_modules}/{total_modules} ({live_modules/total_modules*100:.1f}%)")
    
    return audit_results

if __name__ == "__main__":
    main()
