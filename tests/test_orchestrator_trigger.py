"""
Test Module for Orchestrator Trigger Logic

This module provides test cases for verifying the functionality of the
Orchestrator Automatic Agent Trigger implementation.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

# Mock PROJECT_MEMORY for testing
PROJECT_MEMORY = {}

# Mock SCHEMA_REGISTRY for testing
SCHEMA_REGISTRY = {
    "agents": {
        "hal": {
            "role": "initial builder",
            "dependencies": [],
            "produces": ["README.md", "requirements.txt"],
            "unlocks": ["nova"]
        },
        "nova": {
            "role": "logic writer",
            "dependencies": ["hal"],
            "produces": ["api_routes", "logic_modules"],
            "unlocks": ["critic"]
        }
    },
    "loop": {
        "required_agents": ["hal", "nova"],
        "max_loops": 5,
        "exit_conditions": ["loop_complete == true", "loop_count >= max_loops"]
    }
}

# Import the functions to test (with mocked dependencies)
# In a real implementation, these would be imported from their modules
# For testing purposes, we'll define simplified versions here

def initialize_orchestrator_memory(project_id: str) -> None:
    """Initialize the orchestrator-related memory structures if they don't exist."""
    if project_id not in PROJECT_MEMORY:
        PROJECT_MEMORY[project_id] = {}
    
    memory = PROJECT_MEMORY[project_id]
    
    # Initialize orchestrator decisions array if it doesn't exist
    if "orchestrator_decisions" not in memory:
        memory["orchestrator_decisions"] = []
    
    # Initialize other required fields with defaults if they don't exist
    if "completed_steps" not in memory:
        memory["completed_steps"] = []
    
    if "loop_count" not in memory:
        memory["loop_count"] = 1
    
    if "loop_complete" not in memory:
        memory["loop_complete"] = False
    
    if "next_recommended_agent" not in memory:
        memory["next_recommended_agent"] = None
    
    if "autospawn" not in memory:
        memory["autospawn"] = False
    
    # Initialize orchestrator execution log if it doesn't exist
    if "orchestrator_execution_log" not in memory:
        memory["orchestrator_execution_log"] = []


def trigger_next_agent(project_id: str) -> Dict[str, Any]:
    """Trigger the next agent to run automatically based on the next_recommended_agent in memory."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Get the next recommended agent from memory
    memory = PROJECT_MEMORY[project_id]
    next_agent = memory.get("next_recommended_agent")
    
    # If no agent to run, return early
    if not next_agent:
        result = {
            "status": "no agent to run",
            "agent": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        memory.setdefault("orchestrator_execution_log", []).append(result)
        return result
    
    # Prepare payload for API call
    payload = {
        "project_id": project_id,
        "agent": next_agent
    }
    
    try:
        # Make API call to trigger agent (mocked in tests)
        import requests
        response = requests.post(
            "http://localhost:8080/api/agent/run",
            json=payload
        )
        
        # Create result record
        result = {
            "triggered_agent": next_agent,
            "status_code": response.status_code,
            "response": response.json(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Handle errors
        error_msg = f"Error triggering agent {next_agent}: {str(e)}"
        
        # Create error result record
        result = {
            "triggered_agent": next_agent,
            "status": "error",
            "error_message": error_msg,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Log the result
    memory.setdefault("orchestrator_execution_log", []).append(result)
    memory["last_orchestrator_trigger"] = result
    
    return result


def get_execution_log(project_id: str, limit=None) -> List[Dict[str, Any]]:
    """Retrieve the execution log for a project."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    log_entries = PROJECT_MEMORY[project_id].get("orchestrator_execution_log", [])
    
    if limit is not None:
        return log_entries[-limit:]
    
    return log_entries


def get_last_execution(project_id: str) -> Dict[str, Any]:
    """Retrieve the most recent execution log entry for a project."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    return PROJECT_MEMORY[project_id].get("last_orchestrator_trigger")


class TestOrchestratorTrigger(unittest.TestCase):
    """Test cases for the Orchestrator Trigger functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear the mock PROJECT_MEMORY before each test
        global PROJECT_MEMORY
        PROJECT_MEMORY = {}
        
        # Set up a test project
        self.project_id = "test_project"
        initialize_orchestrator_memory(self.project_id)
        
        # Set up some test data
        PROJECT_MEMORY[self.project_id]["next_recommended_agent"] = "hal"
    
    @patch('requests.post')
    def test_trigger_next_agent_success(self, mock_post):
        """Test that triggering the next agent works correctly."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "message": "Agent hal triggered successfully"
        }
        mock_post.return_value = mock_response
        
        # Trigger the next agent
        result = trigger_next_agent(self.project_id)
        
        # Verify API call
        mock_post.assert_called_once_with(
            "http://localhost:8080/api/agent/run",
            json={"project_id": self.project_id, "agent": "hal"}
        )
        
        # Verify result structure
        self.assertIn("triggered_agent", result)
        self.assertIn("status_code", result)
        self.assertIn("response", result)
        self.assertIn("timestamp", result)
        
        # Verify result content
        self.assertEqual(result["triggered_agent"], "hal")
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["status"], "success")
        
        # Verify execution log was updated
        execution_log = PROJECT_MEMORY[self.project_id]["orchestrator_execution_log"]
        self.assertEqual(len(execution_log), 1)
        self.assertEqual(execution_log[0], result)
        
        # Verify last trigger was set
        self.assertEqual(PROJECT_MEMORY[self.project_id]["last_orchestrator_trigger"], result)
    
    def test_trigger_next_agent_no_agent(self):
        """Test triggering when no agent is recommended."""
        # Clear the next recommended agent
        PROJECT_MEMORY[self.project_id]["next_recommended_agent"] = None
        
        # Trigger the next agent
        result = trigger_next_agent(self.project_id)
        
        # Verify result structure
        self.assertIn("status", result)
        self.assertIn("agent", result)
        self.assertIn("timestamp", result)
        
        # Verify result content
        self.assertEqual(result["status"], "no agent to run")
        self.assertIsNone(result["agent"])
        
        # Verify execution log was updated
        execution_log = PROJECT_MEMORY[self.project_id]["orchestrator_execution_log"]
        self.assertEqual(len(execution_log), 1)
        self.assertEqual(execution_log[0], result)
    
    @patch('requests.post')
    def test_trigger_next_agent_api_error(self, mock_post):
        """Test handling of API errors when triggering."""
        # Mock the API to raise an exception
        mock_post.side_effect = Exception("API connection error")
        
        # Trigger the next agent
        result = trigger_next_agent(self.project_id)
        
        # Verify result structure
        self.assertIn("triggered_agent", result)
        self.assertIn("status", result)
        self.assertIn("error_message", result)
        self.assertIn("timestamp", result)
        
        # Verify result content
        self.assertEqual(result["triggered_agent"], "hal")
        self.assertEqual(result["status"], "error")
        self.assertIn("API connection error", result["error_message"])
        
        # Verify execution log was updated
        execution_log = PROJECT_MEMORY[self.project_id]["orchestrator_execution_log"]
        self.assertEqual(len(execution_log), 1)
        self.assertEqual(execution_log[0], result)
        
        # Verify last trigger was set
        self.assertEqual(PROJECT_MEMORY[self.project_id]["last_orchestrator_trigger"], result)
    
    def test_get_execution_log(self):
        """Test retrieving the execution log."""
        # Create multiple trigger results
        PROJECT_MEMORY[self.project_id]["orchestrator_execution_log"] = [
            {
                "triggered_agent": "hal",
                "status_code": 200,
                "response": {"status": "success"},
                "timestamp": "2025-04-20T10:00:00Z"
            },
            {
                "triggered_agent": "nova",
                "status_code": 200,
                "response": {"status": "success"},
                "timestamp": "2025-04-20T11:00:00Z"
            }
        ]
        
        # Get all log entries
        log_entries = get_execution_log(self.project_id)
        
        # Verify log entries
        self.assertEqual(len(log_entries), 2)
        self.assertEqual(log_entries[0]["triggered_agent"], "hal")
        self.assertEqual(log_entries[1]["triggered_agent"], "nova")
        
        # Test with limit
        limited_log = get_execution_log(self.project_id, 1)
        self.assertEqual(len(limited_log), 1)
        self.assertEqual(limited_log[0]["triggered_agent"], "nova")
    
    def test_get_last_execution(self):
        """Test retrieving the last execution."""
        # Set up a last trigger
        last_trigger = {
            "triggered_agent": "hal",
            "status_code": 200,
            "response": {"status": "success"},
            "timestamp": "2025-04-20T10:00:00Z"
        }
        PROJECT_MEMORY[self.project_id]["last_orchestrator_trigger"] = last_trigger
        
        # Get the last execution
        result = get_last_execution(self.project_id)
        
        # Verify result
        self.assertEqual(result, last_trigger)
        
        # Test with no last trigger
        PROJECT_MEMORY[self.project_id].pop("last_orchestrator_trigger")
        result = get_last_execution(self.project_id)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
