import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/app/projects"
TEST_USER_ID = "test_user"

def test_projects_module():
    """
    Test the /projects endpoints for both POST and GET operations.
    Verifies:
    1. Input validation works correctly
    2. Response format matches requirements
    3. Memory is written with proper metadata
    4. Query functionality works correctly
    """
    print("\n🧪 Testing /projects endpoints...")
    
    # Generate unique IDs for tracing
    project_id = f"test_project_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Test 1: POST to create a new project
    print("\nTest 1: POST to create a new project")
    payload1 = {
        "project_id": project_id,
        "goal": "Build a vertical journaling SaaS",
        "user_id": TEST_USER_ID,
        "tags": ["journaling", "vertical", "foundrflow"],
        "context": "Summary of planning session"
    }
    
    response1 = requests.post(BASE_URL, json=payload1)
    assert response1.status_code == 200, f"Expected status code 200, got {response1.status_code}"
    
    response_data1 = response1.json()
    print(f"Response: {json.dumps(response_data1, indent=2)}")
    
    # Verify response format
    assert "status" in response_data1, "Response missing 'status' field"
    assert response_data1["status"] == "success", f"Expected status 'success', got '{response_data1['status']}'"
    assert "project_id" in response_data1, "Response missing 'project_id' field"
    assert response_data1["project_id"] == project_id, f"Expected project_id '{project_id}', got '{response_data1['project_id']}'"
    assert "created_at" in response_data1, "Response missing 'created_at' field"
    assert "log_id" in response_data1, "Response missing 'log_id' field"
    assert "stored" in response_data1, "Response missing 'stored' field"
    assert response_data1["stored"] == True, f"Expected stored 'true', got '{response_data1['stored']}'"
    
    print("✅ Test 1 passed: POST endpoint works correctly")
    
    # Test 2: POST to create another project with different tags
    print("\nTest 2: POST to create another project with different tags")
    project_id2 = f"test_project_2_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    payload2 = {
        "project_id": project_id2,
        "goal": "Create a task management system",
        "user_id": TEST_USER_ID,
        "tags": ["task", "management", "productivity"],
        "context": "Task management system for teams"
    }
    
    response2 = requests.post(BASE_URL, json=payload2)
    assert response2.status_code == 200, f"Expected status code 200, got {response2.status_code}"
    
    response_data2 = response2.json()
    print(f"Response: {json.dumps(response_data2, indent=2)}")
    
    # Verify response format
    assert "status" in response_data2, "Response missing 'status' field"
    assert response_data2["status"] == "success", f"Expected status 'success', got '{response_data2['status']}'"
    assert "project_id" in response_data2, "Response missing 'project_id' field"
    assert response_data2["project_id"] == project_id2, f"Expected project_id '{project_id2}', got '{response_data2['project_id']}'"
    
    print("✅ Test 2 passed: POST endpoint handles multiple projects correctly")
    
    # Test 3: GET to query by project_id
    print("\nTest 3: GET to query by project_id")
    response3 = requests.get(f"{BASE_URL}?project_id={project_id}")
    assert response3.status_code == 200, f"Expected status code 200, got {response3.status_code}"
    
    response_data3 = response3.json()
    print(f"Response: {json.dumps(response_data3, indent=2)}")
    
    # Verify response format
    assert isinstance(response_data3, list), "Response should be a list"
    assert len(response_data3) == 1, f"Expected 1 project, got {len(response_data3)}"
    assert response_data3[0]["project_id"] == project_id, f"Expected project_id '{project_id}', got '{response_data3[0]['project_id']}'"
    assert response_data3[0]["goal"] == payload1["goal"], f"Expected goal '{payload1['goal']}', got '{response_data3[0]['goal']}'"
    assert response_data3[0]["user_id"] == TEST_USER_ID, f"Expected user_id '{TEST_USER_ID}', got '{response_data3[0]['user_id']}'"
    
    print("✅ Test 3 passed: GET endpoint filters by project_id correctly")
    
    # Test 4: GET to query by user_id
    print("\nTest 4: GET to query by user_id")
    response4 = requests.get(f"{BASE_URL}?user_id={TEST_USER_ID}")
    assert response4.status_code == 200, f"Expected status code 200, got {response4.status_code}"
    
    response_data4 = response4.json()
    print(f"Response: {json.dumps(response_data4, indent=2)}")
    
    # Verify response format
    assert isinstance(response_data4, list), "Response should be a list"
    assert len(response_data4) == 2, f"Expected 2 projects, got {len(response_data4)}"
    
    print("✅ Test 4 passed: GET endpoint filters by user_id correctly")
    
    # Test 5: GET to query by tags
    print("\nTest 5: GET to query by tags")
    response5 = requests.get(f"{BASE_URL}?tags=journaling,vertical")
    assert response5.status_code == 200, f"Expected status code 200, got {response5.status_code}"
    
    response_data5 = response5.json()
    print(f"Response: {json.dumps(response_data5, indent=2)}")
    
    # Verify response format
    assert isinstance(response_data5, list), "Response should be a list"
    assert len(response_data5) == 1, f"Expected 1 project, got {len(response_data5)}"
    assert response_data5[0]["project_id"] == project_id, f"Expected project_id '{project_id}', got '{response_data5[0]['project_id']}'"
    
    print("✅ Test 5 passed: GET endpoint filters by tags correctly")
    
    # Test 6: Error handling with invalid payload
    print("\nTest 6: Error handling with invalid payload")
    invalid_payload = {
        "user_id": TEST_USER_ID,
        # Missing required fields
    }
    
    error_response = requests.post(BASE_URL, json=invalid_payload)
    assert error_response.status_code in [400, 422, 500], f"Expected error status code, got {error_response.status_code}"
    
    print("✅ Test 6 passed: Error handling works correctly")
    
    print("\n🎉 All tests passed! /projects endpoints are working correctly")

if __name__ == "__main__":
    test_projects_module()
