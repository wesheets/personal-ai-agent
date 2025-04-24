"""
System Manifest Update Script for Health Monitor

This script updates the system manifest to enable the Health Monitor hardening layer
and register the health monitor module and schemas.
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.manifest_manager import (
    load_manifest, 
    update_manifest, 
    save_manifest,
    register_module,
    update_schema_checksum
)

def update_health_monitor_manifest():
    """Update the system manifest with health monitor information."""
    try:
        # Load the current manifest
        manifest = load_manifest()
        
        # Register the health monitor module
        register_module(
            module_name="health_monitor",
            file_path="app/modules/health_monitor.py",
            wrapped_with_schema=True,
            last_updated=datetime.utcnow().isoformat()
        )
        
        # Register health monitor schemas
        schemas = [
            "HealthStatus",
            "ComponentType",
            "HealthMetric",
            "ComponentHealth",
            "SystemHealthSummary",
            "HealthCheckRequest",
            "HealthCheckResponse",
            "PredictiveMaintenanceRequest",
            "MaintenancePrediction",
            "PredictiveMaintenanceResponse",
            "SelfHealingAction",
            "SelfHealingRequest",
            "HealingActionResult",
            "SelfHealingResponse",
            "HealthMonitorConfigRequest",
            "HealthMonitorConfigResponse"
        ]
        
        for schema in schemas:
            update_schema_checksum(
                schema_name=schema,
                file_path="app/schemas/health_monitor_schema.py",
                checksum="health_monitor_schema_checksum"
            )
        
        # Enable the health monitor hardening layer
        update_manifest(
            section="hardening_layers",
            key="health_monitor_enabled",
            value=True
        )
        
        # Update manifest metadata
        update_manifest(
            section="manifest_meta",
            key="last_updated",
            value=datetime.utcnow().isoformat()
        )
        
        update_manifest(
            section="manifest_meta",
            key="last_updated_by",
            value="health_monitor_manifest_update.py"
        )
        
        # Save the updated manifest
        save_manifest(manifest)
        
        print("✅ System manifest updated successfully with health monitor information")
        return True
    
    except Exception as e:
        print(f"❌ Error updating system manifest: {str(e)}")
        return False

if __name__ == "__main__":
    update_health_monitor_manifest()
