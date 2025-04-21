"""
Unit tests for the Debugger Agent module.
"""

import unittest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from agents.debugger_agent import (
    parse_failure_logs,
    determine_next_agent,
    generate_patch_plan,
    inject_debugger_report,
    debug_loop_failure
)

class TestDebuggerAgent(unittest.TestCase):
    """Test cases for the Debugger Agent module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample failure logs
        self.timeout_logs = """
        Traceback (most recent call last):
          File "/app/tools/api_client.py", line 42, in call_api
            response = requests.get(url, timeout=5)
          File "/usr/local/lib/python3.10/site-packages/requests/api.py", line 73, in get
            return request('get', url, params=params, **kwargs)
          File "/usr/local/lib/python3.10/site-packages/requests/api.py", line 59, in request
            return session.request(method=method, url=url, **kwargs)
          File "/usr/local/lib/python3.10/site-packages/requests/sessions.py", line 587, in request
            resp = self.send(prep, **send_kwargs)
          File "/usr/local/lib/python3.10/site-packages/requests/sessions.py", line 701, in send
            r = adapter.send(request, **kwargs)
          File "/usr/local/lib/python3.10/site-packages/requests/adapters.py", line 489, in send
            raise ReadTimeout(e, request=request)
        requests.exceptions.ReadTimeout: HTTPConnectionPool(host='api.example.com', port=80): Read timed out. (read timeout=5)
        Error: API request timed out
        """
        
        self.permission_logs = """
        Traceback (most recent call last):
          File "/app/tools/file_manager.py", line 28, in write_file
            with open(path, 'w') as f:
        PermissionError: [Errno 13] Permission denied: '/app/data/config.json'
        Error: Permission denied when writing to file
        """
        
        self.not_found_logs = """
        Traceback (most recent call last):
          File "/app/tools/resource_loader.py", line 15, in load_resource
            with open(resource_path, 'r') as f:
        FileNotFoundError: [Errno 2] No such file or directory: '/app/resources/template.html'
        Error: Resource not found
        """
        
        # Sample memory
        self.memory = {
            "loop_trace": {
                "loop_123": {
                    "status": "failed",
                    "error": "API request timed out"
                }
            }
        }
        
        # Sample loop context
        self.loop_context = {
            "plan": {
                "goal": "Fetch and process user data",
                "steps": [
                    {"description": "Connect to API"},
                    {"description": "Fetch user data"},
                    {"description": "Process and store results"}
                ]
            },
            "failure_reason": "API request timed out"
        }
    
    def test_parse_failure_logs_timeout(self):
        """Test parse_failure_logs with timeout logs."""
        result = parse_failure_logs(self.timeout_logs)
        
        # Check result properties
        self.assertEqual(result["failure_type"], "tool_timeout")
        self.assertIn("details", result)
        self.assertIn("suggested_fix", result["details"])
        self.assertIn("confidence", result)
        self.assertGreater(result["confidence"], 0.8)
        
        # Check extracted details
        self.assertIn("error_message", result["details"])
        self.assertEqual(result["details"]["error_message"], "API request timed out")
    
    def test_parse_failure_logs_permission(self):
        """Test parse_failure_logs with permission error logs."""
        result = parse_failure_logs(self.permission_logs)
        
        # Check result properties
        self.assertEqual(result["failure_type"], "permission_error")
        self.assertIn("details", result)
        self.assertIn("suggested_fix", result["details"])
        self.assertIn("confidence", result)
        
        # Check that error message exists, but don't check exact content
        # since we're more concerned with the failure type detection
        self.assertIn("error_message", result["details"])
    
    def test_parse_failure_logs_not_found(self):
        """Test parse_failure_logs with resource not found logs."""
        result = parse_failure_logs(self.not_found_logs)
        
        # Check result properties
        self.assertEqual(result["failure_type"], "resource_not_found")
        self.assertIn("details", result)
        self.assertIn("suggested_fix", result["details"])
        self.assertIn("confidence", result)
        
        # Check that error message exists, but don't check exact content
        # since we're more concerned with the failure type detection
        self.assertIn("error_message", result["details"])
    
    def test_determine_next_agent(self):
        """Test determine_next_agent function."""
        # Test with various failure types
        self.assertEqual(determine_next_agent("tool_timeout"), "optimizer")
        self.assertEqual(determine_next_agent("api_rate_limit"), "scheduler")
        self.assertEqual(determine_next_agent("permission_error"), "security")
        self.assertEqual(determine_next_agent("resource_not_found"), "researcher")
        self.assertEqual(determine_next_agent("invalid_input"), "validator")
        self.assertEqual(determine_next_agent("unknown"), "critic")
        
        # Test with unknown failure type
        self.assertEqual(determine_next_agent("nonexistent_type"), "critic")
    
    def test_generate_patch_plan(self):
        """Test generate_patch_plan function."""
        # Generate patch plan for timeout
        root_cause = {
            "failure_type": "tool_timeout",
            "details": {
                "suggested_fix": "Increase timeout threshold"
            },
            "confidence": 0.9
        }
        
        patch_plan = generate_patch_plan(root_cause, self.loop_context)
        
        # Check patch plan properties
        self.assertIn("steps", patch_plan)
        self.assertGreater(len(patch_plan["steps"]), 0)
        self.assertIn("next_agent", patch_plan)
        self.assertEqual(patch_plan["next_agent"], "optimizer")
        self.assertIn("confidence", patch_plan)
        self.assertEqual(patch_plan["confidence"], 0.9)
        self.assertIn("suggested_fix", patch_plan)
        self.assertEqual(patch_plan["suggested_fix"], "Increase timeout threshold")
    
    def test_inject_debugger_report(self):
        """Test inject_debugger_report function."""
        # Inject debugger report
        updated_memory = inject_debugger_report(
            self.memory,
            "loop_123",
            self.timeout_logs,
            self.loop_context
        )
        
        # Check that report was injected
        self.assertIn("debugger_reports", updated_memory)
        self.assertEqual(len(updated_memory["debugger_reports"]), 1)
        
        # Check report properties
        report = updated_memory["debugger_reports"][0]
        self.assertEqual(report["loop_id"], "loop_123")
        self.assertEqual(report["failure_type"], "tool_timeout")
        self.assertIn("suggested_fix", report)
        self.assertIn("patch_plan", report)
        self.assertIn("steps", report["patch_plan"])
        self.assertIn("next_agent", report)
        
        # Check loop trace update
        self.assertIn("failures", updated_memory["loop_trace"]["loop_123"])
        self.assertEqual(len(updated_memory["loop_trace"]["loop_123"]["failures"]), 1)
        self.assertEqual(updated_memory["loop_trace"]["loop_123"]["failures"][0]["type"], "debugger_report")
    
    def test_debug_loop_failure(self):
        """Test debug_loop_failure function."""
        # Debug loop failure
        updated_memory = debug_loop_failure(
            "loop_123",
            self.timeout_logs,
            self.memory,
            self.loop_context
        )
        
        # Check that report was injected
        self.assertIn("debugger_reports", updated_memory)
        self.assertEqual(len(updated_memory["debugger_reports"]), 1)
        
        # Check report properties
        report = updated_memory["debugger_reports"][0]
        self.assertEqual(report["loop_id"], "loop_123")
        self.assertEqual(report["failure_type"], "tool_timeout")
        self.assertIn("suggested_fix", report)
        self.assertIn("patch_plan", report)
        self.assertIn("steps", report["patch_plan"])
        self.assertIn("next_agent", report)
    
    def test_debug_loop_failure_with_empty_context(self):
        """Test debug_loop_failure with empty context."""
        # Debug loop failure with empty context
        updated_memory = debug_loop_failure(
            "loop_123",
            self.timeout_logs,
            self.memory
        )
        
        # Check that report was injected
        self.assertIn("debugger_reports", updated_memory)
        self.assertEqual(len(updated_memory["debugger_reports"]), 1)
        
        # Check report properties
        report = updated_memory["debugger_reports"][0]
        self.assertEqual(report["loop_id"], "loop_123")
        self.assertEqual(report["failure_type"], "tool_timeout")
        self.assertIn("suggested_fix", report)
        self.assertIn("patch_plan", report)
        self.assertIn("steps", report["patch_plan"])
        self.assertIn("next_agent", report)
    
    def test_debug_loop_failure_with_unknown_error(self):
        """Test debug_loop_failure with unknown error."""
        # Create unknown error logs
        unknown_logs = """
        Something went wrong but we don't know what.
        """
        
        # Debug loop failure with unknown error
        updated_memory = debug_loop_failure(
            "loop_123",
            unknown_logs,
            self.memory,
            self.loop_context
        )
        
        # Check that report was injected
        self.assertIn("debugger_reports", updated_memory)
        self.assertEqual(len(updated_memory["debugger_reports"]), 1)
        
        # Check report properties
        report = updated_memory["debugger_reports"][0]
        self.assertEqual(report["loop_id"], "loop_123")
        self.assertEqual(report["failure_type"], "unknown")
        self.assertIn("suggested_fix", report)
        self.assertIn("patch_plan", report)
        self.assertIn("steps", report["patch_plan"])
        self.assertIn("next_agent", report)
        self.assertEqual(report["next_agent"], "critic")

if __name__ == "__main__":
    unittest.main()
