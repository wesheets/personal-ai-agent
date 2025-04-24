"""
Update system manifest with SAGE agent cascade mode information
"""

import json
import os
import sys
import datetime

# Path to system manifest
MANIFEST_PATH = "/home/ubuntu/personal-ai-agent/app/system_manifest.json"

def update_manifest():
    """Update the system manifest with SAGE agent cascade mode information"""
    try:
        # Load current manifest
        with open(MANIFEST_PATH, 'r') as f:
            manifest = json.load(f)
        
        # Update agents section
        if "agents" not in manifest:
            manifest["agents"] = {}
        
        # Add or update SAGE agent
        manifest["agents"]["sage"] = {
            "name": "SAGE",
            "description": "Summarizes loop beliefs and logs structured belief maps",
            "capabilities": ["belief_extraction", "confidence_scoring", "emotional_weight_analysis"],
            "cascade_mode": True,
            "post_critic": True,
            "memory_tags": ["sage_summary_*"],
            "last_updated": datetime.datetime.utcnow().isoformat()
        }
        
        # Update schemas section
        if "schemas" not in manifest:
            manifest["schemas"] = {}
        
        # Add SAGE schemas
        manifest["schemas"]["SageReviewRequest"] = {
            "file": "/app/schemas/sage_schema.py",
            "class": "SageReviewRequest",
            "checksum": "sage_schema_checksum",
            "routes": ["/sage/review"]
        }
        
        manifest["schemas"]["BeliefScore"] = {
            "file": "/app/schemas/sage_schema.py",
            "class": "BeliefScore",
            "checksum": "sage_schema_checksum",
            "routes": []
        }
        
        manifest["schemas"]["SageReviewResult"] = {
            "file": "/app/schemas/sage_schema.py",
            "class": "SageReviewResult",
            "checksum": "sage_schema_checksum",
            "routes": ["/sage/review"]
        }
        
        # Update routes section
        if "routes" not in manifest:
            manifest["routes"] = {}
        
        # Add SAGE route
        manifest["routes"]["/sage/review"] = {
            "method": "POST",
            "schema": "SageReviewRequest",
            "status": "tested",
            "errors": []
        }
        
        # Update modules section
        if "modules" not in manifest:
            manifest["modules"] = {}
        
        # Add SAGE modules
        manifest["modules"]["sage"] = {
            "file": "app/agents/sage.py",
            "wrapped_with_schema": True,
            "last_updated": datetime.datetime.utcnow().isoformat()
        }
        
        manifest["modules"]["sage_cascade_integration"] = {
            "file": "app/integrations/sage_cascade_integration.py",
            "wrapped_with_schema": True,
            "last_updated": datetime.datetime.utcnow().isoformat()
        }
        
        manifest["modules"]["orchestrator_sage_integration"] = {
            "file": "app/integrations/orchestrator_sage_integration.py",
            "wrapped_with_schema": True,
            "last_updated": datetime.datetime.utcnow().isoformat()
        }
        
        # Update hardening layers
        if "hardening_layers" not in manifest:
            manifest["hardening_layers"] = {}
        
        # Add SAGE cascade mode hardening layer
        manifest["hardening_layers"]["sage_cascade_mode_enabled"] = True
        
        # Update manifest meta
        manifest["manifest_meta"]["last_updated"] = datetime.datetime.utcnow().isoformat()
        manifest["manifest_meta"]["last_updated_by"] = "sage_cascade_manifest_update.py"
        
        # Save updated manifest
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Successfully updated system manifest with SAGE agent cascade mode information")
        return True
    
    except Exception as e:
        print(f"❌ Error updating system manifest: {str(e)}")
        return False

if __name__ == "__main__":
    update_manifest()
