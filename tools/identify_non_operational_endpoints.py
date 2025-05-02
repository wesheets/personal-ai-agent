#!/usr/bin/env python3
"""
Non-Operational Endpoints Identifier
Identifies and categorizes non-operational endpoints for repair.
"""

import os
import json
from collections import defaultdict

# Configuration
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
SCHEMA_BREADCRUMBS_FILE = "/home/ubuntu/personal-ai-agent/logs/schema_breadcrumbs_analysis.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/non_operational_endpoints.json"

def load_schema_breadcrumbs():
    """Load schema breadcrumbs analysis results"""
    with open(SCHEMA_BREADCRUMBS_FILE, "r") as f:
        return json.load(f)

def categorize_endpoints_by_module(fix_recommendations):
    """Categorize endpoints by module name"""
    module_endpoints = defaultdict(list)
    
    for endpoint in fix_recommendations:
        module_name = endpoint["module_name"]
        module_endpoints[module_name].append(endpoint)
    
    return module_endpoints

def categorize_endpoints_by_fix_type(fix_recommendations):
    """Categorize endpoints by fix type"""
    fix_type_endpoints = defaultdict(list)
    
    for endpoint in fix_recommendations:
        fix_type = endpoint["fix_type"]
        fix_type_endpoints[fix_type].append(endpoint)
    
    return fix_type_endpoints

def identify_critical_paths(module_endpoints):
    """Identify critical API paths that need to be fixed first"""
    critical_paths = []
    
    # Define critical modules
    critical_modules = ["agent", "memory", "loop", "orchestrator", "hal", "forge"]
    
    for module in critical_modules:
        if module in module_endpoints:
            for endpoint in module_endpoints[module]:
                critical_paths.append(endpoint)
    
    return critical_paths

def identify_common_patterns(fix_recommendations):
    """Identify common patterns in non-operational endpoints"""
    patterns = defaultdict(int)
    
    for endpoint in fix_recommendations:
        route_path = endpoint["route_path"]
        
        # Extract path pattern (first two segments)
        parts = route_path.strip("/").split("/")
        if len(parts) >= 2:
            pattern = f"/{parts[0]}/{parts[1]}"
            patterns[pattern] += 1
        elif len(parts) == 1:
            pattern = f"/{parts[0]}"
            patterns[pattern] += 1
    
    # Sort patterns by frequency
    sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_patterns

def identify_endpoints_with_schema_models(fix_recommendations):
    """Identify endpoints that have corresponding schema models"""
    endpoints_with_models = []
    
    for endpoint in fix_recommendations:
        if "schema_models" in endpoint and endpoint["schema_models"]:
            endpoints_with_models.append(endpoint)
    
    return endpoints_with_models

def main():
    """Main function to identify non-operational endpoints"""
    print("Starting non-operational endpoints identification...")
    
    # Load schema breadcrumbs analysis
    breadcrumbs = load_schema_breadcrumbs()
    fix_recommendations = breadcrumbs["fix_recommendations"]
    print(f"Loaded {len(fix_recommendations)} fix recommendations from schema breadcrumbs analysis")
    
    # Categorize endpoints by module
    module_endpoints = categorize_endpoints_by_module(fix_recommendations)
    print(f"Categorized endpoints into {len(module_endpoints)} modules")
    
    # Categorize endpoints by fix type
    fix_type_endpoints = categorize_endpoints_by_fix_type(fix_recommendations)
    print(f"Categorized endpoints into {len(fix_type_endpoints)} fix types")
    
    # Identify critical paths
    critical_paths = identify_critical_paths(module_endpoints)
    print(f"Identified {len(critical_paths)} critical paths")
    
    # Identify common patterns
    common_patterns = identify_common_patterns(fix_recommendations)
    print(f"Identified {len(common_patterns)} common patterns")
    
    # Identify endpoints with schema models
    endpoints_with_models = identify_endpoints_with_schema_models(fix_recommendations)
    print(f"Identified {len(endpoints_with_models)} endpoints with schema models")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Prepare output
    output = {
        "total_non_operational": len(fix_recommendations),
        "by_priority": {
            "high": len([e for e in fix_recommendations if e["priority"] == "high"]),
            "medium": len([e for e in fix_recommendations if e["priority"] == "medium"]),
            "low": len([e for e in fix_recommendations if e["priority"] == "low"])
        },
        "by_fix_type": {
            fix_type: len(endpoints) for fix_type, endpoints in fix_type_endpoints.items()
        },
        "by_module": {
            module: len(endpoints) for module, endpoints in module_endpoints.items()
        },
        "critical_paths": critical_paths,
        "common_patterns": common_patterns[:10],  # Top 10 patterns
        "endpoints_with_models": len(endpoints_with_models),
        "module_endpoints": module_endpoints,
        "fix_type_endpoints": fix_type_endpoints,
        "endpoints_with_schema_models": endpoints_with_models
    }
    
    # Save output to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Non-operational endpoints identification completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    print("\nSummary of Non-Operational Endpoints:")
    print(f"Total: {output['total_non_operational']}")
    print("\nBy Priority:")
    for priority, count in output["by_priority"].items():
        print(f"  {priority.capitalize()}: {count}")
    
    print("\nBy Fix Type:")
    for fix_type, count in output["by_fix_type"].items():
        print(f"  {fix_type}: {count}")
    
    print("\nTop Modules by Endpoint Count:")
    sorted_modules = sorted(output["by_module"].items(), key=lambda x: x[1], reverse=True)
    for module, count in sorted_modules[:5]:
        print(f"  {module}: {count}")
    
    print("\nTop Common Patterns:")
    for pattern, count in output["common_patterns"][:5]:
        print(f"  {pattern}: {count}")
    
    return output

if __name__ == "__main__":
    main()
