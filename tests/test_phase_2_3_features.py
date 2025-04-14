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

from app.core.confidence_retry import ConfidenceRetryManager, get_confidence_retry_manager
from app.core.nudge_manager import NudgeManager, get_nudge_manager
from app.core.task_persistence import TaskPersistenceManager, get_task_persistence_manager, PendingTask

class TestConfidenceRetryManager(unittest.TestCase):
    """Test the confidence retry manager"""
    
    def setUp(self):
        """Set up the test"""
        self.retry_manager = ConfidenceRetryManager(confidence_threshold=0.6)
    
    def test_parse_confidence_percentage(self):
        """Test parsing confidence from percentage format"""
        self.assertEqual(self.retry_manager._parse_confidence("90%"), 0.9)
        self.assertEqual(self.retry_manager._parse_confidence("75 percent"), 0.75)
        self.assertEqual(self.retry_manager._parse_confidence("50% confidence"), 0.5)
    
    def test_parse_confidence_out_of_ten(self):
        """Test parsing confidence from X/10 format"""
        self.assertEqual(self.retry_manager._parse_confidence("7/10"), 0.7)
        self.assertEqual(self.retry_manager._parse_confidence("8 out of 10"), 0.8)
        self.assertEqual(self.retry_manager._parse_confidence("3/10 confidence"), 0.3)
    
    def test_parse_confidence_out_of_five(self):
        """Test parsing confidence from X/5 format"""
        self.assertEqual(self.retry_manager._parse_confidence("4/5"), 0.8)
        self.assertEqual(self.retry_manager._parse_confidence("2 out of 5"), 0.4)
        self.assertEqual(self.retry_manager._parse_confidence("1/5 confidence"), 0.2)
    
    def test_parse_confidence_descriptive(self):
        """Test parsing confidence from descriptive terms"""
        self.assertEqual(self.retry_manager._parse_confidence("high confidence"), 0.9)
        self.assertEqual(self.retry_manager._parse_confidence("medium confidence"), 0.6)
        self.assertEqual(self.retry_manager._parse_confidence("low confidence"), 0.2)
        self.assertEqual(self.retry_manager._parse_confidence("very confident"), 0.9)
        self.assertEqual(self.retry_manager._parse_confidence("somewhat confident"), 0.4)
        self.assertEqual(self.retry_manager._parse_confidence("not very confident"), 0.2)
    
    @patch('app.core.confidence_retry.process_with_model')
    @patch('app.core.confidence_retry.SelfEvaluationPrompt.generate_self_evaluation')
    @patch('app.core.confidence_retry.PromptManager')
    async def test_trigger_retry(self, mock_prompt_manager, mock_generate_self_evaluation, mock_process_with_model):
        """Test triggering a retry"""
        # Mock the prompt manager
        mock_prompt_manager_instance = MagicMock()
        mock_prompt_manager.return_value = mock_prompt_manager_instance
        mock_prompt_manager_instance.get_prompt_chain.return_value = {"system": "You are a helpful assistant"}
        
        # Mock the self-evaluation
        mock_generate_self_evaluation.return_value = {"confidence_level": "High confidence (90%)"}
        
        # Mock the model processing
        mock_process_with_model.return_value = {"content": "Improved response"}
        
        # Test triggering a retry
        retry_data = await self.retry_manager._trigger_retry(
            agent_type="builder",
            model="gpt-4",
            input_text="Create a FastAPI app",
            output_text="Here's a basic FastAPI app",
            confidence_level="Low confidence (40%)",
            reflection_data={"failure_points": "Not enough details"}
        )
        
        # Check that the retry was triggered
        self.assertTrue(retry_data.get("retry_triggered", False))
        self.assertEqual(retry_data.get("original_confidence"), "Low confidence (40%)")
        self.assertEqual(retry_data.get("retry_confidence"), "High confidence (90%)")
        self.assertEqual(retry_data.get("retry_response"), "Improved response")
    
    @patch('app.core.confidence_retry.ConfidenceRetryManager._trigger_retry')
    async def test_check_confidence_below_threshold(self, mock_trigger_retry):
        """Test checking confidence below threshold"""
        # Mock the trigger retry
        mock_trigger_retry.return_value = {"retry_triggered": True}
        
        # Test checking confidence below threshold
        result = await self.retry_manager.check_confidence(
            confidence_level="Low confidence (40%)",
            agent_type="builder",
            model="gpt-4",
            input_text="Create a FastAPI app",
            output_text="Here's a basic FastAPI app",
            reflection_data={"failure_points": "Not enough details"}
        )
        
        # Check that the retry was triggered
        self.assertTrue(result.get("retry_triggered", False))
        mock_trigger_retry.assert_called_once()
    
    async def test_check_confidence_above_threshold(self):
        """Test checking confidence above threshold"""
        # Test checking confidence above threshold
        result = await self.retry_manager.check_confidence(
            confidence_level="High confidence (90%)",
            agent_type="builder",
            model="gpt-4",
            input_text="Create a FastAPI app",
            output_text="Here's a basic FastAPI app",
            reflection_data={"failure_points": "Not enough details"}
        )
        
        # Check that the retry was not triggered
        self.assertEqual(result, {})

class TestNudgeManager(unittest.TestCase):
    """Test the nudge manager"""
    
    def setUp(self):
        """Set up the test"""
        self.nudge_manager = NudgeManager()
        
        # Create a temporary directory for nudge logs
        self.temp_dir = f"/tmp/nudge_logs_{uuid.uuid4()}"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.nudge_manager.log_dir = self.temp_dir
    
    def tearDown(self):
        """Clean up after the test"""
        # Remove the temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_determine_nudge_reason(self):
        """Test determining the nudge reason"""
        self.assertEqual(self.nudge_manager._determine_nudge_reason("i am unsure"), "uncertainty")
        self.assertEqual(self.nudge_manager._determine_nudge_reason("user input needed"), "needs_information")
        self.assertEqual(self.nudge_manager._determine_nudge_reason("blocked"), "blocked")
        self.assertEqual(self.nudge_manager._determine_nudge_reason("other"), "general_assistance")
    
    def test_create_nudge_message(self):
        """Test creating a nudge message"""
        # Test uncertainty nudge
        uncertainty_message = self.nudge_manager._create_nudge_message(
            nudge_reason="uncertainty",
            agent_name="builder",
            reflection_data={"failure_points": "uncertain about the database schema"}
        )
        self.assertIn("uncertain", uncertainty_message.lower())
        self.assertIn("database schema", uncertainty_message.lower())
        
        # Test needs information nudge
        needs_info_message = self.nudge_manager._create_nudge_message(
            nudge_reason="needs_information",
            agent_name="builder",
            reflection_data={"failure_points": "missing information about the API endpoints"}
        )
        self.assertIn("information", needs_info_message.lower())
        self.assertIn("api endpoints", needs_info_message.lower())
        
        # Test blocked nudge
        blocked_message = self.nudge_manager._create_nudge_message(
            nudge_reason="blocked",
            agent_name="builder",
            reflection_data={"failure_points": "blocked by authentication requirements"}
        )
        self.assertIn("blocked", blocked_message.lower())
        self.assertIn("authentication requirements", blocked_message.lower())
        
        # Test general assistance nudge
        general_message = self.nudge_manager._create_nudge_message(
            nudge_reason="general_assistance",
            agent_name="builder",
            reflection_data={}
        )
        self.assertIn("input", general_message.lower())
    
    async def test_check_for_nudge_with_pattern(self):
        """Test checking for nudge with pattern in reflection"""
        # Test with pattern in rationale
        result = await self.nudge_manager.check_for_nudge(
            agent_name="builder",
            input_text="Create a FastAPI app",
            output_text="Here's a basic FastAPI app",
            reflection_data={
                "rationale": "I am unsure about the specific requirements",
                "assumptions": "",
                "improvement_suggestions": "",
                "confidence_level": "",
                "failure_points": ""
            }
        )
        
        # Check that a nudge was needed
        self.assertTrue(result.get("nudge_needed", False))
        self.assertIn("nudge_message", result)
        self.assertEqual(result.get("nudge_reason"), "uncertainty")
        
        # Test with pattern in output
        result = await self.nudge_manager.check_for_nudge(
            agent_name="builder",
            input_text="Create a FastAPI app",
            output_text="I need more information about the database schema",
            reflection_data={
                "rationale": "",
                "assumptions": "",
                "improvement_suggestions": "",
                "confidence_level": "",
                "failure_points": ""
            }
        )
        
        # Check that a nudge was needed
        self.assertTrue(result.get("nudge_needed", False))
        self.assertIn("nudge_message", result)
        self.assertEqual(result.get("nudge_reason"), "needs_information")
    
    async def test_check_for_nudge_without_pattern(self):
        """Test checking for nudge without pattern"""
        # Test without pattern
        result = await self.nudge_manager.check_for_nudge(
            agent_name="builder",
            input_text="Create a FastAPI app",
            output_text="Here's a basic FastAPI app",
            reflection_data={
                "rationale": "I provided a basic FastAPI app",
                "assumptions": "The user wants a simple app",
                "improvement_suggestions": "Could add more features",
                "confidence_level": "High confidence",
                "failure_points": "None"
            }
        )
        
        # Check that no nudge was needed
        self.assertEqual(result, {})
    
    async def test_log_nudge(self):
        """Test logging a nudge"""
        from app.core.nudge_manager import NudgeData
        
        # Create a nudge data
        nudge_data = NudgeData(
            agent_name="builder",
            input_text="Create a FastAPI app",
            output_text="Here's a basic FastAPI app",
            reflection_data={},
            nudge_message="I need more information",
            nudge_reason="needs_information"
        )
        
        # Log the nudge
        await self.nudge_manager._log_nudge(nudge_data)
        
        # Check that the log file was created
        log_file = os.path.join(self.temp_dir, f"{nudge_data.nudge_id}.json")
        self.assertTrue(os.path.exists(log_file))
        
        # Check the log file content
        with open(log_file, "r") as f:
            log_data = json.load(f)
            self.assertEqual(log_data["agent_name"], "builder")
            self.assertEqual(log_data["nudge_message"], "I need more information")
            self.assertEqual(log_data["nudge_reason"], "needs_information")

class TestTaskPersistenceManager(unittest.TestCase):
    """Test the task persistence manager"""
    
    def setUp(self):
        """Set up the test"""
        self.task_manager = TaskPersistenceManager()
        
        # Create a temporary directory for pending tasks
        self.temp_dir = f"/tmp/pending_tasks_{uuid.uuid4()}"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.task_manager.tasks_dir = self.temp_dir
    
    def tearDown(self):
        """Clean up after the test"""
        # Remove the temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    async def test_store_pending_task(self):
        """Test storing a pending task"""
        # Store a pending task
        task_id = await self.task_manager.store_pending_task(
            task_description="Deploy the FastAPI app",
            origin_agent="builder",
            suggested_agent="ops",
            priority=True,
            metadata={"task_category": "deployment"},
            original_input="Create and deploy a FastAPI app",
            original_output="Here's a basic FastAPI app"
        )
        
        # Check that the task file was created
        task_file = os.path.join(self.temp_dir, f"{task_id}.json")
        self.assertTrue(os.path.exists(task_file))
        
        # Check the task file content
        with open(task_file, "r") as f:
            task_data = json.load(f)
            self.assertEqual(task_data["task_description"], "Deploy the FastAPI app")
            self.assertEqual(task_data["origin_agent"], "builder")
            self.assertEqual(task_data["suggested_agent"], "ops")
            self.assertTrue(task_data["priority"])
            self.assertEqual(task_data["metadata"]["task_category"], "deployment")
            self.assertEqual(task_data["original_input"], "Create and deploy a FastAPI app")
            self.assertEqual(task_data["original_output"], "Here's a basic FastAPI app")
            self.assertEqual(task_data["status"], "pending")
    
    async def test_get_pending_tasks(self):
        """Test getting pending tasks"""
        # Store some pending tasks
        task_id1 = await self.task_manager.store_pending_task(
            task_description="Deploy the FastAPI app",
            origin_agent="builder",
            suggested_agent="ops",
            priority=True
        )
        
        task_id2 = await self.task_manager.store_pending_task(
            task_description="Document the API",
            origin_agent="builder",
            suggested_agent="research",
            priority=False
        )
        
        # Get all pending tasks
        tasks = await self.task_manager.get_pending_tasks()
        self.assertEqual(len(tasks), 2)
        
        # Get tasks by origin agent
        builder_tasks = await self.task_manager.get_pending_tasks(origin_agent="builder")
        self.assertEqual(len(builder_tasks), 2)
        
        # Get tasks by suggested agent
        ops_tasks = await self.task_manager.get_pending_tasks(suggested_agent="ops")
        self.assertEqual(len(ops_tasks), 1)
        self.assertEqual(ops_tasks[0].task_description, "Deploy the FastAPI app")
        
        research_tasks = await self.task_manager.get_pending_tasks(suggested_agent="research")
        self.assertEqual(len(research_tasks), 1)
        self.assertEqual(research_tasks[0].task_description, "Document the API")
    
    async def test_get_task(self):
        """Test getting a specific task"""
        # Store a pending task
        task_id = await self.task_manager.store_pending_task(
            task_description="Deploy the FastAPI app",
            origin_agent="builder",
            suggested_agent="ops",
            priority=True
        )
        
        # Get the task
        task = await self.task_manager.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, task_id)
        self.assertEqual(task.task_description, "Deploy the FastAPI app")
        self.assertEqual(task.origin_agent, "builder")
        self.assertEqual(task.suggested_agent, "ops")
        self.assertTrue(task.priority)
        self.assertEqual(task.status, "pending")
        
        # Get a non-existent task
        non_existent_task = await self.task_manager.get_task("non-existent-id")
        self.assertIsNone(non_existent_task)
    
    async def test_update_task_status(self):
        """Test updating task status"""
        # Store a pending task
        task_id = await self.task_manager.store_pending_task(
            task_description="Deploy the FastAPI app",
            origin_agent="builder",
            suggested_agent="ops",
            priority=True
        )
        
        # Update the task status
        updated_task = await self.task_manager.update_task_status(
            task_id=task_id,
            status="executed",
            metadata={"execution_timestamp": datetime.now().isoformat()}
        )
        
        # Check that the task was updated
        self.assertEqual(updated_task.status, "executed")
        self.assertIn("execution_timestamp", updated_task.metadata)
        
        # Get the task again to verify persistence
        task = await self.task_manager.get_task(task_id)
        self.assertEqual(task.status, "executed")
        self.assertIn("execution_timestamp", task.metadata)

def run_tests():
    """Run the tests"""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the test cases
    test_suite.addTest(unittest.makeSuite(TestConfidenceRetryManager))
    test_suite.addTest(unittest.makeSuite(TestNudgeManager))
    test_suite.addTest(unittest.makeSuite(TestTaskPersistenceManager))
    
    # Run the tests
    runner = unittest.TextTestRunner()
    runner.run(test_suite)

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_tests())
