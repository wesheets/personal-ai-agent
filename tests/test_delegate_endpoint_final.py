import requests
import json
import time

# Test endpoint with POST request
def test_delegate_endpoint():
    print("=== Testing POST request to delegate endpoint ===")
    url = "https://web-production-2639.up.railway.app/app/modules/delegate"
    
    # Test payload
    payload = {
        "from_agent": "hal",
        "to_agent": "ash",
        "task": "Test delegate endpoint after fix",
        "delegation_depth": 1
    }
    
    # Make POST request
    print(f"Making POST request to {url}")
    response = requests.post(url, json=payload)
    
    # Print results
    print(f"Status code: {response.status_code}")
    try:
        print(f"Response body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response body: {response.text}")
    
    return response

# Test endpoint with GET request (should return 405)
def test_get_request():
    print("\n=== Testing GET request (should return 405) ===")
    url = "https://web-production-2639.up.railway.app/app/modules/delegate"
    
    # Make GET request
    print(f"Making GET request to {url}")
    response = requests.get(url)
    
    # Print results
    print(f"Status code: {response.status_code}")
    try:
        print(f"Response body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response body: {response.text}")
    
    return response

# Wait for deployment to complete
print("Waiting 60 seconds for deployment to complete...")
time.sleep(60)

# Run tests
post_response = test_delegate_endpoint()
get_response = test_get_request()

# Final summary
print("\n=== Final Test Summary ===")
if post_response.status_code in [200, 429]:
    print("✅ POST request successful (200 OK or 429 Too Many Requests)")
else:
    print(f"❌ POST request failed with status code {post_response.status_code}")

if get_response.status_code == 405:
    print("✅ GET request correctly rejected with 405 Method Not Allowed")
else:
    print(f"❌ GET request test failed with status code {get_response.status_code}")
