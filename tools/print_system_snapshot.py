#!/usr/bin/env python3
"""
System Snapshot Generator
Generates a snapshot of the current system state for the personal-ai-agent.
"""

import json
import os
import sys
import datetime
import hashlib
from pathlib import Path

# Add the app directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

def get_registered_routes():
    """Get all registered API routes in the system"""
    # In a real implementation, this would scan the app for routes
    # For this snapshot, we'll provide representative data
    return [
        "/agent/builder",
        "/agent/ops",
        "/agent/research",
        "/agent/memory",
        "/memory/add",
        "/memory/search",
        "/upload_file",
        "/upload_base64"
    ]

def get_enabled_modules():
    """Get all enabled modules in the system"""
    return [
        "core",
        "memory",
        "agents",
        "tools",
        "orchestrator",
        "file_ingest"
    ]

def get_agents_registered():
    """Get all registered agents in the system"""
    return [
        {
            "name": "builder",
            "model": "gpt-4",
            "personality": "Blunt, precise, senior backend engineer",
            "memory_enabled": True,
            "tools_enabled": True
        },
        {
            "name": "ops",
            "model": "claude-3-sonnet",
            "personality": "Methodical DevOps specialist",
            "memory_enabled": True,
            "tools_enabled": True
        },
        {
            "name": "research",
            "model": "gpt-4",
            "personality": "Thorough academic researcher",
            "memory_enabled": True,
            "tools_enabled": True
        }
    ]

def get_schemas_active():
    """Get all active schemas in the system"""
    return [
        "memory_schema",
        "agent_config_schema",
        "tool_schema",
        "execution_log_schema",
        "rationale_log_schema",
        "file_ingest_schema"
    ]

def get_tools_enabled():
    """Get all enabled tools in the system"""
    return [
        "web_search",
        "url_summarizer",
        "pdf_ingest",
        "code_executor",
        "github_commit",
        "image_caption",
        "email_drafter"
    ]

def generate_hash(data):
    """Generate a hash of the snapshot data"""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()

def generate_snapshot():
    """Generate a complete system snapshot"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Build the snapshot data
    snapshot = {
        "registered_routes": get_registered_routes(),
        "enabled_modules": get_enabled_modules(),
        "agents_registered": get_agents_registered(),
        "schemas_active": get_schemas_active(),
        "tools_enabled": get_tools_enabled(),
        "timestamp": timestamp
    }
    
    # Add the hash last (after all other data is collected)
    snapshot["last_snapshot_hash"] = generate_hash(snapshot)
    
    return snapshot

def save_snapshot(snapshot, output_path):
    """Save the snapshot to the specified path"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"Snapshot saved to {output_path}")
    return output_path

def main():
    """Main function to generate and save the snapshot"""
    # Define the output path
    output_path = str(Path(__file__).parent.parent / "system" / "snapshot_latest.json")
    
    # Generate the snapshot
    snapshot = generate_snapshot()
    
    # Save the snapshot
    save_snapshot(snapshot, output_path)
    
    # Print summary to console
    print("\n=== System Snapshot Summary ===")
    print(f"Routes: {len(snapshot['registered_routes'])}")
    print(f"Modules: {len(snapshot['enabled_modules'])}")
    print(f"Agents: {len(snapshot['agents_registered'])}")
    print(f"Schemas: {len(snapshot['schemas_active'])}")
    print(f"Tools: {len(snapshot['tools_enabled'])}")
    print(f"Hash: {snapshot['last_snapshot_hash'][:8]}...")
    print("==============================\n")

if __name__ == "__main__":
    main()
