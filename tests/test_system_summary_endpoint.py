#!/usr/bin/env python3
"""
Test script for the system summary endpoint.
This script tests both GET and POST methods with different URL formats and parameter passing methods.

Phase 6.3.1 - System Summary POST Endpoint Fix
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Local server
PROJECT_ID = "smart_sync_test_001"  # Test project ID
TIMEOUT = 10  # Request timeout in seconds

# Test URLs - testing both with and without /api prefix
URLS = [
    f"{BASE_URL}/api/system/summary",  # Standard URL format with /api prefix
    f"{BASE_URL}/system/summary",      # Alternative URL format without /api prefix
]

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(message):
    """Print a formatted header message."""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}== {message}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")

def print_success(message):
    """Print a success message."""
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    """Print an error message."""
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    """Print a warning message."""
    print(f"{YELLOW}⚠️ {message}{RESET}")

def print_info(message):
    """Print an info message."""
    print(f"{BLUE}ℹ️ {message}{RESET}")

def test_get_with_query_param(url):
    """Test GET request with project_id as query parameter."""
    print_info(f"Testing GET {url}?project_id={PROJECT_ID}")
    
    try:
        response = requests.get(f"{url}?project_id={PROJECT_ID}", timeout=TIMEOUT)
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:200]}..." if len(response.text) > 200 else f"Response: {response.text}")
        
        if response.status_code == 200:
            print_success(f"GET {url}?project_id={PROJECT_ID} - SUCCESS")
            return True
        else:
            print_error(f"GET {url}?project_id={PROJECT_ID} - FAILED with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"GET {url}?project_id={PROJECT_ID} - EXCEPTION: {str(e)}")
        return False

def test_post_with_query_param(url):
    """Test POST request with project_id as query parameter."""
    print_info(f"Testing POST {url}?project_id={PROJECT_ID}")
    
    try:
        response = requests.post(f"{url}?project_id={PROJECT_ID}", timeout=TIMEOUT)
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:200]}..." if len(response.text) > 200 else f"Response: {response.text}")
        
        if response.status_code == 200:
            print_success(f"POST {url}?project_id={PROJECT_ID} - SUCCESS")
            return True
        else:
            print_error(f"POST {url}?project_id={PROJECT_ID} - FAILED with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"POST {url}?project_id={PROJECT_ID} - EXCEPTION: {str(e)}")
        return False

def test_post_with_json_body(url):
    """Test POST request with project_id in JSON body."""
    print_info(f"Testing POST {url} with JSON body")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "project_id": PROJECT_ID
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:200]}..." if len(response.text) > 200 else f"Response: {response.text}")
        
        if response.status_code == 200:
            print_success(f"POST {url} with JSON body - SUCCESS")
            return True
        else:
            print_error(f"POST {url} with JSON body - FAILED with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"POST {url} with JSON body - EXCEPTION: {str(e)}")
        return False

def main():
    """Main test function."""
    print_header("System Summary Endpoint Test - Phase 6.3.1")
    print_info(f"Testing against server: {BASE_URL}")
    print_info(f"Test project ID: {PROJECT_ID}")
    print_info(f"Timestamp: {datetime.now().isoformat()}")
    
    results = {
        "get_query_param": [],
        "post_query_param": [],
        "post_json_body": []
    }
    
    # Test each URL format
    for url in URLS:
        print_header(f"Testing URL: {url}")
        
        # Test GET with query parameter
        results["get_query_param"].append(test_get_with_query_param(url))
        
        # Test POST with query parameter
        results["post_query_param"].append(test_post_with_query_param(url))
        
        # Test POST with JSON body
        results["post_json_body"].append(test_post_with_json_body(url))
        
        # Add a small delay between tests
        time.sleep(1)
    
    # Print summary
    print_header("Test Summary")
    
    total_tests = len(URLS) * 3  # 3 test types per URL
    successful_tests = sum([sum(results[key]) for key in results])
    
    print_info(f"Total tests: {total_tests}")
    print_info(f"Successful tests: {successful_tests}")
    print_info(f"Failed tests: {total_tests - successful_tests}")
    
    if successful_tests == total_tests:
        print_success("All tests passed! The system summary endpoint is working correctly.")
        return 0
    else:
        print_error(f"Some tests failed. Success rate: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
