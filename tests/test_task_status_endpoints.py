import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/app/task"
TEST_AGENT_ID = "test_agent"

def test_task_status_endpoints():
    """
    Test the /task/status endpoints for both POST and GET operations.
    Verifies:
    1. Input validation works correctly
    2. Response format matches requirements
    3. Memory is written with proper metadata
    4. Query functionality works correctly
    """
    print("\n🧪 Testing /task/status endpoints...")
    
    # Generate unique IDs for tracing
    task_id = str(uuid.uuid4())
    project_id = f"test_project_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    memory_trace_id = str(uuid.uuid4())
    
    # Test 1: POST to log a successful task
    print("\nTest 1: POST to log a successful task")
    payload1 = {
        "task_id": task_id,
        "project_id": project_id,
        "agent_id": TEST_AGENT_ID,
        "memory_trace_id": memory_trace_id,
        "status": "completed",
        "output": "Task completed successfully with result: 42",
        "duration_ms": 1500
    }
    
    response1 = requests.post(f"{BASE_URL}/status", json=payload1)
    assert response1.status_code == 200, f"Expected status code 200, got {response1.status_code}"
    
    response_data1 = response1.json()
    print(f"Response: {json.dumps(response_data1, indent=2)}")
    
    # Verify response format
    assert "status" in response_data1, "Response missing 'status' field"
    assert response_data1["status"] == "success", f"Expected status 'success', got '{response_data1['status']}'"
    assert "log_id" in response_data1, "Response missing 'log_id' field"
    assert "task_id" in response_data1, "Response missing 'task_id' field"
    assert response_data1["task_id"] == task_id, f"Expected task_id '{task_id}', got '{response_data1['task_id']}'"
    assert "timestamp" in response_data1, "Response missing 'timestamp' field"
    assert "stored" in response_data1, "Response missing 'stored' field"
    assert response_data1["stored"] == True, f"Expected stored 'true', got '{response_data1['stored']}'"
    
    print("✅ Test 1 passed: POST endpoint works correctly")
    
    # Test 2: POST to log a failed task
    print("\nTest 2: POST to log a failed task")
    task_id2 = str(uuid.uuid4())
    payload2 = {
        "task_id": task_id2,
        "project_id": project_id,
        "agent_id": TEST_AGENT_ID,
        "memory_trace_id": memory_trace_id,
        "status": "failed",
        "output": None,
        "error": "Task failed due to network error",
        "duration_ms": 500
    }
    
    response2 = requests.post(f"{BASE_URL}/status", json=payload2)
    assert response2.status_code == 200, f"Expected status code 200, got {response2.status_code}"
    
    response_data2 = response2.json()
    print(f"Response: {json.dumps(response_data2, indent=2)}")
    
    # Verify response format
    assert "status" in response_data2, "Response missing 'status' field"
    assert response_data2["status"] == "success", f"Expected status 'success', got '{response_data2['status']}'"
    assert "log_id" in response_data2, "Response missing 'log_id' field"
    assert "task_id" in response_data2, "Response missing 'task_id' field"
    assert response_data2["task_id"] == task_id2, f"Expected task_id '{task_id2}', got '{response_data2['task_id']}'"
    
    print("✅ Test 2 passed: POST endpoint handles failed tasks correctly")
    
    # Test 3: GET to query by task_id
    print("\nTest 3: GET to query by task_id")
    response3 = requests.get(f"{BASE_URL}/status?task_id={task_id}")
    assert response3.status_code == 200, f"Expected status code 200, got {response3.status_code}"
    
    response_data3 = response3.json()
    print(f"Response: {json.dumps(response_data3, indent=2)}")
    
    # Verify response format
    assert "status" in response_data3, "Response missing 'status' field"
    assert response_data3["status"] == "success", f"Expected status 'success', got '{response_data3['status']}'"
    assert "logs" in response_data3, "Response missing 'logs' field"
    assert "count" in response_data3, "Response missing 'count' field"
    assert response_data3["count"] == 1, f"Expected count 1, got {response_data3['count']}"
    assert len(response_data3["logs"]) == 1, f"Expected 1 log, got {len(response_data3['logs'])}"
    assert response_data3["logs"][0]["task_id"] == task_id, f"Expected task_id '{task_id}', got '{response_data3['logs'][0]['task_id']}'"
    
    print("✅ Test 3 passed: GET endpoint filters by task_id correctly")
    
    # Test 4: GET to query by project_id
    print("\nTest 4: GET to query by project_id")
    response4 = requests.get(f"{BASE_URL}/status?project_id={project_id}")
    assert response4.status_code == 200, f"Expected status code 200, got {response4.status_code}"
    
    response_data4 = response4.json()
    print(f"Response: {json.dumps(response_data4, indent=2)}")
    
    # Verify response format
    assert "status" in response_data4, "Response missing 'status' field"
    assert response_data4["status"] == "success", f"Expected status 'success', got '{response_data4['status']}'"
    assert "logs" in response_data4, "Response missing 'logs' field"
    assert "count" in response_data4, "Response missing 'count' field"
    assert response_data4["count"] == 2, f"Expected count 2, got {response_data4['count']}"
    assert len(response_data4["logs"]) == 2, f"Expected 2 logs, got {len(response_data4['logs'])}"
    
    print("✅ Test 4 passed: GET endpoint filters by project_id correctly")
    
    # Test 5: GET to query by agent_id
    print("\nTest 5: GET to query by agent_id")
    response5 = requests.get(f"{BASE_URL}/status?agent_id={TEST_AGENT_ID}")
    assert response5.status_code == 200, f"Expected status code 200, got {response5.status_code}"
    
    response_data5 = response5.json()
    print(f"Response: {json.dumps(response_data5, indent=2)}")
    
    # Verify response format
    assert "status" in response_data5, "Response missing 'status' field"
    assert response_data5["status"] == "success", f"Expected status 'success', got '{response_data5['status']}'"
    assert "logs" in response_data5, "Response missing 'logs' field"
    assert "count" in response_data5, "Response missing 'count' field"
    assert response_data5["count"] == 2, f"Expected count 2, got {response_data5['count']}"
    assert len(response_data5["logs"]) == 2, f"Expected 2 logs, got {len(response_data5['logs'])}"
    
    print("✅ Test 5 passed: GET endpoint filters by agent_id correctly")
    
    # Test 6: GET to query by memory_trace_id
    print("\nTest 6: GET to query by memory_trace_id")
    response6 = requests.get(f"{BASE_URL}/status?memory_trace_id={memory_trace_id}")
    assert response6.status_code == 200, f"Expected status code 200, got {response6.status_code}"
    
    response_data6 = response6.json()
    print(f"Response: {json.dumps(response_data6, indent=2)}")
    
    # Verify response format
    assert "status" in response_data6, "Response missing 'status' field"
    assert response_data6["status"] == "success", f"Expected status 'success', got '{response_data6['status']}'"
    assert "logs" in response_data6, "Response missing 'logs' field"
    assert "count" in response_data6, "Response missing 'count' field"
    assert response_data6["count"] == 2, f"Expected count 2, got {response_data6['count']}"
    assert len(response_data6["logs"]) == 2, f"Expected 2 logs, got {len(response_data6['logs'])}"
    
    print("✅ Test 6 passed: GET endpoint filters by memory_trace_id correctly")
    
    # Test 7: Error handling with invalid payload
    print("\nTest 7: Error handling with invalid payload")
    invalid_payload = {
        "agent_id": TEST_AGENT_ID,
        # Missing required fields
    }
    
    error_response = requests.post(f"{BASE_URL}/status", json=invalid_payload)
    assert error_response.status_code in [400, 422, 500], f"Expected error status code, got {error_response.status_code}"
    
    print("✅ Test 7 passed: Error handling works correctly")
    
    print("\n🎉 All tests passed! /task/status endpoints are working correctly")

if __name__ == "__main__":
    test_task_status_endpoints()
