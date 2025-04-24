#!/usr/bin/env python3
"""
Schema Trace Tool Manifest Update Script

This script updates the system manifest to register the Schema Trace Tool
and enable the schema_trace_tool_enabled hardening layer.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add project root to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("manifest_update")

def update_manifest():
    """Update the system manifest with Schema Trace Tool information."""
    try:
        from app.utils.manifest_manager import (
            update_manifest,
            update_hardening_layer
        )
        
        print("🔄 Updating system manifest for Schema Trace Tool...")
        
        # Add Schema Trace Tool to tools section
        update_manifest("tools", "schema_trace", {
            "name": "Schema Trace Tool",
            "description": "Diagnostic utility that scans the codebase for missing schema definitions and route import errors",
            "version": "1.0.0",
            "path": "tools/schema_trace.py",
            "enabled": True
        })
        print("✅ Registered Schema Trace Tool")
        
        # Enable the schema_trace_tool_enabled hardening layer
        update_hardening_layer("schema_trace_tool_enabled", True)
        print("✅ Updated hardening layers")
        
        # Update manifest with timestamp
        update_manifest("manifest_meta", "last_updated", datetime.now().isoformat())
        print("✅ System manifest updated successfully for Schema Trace Tool")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating manifest: {str(e)}")
        print(f"❌ Failed to update system manifest: {str(e)}")
        return False

if __name__ == "__main__":
    update_manifest()
