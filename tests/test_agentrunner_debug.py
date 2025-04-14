"""
Test script for the AgentRunner debug patch.

This script tests the AgentRunner module with the debug patch to verify
that it properly logs execution and handles errors.
"""

import sys
import os
import json
import traceback

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the AgentRunner module
from app.modules.agent_runner import run_agent, CoreForgeAgent

def test_entry_confirmation():
    """Test that entry confirmation logging works."""
    print("\n=== Testing Entry Confirmation Logging ===\n")
    
    try:
        # Create test messages
        messages = [
            {"role": "user", "content": "What is 2 + 2?"}
        ]
        
        # Call run_agent
        print("Calling run_agent with Core.Forge agent_id...")
        result = run_agent("Core.Forge", messages)
        
        # Check if result is a dict (success) or JSONResponse (error)
        if hasattr(result, "body"):
            # It's a JSONResponse
            body = json.loads(result.body.decode())
            print(f"Received JSONResponse with status code: {result.status_code}")
            print(f"Response body: {json.dumps(body, indent=2)}")
            print("\n❌ Test failed: run_agent returned JSONResponse instead of dict")
            return False
        else:
            # It's a dict
            print(f"Response: {json.dumps(result, indent=2)}")
            print("\n✅ Test passed: Entry confirmation logging should be visible above")
            return True
    
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test that error handling works properly."""
    print("\n=== Testing Error Handling ===\n")
    
    try:
        # Temporarily unset OPENAI_API_KEY to force an error
        original_key = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = ""
        
        # Create test messages
        messages = [
            {"role": "user", "content": "This should fail due to missing API key"}
        ]
        
        # Call run_agent
        print("Calling run_agent with missing API key...")
        result = run_agent("Core.Forge", messages)
        
        # Restore original API key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key
        else:
            del os.environ["OPENAI_API_KEY"]
        
        # Check if result is a JSONResponse with status code 500
        if hasattr(result, "body") and result.status_code == 500:
            body = json.loads(result.body.decode())
            print(f"Received JSONResponse with status code: {result.status_code}")
            print(f"Response body: {json.dumps(body, indent=2)}")
            print("\n✅ Test passed: Error handling returned proper JSONResponse with status 500")
            return True
        else:
            print(f"Unexpected result type: {type(result)}")
            print(f"Result: {result}")
            print("\n❌ Test failed: Error handling did not return JSONResponse with status 500")
            return False
    
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        # Ensure API key is restored
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key

def run_all_tests():
    """Run all tests and report results."""
    print("\n=== Running All AgentRunner Debug Patch Tests ===\n")
    
    tests = [
        ("Entry Confirmation Logging", test_entry_confirmation),
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
