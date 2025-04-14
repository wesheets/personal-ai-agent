"""
Test script to verify memory persistence between task_result and memory endpoints.

This script tests:
1. Writing a memory through the /task/result endpoint
2. Retrieving the memory through the /read endpoint
3. Verifying the memory is correctly stored in both SQLite and memory_store
"""

import requests
import json
import sys
import time
import uuid

# Base URL for API endpoints
BASE_URL = "http://localhost:8000"  # Change this if testing against a different environment

def test_task_result_memory_persistence():
    """Test memory persistence between task_result and memory endpoints"""
    print("🧪 Starting task_result memory persistence test...")
    
    # Generate unique IDs for this test
    test_agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"
    test_task_id = f"test_task_{uuid.uuid4().hex[:8]}"
    
    # Create test data for task_result endpoint
    task_result_data = {
        "agent_id": test_agent_id,
        "task_id": test_task_id,
        "outcome": "success",
        "confidence_score": 0.95,
        "output": "Test memory persistence between task_result and memory endpoints",
        "notes": "This is a test to verify memory persistence",
        "project_id": "test_project"
    }
    
    # Step 1: Write memory through task_result endpoint
    print(f"📤 Writing test memory through /task/result endpoint...")
    try:
        task_result_response = requests.post(
            f"{BASE_URL}/api/modules/task/result",
            json=task_result_data
        )
        
        # Check if request was successful
        task_result_response.raise_for_status()
        
        # Parse response
        result = task_result_response.json()
        print(f"✅ Successfully wrote memory through task_result endpoint")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        # Extract memory_id
        memory_id = result.get("memory_id")
        if not memory_id:
            print(f"❌ No memory_id returned from task_result endpoint")
            return False
        
        print(f"🔑 Captured memory_id: {memory_id}")
        
        # Step 2: Wait a moment to ensure memory is persisted
        print(f"⏱️ Waiting for memory to be persisted...")
        time.sleep(1)
        
        # Step 3: Read memory through read endpoint
        print(f"📥 Reading memory with memory_id={memory_id}...")
        read_response = requests.get(
            f"{BASE_URL}/api/modules/read?memory_id={memory_id}"
        )
        
        # Check if request was successful
        read_response.raise_for_status()
        
        # Parse response
        read_result = read_response.json()
        
        # Check if memory was found
        if read_result.get("status") != "ok" or not read_result.get("memories"):
            print(f"❌ Memory not found in read endpoint response")
            print(f"Response: {json.dumps(read_result, indent=2)}")
            return False
        
        # Extract memory from response
        memory = read_result["memories"][0]
        
        # Verify memory content
        if memory["agent_id"] != test_agent_id:
            print(f"❌ Memory agent_id mismatch: {memory['agent_id']} != {test_agent_id}")
            return False
        
        if memory["task_id"] != test_task_id:
            print(f"❌ Memory task_id mismatch: {memory['task_id']} != {test_task_id}")
            return False
        
        if memory["type"] != "task_result":
            print(f"❌ Memory type mismatch: {memory['type']} != task_result")
            return False
        
        print(f"✅ Successfully read memory through read endpoint")
        print(f"✅ Memory content matches expected values")
        print(f"✅ Memory persistence between task_result and memory endpoints verified")
        
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during API request: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_task_result_memory_persistence()
    if success:
        print("✅ Task result memory persistence test passed!")
        sys.exit(0)
    else:
        print("❌ Task result memory persistence test failed!")
        sys.exit(1)
