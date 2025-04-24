import json
import os
import datetime

def update_manifest():
    """
    Update the system manifest to register the validate_schema_hash schema.
    """
    manifest_path = "app/system_manifest.json"
    
    # Load the current manifest
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # Add the new schema entries
    manifest["schemas"]["ValidateSchemaHashRequest"] = {
        "file": "app/schemas/validate_schema_hash.py",
        "bound_to_routes": [
            "/critic/validate_schema"
        ],
        "version": "v1.0.0",
        "checksum": "initial"
    }
    
    manifest["schemas"]["ValidateSchemaHashResult"] = {
        "file": "app/schemas/validate_schema_hash.py",
        "bound_to_routes": [
            "/critic/validate_schema"
        ],
        "version": "v1.0.0",
        "checksum": "initial"
    }
    
    # Update the manifest metadata
    manifest["manifest_meta"]["last_updated"] = datetime.datetime.now().isoformat()
    manifest["manifest_meta"]["last_updated_by"] = "backend_patch_manifest_update.py"
    
    # Add memory tag for patch history
    memory_tag = f"backend_patch_applied_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    manifest["memory"]["tags"][memory_tag] = {
        "pattern": memory_tag,
        "description": "Backend patch applied to fix missing schema and route imports",
        "schema": "None",
        "retention_days": 30
    }
    
    # Write the updated manifest
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Updated system manifest with validate_schema_hash schema")
    print(f"✅ Added memory tag: {memory_tag}")
    
    return {
        "status": "success",
        "message": "System manifest updated successfully",
        "memory_tag": memory_tag
    }

if __name__ == "__main__":
    update_manifest()
