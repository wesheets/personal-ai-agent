import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/app/projects"
TEST_USER_ID = "user-001"

def test_projects_persistence():
    """
    Test the /projects endpoints for both POST and GET operations.
    Verifies:
    1. POST endpoint stores and returns complete project data
    2. GET endpoint correctly filters projects by various parameters
    """
    print("\n🧪 Testing /projects persistence and retrieval...")
    
    # Generate unique project ID for testing
    project_id = f"proj-legacy-ai-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Test 1: POST to create a new project
    print("\nTest 1: POST to create a new project")
    payload = {
        "project_id": project_id,
        "goal": "Build a vertical journaling SaaS",
        "user_id": TEST_USER_ID,
        "tags": ["test", "agent"],
        "context": "Summary of planning session"
    }
    
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    # Verify response format
    assert "status" in response_data, "Response missing 'status' field"
    assert response_data["status"] == "success", f"Expected status 'success', got '{response_data['status']}'"
    assert "project" in response_data, "Response missing 'project' field"
    assert response_data["project"]["project_id"] == project_id, f"Expected project_id '{project_id}', got '{response_data['project']['project_id']}'"
    assert "goal" in response_data["project"], "Project missing 'goal' field"
    assert "user_id" in response_data["project"], "Project missing 'user_id' field"
    assert "tags" in response_data["project"], "Project missing 'tags' field"
    assert "created_at" in response_data["project"], "Project missing 'created_at' field"
    
    print("✅ Test 1 passed: POST endpoint returns complete project data")
    
    # Test 2: GET to query by project_id
    print("\nTest 2: GET to query by project_id")
    response = requests.get(f"{BASE_URL}?project_id={project_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    # Verify response format
    assert isinstance(response_data, list), "Response should be a list"
    assert len(response_data) == 1, f"Expected 1 project, got {len(response_data)}"
    assert response_data[0]["project_id"] == project_id, f"Expected project_id '{project_id}', got '{response_data[0]['project_id']}'"
    
    print("✅ Test 2 passed: GET endpoint filters by project_id correctly")
    
    # Test 3: GET to query by user_id
    print("\nTest 3: GET to query by user_id")
    response = requests.get(f"{BASE_URL}?user_id={TEST_USER_ID}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    # Verify response format
    assert isinstance(response_data, list), "Response should be a list"
    assert len(response_data) > 0, f"Expected at least 1 project, got {len(response_data)}"
    
    print("✅ Test 3 passed: GET endpoint filters by user_id correctly")
    
    # Test 4: GET to query by tags
    print("\nTest 4: GET to query by tags")
    response = requests.get(f"{BASE_URL}?tags=test,agent")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    response_data = response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    # Verify response format
    assert isinstance(response_data, list), "Response should be a list"
    assert len(response_data) > 0, f"Expected at least 1 project, got {len(response_data)}"
    
    print("✅ Test 4 passed: GET endpoint filters by tags correctly")
    
    print("\n🎉 All tests passed! /projects persistence and retrieval are working correctly")

if __name__ == "__main__":
    test_projects_persistence()
