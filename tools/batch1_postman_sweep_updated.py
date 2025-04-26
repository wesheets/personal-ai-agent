#!/usr/bin/env python3
"""
Updated Batch 1 Postman Sweep Script
This script performs a comprehensive test of the Batch 1 endpoints:
- /api/plan/generate
- /api/loop/validate

It sends valid and invalid payloads to both routes and logs the results.
Updated to include all required fields for loop validation.
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BASE_URL = "https://personal-ai-agent-ji4s.onrender.com"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M")
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs/postman_sweeps"

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# Test cases
test_cases = [
    # /api/plan/generate tests
    {
        "name": "plan_generate_valid",
        "endpoint": "/api/plan/generate",
        "method": "GET",
        "params": {"goal": "Create a simple web application"},
        "expected_status": 200,
        "description": "Valid plan generation request"
    },
    {
        "name": "plan_generate_empty_goal",
        "endpoint": "/api/plan/generate",
        "method": "GET",
        "params": {"goal": ""},
        "expected_status": 422,
        "description": "Empty goal parameter"
    },
    {
        "name": "plan_generate_missing_goal",
        "endpoint": "/api/plan/generate",
        "method": "GET",
        "params": {},
        "expected_status": 422,
        "description": "Missing goal parameter"
    },
    
    # /api/loop/validate tests
    {
        "name": "loop_validate_valid",
        "endpoint": "/api/loop/validate",
        "method": "POST",
        "json": {
            "project_id": "test_project_123",
            "loop_id": "test_loop_123",
            "planned_agents": ["planner", "executor", "reviewer"],
            "plan": "Step 1: Design UI\nStep 2: Implement backend\nStep 3: Test",
            "expected_schema": {"type": "object", "properties": {"result": {"type": "string"}}},
            "max_loops": 5
        },
        "expected_status": 200,
        "description": "Valid loop validation request with all required fields"
    },
    {
        "name": "loop_validate_missing_expected_schema",
        "endpoint": "/api/loop/validate",
        "method": "POST",
        "json": {
            "project_id": "test_project_123",
            "loop_id": "test_loop_123",
            "planned_agents": ["planner", "executor", "reviewer"],
            "plan": "Step 1: Design UI\nStep 2: Implement backend\nStep 3: Test",
            "max_loops": 5
        },
        "expected_status": 422,
        "description": "Missing expected_schema parameter"
    },
    {
        "name": "loop_validate_missing_project_id",
        "endpoint": "/api/loop/validate",
        "method": "POST",
        "json": {
            "loop_id": "test_loop_123",
            "planned_agents": ["planner", "executor", "reviewer"],
            "plan": "Step 1: Design UI\nStep 2: Implement backend\nStep 3: Test",
            "expected_schema": {"type": "object", "properties": {"result": {"type": "string"}}},
            "max_loops": 5
        },
        "expected_status": 422,
        "description": "Missing project_id parameter"
    },
    {
        "name": "loop_validate_missing_planned_agents",
        "endpoint": "/api/loop/validate",
        "method": "POST",
        "json": {
            "project_id": "test_project_123",
            "loop_id": "test_loop_123",
            "plan": "Step 1: Design UI\nStep 2: Implement backend\nStep 3: Test",
            "expected_schema": {"type": "object", "properties": {"result": {"type": "string"}}},
            "max_loops": 5
        },
        "expected_status": 422,
        "description": "Missing planned_agents parameter"
    }
]

def run_test(test_case):
    """Run a single test case and return the result"""
    url = f"{BASE_URL}{test_case['endpoint']}"
    method = test_case["method"]
    
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, params=test_case.get("params", {}), timeout=10)
        elif method == "POST":
            response = requests.post(url, json=test_case.get("json", {}), timeout=10)
        else:
            return {
                "name": test_case["name"],
                "success": False,
                "status_code": None,
                "expected_status": test_case["expected_status"],
                "error": f"Unsupported method: {method}",
                "response_time": 0,
                "response_body": None
            }
        
        response_time = time.time() - start_time
        
        # Try to parse response as JSON
        try:
            response_body = response.json()
        except:
            response_body = response.text
        
        # Check if status code matches expected
        status_match = response.status_code == test_case["expected_status"]
        
        return {
            "name": test_case["name"],
            "endpoint": test_case["endpoint"],
            "method": method,
            "success": status_match,
            "status_code": response.status_code,
            "expected_status": test_case["expected_status"],
            "response_time": response_time,
            "response_body": response_body,
            "description": test_case["description"]
        }
    
    except Exception as e:
        return {
            "name": test_case["name"],
            "endpoint": test_case["endpoint"],
            "method": method,
            "success": False,
            "status_code": None,
            "expected_status": test_case["expected_status"],
            "error": str(e),
            "response_time": time.time() - start_time,
            "response_body": None,
            "description": test_case["description"]
        }

def main():
    """Run all test cases and save results"""
    print(f"Starting Batch 1 Postman sweep against {BASE_URL}...")
    
    results = []
    failures = []
    
    for test_case in test_cases:
        print(f"Running test: {test_case['name']}...")
        result = run_test(test_case)
        results.append(result)
        
        if not result["success"]:
            failures.append(result)
            print(f"❌ FAILED: {test_case['name']} - Got {result['status_code']}, expected {test_case['expected_status']}")
        else:
            print(f"✅ PASSED: {test_case['name']}")
    
    # Prepare summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "total_tests": len(test_cases),
        "passed": len(test_cases) - len(failures),
        "failed": len(failures),
        "results": results
    }
    
    # Save full results
    full_results_path = f"{LOGS_DIR}/batch1_plan_loop_{TIMESTAMP}.json"
    with open(full_results_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Save failures if any
    if failures:
        failures_path = f"{LOGS_DIR}/batch1_plan_loop_failures_{TIMESTAMP}.json"
        with open(failures_path, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "base_url": BASE_URL,
                "total_failures": len(failures),
                "failures": failures
            }, f, indent=2)
    
    # Print summary
    print("\n=== Batch 1 Postman Sweep Summary ===")
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {len(test_cases) - len(failures)}")
    print(f"Failed: {len(failures)}")
    print(f"Full results saved to: {full_results_path}")
    if failures:
        print(f"Failures saved to: {failures_path}")
    
    return summary

if __name__ == "__main__":
    main()
