"""
Test file for the agent/create endpoint.

This module contains tests for the /agent/create endpoint, which enables
creating new agents based on suggestions from the /scope endpoint.
"""

import pytest
import json
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Path to a test agent manifest file to avoid modifying the real one
TEST_MANIFEST_PATH = "/tmp/test_agent_manifest.json"

# Create a backup of the original manifest path
ORIGINAL_MANIFEST_PATH = None

def setup_module(module):
    """Set up the test module by creating a test manifest file."""
    global ORIGINAL_MANIFEST_PATH
    from app.modules.agent_create import AGENT_MANIFEST_PATH
    
    # Save the original path
    ORIGINAL_MANIFEST_PATH = AGENT_MANIFEST_PATH
    
    # Create a test manifest with some sample agents
    test_manifest = {
        "test-agent": {
            "version": "1.0.0",
            "description": "Test agent for unit tests",
            "status": "active",
            "entrypoint": "app/agents/test_agent.py",
            "tone_profile": {
                "style": "concise",
                "emotion": "neutral",
                "vibe": "tester",
                "persona": "Thorough test runner"
            },
            "skills": ["test", "validate"]
        }
    }
    
    # Write the test manifest to the test path
    with open(TEST_MANIFEST_PATH, 'w') as f:
        json.dump(test_manifest, f, indent=2)
    
    # Patch the manifest path in the agent_create module
    import app.modules.agent_create
    app.modules.agent_create.AGENT_MANIFEST_PATH = TEST_MANIFEST_PATH

def teardown_module(module):
    """Clean up after the tests by restoring the original manifest path."""
    # Restore the original manifest path
    if ORIGINAL_MANIFEST_PATH:
        import app.modules.agent_create
        app.modules.agent_create.AGENT_MANIFEST_PATH = ORIGINAL_MANIFEST_PATH
    
    # Remove the test manifest file
    if os.path.exists(TEST_MANIFEST_PATH):
        os.remove(TEST_MANIFEST_PATH)

def test_agent_create_endpoint_valid_agent():
    """Test the agent/create endpoint with a valid agent."""
    # Create a test request for a new agent
    request_data = {
        "agent_name": "echo",
        "skills": ["emotional_analysis", "summarize"],
        "tone_profile": {
            "style": "gentle",
            "emotion": "empathetic",
            "vibe": "grief companion",
            "persona": "Echo is a reflective presence for healing work"
        },
        "description": "Tone-aware agent for emotional memory processing"
    }
    
    # Make the request
    response = client.post("/agent/create", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the response structure
    assert data["status"] == "success"
    assert data["agent_id"] == "echo"
    assert "successfully created" in data["message"]
    
    # Verify the agent was added to the manifest
    with open(TEST_MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)
    
    assert "echo-agent" in manifest
    assert manifest["echo-agent"]["description"] == "Tone-aware agent for emotional memory processing"
    assert "emotional_analysis" in manifest["echo-agent"]["skills"]
    assert "summarize" in manifest["echo-agent"]["skills"]
    assert manifest["echo-agent"]["tone_profile"]["style"] == "gentle"
    assert manifest["echo-agent"]["tone_profile"]["emotion"] == "empathetic"
    assert manifest["echo-agent"]["tone_profile"]["vibe"] == "grief companion"
    assert manifest["echo-agent"]["tone_profile"]["persona"] == "Echo is a reflective presence for healing work"

def test_agent_create_endpoint_duplicate_agent():
    """Test the agent/create endpoint with a duplicate agent."""
    # Create a test request for an agent that already exists
    request_data = {
        "agent_name": "test",
        "skills": ["test", "validate"],
        "tone_profile": {
            "style": "concise",
            "emotion": "neutral",
            "vibe": "tester",
            "persona": "Thorough test runner"
        },
        "description": "Test agent for unit tests"
    }
    
    # Make the request
    response = client.post("/agent/create", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that the response indicates an error
    assert data["status"] == "error"
    assert data["agent_id"] == "test"
    assert "already exists" in data["message"]

def test_agent_create_endpoint_missing_fields():
    """Test the agent/create endpoint with missing required fields."""
    # Create a test request without skills
    request_data = {
        "agent_name": "incomplete",
        "tone_profile": {
            "style": "concise",
            "emotion": "neutral",
            "vibe": "tester",
            "persona": "Incomplete agent"
        },
        "description": "Agent with missing fields"
    }
    
    # Make the request
    response = client.post("/agent/create", json=request_data)
    
    # Check that the response is a 422 error (Unprocessable Entity)
    assert response.status_code == 422
    
    # Create a test request without agent_name
    request_data = {
        "skills": ["test"],
        "tone_profile": {
            "style": "concise",
            "emotion": "neutral",
            "vibe": "tester",
            "persona": "Incomplete agent"
        },
        "description": "Agent with missing fields"
    }
    
    # Make the request
    response = client.post("/agent/create", json=request_data)
    
    # Check that the response is a 422 error (Unprocessable Entity)
    assert response.status_code == 422

def test_agent_create_endpoint_with_suffix():
    """Test the agent/create endpoint with an agent_name that includes the -agent suffix."""
    # Create a test request for a new agent with the -agent suffix
    request_data = {
        "agent_name": "suffix-agent",
        "skills": ["test", "validate"],
        "tone_profile": {
            "style": "concise",
            "emotion": "neutral",
            "vibe": "tester",
            "persona": "Agent with suffix"
        },
        "description": "Test agent with suffix"
    }
    
    # Make the request
    response = client.post("/agent/create", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the response structure
    assert data["status"] == "success"
    assert data["agent_id"] == "suffix-agent"
    
    # Verify the agent was added to the manifest with the correct key
    with open(TEST_MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)
    
    assert "suffix-agent" in manifest

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-xvs", __file__])
