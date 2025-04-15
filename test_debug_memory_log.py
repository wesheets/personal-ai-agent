"""
Test script for debug memory log endpoint.

This script tests the functionality of the debug memory log endpoint.
"""

import requests
import json

# Base URL for API
BASE_URL = "http://0.0.0.0:8000"

def test_debug_memory_log_endpoint():
    """Test the debug memory log endpoint."""
    print("Testing debug memory log endpoint...")
    
    # Send GET request to debug memory log endpoint
    print(f"\nGET /api/debug/memory/log")
    
    try:
        response = requests.get(f"{BASE_URL}/api/debug/memory/log")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ GET /api/debug/memory/log - Success")
            return True
        else:
            print("❌ GET /api/debug/memory/log - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_debug_memory_log_endpoint()
