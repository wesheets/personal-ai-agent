"""
Tests for the agent git protocol enforcer module.

This module contains tests for the agent git protocol enforcer module to ensure it correctly
enforces git protocol standards for agent operations.
"""

import unittest
import json
import os
import sys
import re
import subprocess
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.agent_git_protocol import (
    generate_branch_name,
    validate_commit_message,
    log_pr_metadata,
    enforce_branch_from_main,
    validate_branch_name,
    suggest_pr_title,
    suggest_pr_body,
    get_current_branch,
    extract_info_from_branch
)

class TestAgentGitProtocol(unittest.TestCase):
    """Test cases for the agent git protocol enforcer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock project ID
        self.project_id = "test_project_001"
        
        # Sample data for testing
        self.agent = "hal"
        self.loop_id = 32
        self.file = "LoginForm.jsx"
        self.branch = f"feature/agent-{self.agent}-loop{self.loop_id}-loginform"
        self.commit_msg = f"feat: HAL builds LoginForm.jsx in Loop {self.loop_id}"
        self.pr_url = "https://github.com/example/repo/pull/34"
    
    def test_generate_branch_name(self):
        """Test generating a standardized branch name."""
        # Test with standard inputs
        branch = generate_branch_name(self.agent, self.loop_id, self.file)
        self.assertEqual(branch, self.branch, "Should generate correct branch name")
        
        # Test with file having extension
        branch = generate_branch_name(self.agent, self.loop_id, "LoginForm.jsx")
        self.assertEqual(branch, self.branch, "Should handle file with extension")
        
        # Test with uppercase agent name
        branch = generate_branch_name("HAL", self.loop_id, self.file)
        self.assertEqual(branch, self.branch, "Should normalize agent name to lowercase")
        
        # Test with special characters in file name
        branch = generate_branch_name(self.agent, self.loop_id, "Login-Form.jsx")
        self.assertEqual(branch, self.branch, "Should remove special characters from file name")
    
    def test_validate_commit_message_valid(self):
        """Test validating a valid commit message."""
        # Test with standard format
        is_valid = validate_commit_message(self.commit_msg, self.agent, self.loop_id)
        self.assertTrue(is_valid, "Should validate correct commit message format")
        
        # Test with different verbs
        verbs = ["builds", "creates", "implements", "adds", "updates", "fixes"]
        for verb in verbs:
            commit_msg = f"feat: HAL {verb} LoginForm.jsx in Loop {self.loop_id}"
            is_valid = validate_commit_message(commit_msg, self.agent, self.loop_id)
            self.assertTrue(is_valid, f"Should validate commit message with verb '{verb}'")
        
        # Test with alternative format (without loop mention)
        commit_msg = "feat: HAL builds LoginForm.jsx"
        is_valid = validate_commit_message(commit_msg, self.agent, self.loop_id)
        self.assertTrue(is_valid, "Should validate alternative format without loop mention")
    
    def test_validate_commit_message_invalid(self):
        """Test validating an invalid commit message."""
        # Test with wrong agent name
        commit_msg = f"feat: NOVA builds LoginForm.jsx in Loop {self.loop_id}"
        is_valid = validate_commit_message(commit_msg, self.agent, self.loop_id)
        self.assertFalse(is_valid, "Should reject commit message with wrong agent name")
        
        # Test with wrong loop ID
        commit_msg = f"feat: HAL builds LoginForm.jsx in Loop {self.loop_id + 1}"
        is_valid = validate_commit_message(commit_msg, self.agent, self.loop_id)
        self.assertFalse(is_valid, "Should reject commit message with wrong loop ID")
        
        # Test with wrong format
        commit_msg = f"HAL builds LoginForm.jsx in Loop {self.loop_id}"
        is_valid = validate_commit_message(commit_msg, self.agent, self.loop_id)
        self.assertFalse(is_valid, "Should reject commit message with wrong format")
        
        # Test with missing verb
        commit_msg = f"feat: HAL LoginForm.jsx in Loop {self.loop_id}"
        is_valid = validate_commit_message(commit_msg, self.agent, self.loop_id)
        self.assertFalse(is_valid, "Should reject commit message without verb")
    
    @patch('orchestrator.modules.agent_git_protocol.log_to_memory')
    @patch('orchestrator.modules.agent_git_protocol.log_to_chat')
    def test_log_pr_metadata(self, mock_log_chat, mock_log_memory):
        """Test logging PR metadata."""
        # Call the function
        result = log_pr_metadata(
            project_id=self.project_id,
            agent=self.agent,
            branch=self.branch,
            pr_url=self.pr_url,
            loop_id=self.loop_id,
            file=self.file
        )
        
        # Verify result
        self.assertEqual(result["agent"], self.agent)
        self.assertEqual(result["branch"], self.branch)
        self.assertEqual(result["pr_url"], self.pr_url)
        self.assertEqual(result["loop_id"], self.loop_id)
        self.assertEqual(result["file"], self.file)
        self.assertEqual(result["status"], "open")
        
        # Verify PR title and body
        expected_title = f"Loop {self.loop_id} – {self.agent.upper()} File Contribution: {self.file}"
        expected_body = f"Contract received from Orchestrator. Output validated. Pushed by {self.agent.upper()} for Operator review."
        self.assertEqual(result["pr_title"], expected_title)
        self.assertEqual(result["pr_body"], expected_body)
        
        # Verify timestamp format
        self.assertTrue(re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', result["timestamp"]))
        
        # Verify memory logging calls
        self.assertEqual(mock_log_memory.call_count, 3)
        
        # First call should log to agent_trace
        args, kwargs = mock_log_memory.call_args_list[0]
        self.assertEqual(args[0], self.project_id)
        self.assertTrue("agent_trace" in args[1])
        self.assertTrue(self.agent in args[1]["agent_trace"])
        
        # Second call should log to loop_trace
        args, kwargs = mock_log_memory.call_args_list[1]
        self.assertEqual(args[0], self.project_id)
        self.assertTrue("loop_trace" in args[1])
        
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
        self.assertTrue(self.agent.upper() in args[1]["message"])
        self.assertTrue(str(self.loop_id) in args[1]["message"])
        self.assertTrue(self.pr_url in args[1]["message"])
    
    def test_enforce_branch_from_main_valid(self):
        """Test enforcing branch creation from main with valid branch."""
        # Test with main branch
        is_valid, message = enforce_branch_from_main("main")
        self.assertTrue(is_valid, "Should allow branch creation from main")
        self.assertEqual(message, "Branch will be created from main")
    
    def test_enforce_branch_from_main_invalid(self):
        """Test enforcing branch creation from main with invalid branch."""
        # Test with feature branch
        is_valid, message = enforce_branch_from_main("feature/some-branch")
        self.assertFalse(is_valid, "Should reject branch creation from feature branch")
        self.assertTrue("Cannot create a feature branch from another feature branch" in message)
        
        # Test with other branch
        is_valid, message = enforce_branch_from_main("develop")
        self.assertFalse(is_valid, "Should reject branch creation from non-main branch")
        self.assertTrue("Branches must be created from main" in message)
    
    def test_validate_branch_name_valid(self):
        """Test validating a valid branch name."""
        # Test with valid branch name
        is_valid, message = validate_branch_name(self.branch)
        self.assertTrue(is_valid, "Should validate correct branch name format")
        self.assertEqual(message, "Branch name is valid")
    
    def test_validate_branch_name_invalid(self):
        """Test validating an invalid branch name."""
        # Test with invalid prefix
        is_valid, message = validate_branch_name("fix/agent-hal-loop32-loginform")
        self.assertFalse(is_valid, "Should reject branch with wrong prefix")
        
        # Test with missing agent prefix
        is_valid, message = validate_branch_name("feature/hal-loop32-loginform")
        self.assertFalse(is_valid, "Should reject branch without agent prefix")
        
        # Test with missing loop ID
        is_valid, message = validate_branch_name("feature/agent-hal-loginform")
        self.assertFalse(is_valid, "Should reject branch without loop ID")
        
        # Test with missing file
        is_valid, message = validate_branch_name("feature/agent-hal-loop32")
        self.assertFalse(is_valid, "Should reject branch without file")
    
    def test_suggest_pr_title(self):
        """Test suggesting a PR title."""
        # Test with standard inputs
        title = suggest_pr_title(self.agent, self.loop_id, self.file)
        expected_title = f"Loop {self.loop_id} – {self.agent.upper()} File Contribution: {self.file}"
        self.assertEqual(title, expected_title, "Should suggest correct PR title")
        
        # Test with lowercase agent name
        title = suggest_pr_title("hal", self.loop_id, self.file)
        self.assertEqual(title, expected_title, "Should convert agent name to uppercase")
    
    def test_suggest_pr_body(self):
        """Test suggesting a PR body."""
        # Test with standard inputs
        body = suggest_pr_body(self.agent)
        expected_body = f"Contract received from Orchestrator. Output validated. Pushed by {self.agent.upper()} for Operator review."
        self.assertEqual(body, expected_body, "Should suggest correct PR body")
        
        # Test with lowercase agent name
        body = suggest_pr_body("hal")
        self.assertEqual(body, expected_body, "Should convert agent name to uppercase")
    
    @patch('subprocess.run')
    def test_get_current_branch(self, mock_run):
        """Test getting the current branch."""
        # Mock subprocess.run to return a branch name
        mock_process = MagicMock()
        mock_process.stdout = "main\n"
        mock_run.return_value = mock_process
        
        # Call the function
        branch = get_current_branch()
        
        # Verify result
        self.assertEqual(branch, "main", "Should return current branch name")
        
        # Verify subprocess.run was called correctly
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
    
    @patch('subprocess.run')
    def test_get_current_branch_error(self, mock_run):
        """Test getting the current branch when an error occurs."""
        # Mock subprocess.run to raise an exception
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        
        # Call the function
        branch = get_current_branch()
        
        # Verify result
        self.assertEqual(branch, "", "Should return empty string on error")
    
    def test_extract_info_from_branch_valid(self):
        """Test extracting info from a valid branch name."""
        # Test with valid branch name
        agent, loop_id, file = extract_info_from_branch(self.branch)
        self.assertEqual(agent, self.agent, "Should extract correct agent name")
        self.assertEqual(loop_id, self.loop_id, "Should extract correct loop ID")
        self.assertEqual(file, "loginform", "Should extract correct file name")
    
    def test_extract_info_from_branch_invalid(self):
        """Test extracting info from an invalid branch name."""
        # Test with invalid branch name
        agent, loop_id, file = extract_info_from_branch("feature/some-random-branch")
        self.assertIsNone(agent, "Should return None for agent with invalid branch")
        self.assertIsNone(loop_id, "Should return None for loop ID with invalid branch")
        self.assertIsNone(file, "Should return None for file with invalid branch")

if __name__ == "__main__":
    unittest.main()
