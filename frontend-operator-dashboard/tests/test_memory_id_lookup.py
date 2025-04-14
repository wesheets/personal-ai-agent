import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid
import json
from datetime import datetime

# Import the router to test
from app.api.modules.memory import router, memory_store

# Create a test client
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Test data
test_memory_id = str(uuid.uuid4())
test_memory = {
    "memory_id": test_memory_id,
    "agent_id": "test-agent",
    "type": "test-memory",
    "content": "This is a test memory",
    "tags": ["test", "memory"],
    "timestamp": datetime.utcnow().isoformat(),
    "project_id": "test-project",
    "status": "completed",
    "task_type": "test"
}

@pytest.fixture
def mock_memory_store():
    """Fixture to mock the memory_store with test data"""
    with patch('app.api.modules.memory.memory_store', [test_memory]):
        yield

def test_read_memory_by_id(mock_memory_store):
    """Test reading a memory by its ID"""
    response = client.get(f"/read?memory_id={test_memory_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["memories"]) == 1
    assert data["memories"][0]["memory_id"] == test_memory_id

def test_read_memory_by_id_not_found(mock_memory_store):
    """Test reading a memory by an ID that doesn't exist"""
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/read?memory_id={non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert "not found" in data["message"]

def test_read_memory_with_other_filters(mock_memory_store):
    """Test that memory_id takes precedence over other filters"""
    response = client.get(f"/read?memory_id={test_memory_id}&agent_id=wrong-agent&type=wrong-type")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["memories"]) == 1
    assert data["memories"][0]["memory_id"] == test_memory_id

def test_write_and_read_memory_integration():
    """Integration test for writing a memory and then reading it by ID"""
    # Clear the memory store for this test
    memory_store.clear()
    
    # Write a new memory
    memory_data = {
        "agent_id": "integration-test-agent",
        "memory_type": "integration-test",
        "content": "This is an integration test memory",
        "tags": ["integration", "test"],
        "project_id": "integration-project",
        "status": "testing"
    }
    
    write_response = client.post("/write", json=memory_data)
    assert write_response.status_code == 200
    write_data = write_response.json()
    assert "memory_id" in write_data
    
    # Read the memory by ID
    memory_id = write_data["memory_id"]
    read_response = client.get(f"/read?memory_id={memory_id}")
    assert read_response.status_code == 200
    read_data = read_response.json()
    assert read_data["status"] == "ok"
    assert len(read_data["memories"]) == 1
    assert read_data["memories"][0]["memory_id"] == memory_id
    assert read_data["memories"][0]["agent_id"] == memory_data["agent_id"]
    assert read_data["memories"][0]["type"] == memory_data["memory_type"]
    assert read_data["memories"][0]["content"] == memory_data["content"]
