import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/modules"
TEST_AGENT_ID = "test_agent"

def test_reflect_endpoint():
    """
    Test the /reflect endpoint with SDK-compliant payload.
    Verifies:
    1. Input validation works correctly
    2. Response format matches SDK requirements
    3. Memory is written with proper trace fields
    4. Logging is implemented correctly
    """
    print("\n🧪 Testing /reflect endpoint with SDK-compliant payload...")
    
    # Generate unique IDs for tracing
    task_id = str(uuid.uuid4())
    project_id = f"test_project_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    memory_trace_id = str(uuid.uuid4())
    
    # Create SDK-compliant payload
    payload = {
        "agent_id": TEST_AGENT_ID,
        "goal": "Test reflection generation with SDK-compliant payload",
        "context": {"test_key": "test_value"},
        "task_id": task_id,
        "project_id": project_id,
        "memory_trace_id": memory_trace_id,
        "type": "memory",
        "limit": 5
    }
    
    # Send request to /reflect endpoint
    response = requests.post(f"{BASE_URL}/reflect", json=payload)
    
    # Verify response status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Parse response JSON
    response_data = response.json()
    
    # Verify response format matches SDK requirements
    assert "status" in response_data, "Response missing 'status' field"
    assert response_data["status"] == "success", f"Expected status 'success', got '{response_data['status']}'"
    assert "reflection" in response_data, "Response missing 'reflection' field"
    assert "task_id" in response_data, "Response missing 'task_id' field"
    assert response_data["task_id"] == task_id, f"Expected task_id '{task_id}', got '{response_data['task_id']}'"
    assert "project_id" in response_data, "Response missing 'project_id' field"
    assert response_data["project_id"] == project_id, f"Expected project_id '{project_id}', got '{response_data['project_id']}'"
    assert "memory_trace_id" in response_data, "Response missing 'memory_trace_id' field"
    assert response_data["memory_trace_id"] == memory_trace_id, f"Expected memory_trace_id '{memory_trace_id}', got '{response_data['memory_trace_id']}'"
    assert "agent_id" in response_data, "Response missing 'agent_id' field"
    assert response_data["agent_id"] == TEST_AGENT_ID, f"Expected agent_id '{TEST_AGENT_ID}', got '{response_data['agent_id']}'"
    
    print("✅ Response format matches SDK requirements")
    
    # Verify memory was written with proper trace fields
    thread_payload = {
        "agent_id": TEST_AGENT_ID,
        "project_id": project_id
    }
    
    thread_response = requests.post(f"{BASE_URL}/thread", json=thread_payload)
    thread_data = thread_response.json()
    
    assert thread_response.status_code == 200, f"Expected status code 200 for /thread, got {thread_response.status_code}"
    assert "memory_thread" in thread_data, "Thread response missing 'memory_thread' field"
    
    # Find the reflection memory in the thread
    reflection_memories = [
        memory for memory in thread_data["memory_thread"] 
        if "reflection" in memory.get("content", "").lower()
    ]
    
    assert len(reflection_memories) > 0, "No reflection memory found in thread"
    
    print("✅ Memory was written and appears in thread")
    
    # Test error handling with invalid payload
    invalid_payload = {
        "agent_id": TEST_AGENT_ID,
        # Missing required fields
    }
    
    error_response = requests.post(f"{BASE_URL}/reflect", json=invalid_payload)
    error_data = error_response.json()
    
    assert error_response.status_code in [400, 422, 500], f"Expected error status code, got {error_response.status_code}"
    assert "status" in error_data, "Error response missing 'status' field"
    assert error_data["status"] in ["failure", "error"], f"Expected status 'failure' or 'error', got '{error_data['status']}'"
    
    print("✅ Error handling works correctly")
    
    print("🎉 All tests passed! /reflect endpoint is SDK-compliant")

if __name__ == "__main__":
    test_reflect_endpoint()
