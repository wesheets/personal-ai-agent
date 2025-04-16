"""
Tests for the Agent Verification Module

This module tests the functionality of the agent_verify.py module,
which provides the /agent/verify_task endpoint for agent self-qualification checks.
"""

import json
import os
import pytest
from unittest.mock import patch, mock_open
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.modules.agent_verify import router, extract_required_skills, verify_agent_skills

# Create a test FastAPI app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Sample agent manifest for testing
MOCK_AGENT_MANIFEST = {
    "hal-agent": {
        "version": "1.0.0",
        "description": "Safety and constraint monitoring system",
        "status": "active",
        "entrypoint": "app/agents/hal_agent.py",
        "tone_profile": {
            "style": "formal",
            "emotion": "neutral",
            "vibe": "guardian",
            "persona": "HAL-9000 with fewer red flags"
        },
        "skills": ["reflect", "summarize", "monitor", "analyze"]
    },
    "ash-agent": {
        "version": "0.9.0",
        "description": "Clinical analysis and protocol-driven agent",
        "status": "active",
        "entrypoint": "app/agents/ash_agent.py",
        "tone_profile": {
            "style": "precise",
            "emotion": "calm",
            "vibe": "medical-professional",
            "persona": "Methodical clinician with a focus on accuracy and protocol adherence"
        },
        "skills": ["delegate", "execute", "analyze", "protocol"]
    },
    "test-agent": {
        "version": "0.1.0",
        "description": "Test agent with no skills",
        "status": "experimental",
        "entrypoint": "app/agents/test_agent.py",
        "tone_profile": {
            "style": "neutral",
            "emotion": "neutral",
            "vibe": "neutral",
            "persona": "Test agent"
        },
        "skills": []
    }
}

# Mock the open function to return our test manifest
@pytest.fixture
def mock_manifest():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_AGENT_MANIFEST))):
        yield

def test_extract_required_skills():
    """Test extracting required skills from task descriptions"""
    # Test with explicit skill keywords
    task1 = "Analyze the user's sentiment and summarize their feedback."
    skills1 = extract_required_skills(task1)
    assert "analyze" in skills1
    assert "summarize" in skills1
    
    # Test with related keywords
    task2 = "Track system performance and create a brief assessment."
    skills2 = extract_required_skills(task2)
    assert "monitor" in skills2  # "track" maps to "monitor"
    assert "summarize" in skills2  # "brief" maps to "summarize"
    
    # Test with no clear skill keywords
    task3 = "Handle this request from the user."
    skills3 = extract_required_skills(task3)
    assert len(skills3) == 0  # No clear skills should be extracted

def test_verify_agent_skills(mock_manifest):
    """Test verifying agent skills against required skills"""
    # Test with all matching skills
    qualified1, score1, missing1, matching1 = verify_agent_skills("hal", ["analyze", "summarize"])
    assert qualified1 is True
    assert score1 >= 0.8  # High confidence score
    assert len(missing1) == 0
    assert set(matching1) == {"analyze", "summarize"}
    
    # Test with some matching and some missing skills
    qualified2, score2, missing2, matching2 = verify_agent_skills("hal", ["analyze", "delegate"])
    assert qualified2 is False
    assert 0.4 <= score2 <= 0.6  # Moderate confidence score
    assert set(missing2) == {"delegate"}
    assert set(matching2) == {"analyze"}
    
    # Test with all missing skills
    qualified3, score3, missing3, matching3 = verify_agent_skills("hal", ["delegate", "execute"])
    assert qualified3 is False
    assert score3 <= 0.2  # Low confidence score
    assert set(missing3) == {"delegate", "execute"}
    assert len(matching3) == 0
    
    # Test with no required skills
    qualified4, score4, missing4, matching4 = verify_agent_skills("hal", [])
    assert qualified4 is True
    assert score4 == 0.5  # Neutral score
    assert len(missing4) == 0
    assert len(matching4) == 0
    
    # Test with agent that has no skills
    qualified5, score5, missing5, matching5 = verify_agent_skills("test", ["analyze"])
    assert qualified5 is False
    assert score5 <= 0.2  # Low confidence score
    assert set(missing5) == {"analyze"}
    assert len(matching5) == 0

@patch("app.modules.agent_verify.load_agent_manifest")
def test_verify_task_endpoint_qualified(mock_load_manifest, mock_manifest):
    """Test the verify_task endpoint with a qualified agent"""
    mock_load_manifest.return_value = MOCK_AGENT_MANIFEST
    
    response = client.post(
        "/agent/verify_task",
        json={
            "agent_id": "hal",
            "task_description": "Analyze user feedback and summarize the key points."
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "hal"
    assert data["qualified"] is True
    assert data["confidence_score"] >= 0.8
    assert len(data["missing_skills"]) == 0
    assert set(data["matching_skills"]) == {"analyze", "summarize"}
    assert "fully qualified" in data["justification"].lower()

@patch("app.modules.agent_verify.load_agent_manifest")
def test_verify_task_endpoint_not_qualified(mock_load_manifest, mock_manifest):
    """Test the verify_task endpoint with an unqualified agent"""
    mock_load_manifest.return_value = MOCK_AGENT_MANIFEST
    
    response = client.post(
        "/agent/verify_task",
        json={
            "agent_id": "hal",
            "task_description": "Delegate tasks to other agents and execute the plan."
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "hal"
    assert data["qualified"] is False
    assert data["confidence_score"] <= 0.2
    assert set(data["missing_skills"]) == {"delegate", "execute"}
    assert len(data["matching_skills"]) == 0
    assert "lacks" in data["justification"].lower()
    assert data["suggested_agents"] is not None
    assert "ash" in data["suggested_agents"]  # ash has delegate and execute skills

@patch("app.modules.agent_verify.load_agent_manifest")
def test_verify_task_endpoint_with_explicit_skills(mock_load_manifest, mock_manifest):
    """Test the verify_task endpoint with explicitly provided skills"""
    mock_load_manifest.return_value = MOCK_AGENT_MANIFEST
    
    response = client.post(
        "/agent/verify_task",
        json={
            "agent_id": "hal",
            "task_description": "Handle this complex task.",
            "required_skills": ["analyze", "monitor"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "hal"
    assert data["qualified"] is True
    assert data["confidence_score"] >= 0.8
    assert len(data["missing_skills"]) == 0
    assert set(data["matching_skills"]) == {"analyze", "monitor"}

@patch("app.modules.agent_verify.load_agent_manifest")
def test_verify_task_endpoint_agent_not_found(mock_load_manifest, mock_manifest):
    """Test the verify_task endpoint with a non-existent agent"""
    mock_load_manifest.return_value = MOCK_AGENT_MANIFEST
    
    response = client.post(
        "/agent/verify_task",
        json={
            "agent_id": "nonexistent",
            "task_description": "Analyze user feedback."
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

@patch("app.modules.agent_verify.load_agent_manifest")
def test_verify_task_endpoint_missing_fields(mock_load_manifest, mock_manifest):
    """Test the verify_task endpoint with missing required fields"""
    mock_load_manifest.return_value = MOCK_AGENT_MANIFEST
    
    # Missing agent_id
    response1 = client.post(
        "/agent/verify_task",
        json={
            "task_description": "Analyze user feedback."
        }
    )
    assert response1.status_code == 422
    
    # Missing task_description
    response2 = client.post(
        "/agent/verify_task",
        json={
            "agent_id": "hal"
        }
    )
    assert response2.status_code == 422

@patch("app.modules.agent_verify.load_agent_manifest")
def test_verify_task_endpoint_with_agent_suffix(mock_load_manifest, mock_manifest):
    """Test the verify_task endpoint with agent_id including -agent suffix"""
    mock_load_manifest.return_value = MOCK_AGENT_MANIFEST
    
    response = client.post(
        "/agent/verify_task",
        json={
            "agent_id": "hal-agent",
            "task_description": "Analyze user feedback and summarize the key points."
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "hal-agent"
    assert data["qualified"] is True
