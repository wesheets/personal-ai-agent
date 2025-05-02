#!/usr/bin/env python3
"""
Main.py Patcher for Promethios System Resurrection
Patches main.py with missing router modules identified in the router import analysis.
"""

import os
import json
import re
from pathlib import Path

# Configuration
MAIN_PY_PATH = "/home/ubuntu/personal-ai-agent/app/main.py"
ROUTER_ANALYSIS_FILE = "/home/ubuntu/personal-ai-agent/logs/router_import_analysis.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/route_reconstruction_log.json"
BACKUP_FILE = "/home/ubuntu/personal-ai-agent/app/main.py.bak"

def load_router_analysis():
    """Load router import analysis from file"""
    with open(ROUTER_ANALYSIS_FILE, "r") as f:
        return json.load(f)

def backup_main_py():
    """Create a backup of main.py"""
    import shutil
    shutil.copy2(MAIN_PY_PATH, BACKUP_FILE)
    print(f"Created backup of main.py at {BACKUP_FILE}")

def generate_import_code(missing_routers):
    """Generate code to import missing routers"""
    import_code = "\n# Added missing router imports from schema-led reconstruction\n"
    
    for router in missing_routers:
        module_name = router["module_name"]
        import_code += f"try:\n"
        import_code += f"    from app.routes.{module_name} import router as {module_name}_router\n"
        import_code += f"    {module_name}_loaded = True\n"
        import_code += f"    print(\"✅ Directly loaded {module_name}\")\n"
        import_code += f"except ImportError:\n"
        import_code += f"    {module_name}_loaded = False\n"
        import_code += f"    print(\"⚠️ Could not load {module_name} directly\")\n"
    
    return import_code

def generate_include_code(missing_routers):
    """Generate code to include missing routers"""
    include_code = "\n# Include missing routers from schema-led reconstruction\n"
    
    for router in missing_routers:
        module_name = router["module_name"]
        schema_name = router["schema_name"]
        path_operations = router["path_operations"]
        
        # Generate comment with path operations
        include_code += f"# Router for {schema_name} with paths: "
        for op in path_operations[:2]:  # Show first 2 path operations
            include_code += f"{op['method']} {op['path']}, "
        if len(path_operations) > 2:
            include_code += f"and {len(path_operations) - 2} more\n"
        else:
            include_code += "\n"
        
        # Generate include code
        include_code += f"if {module_name}_loaded:\n"
        include_code += f"    app.include_router({module_name}_router)\n"
        include_code += f"    loaded_routes.append(\"{module_name}\")\n"
        include_code += f"    print(\"✅ Included {module_name}_router\")\n"
        include_code += f"else:\n"
        include_code += f"    failed_routes.append(\"{module_name}\")\n"
        include_code += f"    print(\"⚠️ Failed to include {module_name}_router\")\n"
    
    return include_code

def patch_main_py(import_code, include_code):
    """Patch main.py with missing router imports and includes"""
    with open(MAIN_PY_PATH, "r") as f:
        content = f.read()
    
    # Find insertion points
    import_insertion_point = content.find("# Import missing routes identified in diagnostic report")
    if import_insertion_point == -1:
        import_insertion_point = content.find("# Import routes")
        if import_insertion_point == -1:
            # Fallback to beginning of file
            import_insertion_point = 0
    
    include_insertion_point = content.find("# Register loaded routes in manifest if manifest_initialized")
    if include_insertion_point == -1:
        include_insertion_point = content.find("# Add diagnostics endpoint")
        if include_insertion_point == -1:
            # Fallback to end of file
            include_insertion_point = len(content)
    
    # Insert import code after import section
    new_content = content[:import_insertion_point] + import_code + content[import_insertion_point:]
    
    # Adjust include insertion point based on added import code
    include_insertion_point += len(import_code)
    
    # Insert include code before manifest registration
    new_content = new_content[:include_insertion_point] + include_code + new_content[include_insertion_point:]
    
    # Write updated content back to main.py
    with open(MAIN_PY_PATH, "w") as f:
        f.write(new_content)
    
    print(f"Patched main.py with missing router imports and includes")

def log_changes(missing_routers):
    """Log route reconstruction changes"""
    changes = {
        "timestamp": "20250425_" + "".join(filter(str.isdigit, str(Path(MAIN_PY_PATH).stat().st_mtime))),
        "missing_routers_added": [router["module_name"] for router in missing_routers],
        "schemas_connected": [router["schema_name"] for router in missing_routers],
        "path_operations_added": sum(len(router["path_operations"]) for router in missing_routers),
        "backup_file": BACKUP_FILE
    }
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Save changes to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(changes, f, indent=2)
    
    print(f"Logged route reconstruction changes to {OUTPUT_FILE}")
    
    return changes

def main():
    """Main function to patch main.py with missing router modules"""
    print("Starting main.py patching...")
    
    # Load router import analysis
    router_analysis = load_router_analysis()
    missing_routers = router_analysis["missing_routers"]
    print(f"Loaded router import analysis with {len(missing_routers)} missing routers")
    
    # Backup main.py
    backup_main_py()
    
    # Generate import code
    import_code = generate_import_code(missing_routers)
    print(f"Generated import code for {len(missing_routers)} missing routers")
    
    # Generate include code
    include_code = generate_include_code(missing_routers)
    print(f"Generated include code for {len(missing_routers)} missing routers")
    
    # Patch main.py
    patch_main_py(import_code, include_code)
    
    # Log changes
    changes = log_changes(missing_routers)
    
    print("\nMain.py Patching Summary:")
    print(f"Missing Routers Added: {len(changes['missing_routers_added'])}")
    print(f"Schemas Connected: {len(changes['schemas_connected'])}")
    print(f"Path Operations Added: {changes['path_operations_added']}")
    print(f"Backup File: {changes['backup_file']}")
    
    return changes

if __name__ == "__main__":
    main()
