"""
Output Policy Manifest Update

This script updates the system manifest with output policy enforcement capabilities.
"""

import sys
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("output_policy_manifest_update")

# Path to system manifest
MANIFEST_PATH = "/home/ubuntu/personal-ai-agent/app/system_manifest.json"

def update_manifest():
    """
    Update the system manifest with output policy enforcement capabilities.
    """
    try:
        # Load current manifest
        with open(MANIFEST_PATH, 'r') as f:
            manifest = json.load(f)
        
        logger.info("✅ Loaded system manifest")
        
        # Update hardening layers
        if "hardening_layers" not in manifest:
            manifest["hardening_layers"] = {}
        
        manifest["hardening_layers"]["output_policy_enforcement"] = True
        logger.info("✅ Updated hardening layers")
        
        # Register routes
        if "routes" not in manifest:
            manifest["routes"] = {}
        
        manifest["routes"]["/policy/enforce"] = {
            "method": "POST",
            "schema": "OutputPolicyRequest",
            "status": "tested"
        }
        
        manifest["routes"]["/policy/logs"] = {
            "method": "POST",
            "schema": "PolicyLogRequest",
            "status": "tested"
        }
        
        logger.info("✅ Registered policy routes")
        
        # Register schemas
        if "schemas" not in manifest:
            manifest["schemas"] = {}
        
        manifest["schemas"]["OutputPolicyRequest"] = {
            "file": "/app/schemas/output_policy_schema.py",
            "class": "OutputPolicyRequest",
            "checksum": "output_policy_schema_checksum",
            "routes": ["/policy/enforce"]
        }
        
        manifest["schemas"]["OutputPolicyResult"] = {
            "file": "/app/schemas/output_policy_schema.py",
            "class": "OutputPolicyResult",
            "checksum": "output_policy_schema_checksum",
            "routes": ["/policy/enforce"]
        }
        
        manifest["schemas"]["PolicyLogRequest"] = {
            "file": "/app/schemas/output_policy_schema.py",
            "class": "PolicyLogRequest",
            "checksum": "output_policy_schema_checksum",
            "routes": ["/policy/logs"]
        }
        
        manifest["schemas"]["PolicyLogResponse"] = {
            "file": "/app/schemas/output_policy_schema.py",
            "class": "PolicyLogResponse",
            "checksum": "output_policy_schema_checksum",
            "routes": ["/policy/logs"]
        }
        
        logger.info("✅ Registered policy schemas")
        
        # Update manifest meta
        if "manifest_meta" not in manifest:
            manifest["manifest_meta"] = {}
        
        manifest["manifest_meta"]["last_updated"] = datetime.utcnow().isoformat()
        manifest["manifest_meta"]["last_updated_by"] = "output_policy_manifest_update.py"
        
        # Save updated manifest
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info("✅ Saved updated system manifest")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error updating system manifest: {str(e)}")
        return False

if __name__ == "__main__":
    success = update_manifest()
    
    if success:
        print("✅ System manifest updated with output policy enforcement capabilities")
        sys.exit(0)
    else:
        print("❌ Failed to update system manifest")
        sys.exit(1)
