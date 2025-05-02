#!/usr/bin/env python3
"""
Endpoint Validation Sweep for Promethios System Resurrection
Tests all endpoints on the live backend to verify functionality.
"""

import os
import json
import requests
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Configuration
BACKEND_URL = "https://personal-ai-agent-ji4s.onrender.com"
SCHEMA_ROUTE_MAPPING_FILE = "/home/ubuntu/personal-ai-agent/logs/schema_route_mapping.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/postman_sweep_after_rewire.json"
MAX_WORKERS = 5  # Limit concurrent requests to avoid overwhelming the server

def load_schema_route_mapping():
    """Load schema-route mapping from file"""
    with open(SCHEMA_ROUTE_MAPPING_FILE, "r") as f:
        return json.load(f)

def extract_all_routes(schema_route_mapping):
    """Extract all routes from schema-route mapping"""
    all_routes = []
    
    for schema in schema_route_mapping:
        for module in schema.get("modules_with_routers", []):
            for path_op in module.get("path_operations", []):
                route = {
                    "method": path_op["method"],
                    "path": path_op["path"],
                    "schema_name": schema["schema_name"],
                    "module_name": module["name"]  # Fixed: use 'name' instead of 'module_name'
                }
                all_routes.append(route)
    
    return all_routes

def test_endpoint(route):
    """Test a single endpoint and return the result"""
    method = route["method"]
    path = route["path"]
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
                "error": f"Unsupported method: {method}"
            }
        
        return {
            "route_path": path,
            "method": method,
            "status": f"{response.status_code} {response.reason}",
            "status_code": response.status_code,
            "response_time_ms": int(response.elapsed.total_seconds() * 1000)
        }
    except Exception as e:
        return {
            "route_path": path,
            "method": method,
            "status": "Error",
            "status_code": None,
            "error": str(e)
        }

def run_endpoint_sweep(routes):
    """Run a sweep of all endpoints using thread pool for concurrency"""
    results = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_route = {executor.submit(test_endpoint, route): route for route in routes}
        for future in as_completed(future_to_route):
            route = future_to_route[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Tested {result['method']} {result['route_path']}: {result['status']}")
            except Exception as e:
                print(f"Error testing {route['method']} {route['path']}: {str(e)}")
                results.append({
                    "route_path": route["path"],
                    "method": route["method"],
                    "status": "Error",
                    "status_code": None,
                    "error": str(e)
                })
    
    return results

def analyze_results(results):
    """Analyze the results of the endpoint sweep"""
    total_endpoints = len(results)
    success_count = sum(1 for result in results if result.get("status_code") == 200)
    unprocessable_count = sum(1 for result in results if result.get("status_code") == 422)
    not_found_count = sum(1 for result in results if result.get("status_code") == 404)
    method_not_allowed_count = sum(1 for result in results if result.get("status_code") == 405)
    server_error_count = sum(1 for result in results if result.get("status_code") and result.get("status_code") >= 500)
    error_count = sum(1 for result in results if result.get("status_code") is None)
    
    success_rate = (success_count + unprocessable_count) / total_endpoints * 100 if total_endpoints > 0 else 0
    
    return {
        "total_endpoints": total_endpoints,
        "success_count": success_count,
        "unprocessable_count": unprocessable_count,
        "not_found_count": not_found_count,
        "method_not_allowed_count": method_not_allowed_count,
        "server_error_count": server_error_count,
        "error_count": error_count,
        "success_rate": round(success_rate, 1)
    }

def main():
    """Main function to run endpoint validation sweep"""
    print("Starting endpoint validation sweep...")
    
    # Load schema-route mapping
    schema_route_mapping = load_schema_route_mapping()
    print(f"Loaded schema-route mapping with {len(schema_route_mapping)} schemas")
    
    # Extract all routes
    routes = extract_all_routes(schema_route_mapping)
    print(f"Extracted {len(routes)} routes to test")
    
    # Run endpoint sweep
    results = run_endpoint_sweep(routes)
    
    # Analyze results
    analysis = analyze_results(results)
    print("\nEndpoint Sweep Analysis:")
    print(f"Total Endpoints: {analysis['total_endpoints']}")
    print(f"Success (200 OK): {analysis['success_count']}")
    print(f"Unprocessable Entity (422): {analysis['unprocessable_count']}")
    print(f"Not Found (404): {analysis['not_found_count']}")
    print(f"Method Not Allowed (405): {analysis['method_not_allowed_count']}")
    print(f"Server Errors (5xx): {analysis['server_error_count']}")
    print(f"Connection Errors: {analysis['error_count']}")
    print(f"Success Rate (200 + 422): {analysis['success_rate']}%")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Generate timestamp for memory tag
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    memory_tag = f"postman_sweep_{timestamp}"
    
    # Save results to file
    output = {
        "timestamp": timestamp,
        "memory_tag": memory_tag,
        "backend_url": BACKEND_URL,
        "results": results,
        "analysis": analysis
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Endpoint validation sweep completed. Results saved to {OUTPUT_FILE}")
    print(f"Memory Tag: {memory_tag}")
    
    return output

if __name__ == "__main__":
    main()
