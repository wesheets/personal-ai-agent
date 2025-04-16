"""
Test file for the orchestrator/present endpoint.

This module contains tests for the /orchestrator/present endpoint, which converts
stored project scopes into visual presentation slides with narration.
"""

import pytest
import json
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_orchestrator_present_endpoint_basic():
    """Test the basic functionality of the orchestrator/present endpoint."""
    # Create a test project_id
    project_id = f"test-proj-{str(uuid.uuid4())[:8]}"
    
    # Create a test request
    request_data = {
        "project_id": project_id
    }
    
    # Mock a project scope in memory store
    # This would normally be done by calling /orchestrator/scope
    # but for testing we'll mock it directly
    mock_project_scope(project_id)
    
    # Make the request
    response = client.post("/orchestrator/present", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the response structure
    assert "project_id" in data
    assert "slides" in data
    assert "markdown_script" in data
    assert "status" in data
    
    # Check that the project_id matches the request
    assert data["project_id"] == project_id
    
    # Check that slides is a list
    assert isinstance(data["slides"], list)
    
    # Check that markdown_script is a string
    assert isinstance(data["markdown_script"], str)
    
    # Check that status is "success"
    assert data["status"] == "success"
    
    # Check that each slide has the required fields
    for slide in data["slides"]:
        assert "title" in slide
        assert "content" in slide
        assert "narration_text" in slide

def test_orchestrator_present_endpoint_missing_scope():
    """Test the orchestrator/present endpoint with a missing project scope."""
    # Create a test project_id that doesn't exist
    project_id = f"nonexistent-proj-{str(uuid.uuid4())[:8]}"
    
    # Create a test request
    request_data = {
        "project_id": project_id
    }
    
    # Make the request
    response = client.post("/orchestrator/present", json=request_data)
    
    # Check the response
    assert response.status_code == 404
    
    # Parse the response
    data = response.json()
    
    # Check the response structure
    assert "status" in data
    assert "reason" in data
    
    # Check that status is "error"
    assert data["status"] == "error"
    
    # Check that reason mentions the project_id
    assert project_id in data["reason"]

def test_orchestrator_present_endpoint_slide_count():
    """Test that the orchestrator/present endpoint generates the correct number of slides."""
    # Create a test project_id
    project_id = f"test-proj-{str(uuid.uuid4())[:8]}"
    
    # Create a test request
    request_data = {
        "project_id": project_id
    }
    
    # Mock a project scope in memory store
    mock_project_scope(project_id)
    
    # Make the request
    response = client.post("/orchestrator/present", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that slides is a list with at least 5 slides
    # (Goal, Modules, Agents, Risks, Tasks)
    assert len(data["slides"]) >= 5

def test_orchestrator_present_endpoint_markdown_content():
    """Test that the orchestrator/present endpoint generates proper markdown content."""
    # Create a test project_id
    project_id = f"test-proj-{str(uuid.uuid4())[:8]}"
    
    # Create a test request
    request_data = {
        "project_id": project_id
    }
    
    # Mock a project scope in memory store
    mock_project_scope(project_id)
    
    # Make the request
    response = client.post("/orchestrator/present", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that markdown_script contains key sections
    markdown = data["markdown_script"]
    assert "# Promethios System Plan" in markdown
    assert "## Goal" in markdown
    assert "## Modules Required" in markdown
    assert "## Agents Involved" in markdown
    assert "## Known Risks" in markdown
    assert "## Execution Tasks" in markdown
    assert "## Summary" in markdown

def mock_project_scope(project_id: str):
    """
    Mock a project scope in the memory store for testing.
    
    Args:
        project_id: Project ID to use for the mock scope
    """
    import os
    import json
    from app.modules.memory_writer import write_memory
    
    # Create a mock project scope
    mock_scope = {
        "project_id": project_id,
        "goal": "Create a journaling application with reflection capabilities",
        "required_modules": ["write", "read", "reflect", "summarize"],
        "suggested_agents": [
            {
                "agent_name": "hal",
                "tools": ["reflect", "summarize"],
                "persona": "supportive, analytical"
            },
            {
                "agent_name": "ash",
                "tools": ["delegate", "execute"],
                "persona": "direct, action-oriented"
            }
        ],
        "execution_tasks": [
            "Create project container",
            "Register agents",
            "Train memory with project context",
            "Test summary and reflection loop",
            "Validate trace integrity"
        ],
        "known_risks": [
            "Loop runaway without cycle caps",
            "Missing agent capability validation",
            "Reflection without goal alignment",
            "Output returned without success check"
        ],
        "confidence_scores": {
            "hal": 0.92,
            "ash": 0.87
        },
        "project_dependencies": {
            "summarize": ["write", "reflect"],
            "delegate": ["read"]
        },
        "markdown_summary": "# Project Scope: " + project_id
    }
    
    # Write the mock scope to memory
    write_memory(
        agent_id="system",
        type="project_scope",
        content=json.dumps(mock_scope),
        tags=["project_scope", f"project:{project_id}"],
        project_id=project_id,
        status="active",
        task_type="scope"
    )

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-xvs", __file__])
