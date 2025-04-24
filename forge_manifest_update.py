"""
FORGE Manifest Update Script

This script updates the system manifest with FORGE agent integration.
"""

import os
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("forge_manifest_update")

# Constants
MANIFEST_PATH = os.path.join("app", "system_manifest.json")

def update_manifest():
    """
    Update the system manifest with FORGE agent integration.
    """
    try:
        # Load current manifest
        with open(MANIFEST_PATH, "r") as f:
            manifest = json.load(f)
        
        logger.info("✅ Loaded system manifest")
        
        # Update agents section
        if "agents" not in manifest:
            manifest["agents"] = {}
        
        manifest["agents"]["forge"] = {
            "tools": [
                "scaffold", 
                "wire", 
                "register", 
                "test", 
                "validate", 
                "patch", 
                "version_track",
                "memory_read",
                "memory_write"
            ],
            "schema_wrapped": True,
            "fallbacks": ["log_error", "retry_with_simplified_input", "create_recovery_snapshot"],
            "checksum": "initial"
        }
        
        logger.info("✅ Updated agents section")
        
        # Update schemas section
        if "schemas" not in manifest:
            manifest["schemas"] = {}
        
        manifest["schemas"]["ForgeBuildRequest"] = {
            "file": "app/schemas/forge_schema.py",
            "bound_to_routes": ["/forge/build"],
            "version": "v1.0.0",
            "checksum": "initial"
        }
        
        manifest["schemas"]["ForgeBuildResult"] = {
            "file": "app/schemas/forge_schema.py",
            "bound_to_routes": ["/forge/build"],
            "version": "v1.0.0",
            "checksum": "initial"
        }
        
        manifest["schemas"]["ComponentBuildResult"] = {
            "file": "app/schemas/forge_schema.py",
            "bound_to_routes": [],
            "version": "v1.0.0",
            "checksum": "initial"
        }
        
        manifest["schemas"]["ForgeRevisionRequest"] = {
            "file": "app/schemas/forge_schema.py",
            "bound_to_routes": [],
            "version": "v1.0.0",
            "checksum": "initial"
        }
        
        manifest["schemas"]["ForgeRevisionResult"] = {
            "file": "app/schemas/forge_schema.py",
            "bound_to_routes": [],
            "version": "v1.0.0",
            "checksum": "initial"
        }
        
        logger.info("✅ Updated schemas section")
        
        # Update routes section
        if "routes" not in manifest:
            manifest["routes"] = {}
        
        manifest["routes"]["/forge/build"] = {
            "method": "POST",
            "schema": "ForgeBuildRequest",
            "status": "registered",
            "errors": []
        }
        
        logger.info("✅ Updated routes section")
        
        # Update modules section
        if "modules" not in manifest:
            manifest["modules"] = {}
        
        manifest["modules"]["forge_agent"] = {
            "file": "app/agents/forge_agent.py",
            "wrapped_with_schema": True,
            "last_updated": "2025-04-24T18:58:00.000000"
        }
        
        logger.info("✅ Updated modules section")
        
        # Update memory section
        if "memory" not in manifest:
            manifest["memory"] = {}
        
        if "memory_tags" not in manifest["memory"]:
            manifest["memory"]["memory_tags"] = {}
        
        manifest["memory"]["memory_tags"]["forge_build_log"] = {
            "format": "forge_build_log_{loop_id}_v{version}",
            "description": "Build log for FORGE agent",
            "retention_days": 30
        }
        
        logger.info("✅ Updated memory section")
        
        # Update hardening layers
        if "hardening_layers" not in manifest:
            manifest["hardening_layers"] = {}
        
        manifest["hardening_layers"]["forge_integration_enabled"] = True
        
        logger.info("✅ Updated hardening layers")
        
        # Save updated manifest
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest, f, indent=2)
        
        logger.info("✅ Saved updated manifest")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error updating manifest: {str(e)}")
        return False

if __name__ == "__main__":
    success = update_manifest()
    if success:
        print("✅ Successfully updated system manifest with FORGE agent integration")
    else:
        print("❌ Failed to update system manifest")
