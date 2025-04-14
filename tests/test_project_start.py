"""
Test script for the /api/project/start endpoint.

This script tests the project start endpoint to verify it's properly registered and accessible.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import debug logger
from src.utils.debug_logger import log_test_result

def test_project_start_endpoint():
    """Test the /api/project/start endpoint with a simple goal."""
    
    # Log test start
    log_test_result(
        "Test", 
        "/api/project/start", 
        "INFO", 
        "Starting endpoint test", 
        "Testing if endpoint is properly registered and accessible"
    )
    
    # Test data
    test_data = {
        "goal": "Create a simple hello world program"
    }
    
    # Test against local server
    try:
        # Try local server first
        response = requests.post(
            "http://localhost:3000/api/project/start",
            json=test_data,
            timeout=5  # Short timeout for quick feedback
        )
        
        # Log result
        if response.status_code == 200:
            log_test_result(
                "Test", 
                "/api/project/start", 
                "SUCCESS", 
                "Endpoint is accessible", 
                f"Status code: {response.status_code}"
            )
            print(f"✅ SUCCESS: Endpoint is accessible (Status: {response.status_code})")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            log_test_result(
                "Test", 
                "/api/project/start", 
                "ERROR", 
                "Endpoint returned error", 
                f"Status code: {response.status_code}, Response: {response.text}"
            )
            print(f"❌ ERROR: Endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        # Connection error - server might not be running
        log_test_result(
            "Test", 
            "/api/project/start", 
            "ERROR", 
            "Connection error", 
            "Could not connect to local server. Is it running?"
        )
        print("❌ ERROR: Could not connect to local server. Is it running?")
        
    except Exception as e:
        # Other errors
        log_test_result(
            "Test", 
            "/api/project/start", 
            "ERROR", 
            f"Unexpected error: {str(e)}", 
            "Check server logs for details"
        )
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing /api/project/start endpoint...")
    test_project_start_endpoint()
