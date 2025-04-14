import requests
import uuid
import json
from typing import Dict, Any, List, Optional

# Test configuration
BASE_URL = "http://localhost:3000"  # Update with actual server URL when testing
TEST_AGENT_ID = "test-agent-123"

def test_train_endpoint_with_sdk_contract():
    """
    Comprehensive test for the /train endpoint with Promethios SDK Contract v1.0.0 support
    
    This test verifies:
    1. Training with full metadata
    2. Memory writing with all fields
    3. Memory type and trace linkage
    4. Access permissions storage
    5. Response format compliance
    """
    print("\n=== Testing /train endpoint with SDK Contract v1.0.0 ===")
    
    # Generate unique IDs for testing
    project_id = f"project-{uuid.uuid4()}"
    task_id = str(uuid.uuid4())
    memory_trace_id = f"trace-{uuid.uuid4()}"
    
    # Create test dataset
    test_dataset = [
        {
            "content": "This is a test training item with knowledge domain and persona profile.",
            "tags": ["test", "knowledge_domain", "persona_profile"]
        },
        {
            "content": "This is another test training item for SDK Contract compliance testing.",
            "tags": ["test", "sdk_contract", "v1.0.0"]
        }
    ]
    
    # Create training request with all SDK Contract v1.0.0 fields
    training_request = {
        "agent_id": TEST_AGENT_ID,
        "dataset": test_dataset,
        "goal": "Test SDK Contract v1.0.0 compliance",
        "tags": ["test", "sdk_contract", "v1.0.0"],
        "auto_reflect": False,
        "preview": True,  # Use preview mode to check fields without writing to memory
        "staged": False,
        
        # SDK Contract v1.0.0 fields
        "project_id": project_id,
        "task_id": task_id,
        "memory_trace_id": memory_trace_id,
        "persona_profile": "technical_assistant",
        "knowledge_domain": "software_development",
        "access_permissions": ["admin", "developer"]
    }
    
    # Test 1: Preview mode to verify fields are passed correctly
    print("\n--- Test 1: Preview mode to verify fields ---")
    try:
        response = requests.post(
            f"{BASE_URL}/api/train",
            json=training_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Preview response: {json.dumps(result, indent=2)}")
            
            # Verify SDK Contract fields are included in preview response
            assert result["status"] == "preview", "Status should be 'preview'"
            assert "project_id" in result, "project_id should be in response"
            assert result["project_id"] == project_id, "project_id should match request"
            assert "task_id" in result, "task_id should be in response"
            assert result["task_id"] == task_id, "task_id should match request"
            assert "memory_trace_id" in result, "memory_trace_id should be in response"
            assert result["memory_trace_id"] == memory_trace_id, "memory_trace_id should match request"
            
            # Verify memory entries have correct fields
            for entry in result["memory_entries"]:
                assert entry["type"] == "training", "Memory type should be 'training'"
                assert "project_id" in entry, "project_id should be in memory entry"
                assert entry["project_id"] == project_id, "project_id should match request"
                assert "task_id" in entry, "task_id should be in memory entry"
                assert entry["task_id"] == task_id, "task_id should match request"
                assert "memory_trace_id" in entry, "memory_trace_id should be in memory entry"
                assert entry["memory_trace_id"] == memory_trace_id, "memory_trace_id should match request"
                assert "persona_profile" in entry, "persona_profile should be in memory entry"
                assert entry["persona_profile"] == "technical_assistant", "persona_profile should match request"
                assert "knowledge_domain" in entry, "knowledge_domain should be in memory entry"
                assert entry["knowledge_domain"] == "software_development", "knowledge_domain should match request"
                assert "access_permissions" in entry, "access_permissions should be in memory entry"
                assert "admin" in entry["access_permissions"], "access_permissions should contain 'admin'"
                assert "developer" in entry["access_permissions"], "access_permissions should contain 'developer'"
            
            print("✅ Preview test passed: All SDK Contract fields are correctly included")
        else:
            print(f"❌ Preview test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Preview test error: {str(e)}")
    
    # Test 2: Actual training with SDK Contract fields
    print("\n--- Test 2: Actual training with SDK Contract fields ---")
    training_request["preview"] = False  # Disable preview mode for actual training
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/train",
            json=training_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Training response: {json.dumps(result, indent=2)}")
            
            # Verify SDK Contract response format
            assert result["status"] == "success", "Status should be 'success'"
            assert "memory_id" in result, "memory_id should be in response"
            assert "task_id" in result, "task_id should be in response"
            assert result["task_id"] == task_id, "task_id should match request"
            assert "project_id" in result, "project_id should be in response"
            assert result["project_id"] == project_id, "project_id should match request"
            assert "memory_trace_id" in result, "memory_trace_id should be in response"
            assert result["memory_trace_id"] == memory_trace_id, "memory_trace_id should match request"
            assert "log" in result, "log should be in response"
            
            print("✅ Training test passed: SDK Contract response format is correct")
            
            # Store memory_id for verification in next test
            memory_id = result["memory_id"]
        else:
            print(f"❌ Training test failed: {response.status_code} - {response.text}")
            memory_id = None
    except Exception as e:
        print(f"❌ Training test error: {str(e)}")
        memory_id = None
    
    # Test 3: Verify memory was written correctly (if we have a memory_id)
    if memory_id:
        print("\n--- Test 3: Verify memory was written correctly ---")
        try:
            # Use memory search endpoint to find the written memory
            search_request = {
                "agent_id": TEST_AGENT_ID,
                "query": "test",
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
                    # Verify the first memory has all required fields
                    memory = result["memories"][0]
                    assert memory["type"] == "training", "Memory type should be 'training'"
                    assert "project_id" in memory, "project_id should be in memory"
                    assert memory["project_id"] == project_id, "project_id should match request"
                    assert "task_id" in memory, "task_id should be in memory"
                    assert memory["task_id"] == task_id, "task_id should match request"
                    
                    print("✅ Memory verification test passed: Memory was written with correct fields")
                else:
                    print("❌ Memory verification test failed: No memories found")
            else:
                print(f"❌ Memory verification test failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Memory verification test error: {str(e)}")
    
    # Test 4: Test error handling
    print("\n--- Test 4: Test error handling ---")
    # Create an invalid request (missing required field)
    invalid_request = {
        "agent_id": TEST_AGENT_ID,
        "goal": "Test error handling",
        # Missing required 'dataset' field
        "project_id": project_id,
        "task_id": task_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/train",
            json=invalid_request
        )
        
        if response.status_code != 200:
            error_result = response.json()
            print(f"Error response: {json.dumps(error_result, indent=2)}")
            
            # Verify error response includes SDK Contract fields
            assert error_result["status"] == "error", "Status should be 'error'"
            assert "task_id" in error_result, "task_id should be in error response"
            assert error_result["task_id"] == task_id, "task_id should match request"
            assert "project_id" in error_result, "project_id should be in error response"
            assert error_result["project_id"] == project_id, "project_id should match request"
            
            print("✅ Error handling test passed: Error response includes SDK Contract fields")
        else:
            print("❌ Error handling test failed: Request should have failed but succeeded")
    except Exception as e:
        print(f"❌ Error handling test error: {str(e)}")
    
    print("\n=== Test suite completed ===")

if __name__ == "__main__":
    test_train_endpoint_with_sdk_contract()
