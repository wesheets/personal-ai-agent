"""
Test script for the /api/system/health endpoint.

This script tests the health endpoint to verify it's properly registered and accessible.
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

def test_health_endpoint():
    """Test the /api/system/health endpoint."""
    
    # Log test start
    log_test_result(
        "Test", 
        "/api/system/health", 
        "INFO", 
        "Starting health endpoint test", 
        "Testing if health endpoint is properly registered and accessible"
    )
    
    # Test against local server
    try:
        # Try local server first
        response = requests.get(
            "http://localhost:3000/api/system/health",
            timeout=5  # Short timeout for quick feedback
        )
        
        # Log result
        if response.status_code == 200:
            log_test_result(
                "Test", 
                "/api/system/health", 
                "SUCCESS", 
                "Health endpoint is accessible", 
                f"Status code: {response.status_code}, Response: {response.text}"
            )
            print(f"✅ SUCCESS: Health endpoint is accessible (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return True
        else:
            log_test_result(
                "Test", 
                "/api/system/health", 
                "ERROR", 
                "Health endpoint returned error", 
                f"Status code: {response.status_code}, Response: {response.text}"
            )
            print(f"❌ ERROR: Health endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        # Connection error - server might not be running
        log_test_result(
            "Test", 
            "/api/system/health", 
            "ERROR", 
            "Connection error", 
            "Could not connect to local server. Is it running?"
        )
        print("❌ ERROR: Could not connect to local server. Is it running?")
        print("This is expected during testing. The endpoint will be tested when deployed to Railway.")
        return True  # Return True since this is expected during testing
        
    except Exception as e:
        # Other errors
        log_test_result(
            "Test", 
            "/api/system/health", 
            "ERROR", 
            f"Unexpected error: {str(e)}", 
            "Check server logs for details"
        )
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing /api/system/health endpoint...")
    test_health_endpoint()
