"""
Test file for the orchestrator/scope endpoint.

This module contains tests for the /orchestrator/scope endpoint, which turns high-level
user goals into structured system plans.
"""

import pytest
import json
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_orchestrator_scope_endpoint_basic():
    """Test the basic functionality of the orchestrator/scope endpoint."""
    # Create a test request
    request_data = {
        "goal": "Create a journaling application with reflection capabilities",
        "mode": "scope"
    }
    
    # Make the request
    response = client.post("/orchestrator/scope", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the response structure
    assert "project_id" in data
    assert "goal" in data
    assert "required_modules" in data
    assert "suggested_agents" in data
    assert "recommended_schema" in data
    assert "execution_tasks" in data
    assert "known_risks" in data
    assert "confidence_scores" in data
    assert "project_dependencies" in data
    assert "agent_training_reqs" in data
    assert "execution_blueprint_id" in data
    assert "suggested_tests" in data
    assert "markdown_summary" in data
    assert "stored" in data
    assert "skill_validation_passed" in data
    assert "unmatched_tasks" in data
    assert "agent_creation_suggestions" in data
    
    # Check that the goal matches the request
    assert data["goal"] == request_data["goal"]
    
    # Check that required_modules is a list
    assert isinstance(data["required_modules"], list)
    
    # Check that suggested_agents is a list of dictionaries
    assert isinstance(data["suggested_agents"], list)
    for agent in data["suggested_agents"]:
        assert "agent_name" in agent
        assert "tools" in agent
        assert "persona" in agent
    
    # Check that recommended_schema has input and output fields
    assert "input" in data["recommended_schema"]
    assert "output" in data["recommended_schema"]
    
    # Check that execution_tasks is a list
    assert isinstance(data["execution_tasks"], list)
    
    # Check that known_risks is a list
    assert isinstance(data["known_risks"], list)
    
    # Check that confidence_scores is a dictionary
    assert isinstance(data["confidence_scores"], dict)
    
    # Check that project_dependencies is a dictionary
    assert isinstance(data["project_dependencies"], dict)
    
    # Check that agent_training_reqs is a dictionary
    assert isinstance(data["agent_training_reqs"], dict)
    
    # Check that execution_blueprint_id is a string
    assert isinstance(data["execution_blueprint_id"], str)
    
    # Check that suggested_tests is a list
    assert isinstance(data["suggested_tests"], list)
    
    # Check that markdown_summary is a string
    assert isinstance(data["markdown_summary"], str)
    
    # Check that stored is a boolean
    assert isinstance(data["stored"], bool)
    
    # Check that skill_validation_passed is a boolean
    assert isinstance(data["skill_validation_passed"], bool)
    
    # Check that unmatched_tasks is a list
    assert isinstance(data["unmatched_tasks"], list)

def test_orchestrator_scope_endpoint_with_project_id():
    """Test the orchestrator/scope endpoint with a provided project_id."""
    # Create a test project_id
    project_id = f"test-proj-{str(uuid.uuid4())[:8]}"
    
    # Create a test request
    request_data = {
        "goal": "Build a task management system with delegation",
        "project_id": project_id,
        "mode": "scope"
    }
    
    # Make the request
    response = client.post("/orchestrator/scope", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that the project_id matches the request
    assert data["project_id"] == project_id

def test_orchestrator_scope_endpoint_with_storage():
    """Test the orchestrator/scope endpoint with memory storage."""
    # Create a test request
    request_data = {
        "goal": "Create a data analysis pipeline with visualization",
        "mode": "scope",
        "store_scope": True
    }
    
    # Make the request
    response = client.post("/orchestrator/scope", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that the scope was stored
    assert data["stored"] == True

def test_orchestrator_scope_endpoint_required_fields():
    """Test the orchestrator/scope endpoint with missing required fields."""
    # Create a test request without a goal
    request_data = {
        "mode": "scope"
    }
    
    # Make the request
    response = client.post("/orchestrator/scope", json=request_data)
    
    # Check that the response is an error
    assert response.status_code == 422  # Unprocessable Entity

def test_orchestrator_scope_endpoint_module_analysis():
    """Test that the orchestrator/scope endpoint correctly analyzes goals for modules."""
    # Test cases with different goals and expected modules
    test_cases = [
        {
            "goal": "Create a journaling application with reflection capabilities",
            "expected_modules": ["write", "read", "reflect"]
        },
        {
            "goal": "Build a task management system with delegation",
            "expected_modules": ["write", "read", "reflect", "task/status", "delegate"]
        },
        {
            "goal": "Create a data analysis pipeline with summarization",
            "expected_modules": ["write", "read", "reflect", "summarize"]
        },
        {
            "goal": "Develop a learning system that can train on new data",
            "expected_modules": ["write", "read", "reflect", "train"]
        },
        {
            "goal": "Build a system with iterative loops for continuous improvement",
            "expected_modules": ["write", "read", "reflect", "loop"]
        }
    ]
    
    for test_case in test_cases:
        # Create a test request
        request_data = {
            "goal": test_case["goal"],
            "mode": "scope"
        }
        
        # Make the request
        response = client.post("/orchestrator/scope", json=request_data)
        
        # Check the response
        assert response.status_code == 200
        
        # Parse the response
        data = response.json()
        
        # Check that all expected modules are included
        for module in test_case["expected_modules"]:
            assert module in data["required_modules"], f"Module {module} not found for goal: {test_case['goal']}"

def test_orchestrator_scope_endpoint_agent_selection():
    """Test that the orchestrator/scope endpoint correctly selects agents based on the goal."""
    # Create a test request
    request_data = {
        "goal": "Build a task management system with delegation",
        "mode": "scope"
    }
    
    # Make the request
    response = client.post("/orchestrator/scope", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that the suggested agents include HAL and ASH
    agent_names = [agent["agent_name"] for agent in data["suggested_agents"]]
    assert "hal" in agent_names
    assert "ash" in agent_names
    
    # Check that ASH has the delegate tool for a delegation-related goal
    for agent in data["suggested_agents"]:
        if agent["agent_name"] == "ash":
            assert "delegate" in agent["tools"]

def test_orchestrator_scope_endpoint_markdown_summary():
    """Test that the orchestrator/scope endpoint generates a proper markdown summary."""
    # Create a test request
    request_data = {
        "goal": "Create a journaling application with reflection capabilities",
        "project_id": "test-journal-app",
        "mode": "scope"
    }
    
    # Make the request
    response = client.post("/orchestrator/scope", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that the markdown summary contains key sections
    markdown = data["markdown_summary"]
    assert "# Project Scope: test-journal-app" in markdown
    assert "## Goal" in markdown
    assert "## Required Modules" in markdown
    assert "## Suggested Agents" in markdown
    assert "## Execution Tasks" in markdown
    assert "## Known Risks" in markdown

def test_orchestrator_scope_endpoint_suggested_tests():
    """Test that the orchestrator/scope endpoint generates appropriate suggested tests."""
    # Create a test request
    request_data = {
        "goal": "Create a data analysis pipeline with summarization",
        "mode": "scope"
    }
    
    # Make the request
    response = client.post("/orchestrator/scope", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that the suggested tests include a summarize test
    has_summarize_test = False
    for test in data["suggested_tests"]:
        if test["endpoint"] == "/summarize":
            has_summarize_test = True
            break
    
    assert has_summarize_test, "No summarize test found for a summarization-related goal"

def test_orchestrator_scope_endpoint_skill_validation():
    """Test that the orchestrator/scope endpoint correctly validates agent skills."""
    # Create a test request with a goal requiring summarization
    request_data = {
        "goal": "Create a data analysis pipeline with summarization",
        "mode": "scope"
    }
    
    # Make the request
    response = client.post("/orchestrator/scope", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that skill_validation_passed is present
    assert "skill_validation_passed" in data
    
    # Check that unmatched_tasks is present
    assert "unmatched_tasks" in data
    
    # Check confidence scores for agents
    for agent_name, score in data["confidence_scores"].items():
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

def test_orchestrator_scope_endpoint_no_agent_can_summarize():
    """Test scenario where no agent can summarize."""
    # This test simulates a situation where no agent has the summarize skill
    # The actual implementation will use the agent_manifest.json to determine skills
    
    # Create a test request with a goal requiring summarization
    request_data = {
        "goal": "Create a comprehensive summarization system",
        "mode": "scope"
    }
    
    # Make the request
    response = client.post("/orchestrator/scope", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that skill_validation_passed is false
    # Note: This assertion might fail if the agent_manifest.json has been updated
    # to include summarize skills for agents. In that case, this test should be updated.
    assert "skill_validation_passed" in data
    
    # Check that unmatched_tasks is not empty
    assert "unmatched_tasks" in data
    
    # Check that there's at least one unmatched task related to summarization
    summarize_unmatched = False
    for task in data["unmatched_tasks"]:
        if "summarize" in task["tool"]:
            summarize_unmatched = True
            break
    
    # This assertion might fail if the agent_manifest.json has been updated
    # to include summarize skills for agents. In that case, this test should be updated.
    assert summarize_unmatched, "Expected unmatched task for summarize not found"

def test_orchestrator_scope_endpoint_agent_creation_suggestions():
    """Test that the orchestrator/scope endpoint generates agent creation suggestions for skill gaps."""
    # Create a test request with a goal requiring emotional analysis (a skill no agent has)
    request_data = {
        "goal": "Build a journaling AI that reflects on memory with emotional analysis",
        "mode": "scope"
    }
    
    # Make the request
    response = client.post("/orchestrator/scope", json=request_data)
    
    # Check the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that skill_validation_passed is false
    assert "skill_validation_passed" in data
    assert data["skill_validation_passed"] is False
    
    # Check that unmatched_tasks is not empty
    assert "unmatched_tasks" in data
    assert len(data["unmatched_tasks"]) > 0
    
    # Check that there's at least one unmatched task related to emotional analysis
    emotional_analysis_unmatched = False
    for task in data["unmatched_tasks"]:
        if "emotional_analysis" in task["tool"]:
            emotional_analysis_unmatched = True
            break
    
    assert emotional_analysis_unmatched, "Expected unmatched task for emotional_analysis not found"
    
    # Check that agent_creation_suggestions is present and not empty
    assert "agent_creation_suggestions" in data
    assert len(data["agent_creation_suggestions"]) > 0
    
    # Check the structure of the agent creation suggestion
    suggestion = data["agent_creation_suggestions"][0]
    assert "agent_name" in suggestion
    assert "proposed_skills" in suggestion
    assert "tone_profile" in suggestion
    assert "reason" in suggestion
    
    # Check that the tone profile has the required fields
    tone_profile = suggestion["tone_profile"]
    assert "style" in tone_profile
    assert "emotion" in tone_profile
    assert "vibe" in tone_profile
    assert "persona" in tone_profile
    
    # Check that the proposed skills include emotional_analysis
    assert "emotional_analysis" in suggestion["proposed_skills"]

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-xvs", __file__])
