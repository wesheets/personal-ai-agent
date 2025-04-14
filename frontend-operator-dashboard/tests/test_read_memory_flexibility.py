"""
Test script for flexible memory reading functionality.

This script tests the updated /read endpoint that makes agent_id optional
and ensures project_id, memory_type, and agent_id can be used independently
or together for flexible memory retrieval.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.modules.memory_writer import write_memory, memory_store

client = TestClient(app)

def setup_module():
    """Set up test environment before running tests."""
    # Clear memory store
    memory_store.clear()
    
    # Create test memories for different agents and projects
    write_memory(
        agent_id="hal-agent",
        type="observation",
        content="HAL observation for project A",
        tags=["test", "project-a"],
        project_id="project-a"
    )
    
    write_memory(
        agent_id="hal-agent",
        type="decision",
        content="HAL decision for project B",
        tags=["test", "project-b"],
        project_id="project-b"
    )
    
    write_memory(
        agent_id="ash-agent",
        type="observation",
        content="ASH observation for project A",
        tags=["test", "project-a"],
        project_id="project-a"
    )
    
    write_memory(
        agent_id="ash-agent",
        type="analysis",
        content="ASH analysis for project B",
        tags=["test", "project-b"],
        project_id="project-b"
    )
    
    write_memory(
        agent_id="lifetree-agent",
        type="observation",
        content="Lifetree observation with no project",
        tags=["test", "no-project"]
    )

def test_read_by_just_project_id():
    """Test reading memories filtered by just project_id."""
    response = client.get("/app/modules/read?project_id=project-a")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert len(data["memories"]) == 2
    
    # Verify both memories are from project-a
    for memory in data["memories"]:
        assert memory["project_id"] == "project-a"
    
    # Verify memories from both agents are included
    agent_ids = [memory["agent_id"] for memory in data["memories"]]
    assert "hal-agent" in agent_ids
    assert "ash-agent" in agent_ids

def test_read_by_project_id_and_agent_id():
    """Test reading memories filtered by both project_id and agent_id."""
    response = client.get("/app/modules/read?project_id=project-a&agent_id=hal-agent")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert len(data["memories"]) == 1
    
    # Verify the memory is from project-a and hal-agent
    memory = data["memories"][0]
    assert memory["project_id"] == "project-a"
    assert memory["agent_id"] == "hal-agent"
    assert memory["content"] == "HAL observation for project A"

def test_read_by_just_agent_id():
    """Test reading memories filtered by just agent_id."""
    response = client.get("/app/modules/read?agent_id=ash-agent")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert len(data["memories"]) == 2
    
    # Verify both memories are from ash-agent
    for memory in data["memories"]:
        assert memory["agent_id"] == "ash-agent"
    
    # Verify memories from both projects are included
    project_ids = [memory["project_id"] for memory in data["memories"]]
    assert "project-a" in project_ids
    assert "project-b" in project_ids

def test_read_all_memory():
    """Test reading all memories with no filters."""
    response = client.get("/app/modules/read")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert len(data["memories"]) == 5  # All test memories
    
    # Verify memories from all agents are included
    agent_ids = set(memory["agent_id"] for memory in data["memories"])
    assert agent_ids == {"hal-agent", "ash-agent", "lifetree-agent"}
    
    # Verify memories from all projects are included
    project_ids = set(memory.get("project_id") for memory in data["memories"])
    assert project_ids == {"project-a", "project-b", None}

def test_read_by_memory_type():
    """Test reading memories filtered by memory type."""
    response = client.get("/app/modules/read?type=observation")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert len(data["memories"]) == 3  # All observation memories
    
    # Verify all memories are of type observation
    for memory in data["memories"]:
        assert memory["type"] == "observation"
    
    # Verify memories from different agents are included
    agent_ids = set(memory["agent_id"] for memory in data["memories"])
    assert len(agent_ids) == 3

def test_read_by_memory_type_and_project_id():
    """Test reading memories filtered by both memory type and project_id."""
    response = client.get("/app/modules/read?type=observation&project_id=project-a")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert len(data["memories"]) == 2  # Observation memories from project-a
    
    # Verify all memories are of type observation and from project-a
    for memory in data["memories"]:
        assert memory["type"] == "observation"
        assert memory["project_id"] == "project-a"

def test_read_with_limit():
    """Test reading memories with a limit applied."""
    response = client.get("/app/modules/read?limit=2")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert len(data["memories"]) == 2  # Limited to 2 memories

def test_read_with_tag_filter():
    """Test reading memories filtered by tag."""
    response = client.get("/app/modules/read?tag=no-project")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert len(data["memories"]) == 1
    assert data["memories"][0]["agent_id"] == "lifetree-agent"
    assert "no-project" in data["memories"][0]["tags"]
