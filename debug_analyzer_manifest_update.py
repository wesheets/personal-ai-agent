"""
Debug Analyzer Manifest Update Script

This script updates the system manifest to register the Debug Analyzer agent,
its schemas, routes, and memory tags.
"""

import os
import json
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import manifest manager
from app.utils.manifest_manager import (
    update_manifest,
    register_schema,
    register_route,
    register_agent,
    update_hardening_layer
)

def update_debug_analyzer_manifest():
    """Update system manifest with Debug Analyzer components."""
    print("🔄 Updating system manifest for Debug Analyzer agent...")
    
    # Register schemas
    register_schema(
        schema_name="LoopDebugRequest",
        file_path="app/schemas/debug_schema.py",
        routes=["/debug/analyze-loop"],
        version="v1.0.0"
    )
    register_schema(
        schema_name="LoopDebugResult",
        file_path="app/schemas/debug_schema.py",
        routes=["/debug/analyze-loop"],
        version="v1.0.0"
    )
    register_schema(
        schema_name="LoopIssue",
        file_path="app/schemas/debug_schema.py",
        routes=[],
        version="v1.0.0"
    )
    register_schema(
        schema_name="RepairSuggestion",
        file_path="app/schemas/debug_schema.py",
        routes=[],
        version="v1.0.0"
    )
    print("✅ Registered Debug Analyzer schemas")
    
    # Register routes
    register_route(
        route_path="/debug/analyze-loop",
        method="POST",
        schema_name="LoopDebugRequest",
        status="registered"
    )
    print("✅ Registered Debug Analyzer routes")
    
    # Register agent
    register_agent(
        agent_name="debug_analyzer",
        tools=["analyze_memory", "diagnose_loop", "recommend_fix"],
        schema_wrapped=True,
        fallbacks=["schema_fallback"]
    )
    print("✅ Registered Debug Analyzer agent")
    
    # Register memory tags using update_manifest
    update_manifest(
        "memory",
        "tags",
        {
            "loop_diagnosis": {
                "pattern": "loop_diagnosis_{loop_id}_v{n}",
                "description": "Debug Analyzer diagnosis results for a loop execution",
                "schema": "LoopDebugResult",
                "retention_days": 30
            }
        }
    )
    print("✅ Registered Debug Analyzer memory tags")
    
    # Update hardening layers
    update_hardening_layer("debug_tools_enabled", True)
    
    # Add diagnostic_agents to hardening layers
    update_manifest(
        "hardening_layers",
        "diagnostic_agents",
        ["debug_analyzer"]
    )
    print("✅ Updated hardening layers")
    
    print("✅ System manifest updated successfully for Debug Analyzer agent")
    return True

if __name__ == "__main__":
    update_debug_analyzer_manifest()
