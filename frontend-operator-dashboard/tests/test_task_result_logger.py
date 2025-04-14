"""
Test script for the enhanced task_result logger.

This script tests the functionality of the task_result logger, which stores
task results with proper metadata including task_id, result, project_id, status, and goal_id.
"""

import unittest
import requests
import json
import os
import sys
import uuid
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the necessary modules for direct testing
from app.modules.task_result import log_task_result
from app.api.modules.memory import write_memory, memory_store
from app.db.memory_db import memory_db

class TestTaskResultLogger(unittest.TestCase):
    """Test cases for the enhanced task_result logger."""
    
    def setUp(self):
        """Set up test environment."""
        # Base URL for API requests
        self.base_url = "http://localhost:8000"
        
        # Test data
        self.test_agent_id = "test_agent"
        self.test_user_id = "test_user_001"
        self.test_project_id = "test_project"
        self.test_goal_id = "goal_123"
        
        # Generate a unique task_id for this test run
        self.test_task_id = f"TASK_{uuid.uuid4().hex[:8]}"
        
        # Test request data
        self.test_request_data = {
            "agent_id": self.test_agent_id,
            "user_id": self.test_user_id,
            "task_id": self.test_task_id,
            "result": "success",
            "content": "Task completed successfully with all requirements met",
            "project_id": self.test_project_id,
            "goal_id": self.test_goal_id,
            "status": "completed",
            "confidence_score": 0.95,
            "notes": "Implementation was straightforward with no issues"
        }
    
    async def mock_request(self, data):
        """Create a mock request object with the given data."""
        class MockRequest:
            async def json(self):
                return data
        
        return MockRequest()
    
    def test_task_result_with_metadata(self):
        """Test the task_result logger with full metadata."""
        import asyncio
        
        # Create a mock request with our test data
        mock_request = asyncio.run(self.mock_request(self.test_request_data))
        
        # Call the log_task_result function with the mock request
        result = asyncio.run(log_task_result(mock_request))
        
        # Verify the result structure
        self.assertIsNotNone(result)
        self.assertEqual(result.get("status"), "logged")
        self.assertIsNotNone(result.get("memory_id"))
        
        # Store the memory_id for retrieval test
        memory_id = result.get("memory_id")
        
        # Retrieve the memory from the database
        memory = memory_db.read_memory_by_id(memory_id)
        
        # Verify the memory was stored correctly
        self.assertIsNotNone(memory)
        self.assertEqual(memory.get("agent_id"), self.test_agent_id)
        self.assertEqual(memory.get("type"), "task_result")
        self.assertEqual(memory.get("task_id"), self.test_task_id)
        self.assertEqual(memory.get("project_id"), self.test_project_id)
        
        # Verify metadata was stored correctly
        self.assertIsNotNone(memory.get("metadata"))
        self.assertEqual(memory.get("metadata").get("task_id"), self.test_task_id)
        self.assertEqual(memory.get("metadata").get("result"), "success")
        self.assertEqual(memory.get("metadata").get("project_id"), self.test_project_id)
        self.assertEqual(memory.get("metadata").get("goal_id"), self.test_goal_id)
        self.assertEqual(memory.get("metadata").get("status"), "completed")
        self.assertEqual(memory.get("metadata").get("confidence_score"), 0.95)
        self.assertEqual(memory.get("metadata").get("notes"), "Implementation was straightforward with no issues")
        
        # Verify tags include user scope
        self.assertIn("task_result", memory.get("tags", []))
        self.assertIn("success", memory.get("tags", []))
        self.assertIn(f"user:{self.test_user_id}", memory.get("tags", []))
        
        print(f"✅ Successfully logged task result with memory_id: {memory_id}")
    
    def test_task_result_minimal_data(self):
        """Test the task_result logger with minimal required data."""
        import asyncio
        
        # Create minimal test data with only required fields
        minimal_data = {
            "agent_id": self.test_agent_id,
            "task_id": f"MINIMAL_{uuid.uuid4().hex[:8]}",
            "result": "partial",
            "content": "Minimal test data"
        }
        
        # Create a mock request with minimal data
        mock_request = asyncio.run(self.mock_request(minimal_data))
        
        # Call the log_task_result function with the mock request
        result = asyncio.run(log_task_result(mock_request))
        
        # Verify the result structure
        self.assertIsNotNone(result)
        self.assertEqual(result.get("status"), "logged")
        self.assertIsNotNone(result.get("memory_id"))
        
        # Store the memory_id for retrieval test
        memory_id = result.get("memory_id")
        
        # Retrieve the memory from the database
        memory = memory_db.read_memory_by_id(memory_id)
        
        # Verify the memory was stored correctly
        self.assertIsNotNone(memory)
        self.assertEqual(memory.get("agent_id"), self.test_agent_id)
        self.assertEqual(memory.get("type"), "task_result")
        self.assertEqual(memory.get("task_id"), minimal_data["task_id"])
        
        # Verify metadata was stored correctly
        self.assertIsNotNone(memory.get("metadata"))
        self.assertEqual(memory.get("metadata").get("task_id"), minimal_data["task_id"])
        self.assertEqual(memory.get("metadata").get("result"), "partial")
        
        # Verify tags
        self.assertIn("task_result", memory.get("tags", []))
        self.assertIn("partial", memory.get("tags", []))
        
        print(f"✅ Successfully logged minimal task result with memory_id: {memory_id}")
    
    def test_task_result_audit_compatibility(self):
        """Test that task results can be found by the audit function."""
        import asyncio
        from app.api.modules.orchestrator import audit_agent_performance
        
        # Create a unique task_id for this test
        audit_task_id = f"AUDIT_{uuid.uuid4().hex[:8]}"
        
        # First create a task plan
        write_memory(
            agent_id=self.test_agent_id,
            type="task_plan",
            content=f"Plan for audit test task {audit_task_id}",
            tags=["test", "task_plan"],
            project_id=self.test_project_id,
            task_id=audit_task_id,
            metadata={
                "task_id": audit_task_id,
                "project_id": self.test_project_id
            }
        )
        
        # Now create a task result using our enhanced logger
        result_data = {
            "agent_id": self.test_agent_id,
            "task_id": audit_task_id,
            "result": "success",
            "content": "Audit compatibility test result",
            "project_id": self.test_project_id
        }
        
        # Create a mock request with the result data
        mock_request = asyncio.run(self.mock_request(result_data))
        
        # Call the log_task_result function with the mock request
        result = asyncio.run(log_task_result(mock_request))
        
        # Verify the result was logged
        self.assertIsNotNone(result)
        self.assertEqual(result.get("status"), "logged")
        
        # Now call the audit function to see if it can find our task
        audit_result = asyncio.run(audit_agent_performance(
            agent_id=self.test_agent_id,
            limit=10
        ))
        
        # Verify the audit result contains our task
        self.assertIsNotNone(audit_result)
        
        # Verify the audit result contains our task
        self.assertIsNotNone(audit_result)
        
        # Check if our test task is in the report
        found = False
        for task in audit_result.get("task_report", []):
            if task.get("task_id") == audit_task_id:
                found = True
                self.assertEqual(task.get("status"), "success")
                self.assertIsNotNone(task.get("planned_content"))
                self.assertIsNotNone(task.get("result_content"))
                break
        
        self.assertTrue(found, f"Task with ID {audit_task_id} not found in audit results")
        
        print(f"✅ Successfully verified task result is compatible with audit function")

if __name__ == "__main__":
    unittest.main()
