"""
Test script for Loop + Delegation Cap System.

This script tests the implementation of the Loop + Delegation Cap System,
which enforces hard and soft caps across /loop, /delegate, and /reflect
endpoints to prevent infinite agent loops or runaway delegation chains.
"""

import pytest
import json
import os
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.modules.memory_writer import memory_store, write_memory

client = TestClient(app)

# Path to system caps configuration
SYSTEM_CAPS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "system_caps.json")

def setup_module():
    """Set up test environment before running tests."""
    # Clear memory store
    memory_store.clear()
    
    # Create test memories
    write_memory(
        agent_id="hal",
        type="observation",
        content="Test observation for HAL",
        tags=["test"]
    )
    
    write_memory(
        agent_id="ash",
        type="observation",
        content="Test observation for ASH",
        tags=["test"]
    )

def test_system_caps_config_exists():
    """Test that the system_caps.json configuration file exists."""
    assert os.path.exists(SYSTEM_CAPS_FILE), "System caps configuration file does not exist"
    
    # Verify the file contains the required fields
    with open(SYSTEM_CAPS_FILE, 'r') as f:
        caps = json.load(f)
    
    assert "max_loops_per_task" in caps, "max_loops_per_task not found in system caps"
    assert "max_delegation_depth" in caps, "max_delegation_depth not found in system caps"
    
    # Verify the values are integers
    assert isinstance(caps["max_loops_per_task"], int), "max_loops_per_task is not an integer"
    assert isinstance(caps["max_delegation_depth"], int), "max_delegation_depth is not an integer"

def test_loop_cap_enforcement():
    """Test that the loop cap is enforced in the /loop endpoint."""
    # Get the current cap value
    with open(SYSTEM_CAPS_FILE, 'r') as f:
        caps = json.load(f)
    max_loops = caps["max_loops_per_task"]
    
    # Generate a unique task_id for this test
    task_id = str(uuid.uuid4())
    
    # Execute loops up to the limit
    for i in range(max_loops):
        response = client.post(
            "/app/modules/agent/loop",
            json={
                "agent_id": "hal",
                "loop_type": "reflective",
                "task_id": task_id,
                "loop_count": i
            }
        )
        assert response.status_code == 200, f"Loop {i+1} failed with status code {response.status_code}"
        
        # Verify the response contains the expected fields
        data = response.json()
        assert data["status"] == "success", f"Loop {i+1} returned status {data['status']}"
        assert data["cycle_number"] == i+1, f"Loop {i+1} returned cycle_number {data['cycle_number']}"
    
    # Attempt one more loop beyond the limit
    response = client.post(
        "/app/modules/agent/loop",
        json={
            "agent_id": "hal",
            "loop_type": "reflective",
            "task_id": task_id,
            "loop_count": max_loops
        }
    )
    
    # Verify the response indicates the loop limit was exceeded
    assert response.status_code == 429, f"Expected status code 429, got {response.status_code}"
    
    data = response.json()
    assert data["status"] == "error", f"Expected status 'error', got {data['status']}"
    assert data["reason"] == "Loop limit exceeded", f"Expected reason 'Loop limit exceeded', got {data['reason']}"
    assert data["loop_count"] == max_loops, f"Expected loop_count {max_loops}, got {data['loop_count']}"
    assert data["task_id"] == task_id, f"Expected task_id {task_id}, got {data['task_id']}"
    
    # Verify a system_halt memory was created
    halt_memories = [m for m in memory_store if m["type"] == "system_halt" and "loop_limit" in m["tags"]]
    assert len(halt_memories) > 0, "No system_halt memory was created"

def test_delegation_cap_enforcement():
    """Test that the delegation cap is enforced in the /delegate endpoint."""
    # Get the current cap value
    with open(SYSTEM_CAPS_FILE, 'r') as f:
        caps = json.load(f)
    max_depth = caps["max_delegation_depth"]
    
    # Execute delegations up to the limit
    for i in range(max_depth):
        response = client.post(
            "/app/modules/agent/delegate",
            json={
                "from_agent": "hal",
                "to_agent": "ash",
                "task": f"Test delegation {i+1}",
                "delegation_depth": i
            }
        )
        assert response.status_code == 200, f"Delegation {i+1} failed with status code {response.status_code}"
        
        # Verify the response contains the expected fields
        data = response.json()
        assert data["status"] == "ok", f"Delegation {i+1} returned status {data['status']}"
        assert data["delegation_depth"] == i+1, f"Delegation {i+1} returned delegation_depth {data['delegation_depth']}"
    
    # Attempt one more delegation beyond the limit
    response = client.post(
        "/app/modules/agent/delegate",
        json={
            "from_agent": "hal",
            "to_agent": "ash",
            "task": f"Test delegation {max_depth+1}",
            "delegation_depth": max_depth
        }
    )
    
    # Verify the response indicates the delegation limit was exceeded
    assert response.status_code == 429, f"Expected status code 429, got {response.status_code}"
    
    data = response.json()
    assert data["status"] == "error", f"Expected status 'error', got {data['status']}"
    assert data["reason"] == "Delegation depth exceeded", f"Expected reason 'Delegation depth exceeded', got {data['reason']}"
    assert data["delegation_depth"] == max_depth, f"Expected delegation_depth {max_depth}, got {data['delegation_depth']}"
    assert data["agent_id"] == "ash", f"Expected agent_id 'ash', got {data['agent_id']}"
    
    # Verify a system_halt memory was created
    halt_memories = [m for m in memory_store if m["type"] == "system_halt" and "delegation_limit" in m["tags"]]
    assert len(halt_memories) > 0, "No system_halt memory was created"

def test_reflection_auto_cap():
    """Test that the reflection auto-cap is enforced in the /reflect endpoint."""
    # Get the current cap value
    with open(SYSTEM_CAPS_FILE, 'r') as f:
        caps = json.load(f)
    max_loops = caps["max_loops_per_task"]
    
    # Generate a unique task_id for this test
    task_id = str(uuid.uuid4())
    project_id = "test-project"
    memory_trace_id = str(uuid.uuid4())
    
    # Execute reflections up to the limit
    for i in range(max_loops):
        response = client.post(
            "/app/modules/reflect",
            json={
                "agent_id": "hal",
                "goal": "Test reflection",
                "task_id": task_id,
                "project_id": project_id,
                "memory_trace_id": memory_trace_id,
                "loop_count": i
            }
        )
        assert response.status_code == 200, f"Reflection {i+1} failed with status code {response.status_code}"
        
        # Verify the response contains the expected fields
        data = response.json()
        assert data["status"] == "success", f"Reflection {i+1} returned status {data['status']}"
        assert data["loop_count"] == i+1, f"Reflection {i+1} returned loop_count {data['loop_count']}"
    
    # Attempt one more reflection beyond the limit
    response = client.post(
        "/app/modules/reflect",
        json={
            "agent_id": "hal",
            "goal": "Test reflection",
            "task_id": task_id,
            "project_id": project_id,
            "memory_trace_id": memory_trace_id,
            "loop_count": max_loops
        }
    )
    
    # Verify the response indicates the loop limit was exceeded
    assert response.status_code == 429, f"Expected status code 429, got {response.status_code}"
    
    data = response.json()
    assert data["status"] == "error", f"Expected status 'error', got {data['status']}"
    assert data["reason"] == "Loop limit exceeded", f"Expected reason 'Loop limit exceeded', got {data['reason']}"
    assert data["loop_count"] == max_loops, f"Expected loop_count {max_loops}, got {data['loop_count']}"
    assert data["task_id"] == task_id, f"Expected task_id {task_id}, got {data['task_id']}"
    
    # Verify a system_halt memory was created
    halt_memories = [m for m in memory_store if m["type"] == "system_halt" and "reflection" in m["tags"]]
    assert len(halt_memories) > 0, "No system_halt memory was created for reflection"

def test_configurable_cap_override():
    """Test that the cap values can be overridden for testing."""
    # Save the original cap values
    with open(SYSTEM_CAPS_FILE, 'r') as f:
        original_caps = json.load(f)
    
    try:
        # Override the cap values for testing
        test_caps = {
            "max_loops_per_task": 1,
            "max_delegation_depth": 1
        }
        
        with open(SYSTEM_CAPS_FILE, 'w') as f:
            json.dump(test_caps, f)
        
        # Test loop cap with overridden value
        task_id = str(uuid.uuid4())
        
        # First loop should succeed
        response = client.post(
            "/app/modules/agent/loop",
            json={
                "agent_id": "hal",
                "loop_type": "reflective",
                "task_id": task_id,
                "loop_count": 0
            }
        )
        assert response.status_code == 200, f"Loop 1 failed with status code {response.status_code}"
        
        # Second loop should fail with the overridden cap
        response = client.post(
            "/app/modules/agent/loop",
            json={
                "agent_id": "hal",
                "loop_type": "reflective",
                "task_id": task_id,
                "loop_count": 1
            }
        )
        assert response.status_code == 429, f"Expected status code 429, got {response.status_code}"
        
        # Test delegation cap with overridden value
        # First delegation should succeed
        response = client.post(
            "/app/modules/agent/delegate",
            json={
                "from_agent": "hal",
                "to_agent": "ash",
                "task": "Test delegation override",
                "delegation_depth": 0
            }
        )
        assert response.status_code == 200, f"Delegation 1 failed with status code {response.status_code}"
        
        # Second delegation should fail with the overridden cap
        response = client.post(
            "/app/modules/agent/delegate",
            json={
                "from_agent": "hal",
                "to_agent": "ash",
                "task": "Test delegation override 2",
                "delegation_depth": 1
            }
        )
        assert response.status_code == 429, f"Expected status code 429, got {response.status_code}"
        
    finally:
        # Restore the original cap values
        with open(SYSTEM_CAPS_FILE, 'w') as f:
            json.dump(original_caps, f)
