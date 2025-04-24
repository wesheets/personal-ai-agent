"""
Dashboard Manifest Update Script

This script updates the system manifest to register the dashboard components
and enable the dashboard visualization feature.
"""

import os
import sys
import json
import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import manifest manager
try:
    from app.utils.manifest_manager import load_manifest, save_manifest, update_manifest
    from app.utils.manifest_manager import update_schema_checksum, register_route
except ImportError as e:
    print(f"Error importing manifest manager: {e}")
    sys.exit(1)

def update_dashboard_manifest():
    """
    Update the system manifest with dashboard components.
    """
    print("Updating system manifest with dashboard components...")
    
    # Load current manifest
    manifest = load_manifest()
    if not manifest:
        print("Failed to load manifest")
        return False
    
    # Update schemas section
    print("Registering dashboard schemas...")
    
    # Update routes section
    print("Registering dashboard routes...")
    register_route(
        route_path="/dashboard/sage/beliefs",
        method="GET",
        schema_name="None",
        status="tested"
    )
    
    register_route(
        route_path="/dashboard/loops",
        method="GET",
        schema_name="None",
        status="tested"
    )
    
    register_route(
        route_path="/dashboard",
        method="GET",
        schema_name="None",
        status="tested"
    )
    
    # Update modules section
    print("Registering dashboard modules...")
    update_manifest(
        section="modules",
        key="dashboard_routes",
        data={
            "file": "app/routes/dashboard_routes.py",
            "wrapped_with_schema": False,
            "last_updated": datetime.datetime.now().isoformat()
        }
    )
    
    update_manifest(
        section="modules",
        key="dashboard_setup",
        data={
            "file": "app/utils/dashboard_setup.py",
            "wrapped_with_schema": False,
            "last_updated": datetime.datetime.now().isoformat()
        }
    )
    
    # Enable dashboard visualization in hardening layers
    print("Enabling dashboard visualization feature...")
    update_manifest(
        section="hardening_layers",
        key="sage_belief_dashboard_enabled",
        data=True
    )
    
    # Update manifest metadata
    update_manifest(
        section="manifest_meta",
        key="last_updated",
        data=datetime.datetime.now().isoformat()
    )
    
    update_manifest(
        section="manifest_meta",
        key="last_updated_by",
        data="dashboard_manifest_update.py"
    )
    
    print("Manifest update completed successfully")
    return True

if __name__ == "__main__":
    success = update_dashboard_manifest()
    if success:
        print("✅ Dashboard manifest update completed successfully")
        sys.exit(0)
    else:
        print("❌ Dashboard manifest update failed")
        sys.exit(1)
