"""
Test script for the project initiate endpoint.

This module tests the functionality of the /project/initiate endpoint,
which allows the Orchestrator to create new agent-led projects with
associated goals, memory scopes, and agent assignments.
"""

import unittest
import asyncio
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.api.modules.project_models import ProjectInitiateRequest, ProjectInitiateResponse
from app.db.memory_db import memory_db

class TestProjectInitiateEndpoint(unittest.TestCase):
    """Test cases for the project initiate endpoint."""
    
    def setUp(self):
        """Set up the test client and common test data."""
        self.client = TestClient(app)
        self.test_user_id = f"test_user_{uuid.uuid4().hex[:6]}"
        self.test_agent_id = "hal"  # Using a standard agent ID
    
    def tearDown(self):
        """Clean up after tests by closing database connections."""
        # Close any open database connections to prevent threading issues
        memory_db.close()
        
    def test_project_initiate_basic(self):
        """Test basic project initiation functionality."""
        # Create test request data
        request_data = {
            "user_id": self.test_user_id,
            "project_name": "Test College Counseling",
            "goal": "Finish my test college application",
            "agent_id": self.test_agent_id
        }
        
        # Send request to the endpoint
        response = self.client.post("/api/modules/project/initiate", json=request_data)
        
        # Check response status code
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}: {response.text}")
        
        # Parse response data
        response_data = response.json()
        
        # Check response structure
        self.assertEqual(response_data["status"], "ok", "Expected status 'ok'")
        self.assertIn("project_id", response_data, "Expected 'project_id' in response")
        self.assertIn("goal_id", response_data, "Expected 'goal_id' in response")
        self.assertEqual(response_data["agent_id"], self.test_agent_id, "Expected agent_id to match request")
        
        # Check ID formats
        self.assertTrue(response_data["project_id"].startswith("project_"), "Project ID should start with 'project_'")
        self.assertTrue(response_data["goal_id"].startswith("goal_"), "Goal ID should start with 'goal_'")
        
        # Store IDs for potential use in other tests
        self.project_id = response_data["project_id"]
        self.goal_id = response_data["goal_id"]
        
    def test_project_initiate_memory_integration(self):
        """Test that project initiation properly writes to memory."""
        # Create test request data
        request_data = {
            "user_id": self.test_user_id,
            "project_name": "Memory Integration Test",
            "goal": "Test memory integration",
            "agent_id": self.test_agent_id
        }
        
        # Send request to the endpoint
        response = self.client.post("/api/modules/project/initiate", json=request_data)
        
        # Check response status code
        self.assertEqual(response.status_code, 200, "Expected 200 OK")
        
        # Parse response data
        response_data = response.json()
        project_id = response_data["project_id"]
        
        # Query memory to check if project was registered
        memory_response = self.client.get(
            "/api/modules/memory/read",
            params={
                "agent_id": self.test_agent_id,
                "type": "project_registration",
                "project_id": project_id
            }
        )
        
        # Check memory response
        self.assertEqual(memory_response.status_code, 200, "Expected 200 OK from memory read")
        memory_data = memory_response.json()
        self.assertEqual(memory_data["status"], "ok", "Expected status 'ok' from memory read")
        self.assertGreaterEqual(len(memory_data["memories"]), 1, "Expected at least one memory entry")
        
        # Check goal definition in memory
        goal_memory_response = self.client.get(
            "/api/modules/memory/read",
            params={
                "agent_id": self.test_agent_id,
                "type": "goal_definition",
                "project_id": project_id
            }
        )
        
        # Check goal memory response
        self.assertEqual(goal_memory_response.status_code, 200, "Expected 200 OK from goal memory read")
        goal_memory_data = goal_memory_response.json()
        self.assertEqual(goal_memory_data["status"], "ok", "Expected status 'ok' from goal memory read")
        self.assertGreaterEqual(len(goal_memory_data["memories"]), 1, "Expected at least one goal memory entry")
        
    def test_project_initiate_error_handling(self):
        """Test error handling in project initiation."""
        # Create invalid test request data (missing required fields)
        request_data = {
            "user_id": self.test_user_id,
            # Missing project_name
            "goal": "Test error handling",
            "agent_id": self.test_agent_id
        }
        
        # Send request to the endpoint
        response = self.client.post("/api/modules/project/initiate", json=request_data)
        
        # Check response status code (should be 422 Unprocessable Entity for validation error)
        self.assertEqual(response.status_code, 422, "Expected 422 Unprocessable Entity for missing required field")

if __name__ == "__main__":
    unittest.main()
