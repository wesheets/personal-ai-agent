import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/app/modules"
TEST_AGENT_ID = "test_agent"

def test_summarize_context_handling():
    """
    Test the /summarize endpoint with various context formats to ensure robust handling.
    Verifies:
    1. Context with dictionary items containing 'content' key
    2. Context with string items
    3. Context with mixed item types
    4. Empty context
    5. No context provided (fallback to filtered memories)
    """
    print("\n🧪 Testing /summarize endpoint context handling...")
    
    # Generate unique IDs for tracing
    task_id = str(uuid.uuid4())
    project_id = f"test_project_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    memory_trace_id = str(uuid.uuid4())
    
    # Test 1: Context with dictionary items containing 'content' key
    print("\nTest 1: Context with dictionary items containing 'content' key")
    payload1 = {
        "agent_id": TEST_AGENT_ID,
        "goal": "Test summary with dictionary context items",
        "task_id": task_id,
        "project_id": project_id,
        "memory_trace_id": memory_trace_id,
        "context": [
            {"content": "This is a test memory for summarization."},
            {"content": "The summary should include all key points from the context."}
        ]
    }
    
    response1 = requests.post(f"{BASE_URL}/summarize", json=payload1)
    assert response1.status_code == 200, f"Expected status code 200, got {response1.status_code}"
    print(f"✅ Test 1 passed: {response1.json()['status']}")
    
    # Test 2: Context with string items
    print("\nTest 2: Context with string items")
    payload2 = {
        "agent_id": TEST_AGENT_ID,
        "goal": "Test summary with string context items",
        "task_id": task_id,
        "project_id": project_id,
        "memory_trace_id": memory_trace_id,
        "context": [
            "This is a plain string item.",
            "Another plain string item for testing."
        ]
    }
    
    response2 = requests.post(f"{BASE_URL}/summarize", json=payload2)
    assert response2.status_code == 200, f"Expected status code 200, got {response2.status_code}"
    print(f"✅ Test 2 passed: {response2.json()['status']}")
    
    # Test 3: Context with mixed item types
    print("\nTest 3: Context with mixed item types")
    payload3 = {
        "agent_id": TEST_AGENT_ID,
        "goal": "Test summary with mixed context items",
        "task_id": task_id,
        "project_id": project_id,
        "memory_trace_id": memory_trace_id,
        "context": [
            {"content": "This is a dictionary with content key."},
            "This is a plain string item.",
            {"other_key": "This is a dictionary without content key."},
            123,  # A number
            None  # None value should be skipped
        ]
    }
    
    response3 = requests.post(f"{BASE_URL}/summarize", json=payload3)
    assert response3.status_code == 200, f"Expected status code 200, got {response3.status_code}"
    print(f"✅ Test 3 passed: {response3.json()['status']}")
    
    # Test 4: Empty context
    print("\nTest 4: Empty context")
    payload4 = {
        "agent_id": TEST_AGENT_ID,
        "goal": "Test summary with empty context",
        "task_id": task_id,
        "project_id": project_id,
        "memory_trace_id": memory_trace_id,
        "context": []
    }
    
    response4 = requests.post(f"{BASE_URL}/summarize", json=payload4)
    assert response4.status_code == 200, f"Expected status code 200, got {response4.status_code}"
    print(f"✅ Test 4 passed: {response4.json()['status']}")
    
    # Test 5: No context provided (fallback to filtered memories)
    print("\nTest 5: No context provided (fallback to filtered memories)")
    payload5 = {
        "agent_id": TEST_AGENT_ID,
        "goal": "Test summary without context",
        "task_id": task_id,
        "project_id": project_id,
        "memory_trace_id": memory_trace_id
    }
    
    response5 = requests.post(f"{BASE_URL}/summarize", json=payload5)
    assert response5.status_code == 200, f"Expected status code 200, got {response5.status_code}"
    print(f"✅ Test 5 passed: {response5.json()['status']}")
    
    print("\n🎉 All context handling tests passed! /summarize endpoint is robust against various context formats.")

if __name__ == "__main__":
    test_summarize_context_handling()
