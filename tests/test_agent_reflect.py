"""
Tests for the agent_reflect module.

This module contains tests for the agent_reflect module, which provides
functionality for agents to reflect on the outcome of completed tasks.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the router from the agent_reflect module
from app.modules.agent_reflect import router, ReflectRequest, ReflectResponse

# Create a test client
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Mock the write_memory function
@pytest.fixture
def mock_write_memory():
    with patch("app.modules.agent_reflect.write_memory") as mock:
        # Configure the mock to return a memory with a memory_id
        mock.return_value = {"memory_id": "test-memory-id"}
        yield mock

# Test successful reflection with success outcome
def test_reflect_success(mock_write_memory):
    """Test that a successful reflection is properly processed and stored."""
    # Define the test request
    request_data = {
        "agent_id": "hal",
        "task_id": "task-8734",
        "task_summary": "Summarized all onboarding-related memories",
        "outcome": "success",
        "notes": "Task completed with minimal memory coverage, agent used memory_search and summarization"
    }
    
    # Send the request to the endpoint
    response = client.post("/reflect", json=request_data)
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Check that the response contains the expected fields
    response_data = response.json()
    assert response_data["status"] == "reflected"
    assert response_data["memory_id"] == "test-memory-id"
    assert "reflection" in response_data
    assert "HAL successfully completed the task" in response_data["reflection"]
    
    # Check that write_memory was called with the correct arguments
    mock_write_memory.assert_called_once()
    call_args = mock_write_memory.call_args[1]
    assert call_args["agent_id"] == "hal"
    assert call_args["type"] == "reflection"
    assert call_args["task_id"] == "task-8734"
    assert "success" in call_args["tags"]
    assert call_args["status"] == "success"

# Test successful reflection with failure outcome
def test_reflect_failure(mock_write_memory):
    """Test that a reflection with failure outcome is properly processed and stored."""
    # Define the test request
    request_data = {
        "agent_id": "hal",
        "task_id": "task-8735",
        "task_summary": "Failed to summarize onboarding-related memories",
        "outcome": "failure",
        "notes": "Task failed due to memory retrieval issues"
    }
    
    # Send the request to the endpoint
    response = client.post("/reflect", json=request_data)
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Check that the response contains the expected fields
    response_data = response.json()
    assert response_data["status"] == "reflected"
    assert response_data["memory_id"] == "test-memory-id"
    assert "reflection" in response_data
    assert "HAL encountered challenges with the task" in response_data["reflection"]
    
    # Check that write_memory was called with the correct arguments
    mock_write_memory.assert_called_once()
    call_args = mock_write_memory.call_args[1]
    assert call_args["agent_id"] == "hal"
    assert call_args["type"] == "reflection"
    assert call_args["task_id"] == "task-8735"
    assert "failure" in call_args["tags"]
    assert call_args["status"] == "failure"

# Test reflection with missing required fields
def test_reflect_missing_fields():
    """Test that a reflection with missing required fields returns an error."""
    # Define the test request with missing fields
    request_data = {
        "agent_id": "hal",
        # Missing task_id
        "task_summary": "Summarized all onboarding-related memories",
        "outcome": "success",
        "notes": "Task completed with minimal memory coverage"
    }
    
    # Send the request to the endpoint
    response = client.post("/reflect", json=request_data)
    
    # Check that the response is an error
    assert response.status_code == 422
    
    # Check that the error message mentions the missing field
    response_data = response.json()
    assert "task_id" in str(response_data)

# Test reflection with invalid outcome
def test_reflect_invalid_outcome():
    """Test that a reflection with an invalid outcome returns an error."""
    # Define the test request with an invalid outcome
    request_data = {
        "agent_id": "hal",
        "task_id": "task-8734",
        "task_summary": "Summarized all onboarding-related memories",
        "outcome": "invalid",  # Not "success" or "failure"
        "notes": "Task completed with minimal memory coverage"
    }
    
    # Send the request to the endpoint
    response = client.post("/reflect", json=request_data)
    
    # Check that the response is an error
    assert response.status_code == 422
    
    # Check that the error message mentions the invalid outcome
    response_data = response.json()
    assert "outcome" in str(response_data)

# Test reflection with project_id
def test_reflect_with_project_id(mock_write_memory):
    """Test that a reflection with a project_id is properly processed and stored."""
    # Define the test request with a project_id
    request_data = {
        "agent_id": "hal",
        "task_id": "task-8734",
        "task_summary": "Summarized all onboarding-related memories",
        "outcome": "success",
        "notes": "Task completed with minimal memory coverage",
        "project_id": "project-123"
    }
    
    # Send the request to the endpoint
    response = client.post("/reflect", json=request_data)
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Check that write_memory was called with the correct project_id
    mock_write_memory.assert_called_once()
    call_args = mock_write_memory.call_args[1]
    assert call_args["project_id"] == "project-123"
