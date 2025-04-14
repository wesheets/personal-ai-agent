"""
Test script for the AgentRunner inline debug patch.

This script tests the patched AgentRunner route with inline execution debug logging.
"""

import sys
import os
import json
import traceback
import requests

def test_agentrunner_endpoint():
    """Test the patched AgentRunner endpoint with inline debug logging."""
    print("\n=== Testing AgentRunner Endpoint with Inline Debug ===\n")
    
    try:
        # Define the endpoint URL
        url = "http://localhost:8000/api/modules/agent/run"
        
        # Define the request payload
        payload = {
            "messages": [
                {"role": "user", "content": "What is 2 + 2?"}
            ]
        }
        
        # Send the request
        print(f"Sending POST request to {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        
        # Print the response
        print(f"\nResponse status code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"Response body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Raw response: {response.text}")
        
        # Check if the response is successful
        if response.status_code == 200:
            print("\n✅ Test passed: AgentRunner endpoint returned 200 OK")
            return True
        else:
            print(f"\n❌ Test failed: AgentRunner endpoint returned {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling in the patched AgentRunner endpoint."""
    print("\n=== Testing Error Handling in AgentRunner Endpoint ===\n")
    
    try:
        # Define the endpoint URL
        url = "http://localhost:8000/api/modules/agent/run"
        
        # Define an invalid request payload (missing messages)
        payload = {
            "agent_id": "Core.Forge"
            # Missing messages field
        }
        
        # Send the request
        print(f"Sending POST request to {url} with invalid payload")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        
        # Print the response
        print(f"\nResponse status code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"Response body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Raw response: {response.text}")
        
        # Check if the response is a 400 Bad Request
        if response.status_code == 400:
            print("\n✅ Test passed: AgentRunner endpoint returned 400 Bad Request for invalid payload")
            return True
        else:
            print(f"\n❌ Test failed: AgentRunner endpoint returned {response.status_code} instead of 400")
            return False
    
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("\n=== Running All AgentRunner Inline Debug Patch Tests ===\n")
    
    tests = [
        ("AgentRunner Endpoint", test_agentrunner_endpoint),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n--- Running Test: {name} ---\n")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test {name} failed with exception: {str(e)}")
            traceback.print_exc()
            results.append((name, False))
    
    # Print summary
    print("\n=== Test Results Summary ===\n")
    
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()
