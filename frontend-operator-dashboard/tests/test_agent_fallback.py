"""
Tests for the agent_fallback module.

This module contains tests for the agent_fallback module, which provides
functionality for agents to reroute tasks they cannot perform.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import json
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the router from the agent_fallback module
from app.modules.agent_fallback import router, FallbackRequest, FallbackResponse

# Create a test client
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Mock the write_memory function
@pytest.fixture
def mock_write_memory():
    with patch("app.modules.agent_fallback.write_memory") as mock:
        # Configure the mock to return a memory with a memory_id
        mock.return_value = {"memory_id": "test-memory-id"}
        yield mock

# Mock the get_agent_info function
@pytest.fixture
def mock_get_agent_info():
    with patch("app.modules.agent_fallback.get_agent_info") as mock:
        # Configure the mock to return agent info
        mock.return_value = {"name": "Test Agent", "skills": ["analyze", "summarize"]}
        yield mock

# Mock the delegate_task function
@pytest.fixture
def mock_delegate_task():
    with patch("app.modules.agent_fallback.delegate_task") as mock:
        # Configure the mock to return a successful delegation response
        mock_coro = AsyncMock()
        mock_coro.return_value = {
            "status": "ok",
            "delegation_id": "test-delegation-id",
            "to_agent": "ash",
            "task_id": "task-4558-delegated"
        }
        mock.return_value = mock_coro()
        yield mock

# Test successful fallback with missing_skills reason
def test_fallback_missing_skills(mock_write_memory, mock_get_agent_info, mock_delegate_task):
    """Test that a fallback due to missing skills is properly processed."""
    # Define the test request
    request_data = {
        "agent_id": "hal",
        "task_id": "task-4558",
        "reason": "missing_skills",
        "suggested_agent": "ash",
        "notes": "Agent HAL does not have summarization. Rerouting task to ASH."
    }
    
    # Send the request to the endpoint
    response = client.post("/fallback", json=request_data)
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Check that the response contains the expected fields
    response_data = response.json()
    assert response_data["status"] == "rerouted"
    assert response_data["new_agent"] == "ash"
    assert response_data["delegation_task_id"] == "task-4558-delegated"
    assert response_data["memory_id"] == "test-memory-id"
    
    # Check that write_memory was called with the correct arguments
    mock_write_memory.assert_called_once()
    call_args = mock_write_memory.call_args[1]
    assert call_args["agent_id"] == "hal"
    assert call_args["type"] == "fallback"
    assert call_args["task_id"] == "task-4558"
    assert "fallback" in call_args["tags"]
    assert "reason:missing_skills" in call_args["tags"]
    assert call_args["status"] == "rerouted"
    
    # Check that delegate_task was called with the correct arguments
    mock_delegate_task.assert_called_once()

# Test successful fallback with failed_task reason
def test_fallback_failed_task(mock_write_memory, mock_get_agent_info, mock_delegate_task):
    """Test that a fallback due to a failed task is properly processed."""
    # Define the test request
    request_data = {
        "agent_id": "hal",
        "task_id": "task-4559",
        "reason": "failed_task",
        "suggested_agent": "ash",
        "notes": "Agent HAL failed to complete the task. Rerouting to ASH."
    }
    
    # Send the request to the endpoint
    response = client.post("/fallback", json=request_data)
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Check that the response contains the expected fields
    response_data = response.json()
    assert response_data["status"] == "rerouted"
    assert response_data["new_agent"] == "ash"
    assert response_data["delegation_task_id"] == "task-4559-delegated"
    assert response_data["memory_id"] == "test-memory-id"
    
    # Check that write_memory was called with the correct arguments
    mock_write_memory.assert_called_once()
    call_args = mock_write_memory.call_args[1]
    assert call_args["agent_id"] == "hal"
    assert call_args["type"] == "fallback"
    assert call_args["task_id"] == "task-4559"
    assert "fallback" in call_args["tags"]
    assert "reason:failed_task" in call_args["tags"]
    assert call_args["status"] == "rerouted"

# Test fallback with invalid agent
def test_fallback_invalid_agent(mock_write_memory, mock_get_agent_info):
    """Test that a fallback with an invalid agent returns an error."""
    # Configure the mock to raise an exception for invalid agent
    mock_get_agent_info.side_effect = lambda agent_id: (
        {"name": "Test Agent", "skills": ["analyze", "summarize"]} if agent_id == "hal"
        else pytest.raises(Exception(f"Agent with ID '{agent_id}' not found"))
    )
    
    # Define the test request with an invalid agent
    request_data = {
        "agent_id": "hal",
        "task_id": "task-4558",
        "reason": "missing_skills",
        "suggested_agent": "invalid-agent",
        "notes": "Agent HAL does not have summarization. Rerouting task to invalid agent."
    }
    
    # Send the request to the endpoint
    response = client.post("/fallback", json=request_data)
    
    # Check that the response is an error
    assert response.status_code == 500
    
    # Check that write_memory was not called
    mock_write_memory.assert_not_called()

# Test fallback with missing required fields
def test_fallback_missing_fields():
    """Test that a fallback with missing required fields returns an error."""
    # Define the test request with missing fields
    request_data = {
        "agent_id": "hal",
        # Missing task_id
        "reason": "missing_skills",
        "suggested_agent": "ash",
        "notes": "Agent HAL does not have summarization. Rerouting task to ASH."
    }
    
    # Send the request to the endpoint
    response = client.post("/fallback", json=request_data)
    
    # Check that the response is an error
    assert response.status_code == 422
    
    # Check that the error message mentions the missing field
    response_data = response.json()
    assert "task_id" in str(response_data)

# Test fallback with invalid reason
def test_fallback_invalid_reason(mock_get_agent_info):
    """Test that a fallback with an invalid reason returns an error."""
    # Define the test request with an invalid reason
    request_data = {
        "agent_id": "hal",
        "task_id": "task-4558",
        "reason": "invalid_reason",  # Not one of the valid reasons
        "suggested_agent": "ash",
        "notes": "Agent HAL does not have summarization. Rerouting task to ASH."
    }
    
    # Send the request to the endpoint
    response = client.post("/fallback", json=request_data)
    
    # Check that the response is an error
    assert response.status_code == 422
    
    # Check that the error message mentions the invalid reason
    response_data = response.json()
    assert "reason" in str(response_data)

# Test fallback with delegation failure
def test_fallback_delegation_failure(mock_write_memory, mock_get_agent_info, mock_delegate_task):
    """Test that a fallback with a delegation failure is properly handled."""
    # Configure the mock to raise an exception for delegation failure
    mock_delegate_task.side_effect = Exception("Delegation failed")
    
    # Define the test request
    request_data = {
        "agent_id": "hal",
        "task_id": "task-4558",
        "reason": "missing_skills",
        "suggested_agent": "ash",
        "notes": "Agent HAL does not have summarization. Rerouting task to ASH."
    }
    
    # Send the request to the endpoint
    response = client.post("/fallback", json=request_data)
    
    # Check that the response is an error
    assert response.status_code == 500
    
    # Check that write_memory was called twice (once for the initial fallback, once for the error)
    assert mock_write_memory.call_count == 2
    
    # Check that the second call to write_memory was for the error
    error_call_args = mock_write_memory.call_args_list[1][1]
    assert error_call_args["type"] == "fallback_error"
    assert "error" in error_call_args["tags"]
