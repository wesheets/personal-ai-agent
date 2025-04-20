"""
Tests for the agent action logger module.

This module contains tests for the agent action logger module to ensure it correctly
tracks agent actions during loop execution.
"""

import unittest
import json
import os
import sys
import re
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.agent_action_logger import (
    log_agent_execution,
    log_agent_push,
    get_agent_actions,
    get_loop_agent_actions,
    get_file_actions,
    get_status_emoji
)

class TestAgentActionLogger(unittest.TestCase):
    """Test cases for the agent action logger module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock project ID
        self.project_id = "test_project_001"
        
        # Sample data for testing
        self.agent_name = "nova"
        self.contract_id = "loop_032_nova_contract"
        self.file = "ContactForm.jsx"
        self.status = "complete"
        self.notes = "Validation passed. File committed."
        
        # Git operation data
        self.branch = "feature/agent-hal-loop32-loginform"
        self.commit_message = "feat: HAL creates LoginForm.jsx"
        self.pr_link = "https://github.com/example/repo/pull/34"
    
    @patch('orchestrator.modules.agent_action_logger.log_to_memory')
    @patch('orchestrator.modules.agent_action_logger.log_to_chat')
    def test_log_agent_execution_complete(self, mock_log_chat, mock_log_memory):
        """Test logging a successful agent execution."""
        # Call the function
        result = log_agent_execution(
            project_id=self.project_id,
            agent_name=self.agent_name,
            contract_id=self.contract_id,
            file=self.file,
            status=self.status,
            notes=self.notes
        )
        
        # Verify result
        self.assertEqual(result["agent"], self.agent_name)
        self.assertEqual(result["file"], self.file)
        self.assertEqual(result["contract_id"], self.contract_id)
        self.assertEqual(result["status"], self.status)
        self.assertEqual(result["notes"], self.notes)
        self.assertEqual(result["loop_id"], 32)  # Extracted from contract_id
        
        # Verify timestamp format
        self.assertTrue(re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', result["timestamp"]))
        
        # Verify memory logging calls
        self.assertEqual(mock_log_memory.call_count, 2)
        
        # First call should log to loop_trace
        args, kwargs = mock_log_memory.call_args_list[0]
        self.assertEqual(args[0], self.project_id)
        self.assertTrue("loop_trace" in args[1])
        
        # Second call should log to agent_trace
        args, kwargs = mock_log_memory.call_args_list[1]
        self.assertEqual(args[0], self.project_id)
        self.assertTrue("agent_trace" in args[1])
        self.assertTrue(self.agent_name in args[1]["agent_trace"])
        
        # Verify chat logging call
        mock_log_chat.assert_called_once()
        args, kwargs = mock_log_chat.call_args
        self.assertEqual(args[0], self.project_id)
        self.assertEqual(args[1]["role"], "orchestrator")
        self.assertTrue("✅" in args[1]["message"])  # Success emoji
        self.assertTrue(self.agent_name.upper() in args[1]["message"])
        self.assertTrue(self.file in args[1]["message"])
    
    @patch('orchestrator.modules.agent_action_logger.log_to_memory')
    @patch('orchestrator.modules.agent_action_logger.log_to_chat')
    def test_log_agent_execution_failed(self, mock_log_chat, mock_log_memory):
        """Test logging a failed agent execution."""
        # Call the function with failed status
        result = log_agent_execution(
            project_id=self.project_id,
            agent_name=self.agent_name,
            contract_id=self.contract_id,
            file=self.file,
            status="failed",
            notes="Validation failed. File rejected."
        )
        
        # Verify result
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["notes"], "Validation failed. File rejected.")
        
        # Verify chat logging has failure emoji
        mock_log_chat.assert_called_once()
        args, kwargs = mock_log_chat.call_args
        self.assertTrue("❌" in args[1]["message"])  # Failure emoji
    
    @patch('orchestrator.modules.agent_action_logger.log_to_memory')
    @patch('orchestrator.modules.agent_action_logger.log_to_chat')
    def test_log_agent_execution_invalid_contract_id(self, mock_log_chat, mock_log_memory):
        """Test logging with an invalid contract ID."""
        # Call the function with invalid contract ID
        result = log_agent_execution(
            project_id=self.project_id,
            agent_name=self.agent_name,
            contract_id="invalid_format",
            file=self.file,
            status=self.status
        )
        
        # Verify result still has a loop_id (fallback)
        self.assertTrue("loop_id" in result)
        self.assertIsInstance(result["loop_id"], int)
    
    @patch('orchestrator.modules.agent_action_logger.log_to_memory')
    @patch('orchestrator.modules.agent_action_logger.log_to_chat')
    def test_log_agent_push(self, mock_log_chat, mock_log_memory):
        """Test logging a Git push operation."""
        # Call the function
        result = log_agent_push(
            project_id=self.project_id,
            agent_name="hal",
            branch=self.branch,
            commit_message=self.commit_message,
            pr_link=self.pr_link
        )
        
        # Verify result
        self.assertEqual(result["agent"], "hal")
        self.assertEqual(result["branch"], self.branch)
        self.assertEqual(result["commit"], self.commit_message)
        self.assertEqual(result["status"], "pushed")
        self.assertEqual(result["pr"], self.pr_link)
        
        # Verify extracted loop_id and file from branch name
        self.assertEqual(result["loop_id"], 32)
        self.assertEqual(result["file"], "loginform")
        
        # Verify timestamp format
        self.assertTrue(re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', result["timestamp"]))
        
        # Verify memory logging calls
        self.assertEqual(mock_log_memory.call_count, 3)
        
        # First call should log to loop_trace
        args, kwargs = mock_log_memory.call_args_list[0]
        self.assertEqual(args[0], self.project_id)
        self.assertTrue("loop_trace" in args[1])
        
        # Second call should log to agent_trace
        args, kwargs = mock_log_memory.call_args_list[1]
        self.assertEqual(args[0], self.project_id)
        self.assertTrue("agent_trace" in args[1])
        self.assertTrue("hal" in args[1]["agent_trace"])
        
        # Third call should log to git_operations
        args, kwargs = mock_log_memory.call_args_list[2]
        self.assertEqual(args[0], self.project_id)
        self.assertTrue("git_operations" in args[1])
        
        # Verify chat logging call
        mock_log_chat.assert_called_once()
        args, kwargs = mock_log_chat.call_args
        self.assertEqual(args[0], self.project_id)
        self.assertEqual(args[1]["role"], "orchestrator")
        self.assertTrue("🔀" in args[1]["message"])  # PR emoji
        self.assertTrue("HAL" in args[1]["message"])
        self.assertTrue(self.branch in args[1]["message"])
        self.assertTrue(self.pr_link in args[1]["message"])
    
    @patch('orchestrator.modules.agent_action_logger.log_to_memory')
    @patch('orchestrator.modules.agent_action_logger.log_to_chat')
    def test_log_agent_push_without_pr(self, mock_log_chat, mock_log_memory):
        """Test logging a Git push operation without a PR link."""
        # Call the function without PR link
        result = log_agent_push(
            project_id=self.project_id,
            agent_name="hal",
            branch=self.branch,
            commit_message=self.commit_message
        )
        
        # Verify result doesn't have PR field
        self.assertFalse("pr" in result)
        
        # Verify chat logging has different emoji
        mock_log_chat.assert_called_once()
        args, kwargs = mock_log_chat.call_args
        self.assertTrue("🔄" in args[1]["message"])  # Push emoji
        self.assertFalse("created PR" in args[1]["message"])
    
    @patch('orchestrator.modules.agent_action_logger.log_to_memory')
    @patch('orchestrator.modules.agent_action_logger.log_to_chat')
    def test_log_agent_push_invalid_branch_name(self, mock_log_chat, mock_log_memory):
        """Test logging with an invalid branch name format."""
        # Call the function with invalid branch name
        result = log_agent_push(
            project_id=self.project_id,
            agent_name="hal",
            branch="feature/some-random-branch",
            commit_message=self.commit_message
        )
        
        # Verify result doesn't have loop_id or file
        self.assertFalse("loop_id" in result)
        self.assertFalse("file" in result)
        
        # Verify it still logs to agent_trace and git_operations
        self.assertEqual(mock_log_memory.call_count, 2)  # Only 2 calls, not 3
    
    def test_get_status_emoji(self):
        """Test getting status emojis."""
        self.assertEqual(get_status_emoji("complete"), "✅")
        self.assertEqual(get_status_emoji("failed"), "❌")
        self.assertEqual(get_status_emoji("in_progress"), "🔄")
        self.assertEqual(get_status_emoji("blocked"), "⛔")
        self.assertEqual(get_status_emoji("warning"), "⚠️")
        self.assertEqual(get_status_emoji("pushed"), "🔄")
        self.assertEqual(get_status_emoji("merged"), "🔀")
        self.assertEqual(get_status_emoji("unknown_status"), "ℹ️")  # Default
    
    @patch('builtins.print')
    def test_get_agent_actions(self, mock_print):
        """Test getting agent actions."""
        actions = get_agent_actions(self.project_id, self.agent_name, limit=5)
        self.assertEqual(len(actions), 0)  # Mock implementation returns empty list
        mock_print.assert_called()  # Verify print was called
    
    @patch('builtins.print')
    def test_get_loop_agent_actions(self, mock_print):
        """Test getting loop agent actions."""
        actions = get_loop_agent_actions(self.project_id, 32, agent_name="hal")
        self.assertEqual(len(actions), 0)  # Mock implementation returns empty list
        mock_print.assert_called()  # Verify print was called
    
    @patch('builtins.print')
    def test_get_file_actions(self, mock_print):
        """Test getting file actions."""
        actions = get_file_actions(self.project_id, self.file)
        self.assertEqual(len(actions), 0)  # Mock implementation returns empty list
        mock_print.assert_called()  # Verify print was called
    
    @patch('orchestrator.modules.agent_action_logger.log_to_memory')
    @patch('orchestrator.modules.agent_action_logger.log_to_chat')
    def test_contract_received_logging(self, mock_log_chat, mock_log_memory):
        """Test logging a contract received action."""
        # Call the function with contract received status
        result = log_agent_execution(
            project_id=self.project_id,
            agent_name=self.agent_name,
            contract_id=self.contract_id,
            file=self.file,
            status="contract_received",
            notes="Agent received execution contract"
        )
        
        # Verify result
        self.assertEqual(result["status"], "contract_received")
        self.assertEqual(result["notes"], "Agent received execution contract")
        
        # Verify memory logging
        self.assertEqual(mock_log_memory.call_count, 2)
    
    @patch('orchestrator.modules.agent_action_logger.log_to_memory')
    @patch('orchestrator.modules.agent_action_logger.log_to_chat')
    def test_file_built_logging(self, mock_log_chat, mock_log_memory):
        """Test logging a file built action."""
        # Call the function with file built status
        result = log_agent_execution(
            project_id=self.project_id,
            agent_name=self.agent_name,
            contract_id=self.contract_id,
            file=self.file,
            status="file_built",
            notes="Agent completed file construction"
        )
        
        # Verify result
        self.assertEqual(result["status"], "file_built")
        self.assertEqual(result["notes"], "Agent completed file construction")
        
        # Verify memory logging
        self.assertEqual(mock_log_memory.call_count, 2)
    
    @patch('orchestrator.modules.agent_action_logger.log_to_memory')
    @patch('orchestrator.modules.agent_action_logger.log_to_chat')
    def test_validation_passed_logging(self, mock_log_chat, mock_log_memory):
        """Test logging a validation passed action."""
        # Call the function with validation passed status
        result = log_agent_execution(
            project_id=self.project_id,
            agent_name=self.agent_name,
            contract_id=self.contract_id,
            file=self.file,
            status="validation_passed",
            notes="File passed schema validation"
        )
        
        # Verify result
        self.assertEqual(result["status"], "validation_passed")
        self.assertEqual(result["notes"], "File passed schema validation")
        
        # Verify memory logging
        self.assertEqual(mock_log_memory.call_count, 2)
    
    @patch('orchestrator.modules.agent_action_logger.log_to_memory')
    @patch('orchestrator.modules.agent_action_logger.log_to_chat')
    def test_pr_pushed_logging(self, mock_log_chat, mock_log_memory):
        """Test logging a PR pushed action via log_agent_push."""
        # Call the function
        result = log_agent_push(
            project_id=self.project_id,
            agent_name=self.agent_name,
            branch=f"feature/agent-{self.agent_name}-loop32-{self.file}",
            commit_message=f"feat: {self.agent_name.upper()} creates {self.file}",
            pr_link="https://github.com/example/repo/pull/35"
        )
        
        # Verify result
        self.assertEqual(result["status"], "pushed")
        self.assertEqual(result["agent"], self.agent_name)
        self.assertTrue("pr" in result)
        
        # Verify memory logging
        self.assertEqual(mock_log_memory.call_count, 3)  # loop_trace, agent_trace, git_operations
        
        # Verify chat logging
        mock_log_chat.assert_called_once()
        args, kwargs = mock_log_chat.call_args
        self.assertTrue("PR" in args[1]["message"])

if __name__ == "__main__":
    unittest.main()
