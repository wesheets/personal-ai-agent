import requests
import json
import uuid
from typing import Dict, Any, List, Optional

# Test configuration
BASE_URL = "http://localhost:3000"  # Update with actual server URL when testing

def test_delegate_memory_writing():
    """
    Test the /delegate endpoint to verify memory writing functionality
    
    This test verifies:
    1. Memory is written for both from_agent and to_agent
    2. Memory appears in /memory/thread for both agents
    3. Memory includes task_id, project_id, memory_trace_id
    4. Memory writing occurs even when auto_execute is false
    """
    print("\n=== Testing /delegate endpoint memory writing ===")
    
    # Generate unique IDs for testing
    task_id = f"delegate-test-{uuid.uuid4()}"
    project_id = "musemind"
    memory_trace_id = f"trace-{uuid.uuid4()}"
    
    # Create test request
    delegate_request = {
        "task_id": task_id,
        "project_id": project_id,
        "from_agent": "hal",
        "agent_name": "ash",  # to_agent
        "memory_trace_id": memory_trace_id,
        "task": "Summarize the last loop snapshot",
        "objective": "Summarize the last loop snapshot",
        "required_capabilities": ["summarize"],
        "input_data": {"summary_type": "basic"},
        "auto_execute": False
    }
    
    print(f"\n--- Test request: {json.dumps(delegate_request, indent=2)} ---")
    
    try:
        # Send delegation request
        response = requests.post(
            f"{BASE_URL}/api/modules/delegate",
            json=delegate_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Delegation response: {json.dumps(result, indent=2)}")
            
            # Verify delegation response
            assert "status" in result, "Response should include 'status' field"
            assert result["status"] == "success", "Status should be 'success'"
            assert "delegation_id" in result, "Response should include 'delegation_id' field"
            
            print("✅ Delegation request successful")
        else:
            print(f"❌ Delegation request failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Delegation request error: {str(e)}")
        return
    
    # Wait a moment for memory to be written
    import time
    time.sleep(1)
    
    # Test 1: Check memory thread for from_agent (hal)
    print("\n--- Test 1: Check memory thread for from_agent (hal) ---")
    try:
        thread_request = {
            "agent_id": "hal",
            "project_id": project_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/memory/thread",
            json=thread_request
        )
        
        if response.status_code == 200:
            result = response.json()
            memories = result.get("memories", [])
            
            # Find our delegation memory
            delegation_memories = [m for m in memories if 
                                  m.get("task_id") == task_id and 
                                  m.get("type") == "delegation_log"]
            
            if delegation_memories:
                memory = delegation_memories[0]
                print(f"Found delegation memory for hal: {json.dumps(memory, indent=2)}")
                
                # Verify memory fields
                assert memory["agent_id"] == "hal", "Memory agent_id should be 'hal'"
                assert memory["type"] == "delegation_log", "Memory type should be 'delegation_log'"
                assert memory["project_id"] == project_id, "Memory project_id should match request"
                assert memory["task_id"] == task_id, "Memory task_id should match request"
                assert memory["memory_trace_id"] == memory_trace_id, "Memory trace_id should match request"
                assert "to:ash" in memory["tags"], "Memory tags should include 'to:ash'"
                assert memory["status"] == "delegated", "Memory status should be 'delegated'"
                
                print("✅ Memory writing for from_agent (hal) verified")
            else:
                print("❌ No delegation memory found for hal")
        else:
            print(f"❌ Memory thread request failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Memory thread request error: {str(e)}")
    
    # Test 2: Check memory thread for to_agent (ash)
    print("\n--- Test 2: Check memory thread for to_agent (ash) ---")
    try:
        thread_request = {
            "agent_id": "ash",
            "project_id": project_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/memory/thread",
            json=thread_request
        )
        
        if response.status_code == 200:
            result = response.json()
            memories = result.get("memories", [])
            
            # Find our delegation memory
            delegation_memories = [m for m in memories if 
                                  m.get("task_id") == task_id and 
                                  m.get("type") == "delegation_log"]
            
            if delegation_memories:
                memory = delegation_memories[0]
                print(f"Found delegation memory for ash: {json.dumps(memory, indent=2)}")
                
                # Verify memory fields
                assert memory["agent_id"] == "ash", "Memory agent_id should be 'ash'"
                assert memory["type"] == "delegation_log", "Memory type should be 'delegation_log'"
                assert memory["project_id"] == project_id, "Memory project_id should match request"
                assert memory["task_id"] == task_id, "Memory task_id should match request"
                assert memory["memory_trace_id"] == memory_trace_id, "Memory trace_id should match request"
                assert "from:hal" in memory["tags"], "Memory tags should include 'from:hal'"
                assert memory["status"] == "pending", "Memory status should be 'pending'"
                
                print("✅ Memory writing for to_agent (ash) verified")
            else:
                print("❌ No delegation memory found for ash")
        else:
            print(f"❌ Memory thread request failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Memory thread request error: {str(e)}")
    
    # Test 3: Check observer report
    print("\n--- Test 3: Check observer report ---")
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
            print(f"Observer report: {json.dumps(result, indent=2)}")
            
            # Check if our delegation is in the report
            delegations = result.get("delegations", [])
            found_delegation = False
            
            for delegation in delegations:
                if delegation.get("task_id") == task_id:
                    found_delegation = True
                    print(f"Found delegation in observer report: {json.dumps(delegation, indent=2)}")
                    break
            
            if found_delegation:
                print("✅ Delegation found in observer report")
            else:
                print("❌ Delegation not found in observer report")
        else:
            print(f"❌ Observer report request failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Observer report request error: {str(e)}")
    
    print("\n=== Test suite completed ===")

if __name__ == "__main__":
    test_delegate_memory_writing()
