#!/usr/bin/env python3
"""
Final Endpoint Verification for Promethios System Resurrection
Verifies the overall operational status of all endpoints after attempted fixes.
"""

import os
import json
import requests
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Configuration
BACKEND_URL = "https://personal-ai-agent-ji4s.onrender.com"
POSTMAN_SWEEP_FILE = "/home/ubuntu/personal-ai-agent/logs/postman_sweep_after_rewire.json"
ENDPOINT_FIX_FILE = "/home/ubuntu/personal-ai-agent/logs/endpoint_fix_results.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/final_endpoint_verification.json"
MAX_WORKERS = 5  # Limit concurrent requests to avoid overwhelming the server

def load_previous_results():
    """Load previous sweep and fix results"""
    with open(POSTMAN_SWEEP_FILE, "r") as f:
        sweep_results = json.load(f)
    
    with open(ENDPOINT_FIX_FILE, "r") as f:
        fix_results = json.load(f)
    
    return sweep_results, fix_results

def extract_all_endpoints(sweep_results):
    """Extract all endpoints from previous sweep results"""
    return sweep_results["results"]

def test_endpoint(endpoint):
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
                "previous_status_code": endpoint.get("status_code")
            }
        
        return {
            "route_path": path,
            "method": method,
            "status": f"{response.status_code} {response.reason}",
            "status_code": response.status_code,
            "response_time_ms": int(response.elapsed.total_seconds() * 1000),
            "previous_status_code": endpoint.get("status_code")
        }
    except Exception as e:
        return {
            "route_path": path,
            "method": method,
            "status": "Error",
            "status_code": None,
            "error": str(e),
            "previous_status_code": endpoint.get("status_code")
        }

def run_final_verification(endpoints):
    """Run a final verification of all endpoints"""
    results = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_endpoint = {executor.submit(test_endpoint, endpoint): endpoint for endpoint in endpoints}
        for future in as_completed(future_to_endpoint):
            endpoint = future_to_endpoint[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Verified {result['method']} {result['route_path']}: {result['status']}")
            except Exception as e:
                print(f"Error verifying {endpoint['method']} {endpoint['route_path']}: {str(e)}")
                results.append({
                    "route_path": endpoint["route_path"],
                    "method": endpoint["method"],
                    "status": "Error",
                    "status_code": None,
                    "error": str(e),
                    "previous_status_code": endpoint.get("status_code")
                })
    
    return results

def analyze_results(results):
    """Analyze the results of the final verification"""
    total_endpoints = len(results)
    success_count = sum(1 for result in results if result.get("status_code") == 200)
    unprocessable_count = sum(1 for result in results if result.get("status_code") == 422)
    not_found_count = sum(1 for result in results if result.get("status_code") == 404)
    method_not_allowed_count = sum(1 for result in results if result.get("status_code") == 405)
    server_error_count = sum(1 for result in results if result.get("status_code") and result.get("status_code") >= 500)
    error_count = sum(1 for result in results if result.get("status_code") is None)
    
    # Calculate improved endpoints
    improved_count = sum(1 for result in results if 
                         (result.get("status_code") in [200, 422]) and 
                         (result.get("previous_status_code") not in [200, 422]))
    
    # Calculate degraded endpoints
    degraded_count = sum(1 for result in results if 
                         (result.get("status_code") not in [200, 422]) and 
                         (result.get("previous_status_code") in [200, 422]))
    
    success_rate = (success_count + unprocessable_count) / total_endpoints * 100 if total_endpoints > 0 else 0
    
    return {
        "total_endpoints": total_endpoints,
        "success_count": success_count,
        "unprocessable_count": unprocessable_count,
        "not_found_count": not_found_count,
        "method_not_allowed_count": method_not_allowed_count,
        "server_error_count": server_error_count,
        "error_count": error_count,
        "improved_count": improved_count,
        "degraded_count": degraded_count,
        "success_rate": round(success_rate, 1)
    }

def main():
    """Main function to verify the overall operational status of all endpoints"""
    print("Starting final endpoint verification...")
    
    # Load previous results
    sweep_results, fix_results = load_previous_results()
    print(f"Loaded previous sweep results with {len(sweep_results['results'])} endpoints")
    print(f"Loaded previous fix results with {fix_results['critical_endpoints']} critical endpoints")
    
    # Extract all endpoints
    endpoints = extract_all_endpoints(sweep_results)
    print(f"Extracted {len(endpoints)} endpoints to verify")
    
    # Run final verification
    results = run_final_verification(endpoints)
    
    # Analyze results
    analysis = analyze_results(results)
    print("\nFinal Endpoint Verification Analysis:")
    print(f"Total Endpoints: {analysis['total_endpoints']}")
    print(f"Success (200 OK): {analysis['success_count']}")
    print(f"Unprocessable Entity (422): {analysis['unprocessable_count']}")
    print(f"Not Found (404): {analysis['not_found_count']}")
    print(f"Method Not Allowed (405): {analysis['method_not_allowed_count']}")
    print(f"Server Errors (5xx): {analysis['server_error_count']}")
    print(f"Connection Errors: {analysis['error_count']}")
    print(f"Improved Endpoints: {analysis['improved_count']}")
    print(f"Degraded Endpoints: {analysis['degraded_count']}")
    print(f"Success Rate (200 + 422): {analysis['success_rate']}%")
    
    # Compare with previous sweep
    previous_success_rate = sweep_results["analysis"]["success_rate"]
    success_rate_change = analysis["success_rate"] - previous_success_rate
    print(f"Previous Success Rate: {previous_success_rate}%")
    print(f"Success Rate Change: {success_rate_change:+.1f}%")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Generate timestamp for memory tag
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    memory_tag = f"final_verification_{timestamp}"
    
    # Save results to file
    output = {
        "timestamp": timestamp,
        "memory_tag": memory_tag,
        "backend_url": BACKEND_URL,
        "results": results,
        "analysis": analysis,
        "previous_success_rate": previous_success_rate,
        "success_rate_change": success_rate_change,
        "resurrection_status": "completed" if analysis["success_rate"] >= 90 else "partial"
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Final endpoint verification completed. Results saved to {OUTPUT_FILE}")
    print(f"Memory Tag: {memory_tag}")
    print(f"Resurrection Status: {output['resurrection_status'].upper()}")
    
    return output

if __name__ == "__main__":
    main()
