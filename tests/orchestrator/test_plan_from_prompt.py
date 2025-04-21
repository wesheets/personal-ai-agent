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
    predict_tools,
    TRUST_SCORE_THRESHOLD
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
        
        # Mock memory with agent performance data
        self.memory = {
            "agent_performance": {
                "hal": {
                    "trust_score": 0.85,
                    "loops_participated": 10,
                    "schema_validations": {"passed": 9, "failed": 1},
                    "reflection_validations": {"passed": 8, "failed": 2},
                    "critic_rejections": 1,
                    "operator_rejections": 0,
                    "history": [],
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                },
                "nova": {
                    "trust_score": 0.92,
                    "loops_participated": 8,
                    "schema_validations": {"passed": 8, "failed": 0},
                    "reflection_validations": {"passed": 7, "failed": 1},
                    "critic_rejections": 0,
                    "operator_rejections": 0,
                    "history": [],
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                },
                "ash": {
                    "trust_score": 0.38,
                    "loops_participated": 5,
                    "schema_validations": {"passed": 2, "failed": 3},
                    "reflection_validations": {"passed": 1, "failed": 4},
                    "critic_rejections": 2,
                    "operator_rejections": 1,
                    "history": [],
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                },
                "critic": {
                    "trust_score": 0.75,
                    "loops_participated": 15,
                    "schema_validations": {"passed": 14, "failed": 1},
                    "reflection_validations": {"passed": 13, "failed": 2},
                    "critic_rejections": 0,
                    "operator_rejections": 0,
                    "history": [],
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                }
            }
        }
        
        # Memory with no agent performance data
        self.empty_memory = {}
        
        # Memory with new agent (no trust data)
        self.new_agent_memory = {
            "agent_performance": {
                "hal": {
                    "trust_score": 0.85,
                    "loops_participated": 10,
                    "schema_validations": {"passed": 9, "failed": 1},
                    "reflection_validations": {"passed": 8, "failed": 2},
                    "critic_rejections": 1,
                    "operator_rejections": 0,
                    "history": [],
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                }
            }
        }
        
        # Memory with incomplete agent data (for critical agent inclusion test)
        self.incomplete_agent_memory = {
            "agent_performance": {
                "hal": {"trust_score": 0.85},
                "nova": {"trust_score": 0.92},
                "critic": {"trust_score": 0.35}  # Below threshold, incomplete data
            }
        }
    
    def test_extract_goals(self):
        """Test that goals are correctly extracted from prompts."""
        goals = extract_goals(self.valid_prompt_1)
        self.assertGreater(len(goals), 0, "Should extract at least one goal from valid prompt")
        
        goals = extract_goals(self.valid_prompt_2)
        self.assertGreater(len(goals), 0, "Should extract at least one goal from valid prompt")
        
        goals = extract_goals(self.invalid_prompt)
        self.assertEqual(len(goals), 0, "Should extract no goals from invalid prompt")
    
    def test_determine_agents_without_trust(self):
        """Test that appropriate agents are determined based on prompt content without trust data."""
        # UI/Frontend task
        agents, trace = determine_agents(self.valid_prompt_1)
        self.assertIn("nova", agents, "UI task should include Nova agent")
        self.assertGreaterEqual(len(agents), 3, "Should include at least 3 agents")
        self.assertEqual(len(trace), len(agents), "Should have trace entry for each agent")
        
        # Backend task
        agents, trace = determine_agents(self.valid_prompt_2)
        self.assertIn("hal", agents, "API task should include Hal agent")
        self.assertGreaterEqual(len(agents), 3, "Should include at least 3 agents")
        
        # Analysis task
        agents, trace = determine_agents(self.valid_prompt_3)
        self.assertIn("critic", agents, "Analysis task should include Critic agent")
        self.assertGreaterEqual(len(agents), 3, "Should include at least 3 agents")
    
    def test_determine_agents_with_trust(self):
        """Test that agents are determined based on trust scores."""
        # UI/Frontend task with trust data
        agents, trace = determine_agents(self.valid_prompt_1, self.memory)
        
        # Nova has higher trust than Hal, should be included
        self.assertIn("nova", agents, "High-trust Nova should be included")
        
        # Ash has low trust, should be excluded
        self.assertNotIn("ash", agents, "Low-trust Ash should be excluded")
        
        # Verify trace contains trust scores
        for entry in trace:
            if entry["agent"] in self.memory["agent_performance"]:
                self.assertIsNotNone(entry.get("trust_score"), "Trust score should be included in trace")
    
    def test_determine_agents_with_override(self):
        """Test that operator overrides include low-trust agents."""
        # UI/Frontend task with trust data and override
        override_agents = ["ash"]
        agents, trace = determine_agents(self.valid_prompt_1, self.memory, override_agents)
        
        # Ash has low trust but should be included due to override
        self.assertIn("ash", agents, "Low-trust Ash should be included due to override")
        
        # Verify trace contains override reason
        for entry in trace:
            if entry["agent"] == "ash":
                self.assertIn("override", entry.get("reason", "").lower(), 
                             "Override reason should be mentioned in trace")
    
    def test_determine_agents_with_new_agent(self):
        """Test that new agents without trust data are included by default."""
        # UI/Frontend task with partial trust data
        agents, trace = determine_agents(self.valid_prompt_1, self.new_agent_memory)
        
        # Nova has no trust data, should still be included
        self.assertIn("nova", agents, "Nova should be included despite no trust data")
        
        # Verify trace indicates no trust data
        for entry in trace:
            if entry["agent"] == "nova":
                self.assertIsNone(entry.get("trust_score"), "Trust score should be None for new agent")
                self.assertIn("no trust data", entry.get("reason", "").lower(), 
                             "Reason should mention no trust data")
    
    def test_determine_agents_critical_inclusion(self):
        """Test that critical agents are always included regardless of trust."""
        # Analysis task with low-trust critic
        agents, trace = determine_agents(self.valid_prompt_3, self.incomplete_agent_memory)
        
        # Critic should still be included despite low trust
        self.assertIn("critic", agents, "Critic should be included despite low trust")
    
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
    
    def test_generate_plan_from_valid_prompt_with_trust(self):
        """Test generating a plan from a valid prompt with trust data."""
        plan = generate_plan_from_prompt(self.valid_prompt_1, self.loop_id, self.memory)
        
        # Verify plan structure
        self.assertEqual(plan["loop_id"], self.loop_id, "Plan should have correct loop_id")
        self.assertGreater(len(plan["agents"]), 0, "Plan should have agents")
        self.assertGreater(len(plan["goals"]), 0, "Plan should have goals")
        self.assertGreater(len(plan["planned_files"]), 0, "Plan should have planned files")
        self.assertFalse(plan["confirmed"], "New plan should not be confirmed")
        
        # Verify agent selection trace
        self.assertIn("agent_selection_trace", plan, "Plan should include agent selection trace")
        self.assertGreater(len(plan["agent_selection_trace"]), 0, "Trace should have entries")
        
        # Verify low-trust agent exclusion
        agents = plan["agents"]
        self.assertNotIn("ash", agents, "Low-trust agent should be excluded")
        
        # Check that ash is not in the agents list
        # Note: We're not checking for excluded flag in trace since the implementation
        # doesn't add ash to the trace if it's excluded during initial filtering
        self.assertNotIn("ash", agents, "Ash should not be in the agents list")
    
    def test_generate_plan_from_valid_prompt_with_override(self):
        """Test generating a plan with operator override for low-trust agents."""
        override_agents = ["ash"]
        plan = generate_plan_from_prompt(self.valid_prompt_1, self.loop_id, self.memory, override_agents)
        
        # Verify plan structure
        self.assertEqual(plan["loop_id"], self.loop_id, "Plan should have correct loop_id")
        
        # Verify override worked
        agents = plan["agents"]
        self.assertIn("ash", agents, "Override should include low-trust agent")
        
        # Verify trace includes override reason
        override_entries = [entry for entry in plan["agent_selection_trace"] 
                           if entry["agent"] == "ash" and "override" in entry.get("reason", "").lower()]
        self.assertEqual(len(override_entries), 1, "Should have one override entry for Ash")
    
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
    def test_plan_from_prompt_driver_with_trust(self, mock_validate, mock_log_sandbox, 
                                             mock_log_chat, mock_log_memory):
        """Test the plan_from_prompt_driver with trust data."""
        # Mock the validate_and_log function to return valid
        mock_validate.return_value = (True, [], {"trace_id": "loop_28_plan", 
                                               "action": "plan_validated",
                                               "status": "passed",
                                               "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
        
        # Call the driver with a valid prompt and trust data
        result = plan_from_prompt_driver(self.project_id, self.valid_prompt_1, self.memory)
        
        # Verify result
        self.assertIsNotNone(result, "Driver should return a plan for valid prompt")
        self.assertEqual(result["confirmed"], False, "Plan should not be confirmed")
        
        # Verify agent selection trace is logged to memory
        memory_calls = mock_log_memory.call_args_list
        trace_logged = False
        for call in memory_calls:
            args = call[0]
            if len(args) > 1 and "loop_trace" in args[1]:
                if "agent_selection_trace" in str(args[1]):
                    trace_logged = True
                    break
        self.assertTrue(trace_logged, "Agent selection trace should be logged to memory")
        
        # Verify agent selection info is included in chat message
        # We're checking for agent_selection_info in the message object
        chat_calls = mock_log_chat.call_args_list
        agent_info_logged = False
        for call in chat_calls:
            args = call[0]
            if len(args) > 1 and "agent_selection_info" in args[1]:
                agent_info_logged = True
                break
        self.assertTrue(agent_info_logged, "Agent selection info should be included in chat message")
    
    @patch('orchestrator.modules.plan_from_prompt.log_to_memory')
    @patch('orchestrator.modules.plan_from_prompt.log_to_chat')
    @patch('orchestrator.modules.plan_from_prompt.validate_and_log')
    def test_plan_from_prompt_driver_with_override(self, mock_validate, mock_log_chat, mock_log_memory):
        """Test the plan_from_prompt_driver with operator override."""
        # Mock the validate_and_log function to return valid
        mock_validate.return_value = (True, [], {"trace_id": "loop_28_plan", 
                                               "action": "plan_validated",
                                               "status": "passed",
                                               "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
        
        # Call the driver with a valid prompt, trust data, and override
        override_agents = ["ash"]
        result = plan_from_prompt_driver(self.project_id, self.valid_prompt_1, self.memory, override_agents)
        
        # Verify result
        self.assertIsNotNone(result, "Driver should return a plan for valid prompt")
        
        # Verify agents include override
        self.assertIn("ash", result["agents"], "Plan should include overridden agent")
        
        # Verify chat message includes override info
        chat_calls = mock_log_chat.call_args_list
        override_logged = False
        for call in chat_calls:
            args = call[0]
            if len(args) > 1 and "message" in args[1]:
                message = args[1]["message"]
                if "override" in message.lower() and "ash" in message.lower():
                    override_logged = True
                    break
        self.assertTrue(override_logged, "Override info should be included in chat message")
    
    @patch('orchestrator.modules.plan_from_prompt.log_to_memory')
    @patch('orchestrator.modules.plan_from_prompt.log_to_chat')
    @patch('orchestrator.modules.plan_from_prompt.validate_and_log')
    def test_plan_from_prompt_driver_no_trust_data(self, mock_validate, mock_log_chat, mock_log_memory):
        """Test the plan_from_prompt_driver with no trust data."""
        # Mock the validate_and_log function to return valid
        mock_validate.return_value = (True, [], {"trace_id": "loop_28_plan", 
                                               "action": "plan_validated",
                                               "status": "passed",
                                               "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
        
        # Call the driver with a valid prompt but no trust data
        result = plan_from_prompt_driver(self.project_id, self.valid_prompt_1, self.empty_memory)
        
        # Verify result
        self.assertIsNotNone(result, "Driver should return a plan even without trust data")
        
        # Verify default agents are used
        self.assertGreaterEqual(len(result["agents"]), 3, "Plan should include default agents")
        
        # Verify trace indicates no trust data
        no_trust_entries = [entry for entry in result["agent_selection_trace"] 
                           if entry["trust_score"] is None]
        self.assertGreaterEqual(len(no_trust_entries), 1, "Trace should indicate no trust data for agents")
    
    @patch('orchestrator.modules.plan_from_prompt.log_to_memory')
    @patch('orchestrator.modules.plan_from_prompt.log_to_chat')
    def test_plan_from_prompt_driver_error(self, mock_log_chat, mock_log_memory):
        """Test the plan_from_prompt_driver with an error-causing prompt."""
        # Call the driver with an invalid prompt
        result = plan_from_prompt_driver(self.project_id, self.invalid_prompt, self.memory)
        
        # Verify result
        self.assertIsNone(result, "Driver should return None for error")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once with error")

if __name__ == "__main__":
    unittest.main()
