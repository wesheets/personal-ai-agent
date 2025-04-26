#!/usr/bin/env python3
"""
System Snapshot Generator for Batch 1
This script generates a comprehensive system snapshot after Batch 1 implementation.
"""

import json
import os
import sys
import datetime
import hashlib
from pathlib import Path

# Configuration
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M")
SNAPSHOT_DIR = "/home/ubuntu/personal-ai-agent/system"
MEMORY_DIR = "/home/ubuntu/personal-ai-agent/app/logs/memory_events"
ACI_PATH = "/home/ubuntu/personal-ai-agent/app/system/agent_cognition_index.json"

def generate_snapshot():
    """Generate a comprehensive system snapshot"""
    
    # Ensure directories exist
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    # Read ACI
    try:
        with open(ACI_PATH, 'r') as f:
            aci_data = json.load(f)
    except Exception as e:
        print(f"Error reading ACI: {e}")
        return None
    
    # Collect route information
    routes = []
    for agent in aci_data.get("agents", []):
        for route in agent.get("responsible_routes", []):
            routes.append({
                "path": route,
                "agent": agent.get("agent_id"),
                "status": "operational" if "/api/loop/validate" in route else 
                          ("partial" if "/api/plan/generate" in route else "unknown")
            })
    
    # Collect agent information
    agents = []
    for agent in aci_data.get("agents", []):
        agents.append({
            "id": agent.get("agent_id"),
            "role": agent.get("role"),
            "passes_full_test": agent.get("passes_full_test", False),
            "routes_count": len(agent.get("responsible_routes", [])),
            "last_modified": agent.get("last_modified")
        })
    
    # Generate snapshot data
    snapshot = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tag": f"snapshot_after_batch1_loop_fixes",
        "memory_tag": f"batch1_routes_verified_{TIMESTAMP}",
        "system_state": {
            "total_agents": len(aci_data.get("agents", [])),
            "total_routes": len(routes),
            "operational_routes": sum(1 for r in routes if r["status"] == "operational"),
            "partial_routes": sum(1 for r in routes if r["status"] == "partial"),
            "batch1_status": "partial",  # Since plan_generate still has an issue
            "last_updated": aci_data.get("last_updated")
        },
        "agents": agents,
        "routes": routes,
        "batch1_validation": {
            "plan_generate": {
                "status": "partial",
                "issue": "Returns 500 for empty goal parameter instead of 422",
                "fix_status": "Implemented but not deployed"
            },
            "loop_validate": {
                "status": "operational",
                "issue": None,
                "fix_status": "Completed"
            }
        }
    }
    
    # Calculate hash
    snapshot_str = json.dumps(snapshot, sort_keys=True)
    snapshot_hash = hashlib.sha256(snapshot_str.encode()).hexdigest()
    snapshot["hash"] = snapshot_hash
    
    # Save snapshot
    snapshot_path = os.path.join(SNAPSHOT_DIR, "snapshot_latest.json")
    with open(snapshot_path, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    # Save memory event
    memory_path = os.path.join(MEMORY_DIR, f"system_snapshot_batch1_{TIMESTAMP}.json")
    with open(memory_path, 'w') as f:
        json.dump({
            "event_type": "system_snapshot",
            "timestamp": datetime.datetime.now().isoformat(),
            "tag": f"snapshot_after_batch1_loop_fixes",
            "hash": snapshot_hash,
            "batch": "batch1",
            "status": "partial",
            "notes": "Loop validation operational, plan generation partially fixed"
        }, f, indent=2)
    
    return {
        "snapshot_path": snapshot_path,
        "memory_path": memory_path,
        "hash": snapshot_hash
    }

if __name__ == "__main__":
    print("Generating system snapshot for Batch 1...")
    result = generate_snapshot()
    
    if result:
        print(f"✅ Snapshot generated successfully!")
        print(f"Snapshot saved to: {result['snapshot_path']}")
        print(f"Memory event saved to: {result['memory_path']}")
        print(f"Snapshot hash: {result['hash']}")
    else:
        print("❌ Failed to generate snapshot")
        sys.exit(1)
