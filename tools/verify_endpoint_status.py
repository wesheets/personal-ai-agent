#!/usr/bin/env python3
"""
Endpoint Status Verification
Verifies the status of all endpoints after the Postman sweep validation.
"""

import os
import json
import datetime
from collections import defaultdict

# Configuration
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
POSTMAN_SWEEP_FILE = "/home/ubuntu/personal-ai-agent/logs/postman_sweep_after_deploy.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/endpoint_status_verification.json"
MEMORY_EVENT_FILE = "/home/ubuntu/personal-ai-agent/app/logs/memory_events/endpoint_verification_results_{timestamp}.json"

def load_postman_sweep_results():
    """Load Postman sweep validation results"""
    with open(POSTMAN_SWEEP_FILE, "r") as f:
        return json.load(f)

def categorize_endpoints_by_status(results):
    """Categorize endpoints by their status code"""
    status_endpoints = defaultdict(list)
    
    for endpoint in results:
        status_code = endpoint.get("status_code")
        if status_code is None:
            status_code = "error"
        status_endpoints[status_code].append(endpoint)
    
    return status_endpoints

def categorize_endpoints_by_module(results):
    """Categorize endpoints by their module"""
    module_endpoints = defaultdict(list)
    
    for endpoint in results:
        route_path = endpoint["route_path"]
        parts = route_path.strip("/").split("/")
        
        if parts:
            module = parts[0]
            module_endpoints[module].append(endpoint)
        else:
            module_endpoints["root"].append(endpoint)
    
    return module_endpoints

def analyze_fixed_endpoints(results, fixed_endpoints):
    """Analyze the status of fixed endpoints"""
    fixed_status = defaultdict(list)
    
    for endpoint in results:
        if endpoint.get("was_fixed"):
            status_code = endpoint.get("status_code")
            if status_code is None:
                status_code = "error"
            fixed_status[status_code].append(endpoint)
    
    return fixed_status

def identify_critical_failures(status_endpoints):
    """Identify critical failures that need immediate attention"""
    critical_failures = []
    
    # Server errors are critical
    if 500 in status_endpoints:
        critical_failures.extend(status_endpoints[500])
    
    # Check for other 5xx errors
    for status_code in status_endpoints:
        if isinstance(status_code, int) and status_code >= 500:
            critical_failures.extend(status_endpoints[status_code])
    
    # Connection errors are critical
    if "error" in status_endpoints:
        critical_failures.extend(status_endpoints["error"])
    
    return critical_failures

def generate_next_batch_recommendations(status_endpoints, module_endpoints):
    """Generate recommendations for the next batch of endpoints to fix"""
    recommendations = []
    
    # First, include all 5xx errors
    for status_code in status_endpoints:
        if isinstance(status_code, int) and status_code >= 500:
            for endpoint in status_endpoints[status_code]:
                recommendations.append({
                    "endpoint": endpoint,
                    "reason": f"Server error ({status_code})",
                    "priority": "high"
                })
    
    # Then, include 404 errors for critical modules
    critical_modules = ["agent", "memory", "loop", "orchestrator", "hal", "forge"]
    for module in critical_modules:
        if module in module_endpoints:
            for endpoint in module_endpoints[module]:
                if endpoint.get("status_code") == 404:
                    recommendations.append({
                        "endpoint": endpoint,
                        "reason": f"Critical module ({module}) with 404",
                        "priority": "medium"
                    })
    
    # Limit to 10 recommendations
    return recommendations[:10]

def main():
    """Main function to verify endpoint status"""
    print("Starting endpoint status verification...")
    
    # Load Postman sweep results
    sweep_results = load_postman_sweep_results()
    results = sweep_results["results"]
    analysis = sweep_results["analysis"]
    fixed_endpoints = sweep_results["fixed_endpoints"]
    print(f"Loaded Postman sweep results with {len(results)} endpoints")
    
    # Categorize endpoints by status
    status_endpoints = categorize_endpoints_by_status(results)
    print("Categorized endpoints by status:")
    for status, endpoints in status_endpoints.items():
        print(f"  {status}: {len(endpoints)}")
    
    # Categorize endpoints by module
    module_endpoints = categorize_endpoints_by_module(results)
    print(f"Categorized endpoints into {len(module_endpoints)} modules")
    
    # Analyze fixed endpoints
    fixed_status = analyze_fixed_endpoints(results, fixed_endpoints)
    print("Analyzed fixed endpoints:")
    for status, endpoints in fixed_status.items():
        print(f"  {status}: {len(endpoints)}")
    
    # Identify critical failures
    critical_failures = identify_critical_failures(status_endpoints)
    print(f"Identified {len(critical_failures)} critical failures")
    
    # Generate next batch recommendations
    next_batch = generate_next_batch_recommendations(status_endpoints, module_endpoints)
    print(f"Generated {len(next_batch)} recommendations for next batch")
    
    # Generate timestamp for memory tag
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    memory_tag = f"endpoint_verification_{timestamp}"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Prepare output
    output = {
        "timestamp": timestamp,
        "memory_tag": memory_tag,
        "total_endpoints": len(results),
        "success_count": analysis["success_count"],
        "unprocessable_count": analysis["unprocessable_count"],
        "not_found_count": analysis["not_found_count"],
        "server_error_count": analysis["server_error_count"],
        "error_count": analysis["error_count"],
        "success_rate": analysis["success_rate"],
        "fixed_endpoints": {
            "total": len(fixed_endpoints),
            "success_rate": analysis["fix_success_rate"],
            "status_breakdown": {str(status): len(endpoints) for status, endpoints in fixed_status.items()}
        },
        "status_endpoints": {str(status): len(endpoints) for status, endpoints in status_endpoints.items()},
        "module_endpoints": {module: len(endpoints) for module, endpoints in module_endpoints.items()},
        "critical_failures": [
            {
                "method": failure["method"],
                "route_path": failure["route_path"],
                "status": failure["status"],
                "status_code": failure["status_code"]
            }
            for failure in critical_failures
        ],
        "next_batch_recommendations": [
            {
                "method": rec["endpoint"]["method"],
                "route_path": rec["endpoint"]["route_path"],
                "reason": rec["reason"],
                "priority": rec["priority"]
            }
            for rec in next_batch
        ]
    }
    
    # Save output to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Endpoint status verification completed. Results saved to {OUTPUT_FILE}")
    
    # Save memory event
    memory_event_file = MEMORY_EVENT_FILE.format(timestamp=timestamp)
    os.makedirs(os.path.dirname(memory_event_file), exist_ok=True)
    
    memory_event = {
        "event_type": "endpoint_verification",
        "timestamp": timestamp,
        "tag": memory_tag,
        "success_rate": analysis["success_rate"],
        "fixed_endpoints_success_rate": analysis["fix_success_rate"],
        "status_breakdown": {str(status): len(endpoints) for status, endpoints in status_endpoints.items()},
        "critical_failures_count": len(critical_failures),
        "next_steps": "Deploy local fixes to server and continue fixing remaining endpoints"
    }
    
    with open(memory_event_file, 'w') as f:
        json.dump(memory_event, f, indent=2)
    
    print(f"Memory event saved to {memory_event_file}")
    
    return output

if __name__ == "__main__":
    main()
