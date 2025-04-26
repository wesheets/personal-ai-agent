#!/usr/bin/env python3
"""
Final Validation Script
Validates all fixed endpoints with a Postman sweep against the live server.
"""

import os
import json
import datetime
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
DIRECT_FIX_RESULTS_FILE = "/home/ubuntu/personal-ai-agent/logs/direct_fix_implementation_results.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/final_validation_results.json"
BASE_URL = "https://personal-ai-agent-ji4s.onrender.com"
MAX_WORKERS = 5  # Number of concurrent requests
TIMEOUT = 10  # Request timeout in seconds

def load_fix_results():
    """Load direct fix implementation results"""
    with open(DIRECT_FIX_RESULTS_FILE, "r") as f:
        return json.load(f)

def test_endpoint(endpoint_info):
    """Test a single endpoint and return the result"""
    method = endpoint_info["method"]
    route_path = endpoint_info["route_path"]
    
    # Replace path parameters with test values
    url_path = route_path
    for param in route_path.split("/"):
        if param.startswith("{") and param.endswith("}"):
            param_name = param[1:-1]
            url_path = url_path.replace(param, f"test_{param_name}")
    
    url = f"{BASE_URL}{url_path}"
    
    # Prepare request data
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    data = None
    if method in ["POST", "PUT", "PATCH"]:
        # Create a simple test payload
        data = {
            "test": True,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add specific fields for certain endpoints
        if route_path == "/config":
            data = {
                "agent_id": "test_agent",
                "permissions": [
                    {
                        "tool_id": "search",
                        "enabled": True,
                        "permission_level": "read_write",
                        "rate_limit": 10
                    }
                ],
                "fallback_behavior": {
                    "retry_count": 3,
                    "fallback_agent": "default",
                    "error_response_template": "I'm sorry, I couldn't complete that task.",
                    "log_failures": True
                },
                "memory_access_level": "read_write",
                "custom_settings": {
                    "max_tokens": 4096,
                    "temperature": 0.7
                }
            }
    
    # Make the request
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=TIMEOUT)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=TIMEOUT)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data, timeout=TIMEOUT)
        else:
            return {
                "method": method,
                "route_path": route_path,
                "url": url,
                "status_code": None,
                "status": "error",
                "message": f"Unsupported method: {method}",
                "response": None,
                "fix_status": endpoint_info["status"],
                "fix_message": endpoint_info["message"]
            }
        
        # Get response data
        try:
            response_data = response.json()
        except:
            response_data = {"text": response.text[:500]}
        
        return {
            "method": method,
            "route_path": route_path,
            "url": url,
            "status_code": response.status_code,
            "status": "success" if response.status_code in [200, 201, 202, 204, 422] else "error",
            "message": f"Endpoint returned {response.status_code}",
            "response": response_data,
            "fix_status": endpoint_info["status"],
            "fix_message": endpoint_info["message"]
        }
    except requests.exceptions.Timeout:
        return {
            "method": method,
            "route_path": route_path,
            "url": url,
            "status_code": None,
            "status": "error",
            "message": "Request timed out",
            "response": None,
            "fix_status": endpoint_info["status"],
            "fix_message": endpoint_info["message"]
        }
    except requests.exceptions.RequestException as e:
        return {
            "method": method,
            "route_path": route_path,
            "url": url,
            "status_code": None,
            "status": "error",
            "message": f"Request error: {str(e)}",
            "response": None,
            "fix_status": endpoint_info["status"],
            "fix_message": endpoint_info["message"]
        }
    except Exception as e:
        return {
            "method": method,
            "route_path": route_path,
            "url": url,
            "status_code": None,
            "status": "error",
            "message": f"Error: {str(e)}",
            "response": None,
            "fix_status": endpoint_info["status"],
            "fix_message": endpoint_info["message"]
        }

def validate_fixes(fix_results):
    """Validate the implemented fixes with a Postman sweep"""
    fixed_endpoints = fix_results["fixed_endpoints"]
    
    # Test all fixed endpoints
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_endpoint = {executor.submit(test_endpoint, endpoint_info): endpoint_info for endpoint_info in fixed_endpoints}
        for future in as_completed(future_to_endpoint):
            endpoint_info = future_to_endpoint[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Tested {result['method']} {result['route_path']}: {result['status_code']} ({result['status']})")
            except Exception as e:
                print(f"Error testing {endpoint_info['method']} {endpoint_info['route_path']}: {str(e)}")
                results.append({
                    "method": endpoint_info["method"],
                    "route_path": endpoint_info["route_path"],
                    "url": f"{BASE_URL}{endpoint_info['route_path']}",
                    "status_code": None,
                    "status": "error",
                    "message": f"Error: {str(e)}",
                    "response": None,
                    "fix_status": endpoint_info["status"],
                    "fix_message": endpoint_info["message"]
                })
    
    return results

def main():
    """Main function to validate the implemented fixes"""
    print("Starting final validation of implemented fixes...")
    
    # Load fix results
    fix_results = load_fix_results()
    print(f"Loaded fix results with {len(fix_results['fixed_endpoints'])} fixed endpoints")
    
    # Validate fixes
    validation_results = validate_fixes(fix_results)
    
    # Calculate success rate
    success_count = sum(1 for result in validation_results if result["status"] == "success")
    total_count = len(validation_results)
    success_rate = success_count / total_count if total_count > 0 else 0
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Prepare output
    output = {
        "timestamp": timestamp,
        "total_endpoints": total_count,
        "success_count": success_count,
        "success_rate": success_rate,
        "results": validation_results
    }
    
    # Save output to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Final validation completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    print("\nValidation Summary:")
    print(f"Total Endpoints: {output['total_endpoints']}")
    print(f"Success: {output['success_count']} ({output['success_rate'] * 100:.1f}%)")
    
    print("\nEndpoint Status:")
    status_counts = {}
    for result in validation_results:
        status_code = result["status_code"]
        if status_code is None:
            status_code = "error"
        status_counts[status_code] = status_counts.get(status_code, 0) + 1
    
    for status_code, count in sorted(status_counts.items()):
        print(f"  {status_code}: {count}")
    
    print("\nSuccessful Endpoints:")
    for result in validation_results:
        if result["status"] == "success":
            print(f"  {result['method']} {result['route_path']}: {result['status_code']}")
    
    return output

if __name__ == "__main__":
    main()
