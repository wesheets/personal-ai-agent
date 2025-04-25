#!/usr/bin/env python3
"""
Endpoint Repair Prioritizer
Prioritizes non-operational endpoints for repair based on various criteria.
"""

import os
import json
from collections import defaultdict

# Configuration
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
NON_OPERATIONAL_FILE = "/home/ubuntu/personal-ai-agent/logs/non_operational_endpoints.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/endpoint_repair_priorities.json"

def load_non_operational_endpoints():
    """Load non-operational endpoints analysis"""
    with open(NON_OPERATIONAL_FILE, "r") as f:
        return json.load(f)

def prioritize_by_critical_path(non_operational):
    """Prioritize endpoints by critical path"""
    critical_paths = non_operational["critical_paths"]
    
    # Sort critical paths by priority
    critical_paths.sort(key=lambda x: 0 if x["priority"] == "high" else (1 if x["priority"] == "medium" else 2))
    
    return critical_paths

def prioritize_by_fix_complexity(non_operational):
    """Prioritize endpoints by fix complexity"""
    # Endpoints with schema models are easier to fix
    endpoints_with_models = non_operational["endpoints_with_schema_models"]
    
    # Sort by fix type (server_error is more complex than missing_route)
    endpoints_with_models.sort(key=lambda x: 0 if x["fix_type"] == "missing_route" else 1)
    
    return endpoints_with_models

def prioritize_by_module_importance(non_operational):
    """Prioritize endpoints by module importance"""
    module_endpoints = non_operational["module_endpoints"]
    
    # Define important modules in order of importance
    important_modules = [
        "agent", "memory", "loop", "orchestrator", "hal", "forge",
        "health", "guardian", "historian", "nova", "sage",
        "drift", "debugger", "critic"
    ]
    
    prioritized_by_module = []
    
    # Add endpoints from important modules in order
    for module in important_modules:
        if module in module_endpoints:
            prioritized_by_module.extend(module_endpoints[module])
    
    return prioritized_by_module

def prioritize_by_common_patterns(non_operational):
    """Prioritize endpoints by common patterns"""
    common_patterns = non_operational["common_patterns"]
    fix_recommendations = []
    
    # Flatten all endpoints
    for module_endpoints in non_operational["module_endpoints"].values():
        fix_recommendations.extend(module_endpoints)
    
    # Group endpoints by pattern
    pattern_endpoints = defaultdict(list)
    for endpoint in fix_recommendations:
        route_path = endpoint["route_path"]
        parts = route_path.strip("/").split("/")
        
        if len(parts) >= 2:
            pattern = f"/{parts[0]}/{parts[1]}"
        elif len(parts) == 1:
            pattern = f"/{parts[0]}"
        else:
            pattern = "/"
        
        pattern_endpoints[pattern].append(endpoint)
    
    # Sort patterns by frequency
    prioritized_by_pattern = []
    for pattern, _ in common_patterns:
        if pattern in pattern_endpoints:
            prioritized_by_pattern.extend(pattern_endpoints[pattern])
    
    return prioritized_by_pattern

def create_repair_batches(prioritized_endpoints, batch_size=10):
    """Create repair batches of endpoints"""
    batches = []
    
    # Create batches
    for i in range(0, len(prioritized_endpoints), batch_size):
        batch = prioritized_endpoints[i:i+batch_size]
        batches.append(batch)
    
    return batches

def main():
    """Main function to prioritize endpoints for repair"""
    print("Starting endpoint repair prioritization...")
    
    # Load non-operational endpoints analysis
    non_operational = load_non_operational_endpoints()
    print(f"Loaded analysis for {non_operational['total_non_operational']} non-operational endpoints")
    
    # Prioritize by critical path
    critical_path_priorities = prioritize_by_critical_path(non_operational)
    print(f"Prioritized {len(critical_path_priorities)} endpoints by critical path")
    
    # Prioritize by fix complexity
    fix_complexity_priorities = prioritize_by_fix_complexity(non_operational)
    print(f"Prioritized {len(fix_complexity_priorities)} endpoints by fix complexity")
    
    # Prioritize by module importance
    module_importance_priorities = prioritize_by_module_importance(non_operational)
    print(f"Prioritized {len(module_importance_priorities)} endpoints by module importance")
    
    # Prioritize by common patterns
    common_pattern_priorities = prioritize_by_common_patterns(non_operational)
    print(f"Prioritized {len(common_pattern_priorities)} endpoints by common patterns")
    
    # Create a unified priority list
    # Start with critical paths
    unified_priorities = []
    endpoint_ids = set()
    
    # Add endpoints from each priority list, avoiding duplicates
    for priority_list in [critical_path_priorities, module_importance_priorities, fix_complexity_priorities, common_pattern_priorities]:
        for endpoint in priority_list:
            endpoint_id = f"{endpoint['method']}:{endpoint['route_path']}"
            if endpoint_id not in endpoint_ids:
                unified_priorities.append(endpoint)
                endpoint_ids.add(endpoint_id)
    
    print(f"Created unified priority list with {len(unified_priorities)} endpoints")
    
    # Create repair batches
    repair_batches = create_repair_batches(unified_priorities)
    print(f"Created {len(repair_batches)} repair batches")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Prepare output
    output = {
        "total_endpoints": len(unified_priorities),
        "total_batches": len(repair_batches),
        "critical_path_count": len(critical_path_priorities),
        "fix_complexity_count": len(fix_complexity_priorities),
        "module_importance_count": len(module_importance_priorities),
        "common_pattern_count": len(common_pattern_priorities),
        "unified_priorities": unified_priorities,
        "repair_batches": repair_batches
    }
    
    # Save output to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Endpoint repair prioritization completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary of first batch
    print("\nFirst Repair Batch:")
    for i, endpoint in enumerate(repair_batches[0][:5]):
        print(f"  {i+1}. {endpoint['method']} {endpoint['route_path']} (Priority: {endpoint['priority']}, Fix Type: {endpoint['fix_type']})")
    
    if len(repair_batches[0]) > 5:
        print(f"  ... and {len(repair_batches[0]) - 5} more endpoints in first batch")
    
    return output

if __name__ == "__main__":
    main()
