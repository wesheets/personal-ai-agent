#!/usr/bin/env python3
"""
Non-Operational Endpoints Identifier
Identifies remaining non-operational endpoints that still need fixing.
"""

import os
import json
import datetime
from collections import defaultdict

# Configuration
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
FRESH_SWEEP_FILE = "/home/ubuntu/personal-ai-agent/logs/postman_sweep_after_deployment.json"
SCHEMA_BREADCRUMBS_FILE = "/home/ubuntu/personal-ai-agent/logs/schema_breadcrumbs_analysis.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/remaining_non_operational_endpoints.json"

def load_fresh_sweep():
    """Load fresh Postman sweep results"""
    with open(FRESH_SWEEP_FILE, "r") as f:
        return json.load(f)

def load_schema_breadcrumbs():
    """Load schema breadcrumbs analysis"""
    with open(SCHEMA_BREADCRUMBS_FILE, "r") as f:
        return json.load(f)

def identify_non_operational_endpoints(fresh_sweep):
    """Identify non-operational endpoints from fresh sweep results"""
    non_operational = []
    
    for endpoint in fresh_sweep["results"]:
        status_code = endpoint.get("status_code")
        
        # Consider endpoints with status codes other than 200 or 422 as non-operational
        if status_code not in [200, 422]:
            non_operational.append({
                "method": endpoint["method"],
                "route_path": endpoint["route_path"],
                "status_code": status_code,
                "status": endpoint["status"],
                "was_fixed": endpoint.get("was_fixed", False)
            })
    
    return non_operational

def categorize_by_status(endpoints):
    """Categorize endpoints by their status code"""
    status_endpoints = defaultdict(list)
    
    for endpoint in endpoints:
        status_code = endpoint["status_code"]
        if status_code is None:
            status_code = "error"
        status_endpoints[status_code].append(endpoint)
    
    return status_endpoints

def categorize_by_module(endpoints):
    """Categorize endpoints by their module"""
    module_endpoints = defaultdict(list)
    
    for endpoint in endpoints:
        route_path = endpoint["route_path"]
        parts = route_path.strip("/").split("/")
        
        if parts:
            module = parts[0]
            module_endpoints[module].append(endpoint)
        else:
            module_endpoints["root"].append(endpoint)
    
    return module_endpoints

def match_with_schema_breadcrumbs(non_operational, schema_breadcrumbs):
    """Match non-operational endpoints with schema breadcrumbs"""
    matched_endpoints = []
    
    # Create a lookup dictionary for schema routes
    schema_routes = {}
    for schema_name, schema_data in schema_breadcrumbs["schema_route_map"].items():
        if schema_data.get("actual_routes"):
            for route in schema_data["actual_routes"]:
                # We don't have method information in the schema data, so we'll match by path only
                schema_routes[route] = {
                    "schema_name": schema_name,
                    "schema_file": schema_data["schema_info"]["file_path"],
                    "route_file": schema_data.get("route_file"),
                    "models": schema_data["schema_info"]["models"]
                }
    
    # Match non-operational endpoints with schema routes
    for endpoint in non_operational:
        method = endpoint["method"]
        route_path = endpoint["route_path"]
        
        # Try exact match first
        if route_path in schema_routes:
            matched_endpoints.append({
                **endpoint,
                "schema_match": schema_routes[route_path]
            })
        else:
            # Try to find a partial match by checking if any schema route is a prefix of this route
            # or if this route matches a schema route with path parameters
            matched = False
            for schema_path, schema_value in schema_routes.items():
                if is_path_match(route_path, schema_path):
                    matched_endpoints.append({
                        **endpoint,
                        "schema_match": schema_value,
                        "partial_match": True
                    })
                    matched = True
                    break
            
            if not matched:
                # No match found
                matched_endpoints.append({
                    **endpoint,
                    "schema_match": None
                })
    
    return matched_endpoints

def is_path_match(actual_path, schema_path):
    """Check if an actual path matches a schema path with parameters"""
    # Replace test_id placeholders with {param} format for comparison
    if "test_" in actual_path:
        parts = actual_path.split("/")
        for i, part in enumerate(parts):
            if part.startswith("test_"):
                parts[i] = "{" + part[5:] + "}"
        actual_path_normalized = "/".join(parts)
    else:
        actual_path_normalized = actual_path
    
    # Direct comparison with schema path
    if actual_path_normalized == schema_path:
        return True
    
    # Check if paths match when ignoring path parameters
    actual_parts = actual_path.strip("/").split("/")
    schema_parts = schema_path.strip("/").split("/")
    
    if len(actual_parts) != len(schema_parts):
        return False
    
    for i, (actual, schema) in enumerate(zip(actual_parts, schema_parts)):
        if "{" in schema and "}" in schema:
            # This is a path parameter, so it can match anything
            continue
        elif actual != schema:
            return False
    
    return True

def main():
    """Main function to identify remaining non-operational endpoints"""
    print("Starting identification of remaining non-operational endpoints...")
    
    # Load data
    fresh_sweep = load_fresh_sweep()
    schema_breadcrumbs = load_schema_breadcrumbs()
    print(f"Loaded fresh sweep with {len(fresh_sweep['results'])} endpoints and schema breadcrumbs with {len(schema_breadcrumbs['schema_route_map'])} schemas")
    
    # Identify non-operational endpoints
    non_operational = identify_non_operational_endpoints(fresh_sweep)
    print(f"Identified {len(non_operational)} non-operational endpoints")
    
    # Categorize by status
    status_endpoints = categorize_by_status(non_operational)
    print("Categorized non-operational endpoints by status:")
    for status, endpoints in status_endpoints.items():
        print(f"  {status}: {len(endpoints)}")
    
    # Categorize by module
    module_endpoints = categorize_by_module(non_operational)
    print(f"Categorized non-operational endpoints into {len(module_endpoints)} modules")
    
    # Match with schema breadcrumbs
    matched_endpoints = match_with_schema_breadcrumbs(non_operational, schema_breadcrumbs)
    
    # Count matches
    with_schema_match = sum(1 for endpoint in matched_endpoints if endpoint.get("schema_match") is not None)
    without_schema_match = sum(1 for endpoint in matched_endpoints if endpoint.get("schema_match") is None)
    partial_matches = sum(1 for endpoint in matched_endpoints if endpoint.get("partial_match", False))
    
    print(f"Matched {with_schema_match} endpoints with schema breadcrumbs ({partial_matches} partial matches)")
    print(f"Could not match {without_schema_match} endpoints with schema breadcrumbs")
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Prepare output
    output = {
        "timestamp": timestamp,
        "total_endpoints": len(fresh_sweep["results"]),
        "operational_count": len(fresh_sweep["results"]) - len(non_operational),
        "non_operational_count": len(non_operational),
        "status_breakdown": {str(status): len(endpoints) for status, endpoints in status_endpoints.items()},
        "module_breakdown": {module: len(endpoints) for module, endpoints in module_endpoints.items()},
        "schema_match_count": with_schema_match,
        "no_schema_match_count": without_schema_match,
        "partial_match_count": partial_matches,
        "non_operational_endpoints": matched_endpoints
    }
    
    # Save output to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Identification of remaining non-operational endpoints completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    print("\nNon-Operational Endpoints Summary:")
    print(f"Total Endpoints: {output['total_endpoints']}")
    print(f"Operational Endpoints: {output['operational_count']} ({round(output['operational_count'] / output['total_endpoints'] * 100, 1)}%)")
    print(f"Non-Operational Endpoints: {output['non_operational_count']} ({round(output['non_operational_count'] / output['total_endpoints'] * 100, 1)}%)")
    
    print("\nStatus Breakdown:")
    for status, count in output["status_breakdown"].items():
        print(f"  {status}: {count}")
    
    print("\nTop Modules with Non-Operational Endpoints:")
    sorted_modules = sorted(output["module_breakdown"].items(), key=lambda x: x[1], reverse=True)
    for module, count in sorted_modules[:5]:
        print(f"  {module}: {count}")
    
    print("\nSchema Matching:")
    print(f"  With Schema Match: {output['schema_match_count']} ({round(output['schema_match_count'] / output['non_operational_count'] * 100, 1)}%)")
    print(f"  Partial Matches: {output['partial_match_count']} ({round(output['partial_match_count'] / output['non_operational_count'] * 100, 1)}%)")
    print(f"  Without Schema Match: {output['no_schema_match_count']} ({round(output['no_schema_match_count'] / output['non_operational_count'] * 100, 1)}%)")
    
    return output

if __name__ == "__main__":
    main()
