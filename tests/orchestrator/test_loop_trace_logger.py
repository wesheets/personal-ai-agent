"""
Tests for the loop trace logger module.

This module contains tests for the loop trace logger module to ensure it correctly
logs all events and actions during loop execution.
"""

import unittest
import json
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.loop_trace_logger import (
    log_loop_event,
    log_agent_action,
    log_loop_status,
    log_file_operation,
    log_validation_event,
    get_loop_trace
)

class TestLoopTraceLogger(unittest.TestCase):
    """Test cases for the loop trace logger module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample data for testing
        self.project_id = "test_project_001"
        self.loop_id = 30
        
    @patch('orchestrator.modules.loop_trace_logger.log_to_memory')
    def test_log_loop_event(self, mock_log_memory):
        """Test logging a general event to the loop trace."""
        # Create a test event
        event = {
            "type": "test_event",
            "data": "test_data"
        }
        
        # Log the event
        result = log_loop_event(self.project_id, self.loop_id, event)
        
        # Verify result
        self.assertEqual(result["type"], "test_event", "Event type should be preserved")
        self.assertEqual(result["data"], "test_data", "Event data should be preserved")
        self.assertIn("timestamp", result, "Timestamp should be added")
        self.assertEqual(result["loop_id"], self.loop_id, "Loop ID should be added")
        
        # Verify logging call
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        
    @patch('orchestrator.modules.loop_trace_logger.log_to_memory')
    @patch('orchestrator.modules.loop_trace_logger.log_to_chat_messages')
    @patch('orchestrator.modules.loop_trace_logger.update_orchestrator_sandbox')
    def test_log_agent_action(self, mock_update_sandbox, mock_log_chat, mock_log_memory):
        """Test logging an agent action."""
        # Log an agent action
        result = log_agent_action(
            self.project_id, 
            self.loop_id, 
            "hal", 
            "Timeline.jsx", 
            "success", 
            "File scaffolded"
        )
        
        # Verify result
        self.assertEqual(result["type"], "agent_execution", "Event type should be agent_execution")
        self.assertEqual(result["agent"], "hal", "Agent should be hal")
        self.assertEqual(result["file"], "Timeline.jsx", "File should be Timeline.jsx")
        self.assertEqual(result["status"], "success", "Status should be success")
        self.assertEqual(result["notes"], "File scaffolded", "Notes should be preserved")
        self.assertIn("timestamp", result, "Timestamp should be added")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        self.assertEqual(mock_update_sandbox.call_count, 1, "Should update sandbox once")
        
    @patch('orchestrator.modules.loop_trace_logger.log_to_memory')
    @patch('orchestrator.modules.loop_trace_logger.log_to_chat_messages')
    def test_log_loop_status_completed(self, mock_log_chat, mock_log_memory):
        """Test logging a completed loop status."""
        # Log a completed loop status
        result = log_loop_status(
            self.project_id, 
            self.loop_id, 
            "completed"
        )
        
        # Verify result
        self.assertEqual(result["type"], "loop_status", "Event type should be loop_status")
        self.assertEqual(result["status"], "completed", "Status should be completed")
        self.assertIn("timestamp", result, "Timestamp should be added")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        
        # Verify chat message
        chat_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("completed successfully", chat_message, "Chat message should indicate completion")
        
    @patch('orchestrator.modules.loop_trace_logger.log_to_memory')
    @patch('orchestrator.modules.loop_trace_logger.log_to_chat_messages')
    def test_log_loop_status_aborted(self, mock_log_chat, mock_log_memory):
        """Test logging an aborted loop status with reason."""
        # Log an aborted loop status
        reason = "CRITIC failed schema validation"
        result = log_loop_status(
            self.project_id, 
            self.loop_id, 
            "aborted",
            reason
        )
        
        # Verify result
        self.assertEqual(result["type"], "loop_status", "Event type should be loop_status")
        self.assertEqual(result["status"], "aborted", "Status should be aborted")
        self.assertEqual(result["reason"], reason, "Reason should be preserved")
        self.assertIn("timestamp", result, "Timestamp should be added")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        
        # Verify chat message
        chat_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("aborted", chat_message, "Chat message should indicate abortion")
        self.assertIn(reason, chat_message, "Chat message should include reason")
        
    @patch('orchestrator.modules.loop_trace_logger.log_to_memory')
    @patch('orchestrator.modules.loop_trace_logger.log_to_chat_messages')
    def test_log_file_operation(self, mock_log_chat, mock_log_memory):
        """Test logging a file operation."""
        # Log a file operation
        result = log_file_operation(
            self.project_id, 
            self.loop_id, 
            "nova", 
            "styles.css", 
            "create", 
            "success"
        )
        
        # Verify result
        self.assertEqual(result["type"], "file_operation", "Event type should be file_operation")
        self.assertEqual(result["agent"], "nova", "Agent should be nova")
        self.assertEqual(result["file"], "styles.css", "File should be styles.css")
        self.assertEqual(result["operation"], "create", "Operation should be create")
        self.assertEqual(result["status"], "success", "Status should be success")
        self.assertIn("timestamp", result, "Timestamp should be added")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        
    @patch('orchestrator.modules.loop_trace_logger.log_to_memory')
    @patch('orchestrator.modules.loop_trace_logger.log_to_chat_messages')
    def test_log_validation_event_passed(self, mock_log_chat, mock_log_memory):
        """Test logging a successful validation event."""
        # Log a validation event
        result = log_validation_event(
            self.project_id, 
            self.loop_id, 
            "critic", 
            "Timeline.jsx", 
            "schema", 
            "passed"
        )
        
        # Verify result
        self.assertEqual(result["type"], "validation", "Event type should be validation")
        self.assertEqual(result["agent"], "critic", "Agent should be critic")
        self.assertEqual(result["file"], "Timeline.jsx", "File should be Timeline.jsx")
        self.assertEqual(result["validation_type"], "schema", "Validation type should be schema")
        self.assertEqual(result["status"], "passed", "Status should be passed")
        self.assertIn("timestamp", result, "Timestamp should be added")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        
    @patch('orchestrator.modules.loop_trace_logger.log_to_memory')
    @patch('orchestrator.modules.loop_trace_logger.log_to_chat_messages')
    def test_log_validation_event_failed(self, mock_log_chat, mock_log_memory):
        """Test logging a failed validation event with errors."""
        # Log a validation event with errors
        errors = ["Missing required field 'title'", "Invalid type for field 'count'"]
        result = log_validation_event(
            self.project_id, 
            self.loop_id, 
            "critic", 
            "Timeline.jsx", 
            "schema", 
            "failed",
            errors
        )
        
        # Verify result
        self.assertEqual(result["type"], "validation", "Event type should be validation")
        self.assertEqual(result["status"], "failed", "Status should be failed")
        self.assertEqual(result["errors"], errors, "Errors should be preserved")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        
        # Verify chat message
        chat_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn(errors[0], chat_message, "Chat message should include first error")
        self.assertIn("+1 more", chat_message, "Chat message should indicate more errors")
        
    def test_multiple_events_sequence(self):
        """Test logging multiple events in sequence to verify timestamp ordering."""
        # This test will use the real functions to verify timestamp ordering
        with patch('orchestrator.modules.loop_trace_logger.log_to_memory') as mock_log_memory:
            with patch('orchestrator.modules.loop_trace_logger.log_to_chat_messages'):
                with patch('orchestrator.modules.loop_trace_logger.update_orchestrator_sandbox'):
                    # Log multiple events in sequence
                    event1 = log_agent_action(self.project_id, self.loop_id, "hal", "Timeline.jsx", "success")
                    event2 = log_file_operation(self.project_id, self.loop_id, "hal", "Timeline.jsx", "create", "success")
                    event3 = log_validation_event(self.project_id, self.loop_id, "critic", "Timeline.jsx", "schema", "passed")
                    event4 = log_loop_status(self.project_id, self.loop_id, "completed")
                    
                    # Extract timestamps
                    timestamp1 = datetime.strptime(event1["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
                    timestamp2 = datetime.strptime(event2["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
                    timestamp3 = datetime.strptime(event3["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
                    timestamp4 = datetime.strptime(event4["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
                    
                    # Verify timestamp ordering
                    self.assertLessEqual(timestamp1, timestamp2, "Event 1 should be before or at same time as event 2")
                    self.assertLessEqual(timestamp2, timestamp3, "Event 2 should be before or at same time as event 3")
                    self.assertLessEqual(timestamp3, timestamp4, "Event 3 should be before or at same time as event 4")
                    
                    # Verify number of logging calls
                    self.assertEqual(mock_log_memory.call_count, 4, "Should log to memory four times")

if __name__ == "__main__":
    unittest.main()
