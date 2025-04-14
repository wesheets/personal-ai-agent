import pytest
import json
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import httpx

# Import the router to test
from app.api.project.start import router

# Create a test FastAPI app
app = FastAPI()
app.include_router(router, prefix="/api/project")

# Create a test client
client = TestClient(app)

def test_project_start_validation():
    """Test that the endpoint validates the request format."""
    # Test missing goal field
    response = client.post("/api/project/start", json={})
    assert response.status_code == 400
    assert "goal" in response.text.lower()
    
    # Test invalid request format
    response = client.post("/api/project/start", json="not a dict")
    assert response.status_code == 400  # Updated to match actual implementation

@patch("httpx.AsyncClient.post")
def test_project_start_success(mock_post):
    """Test successful project start with mocked chain response."""
    # Mock the chain response
    mock_chain_response = MagicMock()
    mock_chain_response.status_code = 200
    mock_chain_response.json.return_value = {
        "chain_id": str(uuid.uuid4()),
        "status": "complete",
        "steps": [
            {
                "agent": "hal",
                "status": "complete",
                "reflection": "I completed the task successfully.",
                "outputs": ["def capitalize_words(sentence):\n    return ' '.join(word.capitalize() for word in sentence.split())"]
            },
            {
                "agent": "ash",
                "status": "complete",
                "reflection": "I summarized HAL's output.",
                "outputs": ["HAL created a function that capitalizes each word in a sentence by splitting the string, capitalizing each word, and joining them back together."]
            },
            {
                "agent": "nova",
                "status": "complete",
                "reflection": "I created a simple HTML preview.",
                "outputs": ["<div class='code-preview'><pre>def capitalize_words(sentence):\n    return ' '.join(word.capitalize() for word in sentence.split())</pre></div>"]
            }
        ]
    }
    mock_post.return_value = mock_chain_response
    
    # Test the endpoint
    response = client.post("/api/project/start", json={"goal": "Write a Python function that capitalizes every word in a sentence"})
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert "project_id" in data
    assert "chain_id" in data
    assert "agents" in data
    assert len(data["agents"]) == 3
    assert data["agents"][0]["agent"] == "hal"
    assert data["agents"][1]["agent"] == "ash"
    assert data["agents"][2]["agent"] == "nova"
    
    # Verify the chain was called with the correct payload
    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert "json" in call_args
    instruction_chain = call_args["json"]
    assert len(instruction_chain) == 3
    assert instruction_chain[0]["agent"] == "hal"
    assert instruction_chain[0]["goal"] == "Write a Python function that capitalizes every word in a sentence"
    assert "project_id" in instruction_chain[0]
    assert instruction_chain[1]["agent"] == "ash"
    assert instruction_chain[2]["agent"] == "nova"

@patch("httpx.AsyncClient.post")
def test_project_start_chain_failure(mock_post):
    """Test handling of chain execution failure."""
    # Mock the chain response
    mock_chain_response = MagicMock()
    mock_chain_response.status_code = 500
    mock_chain_response.text = "Internal server error"
    mock_post.return_value = mock_chain_response
    
    # Test the endpoint
    response = client.post("/api/project/start", json={"goal": "Write a Python function that capitalizes every word in a sentence"})
    
    # Verify the response
    assert response.status_code == 500
    data = response.json()
    assert "status" in data
    assert data["status"] == "error"
    assert "message" in data
    assert "Chain execution failed" in data["message"]

@patch("httpx.AsyncClient.post")
def test_project_start_connection_error(mock_post):
    """Test handling of connection error during chain execution."""
    # Mock a connection error
    mock_post.side_effect = httpx.RequestError("Connection error")
    
    # Test the endpoint
    response = client.post("/api/project/start", json={"goal": "Write a Python function that capitalizes every word in a sentence"})
    
    # Verify the response
    assert response.status_code == 500
    data = response.json()
    assert "status" in data
    assert data["status"] == "error"
    assert "message" in data
    assert "Connection error" in data["message"]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
