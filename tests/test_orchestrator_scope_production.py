import requests
import json
import time

# Test script for the /orchestrator/scope endpoint
print("Testing /orchestrator/scope endpoint...")

# Production URL
base_url = "https://web-production-2639.up.railway.app"
endpoint = "/orchestrator/scope"
url = base_url + endpoint

# Test payload
payload = {
    "goal": "Build a journaling AI that reflects on memory",
    "project_id": "proj-journal-test",
    "store_scope": True
}

# Wait for deployment to complete (30 seconds)
print("Waiting for deployment to complete...")
time.sleep(30)

# Make POST request
print(f"Making POST request to {url}")
try:
    response = requests.post(url, json=payload)
    
    # Print response status code
    print(f"Status code: {response.status_code}")
    
    # Print response body
    try:
        response_json = response.json()
        print(f"Response body: {json.dumps(response_json, indent=2)}")
    except:
        print(f"Response body: {response.text}")
    
    # Check if the request was successful
    if response.status_code == 200:
        print("✅ Test successful! The /orchestrator/scope endpoint is working correctly.")
    else:
        print("❌ Test failed. The endpoint returned a non-200 status code.")
except Exception as e:
    print(f"❌ Error making request: {str(e)}")

# Also test with GET request to verify it returns 405 Method Not Allowed
print("\nTesting GET request (should return 405 Method Not Allowed)...")
try:
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 405:
        print("✅ GET request correctly returned 405 Method Not Allowed.")
    else:
        print("❌ GET request test failed. Expected 405, got {response.status_code}.")
except Exception as e:
    print(f"❌ Error making GET request: {str(e)}")
