#!/usr/bin/env python3
"""
System Manifest Updater for Promethios System Resurrection
Updates system manifest files with newly wired modules from route reconstruction.
"""

import os
import json
import datetime
from pathlib import Path

# Configuration
APP_MANIFEST_PATH = "/home/ubuntu/personal-ai-agent/app/system_manifest.json"
CORE_MANIFEST_PATH = "/home/ubuntu/personal-ai-agent/app/core/system_manifest.json"
ROUTE_RECONSTRUCTION_LOG = "/home/ubuntu/personal-ai-agent/logs/route_reconstruction_log.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/manifest_update_log.json"

def load_route_reconstruction_log():
    """Load route reconstruction log from file"""
    with open(ROUTE_RECONSTRUCTION_LOG, "r") as f:
        return json.load(f)

def load_manifest(manifest_path):
    """Load system manifest from file"""
    with open(manifest_path, "r") as f:
        return json.load(f)

def update_manifest_routes(manifest, missing_routers):
    """Update manifest routes with newly wired modules"""
    # Update loaded_routes in manifest_meta
    if "manifest_meta" in manifest and "loaded_routes" in manifest["manifest_meta"]:
        for router in missing_routers:
            if router not in manifest["manifest_meta"]["loaded_routes"]:
                manifest["manifest_meta"]["loaded_routes"].append(router)
        print(f"Updated loaded_routes in manifest_meta with {len(missing_routers)} new routers")
    
    # Update last_updated timestamp
    if "manifest_meta" in manifest:
        manifest["manifest_meta"]["last_updated"] = datetime.datetime.now().isoformat()
    
    # Add memory tag for this update
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    memory_tag = f"route_reconstruction_{timestamp}"
    if "manifest_meta" in manifest:
        manifest["manifest_meta"]["memory_tag"] = memory_tag
    
    return manifest, memory_tag

def update_manifest_schemas(manifest, schemas_connected):
    """Update manifest schemas with newly connected schemas"""
    # Add or update schemas in the schemas section
    if "schemas" in manifest:
        for schema_name in schemas_connected:
            # Check if schema already exists
            schema_key = schema_name.replace("_schema", "")
            if schema_key not in manifest["schemas"]:
                # Add new schema entry
                manifest["schemas"][schema_key] = {
                    "file": f"app/schemas/{schema_name}.py",
                    "bound_to_routes": [],  # Will be populated during endpoint validation
                    "version": "v1.0.0",
                    "checksum": "initial"
                }
        print(f"Updated schemas section with {len(schemas_connected)} connected schemas")
    
    return manifest

def save_manifest(manifest, manifest_path):
    """Save updated manifest to file"""
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved updated manifest to {manifest_path}")

def log_changes(app_manifest_updated, core_manifest_updated, missing_routers, schemas_connected, memory_tag):
    """Log manifest update changes"""
    changes = {
        "timestamp": datetime.datetime.now().isoformat(),
        "memory_tag": memory_tag,
        "app_manifest_updated": app_manifest_updated,
        "core_manifest_updated": core_manifest_updated,
        "routers_added": missing_routers,
        "schemas_connected": schemas_connected
    }
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Save changes to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(changes, f, indent=2)
    
    print(f"Logged manifest update changes to {OUTPUT_FILE}")
    
    return changes

def main():
    """Main function to update system manifest files"""
    print("Starting system manifest update...")
    
    # Load route reconstruction log
    reconstruction_log = load_route_reconstruction_log()
    missing_routers = reconstruction_log["missing_routers_added"]
    schemas_connected = reconstruction_log["schemas_connected"]
    print(f"Loaded route reconstruction log with {len(missing_routers)} missing routers and {len(schemas_connected)} connected schemas")
    
    # Update app manifest
    app_manifest_updated = False
    if os.path.exists(APP_MANIFEST_PATH):
        app_manifest = load_manifest(APP_MANIFEST_PATH)
        app_manifest, memory_tag = update_manifest_routes(app_manifest, missing_routers)
        app_manifest = update_manifest_schemas(app_manifest, schemas_connected)
        save_manifest(app_manifest, APP_MANIFEST_PATH)
        app_manifest_updated = True
        print(f"Updated app manifest at {APP_MANIFEST_PATH}")
    else:
        print(f"App manifest not found at {APP_MANIFEST_PATH}")
        memory_tag = datetime.datetime.now().strftime("route_reconstruction_%Y%m%d_%H%M")
    
    # Update core manifest
    core_manifest_updated = False
    if os.path.exists(CORE_MANIFEST_PATH):
        core_manifest = load_manifest(CORE_MANIFEST_PATH)
        core_manifest, _ = update_manifest_routes(core_manifest, missing_routers)
        core_manifest = update_manifest_schemas(core_manifest, schemas_connected)
        save_manifest(core_manifest, CORE_MANIFEST_PATH)
        core_manifest_updated = True
        print(f"Updated core manifest at {CORE_MANIFEST_PATH}")
    else:
        print(f"Core manifest not found at {CORE_MANIFEST_PATH}")
    
    # Log changes
    changes = log_changes(app_manifest_updated, core_manifest_updated, missing_routers, schemas_connected, memory_tag)
    
    print("\nSystem Manifest Update Summary:")
    print(f"App Manifest Updated: {app_manifest_updated}")
    print(f"Core Manifest Updated: {core_manifest_updated}")
    print(f"Routers Added: {len(missing_routers)}")
    print(f"Schemas Connected: {len(schemas_connected)}")
    print(f"Memory Tag: {memory_tag}")
    
    return changes

if __name__ == "__main__":
    main()
