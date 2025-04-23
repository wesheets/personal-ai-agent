#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Tool for Promethios Backend

This script tests all API endpoints in the Promethios backend and reports their status.
It can be used to verify that all endpoints are working correctly after deployment.

Usage:
  python test_endpoints.py [--base-url URL] [--verbose] [--output FILE]

Options:
  --base-url URL    Base URL of the API (default: https://web-production-2639.up.railway.app)
  --verbose         Show detailed information for each endpoint
  --output FILE     Write results to a file in JSON format
"""

import argparse
import json
import requests
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define the endpoints to test
ENDPOINTS = {
    # System endpoints
    "GET /health": {"method": "GET", "path": "/health", "expected": 200},
    "GET /api/system/health": {"method": "GET", "path": "/api/system/health", "expected": 200},
    "GET /api/ping": {"method": "GET", "path": "/api/ping", "expected": 200},
    
    # Memory endpoints
    "POST /api/memory/write": {
        "method": "POST", 
        "path": "/api/memory/write", 
        "expected": 200,
        "json": {"project_id": "test", "agent": "test", "type": "note", "content": "Test memory write"}
    },
    "GET /api/memory/read": {
        "method": "GET", 
        "path": "/api/memory/read", 
        "expected": 200,
        "params": {"project_id": "test"}
    },
    
    # Loop endpoints
    "POST /api/loop/respond": {
        "method": "POST", 
        "path": "/api/loop/respond", 
        "expected": 200,
        "json": {
            "loop_id": "test", 
            "project_id": "test", 
            "agent": "hal", 
            "input_key": "build_task", 
            "response_type": "code", 
            "target_file": "test.jsx"
        }
    },
    
    # Agent endpoints
    "GET /api/modules/agent/list": {"method": "GET", "path": "/api/modules/agent/list", "expected": 200},
    "POST /api/modules/agent/run": {
        "method": "POST", 
        "path": "/api/modules/agent/run", 
        "expected": 200,
        "json": {"agent": "test", "input": "Test input"}
    },
    
    # Plan endpoints
    "POST /api/modules/plan/generate": {
        "method": "POST", 
        "path": "/api/modules/plan/generate", 
        "expected": 200,
        "json": {"project_id": "test", "input": "Test input"}
    },
    
    # Diagnostics endpoints
    "GET /diagnostics/router-check": {"method": "GET", "path": "/diagnostics/router-check", "expected": 200},
    "GET /schema-injection-test": {"method": "GET", "path": "/schema-injection-test", "expected": 200},
    
    # Additional endpoints to test
    "GET /api/modules/orchestrator/status": {"method": "GET", "path": "/api/modules/orchestrator/status", "expected": 200},
    "GET /api/modules/debug/routes": {"method": "GET", "path": "/api/modules/debug/routes", "expected": 200},
    "GET /api/modules/system/routes": {"method": "GET", "path": "/api/modules/system/routes", "expected": 200},
    "GET /api/modules/system/version": {"method": "GET", "path": "/api/modules/system/version", "expected": 200},
    "GET /api/modules/system/status": {"method": "GET", "path": "/api/modules/system/status", "expected": 200},
    "GET /api/modules/system/config": {"method": "GET", "path": "/api/modules/system/config", "expected": 200},
    "GET /api/modules/system/logs": {"method": "GET", "path": "/api/modules/system/logs", "expected": 200},
    "GET /api/modules/system/metrics": {"method": "GET", "path": "/api/modules/system/metrics", "expected": 200},
    "GET /api/modules/system/health": {"method": "GET", "path": "/api/modules/system/health", "expected": 200},
    "GET /api/modules/system/info": {"method": "GET", "path": "/api/modules/system/info", "expected": 200},
    "GET /api/modules/system/ping": {"method": "GET", "path": "/api/modules/system/ping", "expected": 200},
    "GET /api/modules/system/time": {"method": "GET", "path": "/api/modules/system/time", "expected": 200},
    "GET /api/modules/system/uptime": {"method": "GET", "path": "/api/modules/system/uptime", "expected": 200},
    "GET /api/modules/system/memory": {"method": "GET", "path": "/api/modules/system/memory", "expected": 200},
    "GET /api/modules/system/cpu": {"method": "GET", "path": "/api/modules/system/cpu", "expected": 200},
    "GET /api/modules/system/disk": {"method": "GET", "path": "/api/modules/system/disk", "expected": 200},
    "GET /api/modules/system/network": {"method": "GET", "path": "/api/modules/system/network", "expected": 200},
    "GET /api/modules/system/processes": {"method": "GET", "path": "/api/modules/system/processes", "expected": 200},
    "GET /api/modules/system/users": {"method": "GET", "path": "/api/modules/system/users", "expected": 200},
    "GET /api/modules/system/groups": {"method": "GET", "path": "/api/modules/system/groups", "expected": 200},
}

def test_endpoint(base_url, name, config, verbose=False):
    """Test a single endpoint and return the result."""
    url = f"{base_url}{config['path']}"
    method = config['method']
    expected = config.get('expected', 200)
    
    start_time = time.time()
    try:
        if method == "GET":
            params = config.get('params', {})
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            json_data = config.get('json', {})
            response = requests.post(url, json=json_data, timeout=10)
        else:
            return {
                "name": name,
                "url": url,
                "method": method,
                "status": "ERROR",
                "status_code": None,
                "expected": expected,
                "response_time": 0,
                "error": f"Unsupported method: {method}"
            }
        
        response_time = time.time() - start_time
        status = "OK" if response.status_code == expected else "FAIL"
        
        result = {
            "name": name,
            "url": url,
            "method": method,
            "status": status,
            "status_code": response.status_code,
            "expected": expected,
            "response_time": round(response_time * 1000, 2)  # Convert to ms
        }
        
        if verbose and response.status_code == 200:
            try:
                result["response"] = response.json()
            except:
                result["response"] = response.text[:100] + "..." if len(response.text) > 100 else response.text
                
        return result
    
    except Exception as e:
        response_time = time.time() - start_time
        return {
            "name": name,
            "url": url,
            "method": method,
            "status": "ERROR",
            "status_code": None,
            "expected": expected,
            "response_time": round(response_time * 1000, 2),
            "error": str(e)
        }

def run_tests(base_url, verbose=False, max_workers=10):
    """Run tests for all endpoints concurrently."""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_endpoint = {
            executor.submit(test_endpoint, base_url, name, config, verbose): name
            for name, config in ENDPOINTS.items()
        }
        
        for future in as_completed(future_to_endpoint):
            result = future.result()
            results.append(result)
    
    # Sort results by name for consistent output
    results.sort(key=lambda x: x["name"])
    return results

def print_summary(results):
    """Print a summary of the test results."""
    total = len(results)
    ok_count = sum(1 for r in results if r["status"] == "OK")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    
    print(f"\n{'=' * 80}")
    print(f"ENDPOINT TEST SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total endpoints tested: {total}")
    print(f"Success: {ok_count} ({ok_count/total*100:.1f}%)")
    print(f"Failed: {fail_count} ({fail_count/total*100:.1f}%)")
    print(f"Errors: {error_count} ({error_count/total*100:.1f}%)")
    print(f"{'=' * 80}\n")

def print_results(results, verbose=False):
    """Print the test results in a readable format."""
    # Group results by status
    ok_results = [r for r in results if r["status"] == "OK"]
    fail_results = [r for r in results if r["status"] == "FAIL"]
    error_results = [r for r in results if r["status"] == "ERROR"]
    
    # Print successful endpoints
    if ok_results:
        print(f"\n✅ SUCCESSFUL ENDPOINTS ({len(ok_results)})")
        print("-" * 80)
        for r in ok_results:
            print(f"{r['method']} {r['url']} - {r['status_code']} ({r['response_time']}ms)")
    
    # Print failed endpoints
    if fail_results:
        print(f"\n❌ FAILED ENDPOINTS ({len(fail_results)})")
        print("-" * 80)
        for r in fail_results:
            print(f"{r['method']} {r['url']} - Got: {r['status_code']}, Expected: {r['expected']} ({r['response_time']}ms)")
    
    # Print error endpoints
    if error_results:
        print(f"\n⚠️ ERROR ENDPOINTS ({len(error_results)})")
        print("-" * 80)
        for r in error_results:
            print(f"{r['method']} {r['url']} - Error: {r.get('error', 'Unknown error')} ({r['response_time']}ms)")
    
    # Print detailed results if verbose
    if verbose:
        print(f"\n📊 DETAILED RESULTS")
        print("-" * 80)
        for r in results:
            print(f"\n{r['method']} {r['path']}")
            print(f"  Status: {r['status']}")
            print(f"  Status Code: {r['status_code']}")
            print(f"  Expected: {r['expected']}")
            print(f"  Response Time: {r['response_time']}ms")
            if "error" in r:
                print(f"  Error: {r['error']}")
            if "response" in r:
                print(f"  Response: {json.dumps(r['response'], indent=2)[:200]}...")

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Test API endpoints")
    parser.add_argument("--base-url", default="https://web-production-2639.up.railway.app",
                        help="Base URL of the API")
    parser.add_argument("--verbose", action="store_true",
                        help="Show detailed information for each endpoint")
    parser.add_argument("--output", help="Write results to a file in JSON format")
    args = parser.parse_args()
    
    print(f"Testing API endpoints at {args.base_url}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing {len(ENDPOINTS)} endpoints...")
    
    start_time = time.time()
    results = run_tests(args.base_url, args.verbose)
    total_time = time.time() - start_time
    
    print_summary(results)
    print_results(results, args.verbose)
    
    print(f"\nTotal execution time: {total_time:.2f} seconds")
    
    if args.output:
        with open(args.output, 'w') as f:
            output_data = {
                "timestamp": datetime.now().isoformat(),
                "base_url": args.base_url,
                "total_endpoints": len(ENDPOINTS),
                "execution_time": total_time,
                "results": results
            }
            json.dump(output_data, f, indent=2)
            print(f"\nResults written to {args.output}")

if __name__ == "__main__":
    main()
