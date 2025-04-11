import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import json

# Import the router to test
from app.modules.orchestrator_build import router, find_best_agent_for_task, delegate_task_to_agent

# Create a test client
client = TestClient(router)

# Mock the write_memory function
@pytest.fixture
def mock_write_memory():
    with patch("app.modules.orchestrator_build.write_memory") as mock:
        mock.return_value = {"memory_id": "test-memory-id"}
        yield mock

# Mock the verify_agent_for_task function
@pytest.fixture
def mock_verify_agent_for_task():
    with patch("app.modules.orchestrator_build.verify_agent_for_task") as mock:
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.qualified = True
        mock_response.confidence_score = 0.8
        mock_response.agent_id = "hal"
        mock_response.justification = "Agent is fully qualified with all required skills."
        mock_response.suggested_agents = ["ash"]
        mock_response.dict.return_value = {
            "qualified": True,
            "confidence_score": 0.8,
            "agent_id": "hal",
            "justification": "Agent is fully qualified with all required skills.",
            "suggested_agents": ["ash"]
        }
        
        async_mock = AsyncMock(return_value=mock_response)
        mock.side_effect = async_mock
        yield mock

# Mock the delegate_task_internal function
@pytest.fixture
def mock_delegate_task_internal():
    with patch("app.modules.orchestrator_build.delegate_task_internal") as mock:
        mock_response = {
            "status": "ok",
            "delegation_id": "test-delegation-id",
            "to_agent": "hal",
            "task_id": "task-001-delegated",
            "delegation_depth": 1,
            "result_summary": "Agent accepted task.",
            "feedback_required": False
        }
        async_mock = AsyncMock(return_value=mock_response)
        mock.side_effect = async_mock
        yield mock

# Test successful execution of a task plan
@pytest.mark.asyncio
async def test_execute_task_plan_success(mock_write_memory, mock_verify_agent_for_task, mock_delegate_task_internal):
    # Test data
    test_data = {
        "plan_id": "plan-87234",
        "tasks": [
            {
                "task_id": "task-001",
                "description": "Summarize project onboarding logs",
                "required_skills": ["summarization", "memory_search"]
            },
            {
                "task_id": "task-002",
                "description": "Reflect on the user's recent actions",
                "required_skills": ["reflection", "context_analysis"]
            }
        ],
        "project_id": "project-123"
    }
    
    # Make the request
    response = await client.post("/build", json=test_data)
    
    # Check response
    assert response.status_code == 200
    assert response.json()["status"] == "executing"
    assert len(response.json()["delegated_tasks"]) == 2
    assert response.json()["memory_id"] == "test-memory-id"
    
    # Verify function calls
    assert mock_verify_agent_for_task.call_count == 2
    assert mock_delegate_task_internal.call_count == 2
    mock_write_memory.assert_called_once()

# Test execution with unqualified agent
@pytest.mark.asyncio
async def test_execute_task_plan_unqualified_agent(mock_write_memory, mock_verify_agent_for_task, mock_delegate_task_internal):
    # Configure mock to return unqualified for the second task
    mock_responses = [
        MagicMock(
            qualified=True,
            confidence_score=0.8,
            agent_id="hal",
            justification="Agent is fully qualified with all required skills.",
            suggested_agents=["ash"],
            dict=lambda: {
                "qualified": True,
                "confidence_score": 0.8,
                "agent_id": "hal",
                "justification": "Agent is fully qualified with all required skills.",
                "suggested_agents": ["ash"]
            }
        ),
        MagicMock(
            qualified=False,
            confidence_score=0.2,
            agent_id="hal",
            justification="Agent lacks required skills: context_analysis.",
            suggested_agents=None,
            dict=lambda: {
                "qualified": False,
                "confidence_score": 0.2,
                "agent_id": "hal",
                "justification": "Agent lacks required skills: context_analysis.",
                "suggested_agents": None
            }
        )
    ]
    
    mock_verify_agent_for_task.side_effect = AsyncMock(side_effect=mock_responses)
    
    # Test data
    test_data = {
        "plan_id": "plan-87234",
        "tasks": [
            {
                "task_id": "task-001",
                "description": "Summarize project onboarding logs",
                "required_skills": ["summarization", "memory_search"]
            },
            {
                "task_id": "task-002",
                "description": "Reflect on the user's recent actions",
                "required_skills": ["reflection", "context_analysis"]
            }
        ],
        "project_id": "project-123"
    }
    
    # Make the request
    response = await client.post("/build", json=test_data)
    
    # Check response
    assert response.status_code == 200
    assert response.json()["status"] == "executing"
    assert len(response.json()["delegated_tasks"]) == 1  # Only one task should be delegated
    
    # Verify function calls
    assert mock_verify_agent_for_task.call_count == 2
    assert mock_delegate_task_internal.call_count == 1  # Only one delegation should occur
    mock_write_memory.assert_called_once()

# Test execution with delegation failure
@pytest.mark.asyncio
async def test_execute_task_plan_delegation_failure(mock_write_memory, mock_verify_agent_for_task, mock_delegate_task_internal):
    # Configure mock to return error for delegation
    mock_delegate_task_internal.side_effect = AsyncMock(return_value={
        "status": "error",
        "log": "Agent not available"
    })
    
    # Test data
    test_data = {
        "plan_id": "plan-87234",
        "tasks": [
            {
                "task_id": "task-001",
                "description": "Summarize project onboarding logs",
                "required_skills": ["summarization", "memory_search"]
            }
        ],
        "project_id": "project-123"
    }
    
    # Make the request
    response = await client.post("/build", json=test_data)
    
    # Check response
    assert response.status_code == 200
    assert response.json()["status"] == "failed"  # Should be failed since no tasks were delegated
    assert len(response.json()["delegated_tasks"]) == 0
    
    # Verify function calls
    assert mock_verify_agent_for_task.call_count == 1
    assert mock_delegate_task_internal.call_count == 1
    mock_write_memory.assert_called_once()

# Test find_best_agent_for_task function
@pytest.mark.asyncio
async def test_find_best_agent_for_task(mock_verify_agent_for_task):
    # Configure mock to return different responses for different agents
    hal_response = MagicMock(
        qualified=True,
        confidence_score=0.6,  # Lower confidence
        agent_id="hal",
        justification="Agent is qualified but with lower confidence.",
        suggested_agents=["ash"],
        dict=lambda: {
            "qualified": True,
            "confidence_score": 0.6,
            "agent_id": "hal",
            "justification": "Agent is qualified but with lower confidence.",
            "suggested_agents": ["ash"]
        }
    )
    
    ash_response = MagicMock(
        qualified=True,
        confidence_score=0.9,  # Higher confidence
        agent_id="ash",
        justification="Agent is fully qualified with high confidence.",
        suggested_agents=None,
        dict=lambda: {
            "qualified": True,
            "confidence_score": 0.9,
            "agent_id": "ash",
            "justification": "Agent is fully qualified with high confidence.",
            "suggested_agents": None
        }
    )
    
    mock_verify_agent_for_task.side_effect = AsyncMock(side_effect=[hal_response, ash_response])
    
    # Test task
    test_task = {
        "task_id": "task-001",
        "description": "Execute complex protocol",
        "required_skills": ["execute", "protocol"]
    }
    
    # Call the function
    result = await find_best_agent_for_task(test_task)
    
    # Check result - should choose ASH due to higher confidence
    assert result["agent_id"] == "ash"
    assert result["confidence_score"] == 0.9
    assert result["qualified"] == True
    
    # Verify function calls
    assert mock_verify_agent_for_task.call_count == 2

# Test delegate_task_to_agent function
@pytest.mark.asyncio
async def test_delegate_task_to_agent(mock_delegate_task_internal):
    # Call the function
    result = await delegate_task_to_agent(
        from_agent="orchestrator",
        to_agent="hal",
        task_id="task-001",
        description="Test task",
        project_id="project-123"
    )
    
    # Check result
    assert result["status"] == "ok"
    assert result["to_agent"] == "hal"
    assert result["task_id"] == "task-001-delegated"
    
    # Verify function calls
    mock_delegate_task_internal.assert_called_once_with(
        from_agent="orchestrator",
        to_agent="hal",
        task_id="task-001",
        notes="Test task",
        project_id="project-123"
    )

# Test error handling in delegate_task_to_agent
@pytest.mark.asyncio
async def test_delegate_task_to_agent_error(mock_delegate_task_internal):
    # Configure mock to raise exception
    mock_delegate_task_internal.side_effect = AsyncMock(side_effect=Exception("Test error"))
    
    # Call the function
    result = await delegate_task_to_agent(
        from_agent="orchestrator",
        to_agent="hal",
        task_id="task-001",
        description="Test task",
        project_id="project-123"
    )
    
    # Check result
    assert result["status"] == "error"
    assert "Test error" in result["log"]
