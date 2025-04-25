#!/usr/bin/env python3
"""
Postman Sweep Validation
Validates the implemented endpoint fixes by running a comprehensive Postman sweep.
"""

import os
import json
import requests
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Configuration
BACKEND_URL = "https://personal-ai-agent-ji4s.onrender.com"
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
FIX_IMPLEMENTATION_FILE = "/home/ubuntu/personal-ai-agent/logs/endpoint_fix_implementation.json"
FINAL_VERIFICATION_FILE = "/home/ubuntu/personal-ai-agent/logs/final_endpoint_verification.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/postman_sweep_after_deploy.json"
FAILING_ROUTES_FILE = "/home/ubuntu/personal-ai-agent/logs/failing_routes_after_deploy.json"
MAX_WORKERS = 5  # Limit concurrent requests to avoid overwhelming the server

def load_previous_results():
    """Load previous verification results and fix implementation results"""
    with open(FINAL_VERIFICATION_FILE, "r") as f:
        verification_results = json.load(f)
    
    with open(FIX_IMPLEMENTATION_FILE, "r") as f:
        fix_results = json.load(f)
    
    return verification_results, fix_results

def extract_all_endpoints(verification_results):
    """Extract all endpoints from previous verification results"""
    return verification_results["results"]

def extract_fixed_endpoints(fix_results):
    """Extract fixed endpoints from fix implementation results"""
    fixed_endpoints = []
    
    for fixed in fix_results["fixed_endpoints"]:
        if fixed["result"]["success"]:
            endpoint = fixed["endpoint"]
            fixed_endpoints.append({
                "method": endpoint["method"],
                "route_path": endpoint["route_path"]
            })
    
    return fixed_endpoints

def is_fixed_endpoint(endpoint, fixed_endpoints_list):
    """Check if an endpoint was fixed in the implementation"""
    for fixed in fixed_endpoints_list:
        if fixed["method"] == endpoint["method"] and fixed["route_path"] == endpoint["route_path"]:
            return True
    return False

def test_endpoint(endpoint, fixed_endpoints_list):
    """Test a single endpoint and return the result"""
    method = endpoint["method"]
    path = endpoint["route_path"]
    url = f"{BACKEND_URL}{path}"
    
    # Replace path parameters with placeholder values
    if "{" in path:
        # For simplicity, replace all path parameters with "test_id"
        url = url.replace("{", "test_").replace("}", "")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            # Send a minimal JSON payload
            response = requests.post(url, json={"test": "data"}, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json={"test": "data"}, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json={"test": "data"}, timeout=10)
        else:
            return {
                "route_path": path,
                "method": method,
                "status": "Unknown method",
                "status_code": None,
                "error": f"Unsupported method: {method}",
                "previous_status_code": endpoint.get("status_code"),
                "was_fixed": is_fixed_endpoint(endpoint, fixed_endpoints_list)
            }
        
        return {
            "route_path": path,
            "method": method,
            "status": f"{response.status_code} {response.reason}",
            "status_code": response.status_code,
            "response_time_ms": int(response.elapsed.total_seconds() * 1000),
            "previous_status_code": endpoint.get("status_code"),
            "was_fixed": is_fixed_endpoint(endpoint, fixed_endpoints_list)
        }
    except Exception as e:
        return {
            "route_path": path,
            "method": method,
            "status": "Error",
            "status_code": None,
            "error": str(e),
            "previous_status_code": endpoint.get("status_code"),
            "was_fixed": is_fixed_endpoint(endpoint, fixed_endpoints_list)
        }

def run_postman_sweep(endpoints, fixed_endpoints_list):
    """Run a comprehensive Postman sweep of all endpoints"""
    results = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_endpoint = {executor.submit(test_endpoint, endpoint, fixed_endpoints_list): endpoint for endpoint in endpoints}
        for future in as_completed(future_to_endpoint):
            endpoint = future_to_endpoint[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Tested {result['method']} {result['route_path']}: {result['status']}")
            except Exception as e:
                print(f"Error testing {endpoint['method']} {endpoint['route_path']}: {str(e)}")
                results.append({
                    "route_path": endpoint["route_path"],
                    "method": endpoint["method"],
                    "status": "Error",
                    "status_code": None,
                    "error": str(e),
                    "previous_status_code": endpoint.get("status_code"),
                    "was_fixed": is_fixed_endpoint(endpoint, fixed_endpoints_list)
                })
    
    return results

def analyze_results(results, fixed_endpoints_list):
    """Analyze the results of the Postman sweep"""
    total_endpoints = len(results)
    success_count = sum(1 for result in results if result.get("status_code") == 200)
    unprocessable_count = sum(1 for result in results if result.get("status_code") == 422)
    not_found_count = sum(1 for result in results if result.get("status_code") == 404)
    method_not_allowed_count = sum(1 for result in results if result.get("status_code") == 405)
    server_error_count = sum(1 for result in results if result.get("status_code") and result.get("status_code") >= 500)
    error_count = sum(1 for result in results if result.get("status_code") is None)
    
    # Calculate fixed endpoints statistics
    fixed_count = len(fixed_endpoints_list)
    fixed_success_count = sum(1 for result in results if result.get("was_fixed") and result.get("status_code") in [200, 422])
    fixed_failure_count = sum(1 for result in results if result.get("was_fixed") and (result.get("status_code") not in [200, 422] or result.get("status_code") is None))
    
    # Calculate success rate
    success_rate = (success_count + unprocessable_count) / total_endpoints * 100 if total_endpoints > 0 else 0
    
    # Calculate fix success rate
    fix_success_rate = fixed_success_count / fixed_count * 100 if fixed_count > 0 else 0
    
    return {
        "total_endpoints": total_endpoints,
        "success_count": success_count,
        "unprocessable_count": unprocessable_count,
        "not_found_count": not_found_count,
        "method_not_allowed_count": method_not_allowed_count,
        "server_error_count": server_error_count,
        "error_count": error_count,
        "fixed_count": fixed_count,
        "fixed_success_count": fixed_success_count,
        "fixed_failure_count": fixed_failure_count,
        "success_rate": round(success_rate, 1),
        "fix_success_rate": round(fix_success_rate, 1)
    }

def extract_failing_routes(results):
    """Extract failing routes from the results"""
    failing_routes = []
    
    for result in results:
        if result.get("status_code") not in [200, 422] or result.get("status_code") is None:
            failing_routes.append(result)
    
    return failing_routes

def main():
    """Main function to run Postman sweep validation"""
    print("Starting Postman sweep validation...")
    
    # Load previous results
    verification_results, fix_results = load_previous_results()
    print(f"Loaded previous verification results with {len(verification_results['results'])} endpoints")
    print(f"Loaded fix implementation results with {fix_results['total_fixed']} fixed endpoints")
    
    # Extract all endpoints and fixed endpoints
    endpoints = extract_all_endpoints(verification_results)
    fixed_endpoints_list = extract_fixed_endpoints(fix_results)
    print(f"Extracted {len(endpoints)} endpoints to test")
    print(f"Extracted {len(fixed_endpoints_list)} fixed endpoints")
    
    # Run Postman sweep
    results = run_postman_sweep(endpoints, fixed_endpoints_list)
    
    # Analyze results
    analysis = analyze_results(results, fixed_endpoints_list)
    print("\nPostman Sweep Analysis:")
    print(f"Total Endpoints: {analysis['total_endpoints']}")
    print(f"Success (200 OK): {analysis['success_count']}")
    print(f"Unprocessable Entity (422): {analysis['unprocessable_count']}")
    print(f"Not Found (404): {analysis['not_found_count']}")
    print(f"Method Not Allowed (405): {analysis['method_not_allowed_count']}")
    print(f"Server Errors (5xx): {analysis['server_error_count']}")
    print(f"Connection Errors: {analysis['error_count']}")
    print(f"Success Rate (200 + 422): {analysis['success_rate']}%")
    print(f"Fixed Endpoints: {analysis['fixed_count']}")
    print(f"Fixed Success Rate: {analysis['fix_success_rate']}%")
    
    # Extract failing routes
    failing_routes = extract_failing_routes(results)
    print(f"Extracted {len(failing_routes)} failing routes")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Generate timestamp for memory tag
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    memory_tag = f"postman_sweep_after_resurrection_{timestamp}"
    
    # Save results to file
    output = {
        "timestamp": timestamp,
        "memory_tag": memory_tag,
        "backend_url": BACKEND_URL,
        "results": results,
        "analysis": analysis,
        "fixed_endpoints": fixed_endpoints_list
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Postman sweep validation completed. Results saved to {OUTPUT_FILE}")
    print(f"Memory Tag: {memory_tag}")
    
    # Save failing routes to file
    failing_output = {
        "timestamp": timestamp,
        "memory_tag": memory_tag,
        "backend_url": BACKEND_URL,
        "failing_routes": failing_routes,
        "total_failing": len(failing_routes)
    }
    
    with open(FAILING_ROUTES_FILE, 'w') as f:
        json.dump(failing_output, f, indent=2)
    
    print(f"Failing routes saved to {FAILING_ROUTES_FILE}")
    
    return output

if __name__ == "__main__":
    main()
