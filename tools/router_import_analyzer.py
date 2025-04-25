#!/usr/bin/env python3
"""
Router Import Analyzer for Promethios System Resurrection
Identifies which router modules are already imported in main.py and which need to be added.
"""

import os
import json
import re
from pathlib import Path

# Configuration
MAIN_PY_PATH = "/home/ubuntu/personal-ai-agent/app/main.py"
SCHEMA_ROUTE_MAPPING_FILE = "/home/ubuntu/personal-ai-agent/logs/schema_route_mapping.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/router_import_analysis.json"

def load_schema_route_mapping():
    """Load schema-route mapping from file"""
    with open(SCHEMA_ROUTE_MAPPING_FILE, "r") as f:
        return json.load(f)

def extract_imported_routers(main_py_content):
    """Extract all router modules imported in main.py"""
    imported_routers = []
    
    # Look for direct imports
    import_pattern = r'from app\.routes\.([a-zA-Z0-9_]+) import router as'
    direct_imports = re.findall(import_pattern, main_py_content)
    imported_routers.extend(direct_imports)
    
    # Look for try/except imports
    try_import_pattern = r'try:\s+from app\.routes\.([a-zA-Z0-9_]+) import router as'
    try_imports = re.findall(try_import_pattern, main_py_content)
    imported_routers.extend(try_imports)
    
    return imported_routers

def extract_included_routers(main_py_content):
    """Extract all router modules included in the FastAPI app"""
    included_routers = []
    
    # Look for app.include_router calls
    include_pattern = r'app\.include_router\(([a-zA-Z0-9_]+)(?:_router)?\)'
    includes = re.findall(include_pattern, main_py_content)
    
    # Clean up router names (remove _router suffix if present)
    for router in includes:
        if router.endswith("_router"):
            router = router[:-7]  # Remove _router suffix
        included_routers.append(router)
    
    return included_routers

def identify_missing_routers(schema_route_mapping, imported_routers):
    """Identify router modules that need to be added to main.py"""
    all_routers = []
    missing_routers = []
    
    # Collect all router modules from schema-route mapping
    for schema in schema_route_mapping:
        for module in schema.get("modules_with_routers", []):
            module_name = module["name"]
            if module_name not in all_routers:
                all_routers.append(module_name)
                # Check if router is already imported
                if module_name not in imported_routers:
                    missing_routers.append({
                        "module_name": module_name,
                        "path": module["path"],
                        "schema_name": schema["schema_name"],
                        "path_operations": module.get("path_operations", [])
                    })
    
    return missing_routers

def main():
    """Main function to analyze router imports"""
    print("Starting router import analysis...")
    
    # Load schema-route mapping
    schema_route_mapping = load_schema_route_mapping()
    print(f"Loaded schema-route mapping with {len(schema_route_mapping)} schemas")
    
    # Read main.py content
    with open(MAIN_PY_PATH, "r") as f:
        main_py_content = f.read()
    
    # Extract imported routers
    imported_routers = extract_imported_routers(main_py_content)
    print(f"Found {len(imported_routers)} imported router modules in main.py")
    
    # Extract included routers
    included_routers = extract_included_routers(main_py_content)
    print(f"Found {len(included_routers)} included router modules in main.py")
    
    # Identify missing routers
    missing_routers = identify_missing_routers(schema_route_mapping, imported_routers)
    print(f"Identified {len(missing_routers)} missing router modules")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Save results to file
    results = {
        "imported_routers": imported_routers,
        "included_routers": included_routers,
        "missing_routers": missing_routers
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Router import analysis completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    print("\nRouter Import Analysis Summary:")
    print(f"Imported Routers: {len(imported_routers)}")
    print(f"Included Routers: {len(included_routers)}")
    print(f"Missing Routers: {len(missing_routers)}")
    
    # Print missing routers
    if missing_routers:
        print("\nMissing Routers:")
        for router in missing_routers[:5]:  # Show first 5 missing routers
            print(f"- {router['module_name']} (schema: {router['schema_name']})")
        if len(missing_routers) > 5:
            print(f"- Plus {len(missing_routers) - 5} more...")
    
    return results

if __name__ == "__main__":
    main()
