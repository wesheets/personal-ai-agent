"""
Test script for the delegate endpoint to verify it accepts POST requests properly.
"""

import requests
import json
import uuid

# Test configuration
BASE_URL = "https://web-production-2639.up.railway.app"
DELEGATE_ENDPOINT = f"{BASE_URL}/app/modules/delegate"

def test_delegate_post_request():
    """Test that the /app/modules/delegate endpoint accepts POST requests."""
    # Generate test data
    task_id = str(uuid.uuid4())
    
    # Prepare request payload
    payload = {
        "from_agent": "hal",
        "to_agent": "ash",
        "task": "Test delegation endpoint",
        "project_id": "test-project",
        "task_id": task_id,
        "memory_trace_id": str(uuid.uuid4()),
        "delegation_depth": 0
    }
    
    # Set headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Make POST request
    print(f"Making POST request to {DELEGATE_ENDPOINT}")
    response = requests.post(DELEGATE_ENDPOINT, json=payload, headers=headers)
    
    # Print response details
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response body: {response.text}")
    
    # Verify response
    if response.status_code == 200:
        print("✅ POST request successful!")
        try:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
    elif response.status_code == 429:
        print("✅ POST request received but returned 429 (expected for cap enforcement)")
        try:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
    else:
        print(f"❌ POST request failed with status code {response.status_code}")

def test_delegate_get_request():
    """Test that the /app/modules/delegate endpoint rejects GET requests."""
    # Make GET request
    print(f"Making GET request to {DELEGATE_ENDPOINT}")
    response = requests.get(DELEGATE_ENDPOINT)
    
    # Print response details
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response body: {response.text}")
    
    # Verify response
    if response.status_code in [404, 405]:
        print("✅ GET request properly rejected with status code 404 or 405")
    else:
        print(f"❌ GET request returned unexpected status code {response.status_code}")

if __name__ == "__main__":
    print("Testing delegate endpoint...")
    print("\n=== Testing POST request ===")
    test_delegate_post_request()
    print("\n=== Testing GET request ===")
    test_delegate_get_request()
    print("\nTests completed.")
