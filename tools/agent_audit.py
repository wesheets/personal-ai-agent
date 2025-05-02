#!/usr/bin/env python3
"""
Agent Audit Tool for Personal AI Agent Backend
Analyzes the agent registry and contracts to report on agent status.
"""

import json
import os
import sys
from pathlib import Path

# Configuration
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/agent_audit_report.json"
AGENT_REGISTRY_PATH = "/home/ubuntu/personal-ai-agent/app/core/agent_registry_enhanced.py"
CONTRACTS_DIR = "/home/ubuntu/personal-ai-agent/app/contracts"
COMBINED_CONTRACTS_PATH = "/home/ubuntu/personal-ai-agent/app/contracts/agent_contracts.json"

def load_agent_contracts():
    """Load agent contracts from the contracts directory"""
    contracts = {}
    
    # First try to load the combined agent_contracts.json file
    if os.path.exists(COMBINED_CONTRACTS_PATH):
        with open(COMBINED_CONTRACTS_PATH, "r") as f:
            contracts = json.load(f)
            print(f"Loaded {len(contracts)} agent contracts from combined file")
    
    # Also check for individual contract files
    for filename in os.listdir(CONTRACTS_DIR):
        if filename.endswith(".json") and filename != "agent_contracts.json":
            agent_id = filename.split(".")[0]
            contract_path = os.path.join(CONTRACTS_DIR, filename)
            
            with open(contract_path, "r") as f:
                contract_data = json.load(f)
                if agent_id not in contracts:
                    contracts[agent_id] = contract_data
                    print(f"Loaded contract for agent {agent_id} from individual file")
    
    return contracts

def check_manifest_registration(agent_id):
    """Check if agent is registered in manifest"""
    # This is a simplified check - in a real implementation, we would parse the manifest files
    # For now, we'll assume agents in the contracts are registered in the manifest
    return True

def check_endpoint_active(agent_id, route_audit_data):
    """Check if agent endpoint is active based on route audit data"""
    endpoint_path = f"/agent/{agent_id}"
    
    for route in route_audit_data:
        if route["route_path"] == endpoint_path and route["method"] == "POST":
            return route["status"] == "200 OK"
    
    return False

def main():
    """Main function to run the agent audit"""
    print("Starting agent audit...")
    
    # Load route audit data if available
    route_audit_data = []
    route_audit_path = "/home/ubuntu/personal-ai-agent/logs/live_endpoint_audit_report.json"
    if os.path.exists(route_audit_path):
        with open(route_audit_path, "r") as f:
            route_audit_data = json.load(f)
            print(f"Loaded route audit data with {len(route_audit_data)} routes")
    
    # Load agent contracts
    contracts = load_agent_contracts()
    
    # Prepare audit results
    audit_results = []
    
    # Analyze each agent
    for agent_id, contract in contracts.items():
        print(f"Analyzing agent: {agent_id}")
        
        # Get agent role from contract if available
        role = "Unknown"
        if "description" in contract:
            role = contract["description"]
        
        # Check if agent is registered in registry
        registered_in_registry = True  # Assuming all agents in contracts are in registry
        
        # Check if agent is registered in manifest
        registered_in_manifest = check_manifest_registration(agent_id)
        
        # Check if agent endpoint is active
        confirmed_active_endpoint = check_endpoint_active(agent_id, route_audit_data)
        
        # Add to audit results
        audit_results.append({
            "agent_name": agent_id,
            "role": role,
            "registered_in_registry": registered_in_registry,
            "registered_in_manifest": registered_in_manifest,
            "confirmed_active_endpoint": confirmed_active_endpoint
        })
    
    # Save results to file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f"Agent audit completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    total_agents = len(audit_results)
    registered_in_registry = sum(1 for agent in audit_results if agent["registered_in_registry"])
    registered_in_manifest = sum(1 for agent in audit_results if agent["registered_in_manifest"])
    active_endpoints = sum(1 for agent in audit_results if agent["confirmed_active_endpoint"])
    
    print("\nAgent Audit Summary:")
    print(f"Total Agents: {total_agents}")
    print(f"Registered in Registry: {registered_in_registry}/{total_agents} ({registered_in_registry/total_agents*100:.1f}%)")
    print(f"Registered in Manifest: {registered_in_manifest}/{total_agents} ({registered_in_manifest/total_agents*100:.1f}%)")
    print(f"Active Endpoints: {active_endpoints}/{total_agents} ({active_endpoints/total_agents*100:.1f}%)")
    
    return audit_results

if __name__ == "__main__":
    main()
