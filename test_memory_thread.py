"""
Test script for memory_thread endpoint.

This script tests the functionality of the memory_thread endpoint.
"""

import requests
import json
import time

# Base URL for API
BASE_URL = "http://0.0.0.0:8000"

def test_memory_thread_endpoint():
    """Test the memory_thread endpoint."""
    print("Testing memory_thread endpoint...")
    
    # Test data
    test_data = {
        "project_id": "test_project",
        "chain_id": "test_chain",
        "agent": "hal",
        "role": "developer",
        "content": "This is a test memory entry",
        "step_type": "task",
        "type": "code"
    }
    
    # Send POST request to add memory thread
    print(f"\nPOST /api/memory/thread")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/memory/thread", json=test_data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ POST /api/memory/thread - Success")
        else:
            print("❌ POST /api/memory/thread - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Wait a moment to ensure data is processed
    time.sleep(1)
    
    # Send GET request to retrieve memory thread
    print(f"\nGET /api/memory/thread/{test_data['project_id']}/{test_data['chain_id']}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/memory/thread/{test_data['project_id']}/{test_data['chain_id']}")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200 and len(response.json()) > 0:
            print("✅ GET /api/memory/thread/{project_id}/{chain_id} - Success")
            return True
        else:
            print("❌ GET /api/memory/thread/{project_id}/{chain_id} - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_memory_thread_endpoint()
