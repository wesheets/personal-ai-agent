import requests
import json
import uuid
from typing import Dict, Any, List, Optional

# Test configuration
BASE_URL = "http://localhost:3000"  # Update with actual server URL when testing
TEST_AGENT_ID = "hal"  # Using HAL as the test agent

def test_train_endpoint_single_memory():
    """
    Comprehensive test for the updated /train endpoint with single memory schema
    
    This test verifies:
    1. Request with single memory block (not a list)
    2. Response structure matches expected format
    3. Memory is written with all fields
    4. Memory appears in /memory/thread
    """
    print("\n=== Testing /train endpoint with single memory schema ===")
    
    # Generate unique IDs for testing
    project_id = "musemind"
    memory_trace_id = f"trace-{uuid.uuid4()}"
    task_id = f"train-test-{uuid.uuid4()}"
    
    # Test 1: Basic request with single memory block
    print("\n--- Test 1: Basic request with single memory block ---")
    try:
        # Create test request with single memory block (not a list)
        train_request = {
            "agent_id": TEST_AGENT_ID,
            "dataset": {
                "project_id": project_id,
                "task_id": task_id,
                "memory_trace_id": memory_trace_id,
                "persona_profile": "supportive coach",
                "knowledge_domain": "creative writing",
                "access_permissions": ["hal", "ash"],
                "content": "This is a test training entry for HAL with single memory schema",
                "tags": ["test", "training", "single-memory"]
            },
            "goal": "Test the updated /train endpoint with single memory schema",
            "tags": ["test", "endpoint", "schema-update"]
        }
        
        print(f"Request: {json.dumps(train_request, indent=2)}")
        
        # Test the endpoint
        response = requests.post(
            f"{BASE_URL}/api/modules/train",
            json=train_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Verify response structure
            assert "status" in result, "Response should include 'status' field"
            assert result["status"] == "success", "Status should be 'success'"
            assert "memory_id" in result, "Response should include 'memory_id' field"
            assert "task_id" in result, "Response should include 'task_id' field"
            assert result["task_id"] == task_id, "task_id should match request"
            assert "project_id" in result, "Response should include 'project_id' field"
            assert result["project_id"] == project_id, "project_id should match request"
            assert "memory_trace_id" in result, "Response should include 'memory_trace_id' field"
            assert result["memory_trace_id"] == memory_trace_id, "memory_trace_id should match request"
            
            print("✅ Basic request test passed: Response structure is correct")
        else:
            print(f"❌ Basic request test failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Basic request test error: {str(e)}")
        return
    
    # Test 2: Check memory thread for the training entry
    print("\n--- Test 2: Check memory thread for the training entry ---")
    try:
        thread_request = {
            "agent_id": TEST_AGENT_ID,
            "project_id": project_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/memory/thread",
            json=thread_request
        )
        
        if response.status_code == 200:
            result = response.json()
            memory_thread = result.get("memory_thread", [])
            
            # Find our training entry in the memory thread
            training_memories = [m for m in memory_thread if 
                               "content" in m and 
                               "single memory schema" in m["content"]]
            
            if training_memories:
                memory = training_memories[0]
                print(f"Found training entry in memory thread: {json.dumps(memory, indent=2)}")
                
                # Verify memory has the correct metadata
                assert memory.get("project_id") == project_id, "Memory should have correct project_id"
                
                print("✅ Memory thread test passed: Training entry appears in memory thread with correct metadata")
            else:
                print("❌ Memory thread test failed: Training entry not found in memory thread")
        else:
            print(f"❌ Memory thread test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Memory thread test error: {str(e)}")
    
    # Test 3: Check observer report for the training entry
    print("\n--- Test 3: Check observer report for the training entry ---")
    try:
        observer_request = {
            "project_id": project_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/observer/report",
            json=observer_request
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if our training entry is in the report
            training_found = False
            for section in result.values():
                if isinstance(section, list):
                    for item in section:
                        if isinstance(item, dict) and "content" in item and "single memory schema" in item["content"]:
                            training_found = True
                            print(f"Found training entry in observer report: {json.dumps(item, indent=2)}")
                            break
            
            if training_found:
                print("✅ Observer report test passed: Training entry appears in observer report")
            else:
                print("❌ Observer report test failed: Training entry not found in observer report")
        else:
            print(f"❌ Observer report test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Observer report test error: {str(e)}")
    
    print("\n=== Test suite completed ===")

if __name__ == "__main__":
    test_train_endpoint_single_memory()
