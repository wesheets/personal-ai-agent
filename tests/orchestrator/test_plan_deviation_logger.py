"""
Tests for the plan deviation logger module.

This module contains tests for the plan deviation logger module to ensure it correctly
logs all instances where loop execution diverges from the original plan.
"""

import unittest
import json
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.plan_deviation_logger import (
    log_plan_deviation,
    log_operator_override,
    log_missing_tool_deviation,
    log_validation_failure,
    log_critic_rejection,
    get_plan_deviations
)

class TestPlanDeviationLogger(unittest.TestCase):
    """Test cases for the plan deviation logger module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample data for testing
        self.project_id = "test_project_001"
        self.loop_id = 30
        
    @patch('orchestrator.modules.plan_deviation_logger.log_to_memory')
    @patch('orchestrator.modules.plan_deviation_logger.log_to_chat_messages')
    @patch('orchestrator.modules.plan_deviation_logger.log_to_cto_warnings')
    def test_log_plan_deviation(self, mock_log_cto, mock_log_chat, mock_log_memory):
        """Test logging a general plan deviation."""
        # Create test data
        cause = "schema_validation_failed"
        affected = {"agent": "nova", "file": "FormLogic.jsx"}
        resolution = "Rerouted to HAL"
        
        # Log the deviation
        result = log_plan_deviation(
            self.project_id, 
            self.loop_id, 
            cause, 
            affected, 
            resolution
        )
        
        # Verify result
        self.assertEqual(result["type"], "plan_deviation", "Event type should be plan_deviation")
        self.assertEqual(result["cause"], cause, "Cause should match input")
        self.assertEqual(result["affected"], affected, "Affected should match input")
        self.assertEqual(result["resolution"], resolution, "Resolution should match input")
        self.assertIn("timestamp", result, "Timestamp should be added")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 2, "Should log to memory twice (loop_trace and plan_deviations)")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        self.assertEqual(mock_log_cto.call_count, 1, "Should log to CTO warnings for schema validation failure")
        
    @patch('orchestrator.modules.plan_deviation_logger.log_to_memory')
    @patch('orchestrator.modules.plan_deviation_logger.log_to_chat_messages')
    def test_log_operator_override(self, mock_log_chat, mock_log_memory):
        """Test logging an operator override."""
        # Create test data
        override_type = "agent_reroute"
        context = {
            "from": "nova",
            "to": "hal",
            "reason": "Incorrect logic in review"
        }
        
        # Log the override
        result = log_operator_override(
            self.project_id, 
            self.loop_id, 
            override_type, 
            context
        )
        
        # Verify result
        self.assertEqual(result["type"], "operator_override", "Event type should be operator_override")
        self.assertEqual(result["override_type"], override_type, "Override type should match input")
        self.assertEqual(result["context"], context, "Context should match input")
        self.assertIn("timestamp", result, "Timestamp should be added")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 2, "Should log to memory twice (loop_trace and plan_deviations)")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        
        # Verify chat message
        chat_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("Operator replaced NOVA with HAL", chat_message, "Chat message should indicate agent replacement")
        self.assertIn("Incorrect logic in review", chat_message, "Chat message should include reason")
        
    @patch('orchestrator.modules.plan_deviation_logger.log_plan_deviation')
    def test_log_missing_tool_deviation(self, mock_log_deviation):
        """Test logging a missing tool deviation."""
        # Create test data
        tool_name = "form_validator"
        agent = "nova"
        fallback = "manual_validation"
        
        # Log the missing tool
        log_missing_tool_deviation(
            self.project_id, 
            self.loop_id, 
            tool_name, 
            agent, 
            fallback
        )
        
        # Verify log_plan_deviation was called with correct parameters
        mock_log_deviation.assert_called_once()
        args, kwargs = mock_log_deviation.call_args
        
        self.assertEqual(kwargs["project_id"], self.project_id, "Project ID should match")
        self.assertEqual(kwargs["loop_id"], self.loop_id, "Loop ID should match")
        self.assertEqual(kwargs["cause"], "tool_unavailable", "Cause should be tool_unavailable")
        self.assertEqual(kwargs["affected"]["tool"], tool_name, "Affected tool should match input")
        self.assertEqual(kwargs["affected"]["agent"], agent, "Affected agent should match input")
        self.assertIn("Agent rerouted to use manual_validation", kwargs["resolution"], "Resolution should mention fallback")
        
    @patch('orchestrator.modules.plan_deviation_logger.log_plan_deviation')
    def test_log_validation_failure(self, mock_log_deviation):
        """Test logging a validation failure."""
        # Create test data
        validation_type = "schema"
        file = "FormLogic.jsx"
        agent = "nova"
        errors = ["Missing required field 'onSubmit'"]
        resolution = "Rerouted to HAL"
        
        # Log the validation failure
        log_validation_failure(
            self.project_id, 
            self.loop_id, 
            validation_type, 
            file, 
            agent, 
            errors, 
            resolution
        )
        
        # Verify log_plan_deviation was called with correct parameters
        mock_log_deviation.assert_called_once()
        args, kwargs = mock_log_deviation.call_args
        
        self.assertEqual(kwargs["project_id"], self.project_id, "Project ID should match")
        self.assertEqual(kwargs["loop_id"], self.loop_id, "Loop ID should match")
        self.assertEqual(kwargs["cause"], "schema_validation_failed", "Cause should be schema_validation_failed")
        self.assertEqual(kwargs["affected"]["file"], file, "Affected file should match input")
        self.assertEqual(kwargs["affected"]["agent"], agent, "Affected agent should match input")
        self.assertEqual(kwargs["affected"]["errors"], errors, "Errors should match input")
        self.assertEqual(kwargs["resolution"], resolution, "Resolution should match input")
        
    @patch('orchestrator.modules.plan_deviation_logger.log_plan_deviation')
    def test_log_critic_rejection(self, mock_log_deviation):
        """Test logging a CRITIC rejection."""
        # Create test data
        file = "Timeline.jsx"
        agent = "nova"
        reason = "Component does not follow design system"
        resolution = "Loop rerouted to HAL"
        
        # Log the CRITIC rejection
        log_critic_rejection(
            self.project_id, 
            self.loop_id, 
            file, 
            agent, 
            reason, 
            resolution
        )
        
        # Verify log_plan_deviation was called with correct parameters
        mock_log_deviation.assert_called_once()
        args, kwargs = mock_log_deviation.call_args
        
        self.assertEqual(kwargs["project_id"], self.project_id, "Project ID should match")
        self.assertEqual(kwargs["loop_id"], self.loop_id, "Loop ID should match")
        self.assertEqual(kwargs["cause"], "critic_rejection", "Cause should be critic_rejection")
        self.assertEqual(kwargs["affected"]["file"], file, "Affected file should match input")
        self.assertEqual(kwargs["affected"]["agent"], agent, "Affected agent should match input")
        self.assertEqual(kwargs["affected"]["reason"], reason, "Reason should match input")
        self.assertEqual(kwargs["resolution"], resolution, "Resolution should match input")
        
    @patch('orchestrator.modules.plan_deviation_logger.log_to_memory')
    @patch('orchestrator.modules.plan_deviation_logger.log_to_chat_messages')
    @patch('orchestrator.modules.plan_deviation_logger.log_to_cto_warnings')
    def test_deviation_chat_messages(self, mock_log_cto, mock_log_chat, mock_log_memory):
        """Test that appropriate chat messages are generated for different deviation types."""
        # Test schema validation failure message
        log_plan_deviation(
            self.project_id,
            self.loop_id,
            "schema_validation_failed",
            {"file": "test.jsx"},
            "Fixed by HAL"
        )
        schema_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("Schema validation failed", schema_message)
        self.assertIn("Fixed by HAL", schema_message)
        
        # Test tool unavailable message
        log_plan_deviation(
            self.project_id,
            self.loop_id,
            "tool_unavailable",
            {"tool": "form_validator"},
            "Using fallback"
        )
        tool_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("Tool form_validator not found", tool_message)
        self.assertIn("Using fallback", tool_message)
        
        # Test CRITIC rejection message
        log_plan_deviation(
            self.project_id,
            self.loop_id,
            "critic_rejection",
            {"file": "Timeline.jsx"},
            "Rerouted to HAL"
        )
        critic_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("CRITIC rejected Timeline.jsx", critic_message)
        self.assertIn("Rerouted to HAL", critic_message)
        
    def test_get_plan_deviations(self):
        """Test retrieving plan deviations."""
        # This is a placeholder test since the function just returns an empty list for now
        deviations = get_plan_deviations(self.project_id, self.loop_id)
        self.assertEqual(deviations, [], "Should return an empty list")
        
        deviations = get_plan_deviations(self.project_id)
        self.assertEqual(deviations, [], "Should return an empty list for all loops")

if __name__ == "__main__":
    unittest.main()
