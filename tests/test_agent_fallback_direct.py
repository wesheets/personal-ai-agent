import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import json

# Import the router to test
from app.modules.agent_fallback import router, delegate_task_internal

# Create a test client
client = TestClient(router)

# Mock the write_memory function
@pytest.fixture
def mock_write_memory():
    with patch("app.modules.agent_fallback.write_memory") as mock:
        mock.return_value = {"memory_id": "test-memory-id"}
        yield mock

# Mock the get_agent_info function
@pytest.fixture
def mock_get_agent_info():
    with patch("app.modules.agent_fallback.get_agent_info") as mock:
        mock.return_value = {"id": "test-agent", "name": "Test Agent"}
        yield mock

# Mock the delegate_task function
@pytest.fixture
def mock_delegate_task():
    with patch("app.modules.agent_fallback.delegate_task") as mock:
        mock_response = {
            "status": "ok",
            "delegation_id": "test-delegation-id",
            "to_agent": "ash",
            "task_id": "task-123-delegated",
            "delegation_depth": 1,
            "result_summary": "Agent accepted task.",
            "feedback_required": False
        }
        async_mock = AsyncMock(return_value=mock_response)
        mock.side_effect = async_mock
        yield mock

# Test successful fallback
@pytest.mark.asyncio
async def test_successful_fallback(mock_write_memory, mock_get_agent_info, mock_delegate_task):
    # Test data
    test_data = {
        "agent_id": "hal",
        "task_id": "task-123",
        "reason": "missing_skills",
        "suggested_agent": "ash",
        "notes": "Agent HAL does not have summarization. Rerouting task to ASH.",
        "project_id": "project-456"
    }
    
    # Mock the delegate_task_internal function
    with patch("app.modules.agent_fallback.delegate_task_internal", new_callable=AsyncMock) as mock_delegate_internal:
        mock_delegate_internal.return_value = {
            "status": "ok",
            "delegation_id": "test-delegation-id",
            "to_agent": "ash",
            "task_id": "task-123-delegated",
            "delegation_depth": 1,
            "result_summary": "Agent accepted task.",
            "feedback_required": False
        }
        
        # Make the request
        response = await client.post("/fallback", json=test_data)
        
        # Check response
        assert response.status_code == 200
        assert response.json() == {
            "status": "rerouted",
            "new_agent": "ash",
            "delegation_task_id": "task-123-delegated",
            "memory_id": "test-memory-id"
        }
        
        # Verify function calls
        mock_get_agent_info.assert_any_call("hal")
        mock_get_agent_info.assert_any_call("ash")
        mock_write_memory.assert_called()
        mock_delegate_internal.assert_called_once_with(
            from_agent="hal",
            to_agent="ash",
            task_id="task-123-delegated",
            notes="Agent HAL does not have summarization. Rerouting task to ASH.",
            project_id="project-456"
        )

# Test fallback with invalid agent
@pytest.mark.asyncio
async def test_fallback_invalid_agent(mock_write_memory):
    # Test data
    test_data = {
        "agent_id": "hal",
        "task_id": "task-123",
        "reason": "missing_skills",
        "suggested_agent": "invalid-agent",
        "notes": "Agent HAL does not have summarization. Rerouting task to invalid agent.",
        "project_id": "project-456"
    }
    
    # Mock get_agent_info to raise exception for invalid agent
    with patch("app.modules.agent_fallback.get_agent_info") as mock_get_agent_info:
        def side_effect(agent_id):
            if agent_id == "invalid-agent":
                raise HTTPException(status_code=404, detail=f"Agent with ID 'invalid-agent' not found")
            return {"id": agent_id, "name": "Test Agent"}
        
        mock_get_agent_info.side_effect = side_effect
        
        # Make the request
        response = await client.post("/fallback", json=test_data)
        
        # Check response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

# Test fallback with delegation failure
@pytest.mark.asyncio
async def test_fallback_delegation_failure(mock_write_memory, mock_get_agent_info):
    # Test data
    test_data = {
        "agent_id": "hal",
        "task_id": "task-123",
        "reason": "missing_skills",
        "suggested_agent": "ash",
        "notes": "Agent HAL does not have summarization. Rerouting task to ASH.",
        "project_id": "project-456"
    }
    
    # Mock delegate_task_internal to raise exception
    with patch("app.modules.agent_fallback.delegate_task_internal", new_callable=AsyncMock) as mock_delegate_internal:
        mock_delegate_internal.side_effect = HTTPException(status_code=500, detail="Delegation failed: Test error")
        
        # Make the request
        response = await client.post("/fallback", json=test_data)
        
        # Check response
        assert response.status_code == 500
        assert "Delegation failed" in response.json()["detail"]
        
        # Verify memory was updated with error
        mock_write_memory.assert_called_with(
            agent_id="hal",
            type="fallback_error",
            content=f"Failed to reroute task task-123 to ash: Delegation failed: Test error",
            tags=["fallback", "error", "reason:missing_skills"],
            project_id="project-456",
            status="error",
            task_id="task-123"
        )

# Test direct function call to delegate_task_internal
@pytest.mark.asyncio
async def test_delegate_task_internal(mock_delegate_task):
    # Call the function directly
    result = await delegate_task_internal(
        from_agent="hal",
        to_agent="ash",
        task_id="task-123",
        notes="Test delegation",
        project_id="project-456"
    )
    
    # Verify result
    assert result["status"] == "ok"
    assert result["to_agent"] == "ash"
    
    # Verify delegate_task was called with correct parameters
    request_arg = mock_delegate_task.call_args[0][0]
    request_json = await request_arg.json()
    
    assert request_json["from_agent"] == "hal"
    assert request_json["to_agent"] == "ash"
    assert request_json["task_id"] == "task-123"
    assert request_json["task"] == "Test delegation"
    assert request_json["project_id"] == "project-456"
    assert request_json["delegation_depth"] == 0
