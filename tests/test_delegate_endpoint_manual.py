import requests
import json
import uuid

# Test configuration
BASE_URL = "https://web-production-2639.up.railway.app"
DELEGATE_ENDPOINT = f"{BASE_URL}/app/modules/delegate"

def test_delegate_post_request():
    """Test that the /app/modules/delegate endpoint accepts POST requests with the specified payload."""
    # Prepare request payload
    payload = {
        "from_agent": "hal",
        "to_agent": "ash",
        "task": "Test cascading delegation",
        "delegation_depth": 2  # Should trigger cap enforcement
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

def test_malformed_request():
    """Test that the endpoint returns 422 for malformed requests."""
    # Prepare malformed payload (missing required fields)
    payload = {
        "agent_id": "ash",
        "goal": "Test cascading delegation",
        "delegation_depth": 2
    }
    
    # Set headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Make POST request
    print(f"Making malformed POST request to {DELEGATE_ENDPOINT}")
    response = requests.post(DELEGATE_ENDPOINT, json=payload, headers=headers)
    
    # Print response details
    print(f"Status code: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Verify response
    if response.status_code == 422:
        print("✅ Malformed request correctly returned 422")
        try:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
    else:
        print(f"❌ Unexpected status code {response.status_code} for malformed request")

def test_delegate_get_request():
    """Test that the /app/modules/delegate endpoint rejects GET requests."""
    # Make GET request
    print(f"Making GET request to {DELEGATE_ENDPOINT}")
    response = requests.get(DELEGATE_ENDPOINT)
    
    # Print response details
    print(f"Status code: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Verify response
    if response.status_code in [404, 405]:
        print("✅ GET request properly rejected with status code 404 or 405")
    else:
        print(f"❌ GET request returned unexpected status code {response.status_code}")

if __name__ == "__main__":
    print("Testing delegate endpoint...")
    print("\n=== Testing POST request with cap enforcement ===")
    test_delegate_post_request()
    print("\n=== Testing malformed request ===")
    test_malformed_request()
    print("\n=== Testing GET request ===")
    test_delegate_get_request()
    print("\nTests completed.")
