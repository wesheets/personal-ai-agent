#!/usr/bin/env python3
"""
System Audit Summary Generator for Personal AI Agent Backend
Combines all audit data into a comprehensive summary report.
"""

import json
import os
import sys
import datetime
from pathlib import Path

# Configuration
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/system_audit_summary.json"
ROUTE_AUDIT_FILE = "/home/ubuntu/personal-ai-agent/logs/live_endpoint_audit_report.json"
AGENT_AUDIT_FILE = "/home/ubuntu/personal-ai-agent/logs/agent_audit_report.json"
SCHEMA_AUDIT_FILE = "/home/ubuntu/personal-ai-agent/logs/schema_audit_report.json"
MODULE_AUDIT_FILE = "/home/ubuntu/personal-ai-agent/logs/module_audit_report.json"

def load_audit_data():
    """Load all audit data from individual audit files"""
    audit_data = {
        "routes": [],
        "agents": [],
        "schemas": [],
        "modules": []
    }
    
    # Load route audit data
    if os.path.exists(ROUTE_AUDIT_FILE):
        with open(ROUTE_AUDIT_FILE, "r") as f:
            audit_data["routes"] = json.load(f)
            print(f"Loaded route audit data with {len(audit_data['routes'])} entries")
    
    # Load agent audit data
    if os.path.exists(AGENT_AUDIT_FILE):
        with open(AGENT_AUDIT_FILE, "r") as f:
            audit_data["agents"] = json.load(f)
            print(f"Loaded agent audit data with {len(audit_data['agents'])} entries")
    
    # Load schema audit data
    if os.path.exists(SCHEMA_AUDIT_FILE):
        with open(SCHEMA_AUDIT_FILE, "r") as f:
            audit_data["schemas"] = json.load(f)
            print(f"Loaded schema audit data with {len(audit_data['schemas'])} entries")
    
    # Load module audit data
    if os.path.exists(MODULE_AUDIT_FILE):
        with open(MODULE_AUDIT_FILE, "r") as f:
            audit_data["modules"] = json.load(f)
            print(f"Loaded module audit data with {len(audit_data['modules'])} entries")
    
    return audit_data

def calculate_statistics(audit_data):
    """Calculate statistics from audit data"""
    stats = {}
    
    # Route statistics
    if audit_data["routes"]:
        total_routes = len(audit_data["routes"])
        working_routes = sum(1 for route in audit_data["routes"] if "200 OK" in route["status"])
        stats["routes"] = {
            "total": total_routes,
            "working": working_routes,
            "percentage": round(working_routes / total_routes * 100, 1) if total_routes > 0 else 0
        }
    
    # Agent statistics
    if audit_data["agents"]:
        total_agents = len(audit_data["agents"])
        registered_agents = sum(1 for agent in audit_data["agents"] if agent["registered_in_registry"])
        active_agents = sum(1 for agent in audit_data["agents"] if agent["confirmed_active_endpoint"])
        stats["agents"] = {
            "total": total_agents,
            "registered": registered_agents,
            "active": active_agents,
            "percentage": round(registered_agents / total_agents * 100, 1) if total_agents > 0 else 0
        }
    
    # Schema statistics
    if audit_data["schemas"]:
        total_schemas = len(audit_data["schemas"])
        validated_schemas = sum(1 for schema in audit_data["schemas"] if schema["validated_pydantic"])
        bound_to_routes = sum(1 for schema in audit_data["schemas"] if schema["bound_to_route"] != "None")
        bound_to_agents = sum(1 for schema in audit_data["schemas"] if schema["bound_to_agent"] != "None")
        stats["schemas"] = {
            "total": total_schemas,
            "validated": validated_schemas,
            "bound_to_routes": bound_to_routes,
            "bound_to_agents": bound_to_agents,
            "percentage": round(validated_schemas / total_schemas * 100, 1) if total_schemas > 0 else 0
        }
    
    # Module statistics
    if audit_data["modules"]:
        total_modules = len(audit_data["modules"])
        registered_modules = sum(1 for module in audit_data["modules"] if module["router_registered"])
        live_modules = sum(1 for module in audit_data["modules"] if module["live_on_backend"])
        stats["modules"] = {
            "total": total_modules,
            "registered": registered_modules,
            "live": live_modules,
            "percentage": round(registered_modules / total_modules * 100, 1) if total_modules > 0 else 0
        }
    
    return stats

def identify_critical_gaps(audit_data, stats):
    """Identify critical gaps and missing pieces"""
    critical_gaps = []
    
    # Check for missing agent endpoints
    if stats.get("agents", {}).get("active", 0) == 0 and stats.get("agents", {}).get("total", 0) > 0:
        critical_gaps.append("No agent endpoints are active")
    
    # Check for specific critical agent endpoints
    critical_agent_endpoints = ["/agent/loop", "/agent/delegate", "/agent/forge", "/agent/hal"]
    for endpoint in critical_agent_endpoints:
        found = False
        for route in audit_data["routes"]:
            if route["route_path"] == endpoint and "200 OK" in route["status"]:
                found = True
                break
        if not found:
            critical_gaps.append(f"Critical endpoint {endpoint} is not operational")
    
    # Check for memory endpoints
    memory_endpoints = ["/memory/add", "/memory/search"]
    memory_operational = False
    for endpoint in memory_endpoints:
        for route in audit_data["routes"]:
            if route["route_path"] == endpoint and "200 OK" in route["status"]:
                memory_operational = True
                break
    if not memory_operational:
        critical_gaps.append("Memory system endpoints are not operational")
    
    # Check for orchestrator endpoints
    orchestrator_endpoints = ["/orchestrator/status", "/orchestrator/consult"]
    orchestrator_operational = False
    for endpoint in orchestrator_endpoints:
        for route in audit_data["routes"]:
            if route["route_path"] == endpoint and "200 OK" in route["status"]:
                orchestrator_operational = True
                break
    if not orchestrator_operational:
        critical_gaps.append("Orchestrator endpoints are not operational")
    
    # Check for schema-agent binding issues
    if stats.get("schemas", {}).get("bound_to_agents", 0) < 5 and stats.get("agents", {}).get("total", 0) >= 5:
        critical_gaps.append("Most schemas are not properly bound to agents")
    
    return critical_gaps

def identify_repair_priorities(critical_gaps, stats):
    """Identify immediate high priority repairs"""
    repair_priorities = []
    
    # Based on critical gaps
    if "No agent endpoints are active" in critical_gaps:
        repair_priorities.append("Deploy and activate agent endpoints, particularly /agent/forge and /agent/hal")
    
    if "Memory system endpoints are not operational" in critical_gaps:
        repair_priorities.append("Restore memory system functionality for agent context persistence")
    
    if "Orchestrator endpoints are not operational" in critical_gaps:
        repair_priorities.append("Fix orchestrator endpoints to enable agent coordination")
    
    # Based on statistics
    if stats.get("routes", {}).get("percentage", 0) < 10:
        repair_priorities.append("Investigate backend deployment issues - most endpoints are returning 404")
    
    if stats.get("schemas", {}).get("bound_to_agents", 0) < 5:
        repair_priorities.append("Fix schema-agent bindings to ensure proper contract enforcement")
    
    # If no specific issues found, add general recommendation
    if not repair_priorities:
        repair_priorities.append("Verify backend deployment configuration and server status")
    
    return repair_priorities

def generate_timestamp():
    """Generate timestamp in the required format"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M")

def main():
    """Main function to generate the system audit summary"""
    print("Starting system audit summary generation...")
    
    # Load all audit data
    audit_data = load_audit_data()
    
    # Calculate statistics
    stats = calculate_statistics(audit_data)
    print("Calculated statistics from audit data")
    
    # Identify critical gaps
    critical_gaps = identify_critical_gaps(audit_data, stats)
    print(f"Identified {len(critical_gaps)} critical gaps")
    
    # Identify repair priorities
    repair_priorities = identify_repair_priorities(critical_gaps, stats)
    print(f"Identified {len(repair_priorities)} repair priorities")
    
    # Generate timestamp for memory tag
    timestamp = generate_timestamp()
    memory_tag = f"system_audit_post_hardening_{timestamp}"
    
    # Create summary report
    summary = {
        "timestamp": timestamp,
        "memory_tag": memory_tag,
        "statistics": stats,
        "critical_gaps": critical_gaps,
        "repair_priorities": repair_priorities
    }
    
    # Save summary to file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"System audit summary completed. Results saved to {OUTPUT_FILE}")
    
    # Print operator console summary
    print("\n=== OPERATOR CONSOLE SUMMARY ===")
    print(f"Routes: {stats.get('routes', {}).get('working', 0)}/{stats.get('routes', {}).get('total', 0)} operational ({stats.get('routes', {}).get('percentage', 0)}%)")
    print(f"Agents: {stats.get('agents', {}).get('registered', 0)}/{stats.get('agents', {}).get('total', 0)} wired ({stats.get('agents', {}).get('percentage', 0)}%)")
    print(f"Schemas: {stats.get('schemas', {}).get('validated', 0)}/{stats.get('schemas', {}).get('total', 0)} validated ({stats.get('schemas', {}).get('percentage', 0)}%)")
    print(f"Modules: {stats.get('modules', {}).get('registered', 0)}/{stats.get('modules', {}).get('total', 0)} wired ({stats.get('modules', {}).get('percentage', 0)}%)")
    
    if critical_gaps:
        print("\nCritical Gaps:")
        for gap in critical_gaps[:2]:  # Show top 2 gaps
            print(f"- {gap}")
        if len(critical_gaps) > 2:
            print(f"- Plus {len(critical_gaps) - 2} more issues...")
    
    print(f"Memory Tag: {memory_tag}")
    print("===============================")
    
    return summary

if __name__ == "__main__":
    main()
