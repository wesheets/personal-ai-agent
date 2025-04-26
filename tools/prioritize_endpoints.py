#!/usr/bin/env python3
"""
Endpoint Prioritizer
Prioritizes the next batch of non-operational endpoints for fixing based on identification results.
"""

import os
import json
import datetime
from collections import defaultdict

# Configuration
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
REMAINING_ENDPOINTS_FILE = "/home/ubuntu/personal-ai-agent/logs/remaining_non_operational_endpoints.json"
DEPLOYMENT_ANALYSIS_FILE = "/home/ubuntu/personal-ai-agent/logs/deployment_fix_analysis.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/next_batch_priorities.json"
BATCH_SIZE = 10  # Number of endpoints to include in the next batch

def load_remaining_endpoints():
    """Load remaining non-operational endpoints"""
    with open(REMAINING_ENDPOINTS_FILE, "r") as f:
        return json.load(f)

def load_deployment_analysis():
    """Load deployment fix analysis"""
    with open(DEPLOYMENT_ANALYSIS_FILE, "r") as f:
        return json.load(f)

def prioritize_by_status(endpoints):
    """Prioritize endpoints by their status code"""
    # 500 errors are higher priority than 404s
    status_priority = {
        500: 1,
        "error": 2,
        404: 3
    }
    
    # Sort endpoints by status priority
    return sorted(endpoints, key=lambda x: status_priority.get(x["status_code"], 999))

def prioritize_by_module(endpoints):
    """Prioritize endpoints by their module importance"""
    # Define critical modules in order of importance
    critical_modules = [
        "agent",
        "memory",
        "loop",
        "orchestrator",
        "hal",
        "forge",
        "health",
        "api",
        "debug"
    ]
    
    # Assign priority scores based on module
    for endpoint in endpoints:
        route_path = endpoint["route_path"]
        parts = route_path.strip("/").split("/")
        
        if parts:
            module = parts[0]
            if module in critical_modules:
                endpoint["module_priority"] = critical_modules.index(module) + 1
            else:
                endpoint["module_priority"] = len(critical_modules) + 1
        else:
            endpoint["module_priority"] = len(critical_modules) + 2
    
    # Sort endpoints by module priority
    return sorted(endpoints, key=lambda x: x["module_priority"])

def prioritize_by_schema_match(endpoints):
    """Prioritize endpoints that have schema matches"""
    # Endpoints with schema matches are easier to fix
    return sorted(endpoints, key=lambda x: 0 if x.get("schema_match") else 1)

def prioritize_by_method(endpoints):
    """Prioritize endpoints by HTTP method importance"""
    # Define method priority (GET and POST are most important)
    method_priority = {
        "GET": 1,
        "POST": 2,
        "PUT": 3,
        "DELETE": 4,
        "PATCH": 5
    }
    
    # Sort endpoints by method priority
    return sorted(endpoints, key=lambda x: method_priority.get(x["method"], 999))

def calculate_composite_priority(endpoints):
    """Calculate a composite priority score for each endpoint"""
    # Define weights for different factors
    weights = {
        "status": 0.4,  # Status code is most important
        "module": 0.3,  # Module importance is next
        "schema": 0.2,  # Having a schema match helps
        "method": 0.1   # Method is least important
    }
    
    # Calculate normalized scores for each factor
    status_scores = {}
    status_priority = {500: 1, "error": 2, 404: 3}
    for i, endpoint in enumerate(prioritize_by_status(endpoints)):
        status_scores[f"{endpoint['method']}:{endpoint['route_path']}"] = 1 - (i / len(endpoints))
    
    module_scores = {}
    for i, endpoint in enumerate(prioritize_by_module(endpoints)):
        module_scores[f"{endpoint['method']}:{endpoint['route_path']}"] = 1 - (i / len(endpoints))
    
    schema_scores = {}
    for i, endpoint in enumerate(prioritize_by_schema_match(endpoints)):
        schema_scores[f"{endpoint['method']}:{endpoint['route_path']}"] = 1 - (i / len(endpoints))
    
    method_scores = {}
    for i, endpoint in enumerate(prioritize_by_method(endpoints)):
        method_scores[f"{endpoint['method']}:{endpoint['route_path']}"] = 1 - (i / len(endpoints))
    
    # Calculate composite score for each endpoint
    for endpoint in endpoints:
        key = f"{endpoint['method']}:{endpoint['route_path']}"
        endpoint["composite_score"] = (
            weights["status"] * status_scores[key] +
            weights["module"] * module_scores[key] +
            weights["schema"] * schema_scores[key] +
            weights["method"] * method_scores[key]
        )
    
    # Sort endpoints by composite score (higher is higher priority)
    return sorted(endpoints, key=lambda x: x["composite_score"], reverse=True)

def select_next_batch(prioritized_endpoints, batch_size=BATCH_SIZE):
    """Select the next batch of endpoints to fix"""
    return prioritized_endpoints[:batch_size]

def generate_fix_strategies(batch):
    """Generate fix strategies for each endpoint in the batch"""
    strategies = []
    
    for endpoint in batch:
        strategy = {
            "endpoint": {
                "method": endpoint["method"],
                "route_path": endpoint["route_path"],
                "status_code": endpoint["status_code"],
                "status": endpoint["status"]
            },
            "priority_score": endpoint["composite_score"],
            "has_schema_match": endpoint.get("schema_match") is not None
        }
        
        # Determine fix type based on status code and schema match
        if endpoint["status_code"] == 500:
            strategy["fix_type"] = "server_error_fix"
            strategy["fix_description"] = "Fix server error by debugging and resolving the exception"
        elif endpoint["status_code"] == 404:
            if endpoint.get("schema_match"):
                strategy["fix_type"] = "route_implementation"
                strategy["fix_description"] = "Implement missing route handler using schema definition"
                strategy["schema_info"] = endpoint["schema_match"]
            else:
                strategy["fix_type"] = "route_registration"
                strategy["fix_description"] = "Register missing route in the application"
        else:
            strategy["fix_type"] = "general_fix"
            strategy["fix_description"] = "Investigate and fix the issue"
        
        # Add specific steps based on fix type
        if strategy["fix_type"] == "server_error_fix":
            strategy["fix_steps"] = [
                "Check server logs for error details",
                "Debug the exception in the route handler",
                "Fix the code causing the error",
                "Add error handling to prevent future errors"
            ]
        elif strategy["fix_type"] == "route_implementation":
            strategy["fix_steps"] = [
                "Create or update the route handler function",
                "Implement request validation using the schema",
                "Add basic response logic",
                "Return appropriate status codes and responses"
            ]
        elif strategy["fix_type"] == "route_registration":
            strategy["fix_steps"] = [
                "Create a new route module if needed",
                "Implement a basic route handler",
                "Register the route in the application",
                "Update main.py to include the router"
            ]
        else:
            strategy["fix_steps"] = [
                "Investigate the specific issue",
                "Implement appropriate fixes",
                "Test the endpoint",
                "Document the changes"
            ]
        
        strategies.append(strategy)
    
    return strategies

def main():
    """Main function to prioritize endpoints and select the next batch"""
    print("Starting endpoint prioritization...")
    
    # Load data
    remaining_endpoints = load_remaining_endpoints()
    deployment_analysis = load_deployment_analysis()
    print(f"Loaded {remaining_endpoints['non_operational_count']} non-operational endpoints")
    
    # Get non-operational endpoints
    non_operational = remaining_endpoints["non_operational_endpoints"]
    
    # Prioritize endpoints
    prioritized_endpoints = calculate_composite_priority(non_operational)
    print(f"Prioritized {len(prioritized_endpoints)} endpoints")
    
    # Select next batch
    next_batch = select_next_batch(prioritized_endpoints)
    print(f"Selected {len(next_batch)} endpoints for the next batch")
    
    # Generate fix strategies
    fix_strategies = generate_fix_strategies(next_batch)
    print(f"Generated fix strategies for {len(fix_strategies)} endpoints")
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Prepare output
    output = {
        "timestamp": timestamp,
        "total_non_operational": remaining_endpoints["non_operational_count"],
        "batch_size": len(next_batch),
        "batch_endpoints": next_batch,
        "fix_strategies": fix_strategies
    }
    
    # Save output to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Endpoint prioritization completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    print("\nNext Batch Summary:")
    print(f"Total Non-Operational Endpoints: {output['total_non_operational']}")
    print(f"Batch Size: {output['batch_size']}")
    
    print("\nTop 5 Endpoints to Fix:")
    for i, strategy in enumerate(fix_strategies[:5]):
        endpoint = strategy["endpoint"]
        print(f"  {i+1}. {endpoint['method']} {endpoint['route_path']} ({endpoint['status']})")
        print(f"     Fix Type: {strategy['fix_type']}")
        print(f"     Priority Score: {strategy['priority_score']:.4f}")
        print(f"     Has Schema Match: {strategy['has_schema_match']}")
    
    return output

if __name__ == "__main__":
    main()
