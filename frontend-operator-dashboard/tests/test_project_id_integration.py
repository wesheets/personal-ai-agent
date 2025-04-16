import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_AGENT_ID = "test-agent"
TEST_PROJECT_ID = f"proj-test-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def test_project_id_integration():
    """
    Test project_id integration across memory and task modules.
    Verifies:
    1. /write endpoint accepts and stores project_id
    2. /read endpoint filters by project_id
    3. /task/status endpoints handle project_id for both POST and GET
    """
    print("\n🧪 Testing project_id integration across memory and task modules...")
    
    # Generate unique IDs for testing
    memory_id = None
    task_id = f"task-{uuid.uuid4()}"
    memory_trace_id = f"trace-{uuid.uuid4()}"
    
    # Test 1: POST to /write with project_id
    print("\nTest 1: POST to /write with project_id")
    write_payload = {
        "agent_id": TEST_AGENT_ID,
        "memory_type": "reflection",
        "content": "Loop completed with no errors.",
        "tags": ["test", "integration"],
        "project_id": TEST_PROJECT_ID
    }
    
    response = requests.post(f"{BASE_URL}/app/modules/write", json=write_payload)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    # Verify response format
    assert "status" in response_data, "Response missing 'status' field"
    assert response_data["status"] == "ok", f"Expected status 'ok', got '{response_data['status']}'"
    assert "memory_id" in response_data, "Response missing 'memory_id' field"
    
    memory_id = response_data["memory_id"]
    print(f"✅ Test 1 passed: /write endpoint accepts project_id")
    
    # Test 2: GET from /read with project_id filter
    print("\nTest 2: GET from /read with project_id filter")
    response = requests.get(f"{BASE_URL}/app/modules/read?agent_id={TEST_AGENT_ID}&project_id={TEST_PROJECT_ID}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    # Verify response format
    assert "status" in response_data, "Response missing 'status' field"
    assert response_data["status"] == "ok", f"Expected status 'ok', got '{response_data['status']}'"
    assert "memories" in response_data, "Response missing 'memories' field"
    assert len(response_data["memories"]) > 0, "Expected at least one memory, got none"
    assert response_data["memories"][0]["project_id"] == TEST_PROJECT_ID, f"Expected project_id '{TEST_PROJECT_ID}', got '{response_data['memories'][0]['project_id']}'"
    
    print(f"✅ Test 2 passed: /read endpoint filters by project_id")
    
    # Test 3: POST to /task/status with project_id
    print("\nTest 3: POST to /task/status with project_id")
    task_status_payload = {
        "task_id": task_id,
        "project_id": TEST_PROJECT_ID,
        "agent_id": TEST_AGENT_ID,
        "memory_trace_id": memory_trace_id,
        "status": "completed",
        "output": "Task completed successfully"
    }
    
    response = requests.post(f"{BASE_URL}/app/task/status", json=task_status_payload)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    # Verify response format
    assert "status" in response_data, "Response missing 'status' field"
    assert response_data["status"] == "success", f"Expected status 'success', got '{response_data['status']}'"
    assert "log_id" in response_data, "Response missing 'log_id' field"
    assert "task_id" in response_data, "Response missing 'task_id' field"
    assert response_data["task_id"] == task_id, f"Expected task_id '{task_id}', got '{response_data['task_id']}'"
    
    print(f"✅ Test 3 passed: /task/status POST endpoint accepts project_id")
    
    # Test 4: GET from /task/status with project_id filter
    print("\nTest 4: GET from /task/status with project_id filter")
    response = requests.get(f"{BASE_URL}/app/task/status?project_id={TEST_PROJECT_ID}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    # Verify response format
    assert "status" in response_data, "Response missing 'status' field"
    assert response_data["status"] == "success", f"Expected status 'success', got '{response_data['status']}'"
    assert "logs" in response_data, "Response missing 'logs' field"
    assert "count" in response_data, "Response missing 'count' field"
    assert response_data["count"] > 0, "Expected at least one log, got none"
    assert response_data["logs"][0]["project_id"] == TEST_PROJECT_ID, f"Expected project_id '{TEST_PROJECT_ID}', got '{response_data['logs'][0]['project_id']}'"
    
    print(f"✅ Test 4 passed: /task/status GET endpoint filters by project_id")
    
    print("\n🎉 All tests passed! project_id integration is working correctly across memory and task modules")

if __name__ == "__main__":
    test_project_id_integration()
