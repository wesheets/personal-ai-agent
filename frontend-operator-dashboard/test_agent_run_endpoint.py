import requests
import uuid
import json
from typing import Dict, Any, List, Optional

# Test configuration
BASE_URL = "http://localhost:3000"  # Update with actual server URL when testing
TEST_AGENT_ID = "hal"  # Using HAL as the test agent

def test_agent_run_endpoint_with_sdk_contract():
    """
    Comprehensive test for the /agent/run endpoint with Promethios SDK Contract v1.0.0 support
    
    This test verifies:
    1. Request with full schema
    2. Response matches expected output format
    3. Memory is written correctly
    4. Observer sees task via /observer/report
    """
    print("\n=== Testing /agent/run endpoint with SDK Contract v1.0.0 ===")
    
    # Generate unique IDs for testing
    task_id = str(uuid.uuid4())
    project_id = "musemind"
    memory_trace_id = f"trace-{uuid.uuid4()}"
    
    # Create test request with full schema
    run_request = {
        "agent_id": TEST_AGENT_ID,
        "task_id": task_id,
        "project_id": project_id,
        "memory_trace_id": memory_trace_id,
        "objective": "Summarize the last five creative entries.",
        "input_data": {
            "memory_limit": 5,
            "context_filter": "creative"
        },
        "expected_output_type": "summary_text"
    }
    
    # Test 1: Basic run with full schema
    print("\n--- Test 1: Basic run with full schema ---")
    try:
        response = requests.post(
            f"{BASE_URL}/api/modules/agent/run",
            json=run_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Verify SDK Contract response format
            assert "status" in result, "Response should include 'status' field"
            assert result["status"] in ["success", "error", "incomplete"], "Status should be 'success', 'error', or 'incomplete'"
            assert "log" in result, "Response should include 'log' field"
            assert "output" in result, "Response should include 'output' field"
            assert "result_text" in result["output"], "Output should include 'result_text' field"
            assert "summary_points" in result["output"], "Output should include 'summary_points' field"
            assert "task_id" in result, "Response should include 'task_id' field"
            assert result["task_id"] == task_id, "task_id should match request"
            assert "project_id" in result, "Response should include 'project_id' field"
            assert result["project_id"] == project_id, "project_id should match request"
            assert "memory_trace_id" in result, "Response should include 'memory_trace_id' field"
            assert result["memory_trace_id"] == memory_trace_id, "memory_trace_id should match request"
            assert "contract_version" in result, "Response should include 'contract_version' field"
            assert result["contract_version"] == "v1.0.0", "contract_version should be 'v1.0.0'"
            
            print("✅ Basic run test passed: SDK Contract response format is correct")
        else:
            print(f"❌ Basic run test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Basic run test error: {str(e)}")
    
    # Test 2: Verify memory writing
    print("\n--- Test 2: Verify memory writing ---")
    try:
        # Use memory search endpoint to find the written memory
        search_request = {
            "agent_id": TEST_AGENT_ID,
            "type": "agent_response",
            "project_id": project_id,
            "task_id": task_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/memory/search",
            json=search_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Found {len(result['memories'])} memories")
            
            if len(result["memories"]) > 0:
                # Verify the memory has all required fields
                memory = result["memories"][0]
                assert memory["type"] == "agent_response", "Memory type should be 'agent_response'"
                assert "project_id" in memory, "Memory should include 'project_id' field"
                assert memory["project_id"] == project_id, "project_id should match request"
                assert "task_id" in memory, "Memory should include 'task_id' field"
                assert memory["task_id"] == task_id, "task_id should match request"
                assert "agent_id" in memory, "Memory should include 'agent_id' field"
                assert memory["agent_id"] == TEST_AGENT_ID, "agent_id should match request"
                
                print("✅ Memory writing test passed: Memory was written with correct fields")
            else:
                print("❌ Memory writing test failed: No memories found")
        else:
            print(f"❌ Memory writing test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Memory writing test error: {str(e)}")
    
    # Test 3: Check observer report
    print("\n--- Test 3: Check observer report ---")
    try:
        # Use observer report endpoint to check if task is visible
        observer_request = {
            "project_id": project_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/observer/report",
            json=observer_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Observer report: {json.dumps(result, indent=2)}")
            
            # Check if our task is in the report
            task_found = False
            if "tasks" in result and len(result["tasks"]) > 0:
                for task in result["tasks"]:
                    if task.get("task_id") == task_id:
                        task_found = True
                        break
            
            if task_found:
                print("✅ Observer report test passed: Task is visible in observer report")
            else:
                print("❌ Observer report test failed: Task not found in observer report")
        else:
            print(f"❌ Observer report test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Observer report test error: {str(e)}")
    
    # Test 4: Test fallback logic for empty responses
    print("\n--- Test 4: Test fallback logic for empty responses ---")
    try:
        # Create a request that would likely result in an empty response
        empty_request = {
            "agent_id": TEST_AGENT_ID,
            "task_id": str(uuid.uuid4()),
            "project_id": project_id,
            "memory_trace_id": memory_trace_id,
            "objective": "",  # Empty objective should trigger fallback logic
            "input_data": {},
            "expected_output_type": "summary_text"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/modules/agent/run",
            json=empty_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Fallback response: {json.dumps(result, indent=2)}")
            
            # Verify fallback logic
            if result["status"] == "incomplete":
                print("✅ Fallback logic test passed: Empty response correctly marked as 'incomplete'")
            else:
                print(f"❌ Fallback logic test failed: Empty response should be 'incomplete', got '{result['status']}'")
        else:
            print(f"❌ Fallback logic test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Fallback logic test error: {str(e)}")
    
    # Test 5: Test error handling
    print("\n--- Test 5: Test error handling ---")
    try:
        # Create an invalid request (missing required field)
        invalid_request = {
            "agent_id": "non_existent_agent",  # Non-existent agent should trigger error
            "task_id": str(uuid.uuid4()),
            "project_id": project_id,
            "objective": "Test error handling"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/modules/agent/run",
            json=invalid_request
        )
        
        if response.status_code != 200:
            error_result = response.json()
            print(f"Error response: {json.dumps(error_result, indent=2)}")
            
            # Verify error response includes SDK Contract fields
            assert error_result["status"] == "error", "Status should be 'error'"
            assert "task_id" in error_result, "Error response should include 'task_id' field"
            assert "project_id" in error_result, "Error response should include 'project_id' field"
            assert "contract_version" in error_result, "Error response should include 'contract_version' field"
            
            print("✅ Error handling test passed: Error response includes SDK Contract fields")
        else:
            print("❌ Error handling test failed: Request should have failed but succeeded")
    except Exception as e:
        print(f"❌ Error handling test error: {str(e)}")
    
    print("\n=== Test suite completed ===")

if __name__ == "__main__":
    test_agent_run_endpoint_with_sdk_contract()
