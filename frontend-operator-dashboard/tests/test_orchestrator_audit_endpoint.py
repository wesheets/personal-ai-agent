"""
Test script for the /orchestrator/audit endpoint.

This script tests the functionality of the /orchestrator/audit endpoint, which compares
task plans with execution results to audit agent performance.
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

# Import the memory module for direct testing
from app.api.modules.memory import write_memory, memory_store
from app.db.memory_db import memory_db
from app.api.modules.orchestrator import audit_agent_performance

class TestOrchestratorAuditEndpoint(unittest.TestCase):
    """Test cases for the /orchestrator/audit endpoint."""
    
    def setUp(self):
        """Set up test environment."""
        # Base URL for API requests
        self.base_url = "http://localhost:8000"
        
        # Test data
        self.test_agent_id = "test_agent"
        self.test_user_id = "test_user_001"
        self.test_project_id = "test_project"
        
        # Generate unique task IDs for this test run
        self.test_task_ids = [f"TASK_{uuid.uuid4().hex[:8]}" for _ in range(3)]
        
        # Create test task plans and results
        self.create_test_data()
    
    def create_test_data(self):
        """Create test task plans and results for auditing."""
        # Create task plans
        for i, task_id in enumerate(self.test_task_ids):
            # Create a task plan
            write_memory(
                agent_id=self.test_agent_id,
                type="task_plan",
                content=f"Plan for task {task_id}: Step 1, Step 2, Step 3",
                tags=["test", "task_plan"],
                project_id=self.test_project_id,
                task_id=task_id,
                metadata={
                    "task_id": task_id,
                    "project_id": self.test_project_id,
                    "user_id": self.test_user_id
                }
            )
            
            # Create task results for the first two tasks only (to test unattempted)
            if i < 2:
                # Success for first task, failure for second
                result = "success" if i == 0 else "failure"
                
                write_memory(
                    agent_id=self.test_agent_id,
                    type="task_result",
                    content=f"Result for task {task_id}: {'Completed successfully' if result == 'success' else 'Failed to complete'}",
                    tags=["test", "task_result", result],
                    project_id=self.test_project_id,
                    task_id=task_id,
                    metadata={
                        "task_id": task_id,
                        "result": result,
                        "project_id": self.test_project_id,
                        "user_id": self.test_user_id
                    }
                )
        
        print(f"✅ Created {len(self.test_task_ids)} test task plans and {len(self.test_task_ids) - 1} test task results")
    
    def test_direct_audit_function(self):
        """Test the audit_agent_performance function directly."""
        import asyncio
        
        # Call the audit function directly and await the result
        audit_result = asyncio.run(audit_agent_performance(
            agent_id=self.test_agent_id,
            limit=10
        ))
        
        # Verify the audit result structure
        self.assertIsNotNone(audit_result)
        self.assertEqual(audit_result.get("agent_id"), self.test_agent_id)
        self.assertIn("audit_summary", audit_result)
        self.assertIn("task_report", audit_result)
        
        # Verify the audit summary
        summary = audit_result.get("audit_summary")
        self.assertGreaterEqual(summary.get("total_planned"), len(self.test_task_ids))
        self.assertGreaterEqual(summary.get("total_attempted"), len(self.test_task_ids) - 1)
        self.assertGreaterEqual(summary.get("successes"), 1)
        self.assertGreaterEqual(summary.get("failures"), 1)
        self.assertGreaterEqual(summary.get("unattempted"), 1)
        
        # Verify the task report
        task_report = audit_result.get("task_report")
        self.assertIsInstance(task_report, list)
        
        # Check if our test tasks are in the report
        found_tasks = 0
        for task in task_report:
            if task.get("task_id") in self.test_task_ids:
                found_tasks += 1
                
                # Verify task structure
                self.assertIn("status", task)
                self.assertIn("planned_content", task)
                
                # Verify status based on which task it is
                task_index = self.test_task_ids.index(task.get("task_id"))
                if task_index == 0:
                    self.assertEqual(task.get("status"), "success")
                    self.assertIsNotNone(task.get("result_content"))
                elif task_index == 1:
                    self.assertEqual(task.get("status"), "failure")
                    self.assertIsNotNone(task.get("result_content"))
                elif task_index == 2:
                    self.assertEqual(task.get("status"), "unattempted")
                    self.assertIsNone(task.get("result_content"))
        
        # Verify we found at least some of our test tasks
        self.assertGreater(found_tasks, 0)
        
        print(f"✅ Successfully tested audit function with {found_tasks} test tasks found in results")
    
    def test_audit_with_task_group(self):
        """Test the audit function with task_group filtering."""
        import asyncio
        
        # Create a special task group for this test
        task_group = f"group_{uuid.uuid4().hex[:8]}"
        
        # Create task plans with the special task group
        special_task_ids = [f"SPECIAL_{uuid.uuid4().hex[:8]}" for _ in range(2)]
        
        for i, task_id in enumerate(special_task_ids):
            # Create a task plan
            write_memory(
                agent_id=self.test_agent_id,
                type="task_plan",
                content=f"Special plan for task {task_id}: Step 1, Step 2",
                tags=["test", "task_plan", task_group],
                project_id=self.test_project_id,
                task_id=task_id,
                metadata={
                    "task_id": task_id,
                    "project_id": self.test_project_id,
                    "task_group": task_group
                }
            )
            
            # Create task result for the first task only
            if i == 0:
                write_memory(
                    agent_id=self.test_agent_id,
                    type="task_result",
                    content=f"Special result for task {task_id}: Completed",
                    tags=["test", "task_result", "success", task_group],
                    project_id=self.test_project_id,
                    task_id=task_id,
                    metadata={
                        "task_id": task_id,
                        "result": "success",
                        "project_id": self.test_project_id,
                        "task_group": task_group
                    }
                )
        
        # Call the audit function with task_group filter and await the result
        audit_result = asyncio.run(audit_agent_performance(
            agent_id=self.test_agent_id,
            limit=10,
            task_group=task_group
        ))
        
        # Verify the audit result contains only tasks from the special group
        self.assertIsNotNone(audit_result)
        
        # Verify the task report
        task_report = audit_result.get("task_report")
        self.assertIsInstance(task_report, list)
        
        # Check if only our special tasks are in the report
        for task in task_report:
            self.assertIn(task.get("task_id"), special_task_ids)
        
        # Verify the summary counts
        summary = audit_result.get("audit_summary")
        self.assertEqual(summary.get("total_planned"), len(special_task_ids))
        self.assertEqual(summary.get("total_attempted"), 1)
        self.assertEqual(summary.get("successes"), 1)
        self.assertEqual(summary.get("unattempted"), 1)
        
        print(f"✅ Successfully tested audit function with task_group filtering")

if __name__ == "__main__":
    unittest.main()
