"""
Test script for the project-scoped /summarize endpoint.

This script tests the functionality of the project-scoped /summarize endpoint,
including input validation, memory filtering, summary generation, and optional
memory storage.
"""

import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from app.modules.memory_writer import memory_store, write_memory

# Create a test client
client = TestClient(app)

# Test data
TEST_PROJECT_ID = "test-project-123"
TEST_AGENT_ID = "test-agent-456"

def setup_test_memories():
    """Set up test memories for the project-scoped summarize endpoint tests."""
    # Clear existing memories
    memory_store.clear()
    
    # Create test memories with different project_ids and agent_ids
    write_memory(
        agent_id=TEST_AGENT_ID,
        type="observation",
        content="This is a test observation for project 123.",
        tags=["test", "observation"],
        project_id=TEST_PROJECT_ID
    )
    
    write_memory(
        agent_id=TEST_AGENT_ID,
        type="reflection",
        content="This is a test reflection for project 123.",
        tags=["test", "reflection"],
        project_id=TEST_PROJECT_ID
    )
    
    write_memory(
        agent_id="other-agent",
        type="observation",
        content="This is a test observation from another agent for project 123.",
        tags=["test", "observation"],
        project_id=TEST_PROJECT_ID
    )
    
    write_memory(
        agent_id=TEST_AGENT_ID,
        type="observation",
        content="This is a test observation for another project.",
        tags=["test", "observation"],
        project_id="other-project"
    )
    
    # Return the number of memories created for the test project
    return len([m for m in memory_store if m["project_id"] == TEST_PROJECT_ID])

def test_project_summarize_endpoint():
    """Test the project-scoped /summarize endpoint with valid input."""
    # Set up test memories
    test_memory_count = setup_test_memories()
    
    # Create test request
    request_data = {
        "project_id": TEST_PROJECT_ID,
        "store_summary": False
    }
    
    # Send request to the endpoint
    response = client.post("/app/modules/project-summarize", json=request_data)
    
    # Check response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["project_id"] == TEST_PROJECT_ID
    assert response_data["memory_count"] == test_memory_count
    assert "summary" in response_data
    assert len(response_data["summary"]) > 0

def test_project_summarize_with_agent_filter():
    """Test the project-scoped /summarize endpoint with agent_id filter."""
    # Set up test memories
    setup_test_memories()
    
    # Create test request with agent_id filter
    request_data = {
        "project_id": TEST_PROJECT_ID,
        "agent_id": TEST_AGENT_ID,
        "store_summary": False
    }
    
    # Send request to the endpoint
    response = client.post("/app/modules/project-summarize", json=request_data)
    
    # Check response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["project_id"] == TEST_PROJECT_ID
    
    # Count memories that match both project_id and agent_id
    expected_count = len([
        m for m in memory_store 
        if m["project_id"] == TEST_PROJECT_ID and m["agent_id"] == TEST_AGENT_ID
    ])
    assert response_data["memory_count"] == expected_count

def test_project_summarize_with_memory_type_filter():
    """Test the project-scoped /summarize endpoint with memory_type filter."""
    # Set up test memories
    setup_test_memories()
    
    # Create test request with memory_type filter
    request_data = {
        "project_id": TEST_PROJECT_ID,
        "memory_type": "observation",
        "store_summary": False
    }
    
    # Send request to the endpoint
    response = client.post("/app/modules/project-summarize", json=request_data)
    
    # Check response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["project_id"] == TEST_PROJECT_ID
    
    # Count memories that match both project_id and memory_type
    expected_count = len([
        m for m in memory_store 
        if m["project_id"] == TEST_PROJECT_ID and m["type"] == "observation"
    ])
    assert response_data["memory_count"] == expected_count

def test_project_summarize_with_store_summary():
    """Test the project-scoped /summarize endpoint with store_summary=True."""
    # Set up test memories
    setup_test_memories()
    
    # Count project_summary memories before the test
    initial_summary_count = len([
        m for m in memory_store 
        if m["type"] == "project_summary" and m["project_id"] == TEST_PROJECT_ID
    ])
    
    # Create test request with store_summary=True
    request_data = {
        "project_id": TEST_PROJECT_ID,
        "store_summary": True
    }
    
    # Send request to the endpoint
    response = client.post("/app/modules/project-summarize", json=request_data)
    
    # Check response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["project_id"] == TEST_PROJECT_ID
    assert "memory_id" in response_data
    
    # Count project_summary memories after the test
    final_summary_count = len([
        m for m in memory_store 
        if m["type"] == "project_summary" and m["project_id"] == TEST_PROJECT_ID
    ])
    
    # Verify that a new project_summary memory was created
    assert final_summary_count == initial_summary_count + 1
    
    # Verify the content of the new project_summary memory
    summary_memories = [
        m for m in memory_store 
        if m["type"] == "project_summary" and m["project_id"] == TEST_PROJECT_ID
    ]
    assert len(summary_memories) > 0
    assert summary_memories[-1]["memory_id"] == response_data["memory_id"]
    assert summary_memories[-1]["content"] == response_data["summary"]

def test_project_summarize_with_invalid_project_id():
    """Test the project-scoped /summarize endpoint with an invalid project_id."""
    # Set up test memories
    setup_test_memories()
    
    # Create test request with invalid project_id
    request_data = {
        "project_id": "non-existent-project",
        "store_summary": False
    }
    
    # Send request to the endpoint
    response = client.post("/app/modules/project-summarize", json=request_data)
    
    # Check response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["project_id"] == "non-existent-project"
    assert response_data["memory_count"] == 0
    assert "No relevant memories found" in response_data["summary"]

def test_project_summarize_with_missing_project_id():
    """Test the project-scoped /summarize endpoint with missing project_id."""
    # Set up test memories
    setup_test_memories()
    
    # Create test request without project_id
    request_data = {
        "store_summary": False
    }
    
    # Send request to the endpoint
    response = client.post("/app/modules/project-summarize", json=request_data)
    
    # Check response
    assert response.status_code == 422  # Validation error
