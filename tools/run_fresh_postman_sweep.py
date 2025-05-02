#!/usr/bin/env python3
"""
Fresh Postman Sweep Against Live Server
Runs a comprehensive Postman sweep against the live server to check the impact of deployed fixes.
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
PREVIOUS_SWEEP_FILE = "/home/ubuntu/personal-ai-agent/logs/postman_sweep_after_deploy.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/postman_sweep_after_deployment.json"
COMPARISON_FILE = "/home/ubuntu/personal-ai-agent/logs/deployment_impact_analysis.json"
MAX_WORKERS = 5  # Limit concurrent requests to avoid overwhelming the server

def load_previous_sweep():
    """Load previous Postman sweep results"""
    with open(PREVIOUS_SWEEP_FILE, "r") as f:
        return json.load(f)

def test_endpoint(endpoint):
    """Test a single endpoint and return the result"""
    method = endpoint["method"]
    path = endpoint["route_path"]
    url = f"{BACKEND_URL}{path}"
    previous_status = endpoint.get("status_code")
    was_fixed = endpoint.get("was_fixed", False)
    
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
                "previous_status_code": previous_status,
                "was_fixed": was_fixed
            }
        
        return {
            "route_path": path,
            "method": method,
            "status": f"{response.status_code} {response.reason}",
            "status_code": response.status_code,
            "response_time_ms": int(response.elapsed.total_seconds() * 1000),
            "previous_status_code": previous_status,
            "was_fixed": was_fixed
        }
    except Exception as e:
        return {
            "route_path": path,
            "method": method,
            "status": "Error",
            "status_code": None,
            "error": str(e),
            "previous_status_code": previous_status,
            "was_fixed": was_fixed
        }

def run_postman_sweep(endpoints):
    """Run a comprehensive Postman sweep of all endpoints"""
    results = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_endpoint = {executor.submit(test_endpoint, endpoint): endpoint for endpoint in endpoints}
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
                    "was_fixed": endpoint.get("was_fixed", False)
                })
    
    return results

def analyze_results(results):
    """Analyze the results of the Postman sweep"""
    total_endpoints = len(results)
    success_count = sum(1 for result in results if result.get("status_code") == 200)
    unprocessable_count = sum(1 for result in results if result.get("status_code") == 422)
    not_found_count = sum(1 for result in results if result.get("status_code") == 404)
    method_not_allowed_count = sum(1 for result in results if result.get("status_code") == 405)
    server_error_count = sum(1 for result in results if result.get("status_code") and result.get("status_code") >= 500)
    error_count = sum(1 for result in results if result.get("status_code") is None)
    
    # Calculate fixed endpoints statistics
    fixed_endpoints = [result for result in results if result.get("was_fixed")]
    fixed_count = len(fixed_endpoints)
    fixed_success_count = sum(1 for result in fixed_endpoints if result.get("status_code") in [200, 422])
    fixed_failure_count = sum(1 for result in fixed_endpoints if result.get("status_code") not in [200, 422] or result.get("status_code") is None)
    
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

def compare_with_previous(current_results, previous_results):
    """Compare current results with previous sweep to measure impact"""
    current_analysis = analyze_results(current_results)
    previous_analysis = previous_results["analysis"]
    
    # Calculate changes
    success_rate_change = current_analysis["success_rate"] - previous_analysis["success_rate"]
    fix_success_rate_change = current_analysis["fix_success_rate"] - previous_analysis["fix_success_rate"]
    
    # Identify endpoints that changed status
    improved_endpoints = []
    degraded_endpoints = []
    
    for current in current_results:
        route_path = current["route_path"]
        method = current["method"]
        current_status = current.get("status_code")
        previous_status = current.get("previous_status_code")
        
        # Skip if status didn't change
        if current_status == previous_status:
            continue
        
        # Check if status improved
        if (previous_status not in [200, 422] and current_status in [200, 422]) or \
           (previous_status is None and current_status is not None) or \
           (previous_status and previous_status >= 500 and current_status and current_status < 500):
            improved_endpoints.append({
                "route_path": route_path,
                "method": method,
                "previous_status": previous_status,
                "current_status": current_status,
                "was_fixed": current.get("was_fixed", False)
            })
        
        # Check if status degraded
        elif (previous_status in [200, 422] and current_status not in [200, 422]) or \
             (previous_status is not None and current_status is None) or \
             (previous_status and previous_status < 500 and current_status and current_status >= 500):
            degraded_endpoints.append({
                "route_path": route_path,
                "method": method,
                "previous_status": previous_status,
                "current_status": current_status,
                "was_fixed": current.get("was_fixed", False)
            })
    
    return {
        "current_analysis": current_analysis,
        "previous_analysis": previous_analysis,
        "success_rate_change": round(success_rate_change, 1),
        "fix_success_rate_change": round(fix_success_rate_change, 1),
        "improved_endpoints_count": len(improved_endpoints),
        "degraded_endpoints_count": len(degraded_endpoints),
        "improved_endpoints": improved_endpoints,
        "degraded_endpoints": degraded_endpoints
    }

def main():
    """Main function to run fresh Postman sweep"""
    print("Starting fresh Postman sweep against live server...")
    
    # Load previous sweep results
    previous_sweep = load_previous_sweep()
    previous_results = previous_sweep["results"]
    print(f"Loaded previous sweep results with {len(previous_results)} endpoints")
    
    # Run fresh Postman sweep
    results = run_postman_sweep(previous_results)
    
    # Analyze results
    analysis = analyze_results(results)
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
    
    # Compare with previous results
    comparison = compare_with_previous(results, previous_sweep)
    print("\nDeployment Impact Analysis:")
    print(f"Success Rate Change: {comparison['success_rate_change']}%")
    print(f"Fixed Endpoints Success Rate Change: {comparison['fix_success_rate_change']}%")
    print(f"Improved Endpoints: {comparison['improved_endpoints_count']}")
    print(f"Degraded Endpoints: {comparison['degraded_endpoints_count']}")
    
    # Generate timestamp for memory tag
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    memory_tag = f"postman_sweep_after_deployment_{timestamp}"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
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
    
    print(f"Fresh Postman sweep completed. Results saved to {OUTPUT_FILE}")
    
    # Save comparison to file
    comparison_output = {
        "timestamp": timestamp,
        "memory_tag": memory_tag,
        "comparison": comparison
    }
    
    with open(COMPARISON_FILE, 'w') as f:
        json.dump(comparison_output, f, indent=2)
    
    print(f"Deployment impact analysis saved to {COMPARISON_FILE}")
    
    return output, comparison

if __name__ == "__main__":
    main()
