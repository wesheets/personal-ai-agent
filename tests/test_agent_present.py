"""
Test file for the agent/present endpoint.

This module contains tests for the /agent/present endpoint, which enables
agents to describe themselves in a structured, narrative format.
"""

import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_agent_present_endpoint_valid_agent():
    """Test the agent/present endpoint with a valid agent."""
    # Create a test request for HAL agent
    request_data = {
        "agent_id": "hal"
    }
    
    # Make the request
    response = client.post("/agent/present", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the response structure
    assert "agent_id" in data
    assert "description" in data
    assert "skills" in data
    assert "tone_profile" in data
    assert "ideal_tasks" in data
    assert "present_markdown" in data
    assert "narration_text" in data
    
    # Check that the agent_id matches the request
    assert data["agent_id"] == "hal"
    
    # Check that skills is a list
    assert isinstance(data["skills"], list)
    
    # Check that tone_profile has the required fields
    assert "style" in data["tone_profile"]
    assert "emotion" in data["tone_profile"]
    assert "vibe" in data["tone_profile"]
    assert "persona" in data["tone_profile"]
    
    # Check that ideal_tasks is a list
    assert isinstance(data["ideal_tasks"], list)
    
    # Check that present_markdown is a string
    assert isinstance(data["present_markdown"], str)
    
    # Check that narration_text is a string
    assert isinstance(data["narration_text"], str)
    assert len(data["narration_text"]) > 0

def test_agent_present_endpoint_missing_agent():
    """Test the agent/present endpoint with a missing agent."""
    # Create a test request with a non-existent agent
    request_data = {
        "agent_id": "nonexistent-agent"
    }
    
    # Make the request
    response = client.post("/agent/present", json=request_data)
    
    # Check that the response is a 404 error
    assert response.status_code == 404
    
    # Parse the response
    data = response.json()
    
    # Check that the response contains an error detail
    assert "detail" in data

def test_agent_present_endpoint_missing_agent_id():
    """Test the agent/present endpoint with a missing agent_id."""
    # Create a test request without an agent_id
    request_data = {}
    
    # Make the request
    response = client.post("/agent/present", json=request_data)
    
    # Check that the response is a 422 error (Unprocessable Entity)
    assert response.status_code == 422
    
    # Parse the response
    data = response.json()
    
    # Check that the response contains an error detail
    assert "detail" in data

def test_agent_present_endpoint_markdown_format():
    """Test that the agent/present endpoint generates properly formatted markdown."""
    # Create a test request for HAL agent
    request_data = {
        "agent_id": "hal"
    }
    
    # Make the request
    response = client.post("/agent/present", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that present_markdown is a string
    assert isinstance(data["present_markdown"], str)
    
    # Check that the markdown contains expected sections
    markdown = data["present_markdown"]
    assert "# HAL: Self-Presentation" in markdown
    assert "## Description" in markdown
    assert "## Skills" in markdown
    assert "## Ideal Tasks" in markdown
    assert "## Persona" in markdown
    assert "## Tone Profile" in markdown

def test_agent_present_endpoint_with_suffix():
    """Test the agent/present endpoint with an agent_id that includes the -agent suffix."""
    # Create a test request for HAL agent with the -agent suffix
    request_data = {
        "agent_id": "hal-agent"
    }
    
    # Make the request
    response = client.post("/agent/present", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that the agent_id matches the request
    assert data["agent_id"] == "hal-agent"

def test_agent_present_endpoint_narration_text():
    """Test that the agent/present endpoint generates non-empty narration text."""
    # Create a test request for HAL agent
    request_data = {
        "agent_id": "hal"
    }
    
    # Make the request
    response = client.post("/agent/present", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that narration_text is a non-empty string
    assert isinstance(data["narration_text"], str)
    assert len(data["narration_text"]) > 0
    
    # Check that the narration text contains the agent name
    assert "HAL" in data["narration_text"]

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-xvs", __file__])
