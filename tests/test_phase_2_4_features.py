import unittest
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.escalation_manager import EscalationManager, get_escalation_manager
from app.core.behavior_manager import BehaviorManager, get_behavior_manager

class TestEscalationManager(unittest.TestCase):
    """Test the escalation manager"""
    
    def setUp(self):
        """Set up the test"""
        self.escalation_manager = EscalationManager()
        
        # Create a temporary directory for escalation logs
        self.temp_dir = f"/tmp/escalation_logs_{uuid.uuid4()}"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.escalation_manager.log_dir = self.temp_dir
    
    def tearDown(self):
        """Clean up after the test"""
        # Remove the temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    async def test_check_for_escalation_retry_count(self):
        """Test checking for escalation based on retry count"""
        # Test with retry count >= 2
        result = await self.escalation_manager.check_for_escalation(
            agent_name="builder",
            task_description="Create a FastAPI app",
            reflection_data={},
            retry_count=2
        )
        
        # Check that escalation was needed
        self.assertTrue(result.get("escalation_needed", False))
        self.assertEqual(result.get("escalation_reason"), "Exceeded retry limit")
        self.assertIn("escalation_id", result)
        
        # Test with retry count < 2
        result = await self.escalation_manager.check_for_escalation(
            agent_name="builder",
            task_description="Create a FastAPI app",
            reflection_data={},
            retry_count=1
        )
        
        # Check that no escalation was needed
        self.assertEqual(result, {})
    
    async def test_check_for_escalation_patterns(self):
        """Test checking for escalation based on patterns in reflection"""
        # Test with pattern in rationale
        result = await self.escalation_manager.check_for_escalation(
            agent_name="builder",
            task_description="Create a FastAPI app",
            reflection_data={
                "rationale": "I'm stuck on how to implement the authentication",
                "assumptions": "",
                "improvement_suggestions": "",
                "confidence_level": "",
                "failure_points": ""
            }
        )
        
        # Check that escalation was needed
        self.assertTrue(result.get("escalation_needed", False))
        self.assertIn("escalation_id", result)
        
        # Test with pattern in failure points
        result = await self.escalation_manager.check_for_escalation(
            agent_name="builder",
            task_description="Create a FastAPI app",
            reflection_data={
                "rationale": "",
                "assumptions": "",
                "improvement_suggestions": "",
                "confidence_level": "",
                "failure_points": "I need help with the database schema"
            }
        )
        
        # Check that escalation was needed
        self.assertTrue(result.get("escalation_needed", False))
        self.assertIn("escalation_id", result)
        
        # Test without pattern
        result = await self.escalation_manager.check_for_escalation(
            agent_name="builder",
            task_description="Create a FastAPI app",
            reflection_data={
                "rationale": "I provided a basic FastAPI app",
                "assumptions": "The user wants a simple app",
                "improvement_suggestions": "Could add more features",
                "confidence_level": "High confidence",
                "failure_points": "None"
            }
        )
        
        # Check that no escalation was needed
        self.assertEqual(result, {})
    
    async def test_log_escalation(self):
        """Test logging an escalation"""
        from app.core.escalation_manager import EscalationData
        
        # Create escalation data
        escalation_data = EscalationData(
            agent_name="builder",
            task_description="Create a FastAPI app",
            escalation_reason="Exceeded retry limit",
            reflection_data={}
        )
        
        # Log the escalation
        await self.escalation_manager._log_escalation(escalation_data)
        
        # Check that the log file was created
        log_file = os.path.join(self.temp_dir, f"{escalation_data.escalation_id}.json")
        self.assertTrue(os.path.exists(log_file))
        
        # Check the log file content
        with open(log_file, "r") as f:
            log_data = json.load(f)
            self.assertEqual(log_data["agent_name"], "builder")
            self.assertEqual(log_data["task_description"], "Create a FastAPI app")
            self.assertEqual(log_data["escalation_reason"], "Exceeded retry limit")
            self.assertEqual(log_data["status"], "pending")
    
    async def test_forward_escalation(self):
        """Test forwarding an escalation"""
        # Create an escalation
        result = await self.escalation_manager.check_for_escalation(
            agent_name="builder",
            task_description="Create a FastAPI app",
            reflection_data={},
            retry_count=2
        )
        
        escalation_id = result.get("escalation_id")
        
        # Mock the process_agent_request function
        with patch('app.core.escalation_manager.process_agent_request') as mock_process:
            # Forward the escalation
            forward_result = await self.escalation_manager.forward_escalation(
                escalation_id=escalation_id,
                target_agent="ops"
            )
            
            # Check the result
            self.assertEqual(forward_result["escalation_id"], escalation_id)
            self.assertEqual(forward_result["forwarded_to"], "ops")
            self.assertEqual(forward_result["status"], "forwarded")
            
            # Check that the escalation was updated
            escalation = await self.escalation_manager.get_escalation(escalation_id)
            self.assertEqual(escalation.forwarded_to_agent, "ops")
            self.assertEqual(escalation.status, "forwarded")
    
    async def test_resolve_escalation(self):
        """Test resolving an escalation"""
        # Create an escalation
        result = await self.escalation_manager.check_for_escalation(
            agent_name="builder",
            task_description="Create a FastAPI app",
            reflection_data={},
            retry_count=2
        )
        
        escalation_id = result.get("escalation_id")
        
        # Resolve the escalation
        resolve_result = await self.escalation_manager.resolve_escalation(
            escalation_id=escalation_id,
            resolution_notes="Fixed the issue"
        )
        
        # Check the result
        self.assertEqual(resolve_result["escalation_id"], escalation_id)
        self.assertEqual(resolve_result["status"], "resolved")
        
        # Check that the escalation was updated
        escalation = await self.escalation_manager.get_escalation(escalation_id)
        self.assertEqual(escalation.status, "resolved")

class TestBehaviorManager(unittest.TestCase):
    """Test the behavior manager"""
    
    def setUp(self):
        """Set up the test"""
        self.behavior_manager = BehaviorManager()
        
        # Create a temporary directory for behavior logs
        self.temp_dir = f"/tmp/behavior_logs_{uuid.uuid4()}"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.behavior_manager.logs_dir = self.temp_dir
    
    def tearDown(self):
        """Clean up after the test"""
        # Remove the temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    async def test_record_feedback(self):
        """Test recording behavior feedback"""
        # Record feedback
        feedback_id = await self.behavior_manager.record_feedback(
            agent_name="builder",
            task_description="Create a FastAPI app",
            was_successful=True,
            user_notes="Great job!",
            task_metadata={"task_category": "code"}
        )
        
        # Check that the agent directory was created
        agent_dir = os.path.join(self.temp_dir, "builder")
        self.assertTrue(os.path.exists(agent_dir))
        
        # Check that the feedback file was created
        feedback_file = os.path.join(agent_dir, f"{feedback_id}.json")
        self.assertTrue(os.path.exists(feedback_file))
        
        # Check the feedback file content
        with open(feedback_file, "r") as f:
            feedback_data = json.load(f)
            self.assertEqual(feedback_data["agent_name"], "builder")
            self.assertEqual(feedback_data["task_description"], "Create a FastAPI app")
            self.assertTrue(feedback_data["was_successful"])
            self.assertEqual(feedback_data["user_notes"], "Great job!")
            self.assertEqual(feedback_data["task_metadata"]["task_category"], "code")
    
    async def test_get_agent_feedback(self):
        """Test getting agent feedback"""
        # Record some feedback
        feedback_id1 = await self.behavior_manager.record_feedback(
            agent_name="builder",
            task_description="Create a FastAPI app",
            was_successful=True,
            user_notes="Great job!"
        )
        
        feedback_id2 = await self.behavior_manager.record_feedback(
            agent_name="builder",
            task_description="Fix a bug",
            was_successful=False,
            user_notes="Needs improvement"
        )
        
        # Get all feedback
        all_feedback = await self.behavior_manager.get_agent_feedback("builder")
        self.assertEqual(len(all_feedback), 2)
        
        # Get successful feedback only
        successful_feedback = await self.behavior_manager.get_agent_feedback("builder", successful_only=True)
        self.assertEqual(len(successful_feedback), 1)
        self.assertEqual(successful_feedback[0]["task_description"], "Create a FastAPI app")
        
        # Get unsuccessful feedback only
        unsuccessful_feedback = await self.behavior_manager.get_agent_feedback("builder", successful_only=False)
        self.assertEqual(len(unsuccessful_feedback), 1)
        self.assertEqual(unsuccessful_feedback[0]["task_description"], "Fix a bug")
    
    async def test_get_feedback_summary(self):
        """Test getting feedback summary"""
        # Record some feedback
        await self.behavior_manager.record_feedback(
            agent_name="builder",
            task_description="Create a FastAPI app",
            was_successful=True
        )
        
        await self.behavior_manager.record_feedback(
            agent_name="builder",
            task_description="Fix a bug",
            was_successful=False
        )
        
        await self.behavior_manager.record_feedback(
            agent_name="builder",
            task_description="Add a feature",
            was_successful=True
        )
        
        # Get the summary
        summary = await self.behavior_manager.get_feedback_summary("builder")
        
        # Check the summary
        self.assertEqual(summary["agent_name"], "builder")
        self.assertEqual(summary["total_tasks"], 3)
        self.assertAlmostEqual(summary["success_rate"], 2/3)
        self.assertTrue(summary["has_feedback"])
        
        # Test with no feedback
        empty_summary = await self.behavior_manager.get_feedback_summary("nonexistent")
        self.assertEqual(empty_summary["total_tasks"], 0)
        self.assertEqual(empty_summary["success_rate"], 0.0)
        self.assertFalse(empty_summary["has_feedback"])
    
    async def test_get_recent_feedback_context(self):
        """Test getting recent feedback context"""
        # Record some feedback
        await self.behavior_manager.record_feedback(
            agent_name="builder",
            task_description="Create a FastAPI app",
            was_successful=True,
            user_notes="Great job!"
        )
        
        await self.behavior_manager.record_feedback(
            agent_name="builder",
            task_description="Fix a bug",
            was_successful=False,
            user_notes="Needs improvement"
        )
        
        # Get the context
        context = await self.behavior_manager.get_recent_feedback_context("builder")
        
        # Check the context
        self.assertIn("Recent Behavior Feedback", context)
        self.assertIn("Create a FastAPI app", context)
        self.assertIn("Fix a bug", context)
        self.assertIn("Great job!", context)
        self.assertIn("Needs improvement", context)
        self.assertIn("Success rate:", context)
        
        # Test with no feedback
        empty_context = await self.behavior_manager.get_recent_feedback_context("nonexistent")
        self.assertEqual(empty_context, "")

def run_tests():
    """Run the tests"""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the test cases
    test_suite.addTest(unittest.makeSuite(TestEscalationManager))
    test_suite.addTest(unittest.makeSuite(TestBehaviorManager))
    
    # Run the tests
    runner = unittest.TextTestRunner()
    runner.run(test_suite)

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_tests())
