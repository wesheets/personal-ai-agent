"""
Tests for the plan from prompt module.

This module contains tests for the plan from prompt module to ensure it correctly
converts natural language prompts into structured loop plans.
"""

import unittest
import json
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.plan_from_prompt import (
    generate_plan_from_prompt,
    plan_from_prompt_driver,
    extract_goals,
    determine_agents,
    predict_files,
    predict_tools
)

class TestPlanFromPrompt(unittest.TestCase):
    """Test cases for the plan from prompt module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample prompts for testing
        self.valid_prompt_1 = "Create a React component for a user profile page with avatar, name, and bio."
        self.valid_prompt_2 = "Build an API endpoint for user authentication with login and registration."
        self.valid_prompt_3 = "Generate a report analyzing user engagement data from the last quarter."
        self.invalid_prompt = ""  # Empty prompt
        self.ambiguous_prompt = "do it"  # Too ambiguous
        
        # Mock project ID
        self.project_id = "test_project_001"
        
        # Mock loop ID
        self.loop_id = 28
        
    def test_extract_goals(self):
        """Test that goals are correctly extracted from prompts."""
        goals = extract_goals(self.valid_prompt_1)
        self.assertGreater(len(goals), 0, "Should extract at least one goal from valid prompt")
        
        goals = extract_goals(self.valid_prompt_2)
        self.assertGreater(len(goals), 0, "Should extract at least one goal from valid prompt")
        
        goals = extract_goals(self.invalid_prompt)
        self.assertEqual(len(goals), 0, "Should extract no goals from invalid prompt")
    
    def test_determine_agents(self):
        """Test that appropriate agents are determined based on prompt content."""
        # UI/Frontend task
        agents = determine_agents(self.valid_prompt_1)
        self.assertIn("nova", agents, "UI task should include Nova agent")
        self.assertGreaterEqual(len(agents), 3, "Should include at least 3 agents")
        
        # Backend task
        agents = determine_agents(self.valid_prompt_2)
        self.assertIn("hal", agents, "API task should include Hal agent")
        self.assertGreaterEqual(len(agents), 3, "Should include at least 3 agents")
        
        # Analysis task
        agents = determine_agents(self.valid_prompt_3)
        self.assertIn("critic", agents, "Analysis task should include Critic agent")
        self.assertGreaterEqual(len(agents), 3, "Should include at least 3 agents")
    
    def test_predict_files(self):
        """Test that appropriate files are predicted based on prompt content."""
        # UI/Frontend task
        files = predict_files(self.valid_prompt_1)
        self.assertGreater(len(files), 0, "Should predict at least one file")
        self.assertTrue(any(".jsx" in file or ".js" in file or ".css" in file for file in files), 
                      "UI task should predict frontend files")
        
        # Backend task
        files = predict_files(self.valid_prompt_2)
        self.assertGreater(len(files), 0, "Should predict at least one file")
        self.assertTrue(any(".js" in file or ".py" in file for file in files), 
                      "API task should predict backend files")
        
        # Analysis task
        files = predict_files(self.valid_prompt_3)
        self.assertGreater(len(files), 0, "Should predict at least one file")
        self.assertTrue(any(".md" in file or ".py" in file for file in files), 
                      "Analysis task should predict report files")
    
    def test_predict_tools(self):
        """Test that appropriate tools are predicted based on prompt content."""
        # UI task might need form_builder
        tools = predict_tools("Create a form for user registration with validation")
        self.assertIn("form_builder", tools, "Form task should predict form_builder tool")
        
        # Data visualization task might need chart_generator
        tools = predict_tools("Create a dashboard with charts showing user activity")
        self.assertIn("chart_generator", tools, "Chart task should predict chart_generator tool")
        
        # Empty prompt should predict no tools
        tools = predict_tools("")
        self.assertEqual(len(tools), 0, "Empty prompt should predict no tools")
    
    def test_generate_plan_from_valid_prompt(self):
        """Test generating a plan from a valid prompt."""
        plan = generate_plan_from_prompt(self.valid_prompt_1, self.loop_id)
        
        # Verify plan structure
        self.assertEqual(plan["loop_id"], self.loop_id, "Plan should have correct loop_id")
        self.assertGreater(len(plan["agents"]), 0, "Plan should have agents")
        self.assertGreater(len(plan["goals"]), 0, "Plan should have goals")
        self.assertGreater(len(plan["planned_files"]), 0, "Plan should have planned files")
        self.assertFalse(plan["confirmed"], "New plan should not be confirmed")
        self.assertIsNone(plan["confirmed_by"], "New plan should have no confirmer")
        self.assertIsNone(plan["confirmed_at"], "New plan should have no confirmation time")
        self.assertIn("timestamp", plan, "Plan should have a timestamp")
    
    def test_generate_plan_from_invalid_prompt(self):
        """Test that generating a plan from an invalid prompt raises an error."""
        with self.assertRaises(ValueError):
            generate_plan_from_prompt(self.invalid_prompt, self.loop_id)
        
        with self.assertRaises(ValueError):
            generate_plan_from_prompt(self.ambiguous_prompt, self.loop_id)
    
    @patch('orchestrator.modules.plan_from_prompt.log_to_memory')
    @patch('orchestrator.modules.plan_from_prompt.log_to_chat')
    @patch('orchestrator.modules.plan_from_prompt.log_to_sandbox')
    @patch('orchestrator.modules.plan_from_prompt.validate_and_log')
    def test_plan_from_prompt_driver_valid(self, mock_validate, mock_log_sandbox, 
                                         mock_log_chat, mock_log_memory):
        """Test the plan_from_prompt_driver with a valid prompt."""
        # Mock the validate_and_log function to return valid
        mock_validate.return_value = (True, [], {"trace_id": "loop_28_plan", 
                                               "action": "plan_validated",
                                               "status": "passed",
                                               "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
        
        # Call the driver with a valid prompt
        result = plan_from_prompt_driver(self.project_id, self.valid_prompt_1)
        
        # Verify result
        self.assertIsNotNone(result, "Driver should return a plan for valid prompt")
        self.assertEqual(result["confirmed"], False, "Plan should not be confirmed")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 2, "Should log to memory twice")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        self.assertEqual(mock_log_sandbox.call_count, 1, "Should log to sandbox once")
    
    @patch('orchestrator.modules.plan_from_prompt.log_to_memory')
    @patch('orchestrator.modules.plan_from_prompt.log_to_chat')
    @patch('orchestrator.modules.plan_from_prompt.validate_and_log')
    def test_plan_from_prompt_driver_invalid(self, mock_validate, mock_log_chat, mock_log_memory):
        """Test the plan_from_prompt_driver with an invalid prompt."""
        # Mock the validate_and_log function to return invalid
        mock_validate.return_value = (False, ["Error: Invalid plan"], {"trace_id": "loop_28_plan", 
                                                                    "action": "plan_validated",
                                                                    "status": "failed",
                                                                    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                                                                    "errors": ["Error: Invalid plan"]})
        
        # Call the driver with a valid prompt (validation will fail due to our mock)
        result = plan_from_prompt_driver(self.project_id, self.valid_prompt_1)
        
        # Verify result
        self.assertIsNone(result, "Driver should return None for invalid plan")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 2, "Should log to memory twice")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once with error")
    
    @patch('orchestrator.modules.plan_from_prompt.log_to_memory')
    @patch('orchestrator.modules.plan_from_prompt.log_to_chat')
    def test_plan_from_prompt_driver_error(self, mock_log_chat, mock_log_memory):
        """Test the plan_from_prompt_driver with an error-causing prompt."""
        # Call the driver with an invalid prompt
        result = plan_from_prompt_driver(self.project_id, self.invalid_prompt)
        
        # Verify result
        self.assertIsNone(result, "Driver should return None for error")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once with error")

if __name__ == "__main__":
    unittest.main()
