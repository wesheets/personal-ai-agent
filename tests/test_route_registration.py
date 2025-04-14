"""
Test script for route registration and method handling for /loop, /delegate, and /reflect modules.

This script tests that all cap-enforced endpoints are correctly registered, exposed,
and respond properly to POST requests.
"""

import pytest
import json
import os
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_loop_endpoint_registration():
    """Test that the /app/modules/loop endpoint is correctly registered and responds to POST requests."""
    # Generate test data
    task_id = str(uuid.uuid4())
    
    # Test POST request
    response = client.post(
        "/app/modules/loop",
        json={
            "agent_id": "hal",
            "loop_type": "reflective",
            "task_id": task_id,
            "loop_count": 3  # Should trigger cap enforcement
        }
    )
    
    # Verify response status code (429 Too Many Requests due to cap enforcement)
    assert response.status_code == 429, f"Expected status code 429, got {response.status_code}"
    
    # Verify response content
    data = response.json()
    assert data["status"] == "error", f"Expected status 'error', got {data['status']}"
    assert data["reason"] == "Loop limit exceeded", f"Expected reason 'Loop limit exceeded', got {data.get('reason')}"
    assert data["loop_count"] == 3, f"Expected loop_count 3, got {data.get('loop_count')}"
    
    # Test GET request (should be rejected)
    response = client.get("/app/modules/loop")
    assert response.status_code in [404, 405], f"Expected status code 404 or 405, got {response.status_code}"

def test_delegate_endpoint_registration():
    """Test that the /app/modules/delegate endpoint is correctly registered and responds to POST requests."""
    # Test POST request
    response = client.post(
        "/app/modules/delegate",
        json={
            "from_agent": "hal",
            "to_agent": "ash",
            "task": "Test delegation",
            "delegation_depth": 2  # Should trigger cap enforcement
        }
    )
    
    # Verify response status code (429 Too Many Requests due to cap enforcement)
    assert response.status_code == 429, f"Expected status code 429, got {response.status_code}"
    
    # Verify response content
    data = response.json()
    assert data["status"] == "error", f"Expected status 'error', got {data['status']}"
    assert data["reason"] == "Delegation depth exceeded", f"Expected reason 'Delegation depth exceeded', got {data.get('reason')}"
    assert data["delegation_depth"] == 2, f"Expected delegation_depth 2, got {data.get('delegation_depth')}"
    
    # Test GET request (should be rejected)
    response = client.get("/app/modules/delegate")
    assert response.status_code in [404, 405], f"Expected status code 404 or 405, got {response.status_code}"

def test_reflect_endpoint_registration():
    """Test that the /app/modules/reflect endpoint is correctly registered and responds to POST requests."""
    # Generate test data
    task_id = str(uuid.uuid4())
    project_id = "test-project"
    memory_trace_id = str(uuid.uuid4())
    
    # Test POST request
    response = client.post(
        "/app/modules/reflect",
        json={
            "agent_id": "hal",
            "goal": "Test reflection",
            "task_id": task_id,
            "project_id": project_id,
            "memory_trace_id": memory_trace_id,
            "loop_count": 3  # Should trigger cap enforcement
        }
    )
    
    # Verify response status code (429 Too Many Requests due to cap enforcement)
    assert response.status_code == 429, f"Expected status code 429, got {response.status_code}"
    
    # Verify response content
    data = response.json()
    assert data["status"] == "error", f"Expected status 'error', got {data['status']}"
    assert data["reason"] == "Loop limit exceeded", f"Expected reason 'Loop limit exceeded', got {data.get('reason')}"
    assert data["loop_count"] == 3, f"Expected loop_count 3, got {data.get('loop_count')}"
    
    # Test GET request (should be rejected)
    response = client.get("/app/modules/reflect")
    assert response.status_code in [404, 405], f"Expected status code 404 or 405, got {response.status_code}"

def test_endpoint_payload_parsing():
    """Test that all three endpoints parse POST JSON bodies cleanly."""
    # Test loop endpoint with minimal payload
    response = client.post(
        "/app/modules/loop",
        json={
            "agent_id": "hal"
        }
    )
    assert response.status_code != 422, f"Loop endpoint failed to parse minimal payload: {response.status_code}"
    
    # Test delegate endpoint with minimal payload
    response = client.post(
        "/app/modules/delegate",
        json={
            "from_agent": "hal",
            "to_agent": "ash",
            "task": "Test delegation"
        }
    )
    assert response.status_code != 422, f"Delegate endpoint failed to parse minimal payload: {response.status_code}"
    
    # Test reflect endpoint with minimal payload
    response = client.post(
        "/app/modules/reflect",
        json={
            "agent_id": "hal",
            "goal": "Test reflection",
            "task_id": str(uuid.uuid4()),
            "project_id": "test-project",
            "memory_trace_id": str(uuid.uuid4())
        }
    )
    assert response.status_code != 422, f"Reflect endpoint failed to parse minimal payload: {response.status_code}"

def test_cap_enforcement_responses():
    """Test that all three endpoints return structured 429 responses when caps are exceeded."""
    # Test loop endpoint cap enforcement
    response = client.post(
        "/app/modules/loop",
        json={
            "agent_id": "hal",
            "loop_count": 3  # Should trigger cap enforcement
        }
    )
    assert response.status_code == 429, f"Expected status code 429 for loop endpoint, got {response.status_code}"
    
    # Test delegate endpoint cap enforcement
    response = client.post(
        "/app/modules/delegate",
        json={
            "from_agent": "hal",
            "to_agent": "ash",
            "task": "Test delegation",
            "delegation_depth": 2  # Should trigger cap enforcement
        }
    )
    assert response.status_code == 429, f"Expected status code 429 for delegate endpoint, got {response.status_code}"
    
    # Test reflect endpoint cap enforcement
    response = client.post(
        "/app/modules/reflect",
        json={
            "agent_id": "hal",
            "goal": "Test reflection",
            "task_id": str(uuid.uuid4()),
            "project_id": "test-project",
            "memory_trace_id": str(uuid.uuid4()),
            "loop_count": 3  # Should trigger cap enforcement
        }
    )
    assert response.status_code == 429, f"Expected status code 429 for reflect endpoint, got {response.status_code}"
