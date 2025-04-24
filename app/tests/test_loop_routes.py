"""
Test cases for loop_routes.py endpoints.

This module contains unit tests for the loop routes API endpoints.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from fastapi.testclient import TestClient
from datetime import datetime

# Import the FastAPI app
from app.main import app
from app.schemas.loop_schema import (
    LoopResponseRequest,
    LoopResponseResult,
    LoopPlanRequest,
    LoopPlanResponse,
    LoopCompletionRequest,
    LoopCompletionResponse,
    LoopValidateRequest,
    LoopValidateResponse
)

# Create test client
client = TestClient(app)

class TestLoopRoutes(unittest.TestCase):
    """Test cases for loop routes."""

    def setUp(self):
        """Set up test environment."""
        # Sample data for tests
        self.loop_id = "test_loop_001"
        self.project_id = "test_project_001"
        
        # Sample loop plan request
        self.plan_request_data = {
            "prompt": "Create a React component for user onboarding",
            "loop_id": self.loop_id,
            "orchestrator_persona": "SAGE"
        }
        
        # Sample loop completion request
        self.completion_request_data = {
            "loop_id": self.loop_id,
            "project_id": self.project_id,
            "executor": "test_executor",
            "notes": "Test loop completion"
        }
        
        # Sample loop validate request
        self.validate_request_data = {
            "loop_id": self.loop_id,
            "loop_data": {
                "step1": "Research",
                "step2": "Design",
                "step3": "Implement"
            },
            "mode": "balanced"
        }
        
        # Sample loop respond request
        self.respond_request_data = {
            "project_id": self.project_id,
            "loop_id": self.loop_id,
            "agent": "hal",
            "response_type": "code",
            "target_file": "TestComponent.jsx",
            "input_key": "build_task"
        }

    @patch('app.routes.loop_routes.read_memory')
    @patch('app.routes.loop_routes.process_build_task')
    @patch('app.routes.loop_routes.write_memory')
    async def test_loop_respond_endpoint(self, mock_write_memory, mock_process_build_task, mock_read_memory):
        """Test the loop respond endpoint."""
        # Mock read_memory to return a memory item
        mock_read_memory.return_value = {
            "content": "Create a React component for user onboarding",
            "timestamp": datetime.now().isoformat()
        }
        
        # Mock process_build_task to return a successful result
        mock_process_build_task.return_value = {
            "status": "success",
            "code": "function TestComponent() { return <div>Test</div>; }",
            "timestamp": datetime.now().isoformat()
        }
        
        # Mock write_memory to return a successful result
        mock_write_memory.return_value = {
            "status": "success",
            "memory_id": "test_memory_001"
        }
        
        # Send request to endpoint
        response = client.post(
            "/api/loop/respond",
            json=self.respond_request_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["agent"], "hal")
        self.assertEqual(data["input_key"], "build_task")
        self.assertTrue("output_tag" in data)
        self.assertTrue("timestamp" in data)
        
        # Verify mocks were called correctly
        mock_read_memory.assert_called_once()
        mock_process_build_task.assert_called_once()
        mock_write_memory.assert_called_once()

    def test_plan_loop(self):
        """Test the plan loop endpoint."""
        # Send request to endpoint
        response = client.post(
            "/api/loop/plan",
            json=self.plan_request_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["loop_id"], self.loop_id)
        self.assertEqual(data["orchestrator_persona"], "SAGE")
        self.assertEqual(data["status"], "success")
        self.assertTrue("plan" in data)
        self.assertTrue("steps" in data["plan"])
        self.assertEqual(len(data["plan"]["steps"]), 3)

    def test_loop_complete_endpoint(self):
        """Test the loop complete endpoint."""
        # Send request to endpoint
        response = client.post(
            "/api/loop/complete",
            json=self.completion_request_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "activated")
        self.assertEqual(data["loop_id"], self.loop_id)
        self.assertEqual(data["project_id"], self.project_id)
        self.assertEqual(data["executor"], "test_executor")
        self.assertTrue("message" in data)
        self.assertTrue("orchestration_status" in data)

    def test_validate_loop(self):
        """Test the validate loop endpoint."""
        # Send request to endpoint
        response = client.post(
            "/api/loop/validate",
            json=self.validate_request_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["loop_id"], self.loop_id)
        self.assertEqual(data["mode"], "balanced")
        self.assertTrue("validation_result" in data)
        self.assertTrue("prepared_loop" in data)
        self.assertEqual(data["processed_by"], "cognitive_control_layer")

    def test_get_loop_trace(self):
        """Test the get loop trace endpoint."""
        # Send request to endpoint
        response = client.get(
            "/api/loop/trace",
            params={"project_id": self.project_id}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue("traces" in data)
        self.assertEqual(len(data["traces"]), 2)
        self.assertTrue("loop_id" in data["traces"][0])
        self.assertTrue("status" in data["traces"][0])
        self.assertTrue("timestamp" in data["traces"][0])
        self.assertTrue("summary" in data["traces"][0])

    def test_add_loop_trace(self):
        """Test the add loop trace endpoint."""
        # Prepare request data
        trace_data = {
            "loop_id": self.loop_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "summary": "Test loop trace"
        }
        
        # Send request to endpoint
        response = client.post(
            "/api/loop/trace",
            json=trace_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["loop_id"], self.loop_id)
        self.assertTrue("message" in data)

    def test_reset_loop(self):
        """Test the reset loop endpoint."""
        # Send request to endpoint
        response = client.post("/api/loop/reset")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue("message" in data)
        self.assertTrue("timestamp" in data)

    def test_persona_reflect(self):
        """Test the persona reflect endpoint."""
        # Prepare request data
        reflect_data = {
            "persona": "SAGE",
            "reflection": "This is a test reflection",
            "loop_id": self.loop_id
        }
        
        # Send request to endpoint
        response = client.post(
            "/api/loop/persona-reflect",
            json=reflect_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["persona"], "SAGE")
        self.assertEqual(data["loop_id"], self.loop_id)
        self.assertTrue("message" in data)

if __name__ == "__main__":
    unittest.main()
