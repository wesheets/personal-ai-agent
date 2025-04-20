"""
Tests for the loop kickoff safeguard.

This module contains tests for the loop executor module to ensure it correctly
verifies conditions before allowing loop execution.
"""

import unittest
import json
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.loop_executor import (
    check_loop_execution_readiness,
    prepare_loop_for_execution,
    execute_loop
)

class TestLoopKickoffSafeguard(unittest.TestCase):
    """Test cases for the loop kickoff safeguard."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample loop plans for testing
        self.valid_plan = {
            "loop_id": 30,
            "agents": ["hal", "nova", "critic"],
            "goals": ["Create a React component for user profile", "Implement form validation"],
            "planned_files": ["src/components/UserProfile.jsx", "src/utils/validation.js"],
            "confirmed": True,
            "confirmed_by": "operator",
            "confirmed_at": "2025-04-20T12:00:00Z"
        }
        
        self.unconfirmed_plan = {
            "loop_id": 31,
            "agents": ["hal", "nova", "critic"],
            "goals": ["Create a React component for user profile", "Implement form validation"],
            "planned_files": ["src/components/UserProfile.jsx", "src/utils/validation.js"],
            "confirmed": False,
            "confirmed_by": "",
            "confirmed_at": "2025-04-20T12:00:00Z"
        }
        
        self.invalid_schema_plan = {
            "loop_id": 32,
            "agents": [],  # Empty agents list, which violates schema
            "goals": ["Create a React component for user profile"],
            "planned_files": ["src/components/UserProfile.jsx"],
            "confirmed": True,
            "confirmed_by": "operator",
            "confirmed_at": "2025-04-20T12:00:00Z"
        }
        
        # Mock project ID
        self.project_id = "test_project_001"
        
    @patch('orchestrator.modules.loop_executor.validate_and_log')
    @patch('orchestrator.modules.loop_executor.predict_required_tools')
    @patch('orchestrator.modules.loop_executor.check_tool_availability')
    def test_ready_when_all_conditions_met(self, mock_check_tools, mock_predict_tools, mock_validate):
        """Test that execution is ready when all conditions are met."""
        # Mock validation to return success
        mock_validate.return_value = (True, [], {})
        
        # Mock tool prediction to return some tools
        mock_predict_tools.return_value = ["file_writer", "component_builder"]
        
        # Mock tool availability to return all available
        mock_check_tools.return_value = {
            "file_writer": "available",
            "component_builder": "available"
        }
        
        # Check readiness
        is_ready, reason, missing_tools = check_loop_execution_readiness(self.valid_plan)
        
        # Verify result
        self.assertTrue(is_ready, "Should be ready when all conditions are met")
        self.assertEqual(len(missing_tools), 0, "Should have no missing tools")
    
    @patch('orchestrator.modules.loop_executor.validate_and_log')
    def test_blocked_when_plan_not_confirmed(self, mock_validate):
        """Test that execution is blocked when plan is not confirmed."""
        # Mock validation to return success (won't be reached)
        mock_validate.return_value = (True, [], {})
        
        # Check readiness
        is_ready, reason, missing_tools = check_loop_execution_readiness(self.unconfirmed_plan)
        
        # Verify result
        self.assertFalse(is_ready, "Should be blocked when plan is not confirmed")
        self.assertIn("not confirmed", reason, "Reason should mention confirmation")
    
    @patch('orchestrator.modules.loop_executor.validate_and_log')
    def test_blocked_when_schema_invalid(self, mock_validate):
        """Test that execution is blocked when schema validation fails."""
        # Mock validation to return failure
        mock_validate.return_value = (False, ["Error: agents array must not be empty"], {})
        
        # Check readiness
        is_ready, reason, missing_tools = check_loop_execution_readiness(self.invalid_schema_plan)
        
        # Verify result
        self.assertFalse(is_ready, "Should be blocked when schema validation fails")
        self.assertIn("schema validation", reason, "Reason should mention schema validation")
    
    @patch('orchestrator.modules.loop_executor.validate_and_log')
    @patch('orchestrator.modules.loop_executor.predict_required_tools')
    @patch('orchestrator.modules.loop_executor.check_tool_availability')
    def test_blocked_when_tools_missing(self, mock_check_tools, mock_predict_tools, mock_validate):
        """Test that execution is blocked when tools are missing."""
        # Mock validation to return success
        mock_validate.return_value = (True, [], {})
        
        # Mock tool prediction to return some tools
        mock_predict_tools.return_value = ["file_writer", "form_validator"]
        
        # Mock tool availability to return some missing
        mock_check_tools.return_value = {
            "file_writer": "available",
            "form_validator": "missing"
        }
        
        # Check readiness
        is_ready, reason, missing_tools = check_loop_execution_readiness(self.valid_plan)
        
        # Verify result
        self.assertFalse(is_ready, "Should be blocked when tools are missing")
        self.assertIn("Missing required tools", reason, "Reason should mention missing tools")
        self.assertIn("form_validator", missing_tools, "Should list missing tools")
    
    @patch('orchestrator.modules.loop_executor.check_loop_execution_readiness')
    @patch('orchestrator.modules.loop_executor.log_to_memory')
    @patch('orchestrator.modules.loop_executor.log_to_chat')
    @patch('orchestrator.modules.loop_executor.predict_required_tools')
    def test_prepare_loop_when_ready(self, mock_predict_tools, mock_log_chat, mock_log_memory, mock_check_readiness):
        """Test preparing a loop when it's ready for execution."""
        # Mock readiness check to return ready
        mock_check_readiness.return_value = (True, "All conditions met", [])
        
        # Mock tool prediction to return some tools
        mock_predict_tools.return_value = ["file_writer", "component_builder"]
        
        # Prepare the loop
        status = prepare_loop_for_execution(self.project_id, self.valid_plan)
        
        # Verify result
        self.assertEqual(status["status"], "ready", "Status should be ready")
        self.assertEqual(status["loop_id"], self.valid_plan["loop_id"], "Loop ID should match")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        
        # Verify chat message indicates readiness
        chat_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("All systems ready", chat_message, "Chat message should indicate readiness")
    
    @patch('orchestrator.modules.loop_executor.check_loop_execution_readiness')
    @patch('orchestrator.modules.loop_executor.log_to_memory')
    @patch('orchestrator.modules.loop_executor.log_to_chat')
    def test_prepare_loop_when_blocked(self, mock_log_chat, mock_log_memory, mock_check_readiness):
        """Test preparing a loop when it's blocked from execution."""
        # Mock readiness check to return blocked
        mock_check_readiness.return_value = (False, "Loop plan not confirmed by operator", [])
        
        # Prepare the loop
        status = prepare_loop_for_execution(self.project_id, self.unconfirmed_plan)
        
        # Verify result
        self.assertEqual(status["status"], "blocked", "Status should be blocked")
        self.assertEqual(status["loop_id"], self.unconfirmed_plan["loop_id"], "Loop ID should match")
        self.assertIn("reason", status, "Status should include block reason")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        
        # Verify chat message indicates blocking
        chat_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("blocked", chat_message, "Chat message should indicate blocking")
    
    @patch('orchestrator.modules.loop_executor.prepare_loop_for_execution')
    @patch('orchestrator.modules.loop_executor.log_to_memory')
    @patch('orchestrator.modules.loop_executor.log_to_chat')
    def test_execute_loop_when_ready(self, mock_log_chat, mock_log_memory, mock_prepare_loop):
        """Test executing a loop when it's ready."""
        # Mock preparation to return ready
        mock_prepare_loop.return_value = {
            "loop_id": self.valid_plan["loop_id"],
            "status": "ready",
            "timestamp": "2025-04-20T12:00:00Z",
            "trace_id": f"loop_{self.valid_plan['loop_id']}_kickoff"
        }
        
        # Execute the loop
        status = execute_loop(self.project_id, self.valid_plan)
        
        # Verify result
        self.assertEqual(status["status"], "execution_started", "Status should be execution_started")
        self.assertEqual(status["loop_id"], self.valid_plan["loop_id"], "Loop ID should match")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        
        # Verify chat message indicates execution started
        chat_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("execution started", chat_message, "Chat message should indicate execution started")
    
    @patch('orchestrator.modules.loop_executor.prepare_loop_for_execution')
    def test_execute_loop_when_blocked(self, mock_prepare_loop):
        """Test executing a loop when it's blocked."""
        # Mock preparation to return blocked
        block_status = {
            "loop_id": self.unconfirmed_plan["loop_id"],
            "status": "blocked",
            "reason": "Loop plan not confirmed by operator",
            "timestamp": "2025-04-20T12:00:00Z"
        }
        mock_prepare_loop.return_value = block_status
        
        # Execute the loop
        status = execute_loop(self.project_id, self.unconfirmed_plan)
        
        # Verify result is the same as the block status
        self.assertEqual(status, block_status, "Should return the block status unchanged")
        self.assertEqual(status["status"], "blocked", "Status should be blocked")

if __name__ == "__main__":
    unittest.main()
