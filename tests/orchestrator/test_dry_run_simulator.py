"""
Test cases for the Dry-Run Agent Execution Mode module.

Tests the ability to simulate file generation without writing to disk or committing to Git.
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.dry_run_simulator import (
    simulate_agent_output,
    log_simulation_result,
    dry_run_driver,
    generate_jsx_preview,
    generate_json_preview,
    generate_md_preview,
    simulate_validation,
    request_operator_approval,
    approve_simulation
)

class TestDryRunSimulator(unittest.TestCase):
    """Test cases for the Dry-Run Agent Execution Mode module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample project and agent data
        self.project_id = "test_project_001"
        self.agent_name = "hal"
        self.loop_id = 33
        
        # Sample contract
        self.contract = {
            "loop_id": self.loop_id,
            "agent": self.agent_name,
            "goal": "Create LoginForm.jsx component",
            "file": "LoginForm.jsx",
            "tools": ["component_builder", "ui_generator"],
            "confirmed": True,
            "received_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "trace_id": f"loop_{self.loop_id}_{self.agent_name}_contract"
        }
        
        # Patch the log_to_memory and log_to_chat functions
        self.memory_patch = patch('orchestrator.modules.dry_run_simulator.log_to_memory')
        self.chat_patch = patch('orchestrator.modules.dry_run_simulator.log_to_chat')
        self.memory_mock = self.memory_patch.start()
        self.chat_mock = self.chat_patch.start()
        
        # Patch the check_tool_availability function to always return True
        self.tool_patch = patch('orchestrator.modules.dry_run_simulator.check_tool_availability', return_value=True)
        self.tool_mock = self.tool_patch.start()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Stop all patches
        self.memory_patch.stop()
        self.chat_patch.stop()
        self.tool_patch.stop()
    
    @patch('orchestrator.modules.dry_run_simulator.generate_jsx_preview')
    def test_simulate_agent_output_jsx(self, mock_generate_jsx):
        """Test simulating output for a JSX file."""
        # Mock the generate_jsx_preview function
        mock_generate_jsx.return_value = """import React from 'react';
function LoginForm() {
  return <div>Login Form</div>;
}
export default LoginForm;"""
        
        # Call the function
        result = simulate_agent_output(self.agent_name, self.contract)
        
        # Check the result
        self.assertEqual(result["file"], "LoginForm.jsx")
        self.assertIsNotNone(result["content_preview"])
        self.assertIn("import React", result["content_preview"])
        self.assertIn("function LoginForm", result["content_preview"])
        self.assertEqual(result["tool_used"], "component_builder")
        self.assertEqual(result["schema_validation_result"], "passed")
        self.assertGreater(result["estimated_tokens"], 0)
    
    def test_simulate_agent_output_missing_tool(self):
        """Test simulating output when a required tool is missing."""
        # Patch check_tool_availability to return False
        with patch('orchestrator.modules.dry_run_simulator.check_tool_availability', return_value=False):
            # Call the function
            result = simulate_agent_output(self.agent_name, self.contract)
            
            # Check the result
            self.assertEqual(result["file"], "LoginForm.jsx")
            self.assertIsNone(result["content_preview"])
            self.assertEqual(result["tool_used"], "component_builder")
            self.assertEqual(result["schema_validation_result"], "failed")
            self.assertIn("Required tool", result["validation_errors"][0])
    
    def test_simulate_agent_output_json(self):
        """Test simulating output for a JSON file."""
        # Create a contract for a JSON file
        json_contract = self.contract.copy()
        json_contract["file"] = "UserModel.json"
        json_contract["goal"] = "Create UserModel.json data model"
        
        # Call the function
        result = simulate_agent_output("nova", json_contract)
        
        # Check the result
        self.assertEqual(result["file"], "UserModel.json")
        self.assertIsNotNone(result["content_preview"])
        self.assertIn("UserModel", result["content_preview"])
        self.assertIn("fields", result["content_preview"])
        self.assertEqual(result["schema_validation_result"], "passed")
    
    def test_simulate_agent_output_md(self):
        """Test simulating output for a Markdown file."""
        # Create a contract for a Markdown file
        md_contract = self.contract.copy()
        md_contract["file"] = "Documentation.md"
        md_contract["goal"] = "Create Documentation.md"
        
        # Call the function
        result = simulate_agent_output("critic", md_contract)
        
        # Check the result
        self.assertEqual(result["file"], "Documentation.md")
        self.assertIsNotNone(result["content_preview"])
        self.assertIn("# Documentation", result["content_preview"])
        self.assertIn("## Overview", result["content_preview"])
        self.assertEqual(result["schema_validation_result"], "passed")
    
    def test_log_simulation_result(self):
        """Test logging simulation results."""
        # Create a sample simulation result
        simulation_result = {
            "file": "LoginForm.jsx",
            "content_preview": "import React from 'react';",
            "tool_used": "component_builder",
            "schema_validation_result": "passed",
            "estimated_tokens": 100
        }
        
        # Call the function
        log_simulation_result(self.project_id, self.agent_name, self.loop_id, simulation_result)
        
        # Check that log_to_memory was called with the expected arguments
        self.memory_mock.assert_any_call(self.project_id, {
            "loop_trace": [unittest.mock.ANY]
        })
        self.memory_mock.assert_any_call(self.project_id, {
            "agent_trace": {
                self.agent_name: [unittest.mock.ANY]
            }
        })
        
        # Check that log_to_chat was called
        self.chat_mock.assert_called()
    
    def test_log_simulation_result_with_errors(self):
        """Test logging simulation results with validation errors."""
        # Create a sample simulation result with errors
        simulation_result = {
            "file": "LoginForm.jsx",
            "content_preview": "import React from 'react';",
            "tool_used": "component_builder",
            "schema_validation_result": "failed",
            "validation_errors": ["Missing component export"],
            "estimated_tokens": 100
        }
        
        # Call the function
        log_simulation_result(self.project_id, self.agent_name, self.loop_id, simulation_result)
        
        # Check that log_to_memory was called with the expected arguments
        self.memory_mock.assert_any_call(self.project_id, {
            "loop_trace": [unittest.mock.ANY]
        })
        
        # Check that log_to_chat was called with error message
        self.chat_mock.assert_called()
        # Get the last call arguments
        args, kwargs = self.chat_mock.call_args
        # Check that the message contains the validation error
        self.assertIn("Validation errors:", args[1]["message"])
    
    @patch('orchestrator.modules.dry_run_simulator.get_agent_contract')
    @patch('orchestrator.modules.dry_run_simulator.simulate_agent_output')
    def test_dry_run_driver(self, mock_simulate, mock_get_contract):
        """Test the dry run driver with a valid contract."""
        # Set up the mock to return our contract
        mock_get_contract.return_value = self.contract
        
        # Set up the mock to return a simulation result
        mock_simulation_result = {
            "file": "LoginForm.jsx",
            "content_preview": "import React from 'react';",
            "tool_used": "component_builder",
            "schema_validation_result": "passed",
            "estimated_tokens": 100
        }
        mock_simulate.return_value = mock_simulation_result
        
        # Call the function
        result = dry_run_driver(self.project_id, self.agent_name)
        
        # Check the result
        self.assertEqual(result["file"], "LoginForm.jsx")
        self.assertIsNotNone(result["content_preview"])
        self.assertEqual(result["schema_validation_result"], "passed")
        self.assertTrue(result["requires_approval"])
        self.assertFalse(result["approved"])
        
        # Check that log_simulation_result was called
        self.memory_mock.assert_called()
        self.chat_mock.assert_called()
    
    @patch('orchestrator.modules.dry_run_simulator.get_agent_contract')
    def test_dry_run_driver_no_contract(self, mock_get_contract):
        """Test the dry run driver when no contract is found."""
        # Set up the mock to return None
        mock_get_contract.return_value = None
        
        # Call the function
        result = dry_run_driver(self.project_id, self.agent_name)
        
        # Check the result
        self.assertIn("error", result)
        self.assertIn("No contract found", result["error"])
        
        # Check that log_to_chat was called with error message
        self.chat_mock.assert_called()
    
    @patch('orchestrator.modules.dry_run_simulator.get_agent_contract')
    @patch('orchestrator.modules.dry_run_simulator.simulate_agent_output')
    def test_dry_run_driver_without_approval(self, mock_simulate, mock_get_contract):
        """Test the dry run driver without requiring approval."""
        # Set up the mock to return our contract
        mock_get_contract.return_value = self.contract
        
        # Set up the mock to return a simulation result
        mock_simulation_result = {
            "file": "LoginForm.jsx",
            "content_preview": "import React from 'react';",
            "tool_used": "component_builder",
            "schema_validation_result": "passed",
            "estimated_tokens": 100
        }
        mock_simulate.return_value = mock_simulation_result
        
        # Call the function with require_approval=False
        result = dry_run_driver(self.project_id, self.agent_name, require_approval=False)
        
        # Check the result
        self.assertEqual(result["file"], "LoginForm.jsx")
        self.assertFalse(result["requires_approval"])
        self.assertFalse(result["approved"])
    
    def test_request_operator_approval(self):
        """Test requesting operator approval."""
        # Create a sample simulation result
        simulation_result = {
            "file": "LoginForm.jsx",
            "content_preview": "import React from 'react';",
            "tool_used": "component_builder",
            "schema_validation_result": "passed",
            "estimated_tokens": 100
        }
        
        # Call the function
        request_operator_approval(self.project_id, self.agent_name, simulation_result)
        
        # Check that log_to_memory was called with approval request
        self.memory_mock.assert_called_with(self.project_id, {
            "approval_requests": [unittest.mock.ANY]
        })
        
        # Check that log_to_chat was called with approval request message
        self.chat_mock.assert_called()
        # Get the last call arguments
        args, kwargs = self.chat_mock.call_args
        # Check that the message contains the approval request
        self.assertIn("Requesting approval", args[1]["message"])
    
    def test_approve_simulation(self):
        """Test approving a simulation."""
        # Call the function
        result = approve_simulation(self.project_id, self.agent_name, "LoginForm.jsx")
        
        # Check the result
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["agent"], self.agent_name)
        self.assertEqual(result["file"], "LoginForm.jsx")
        
        # Check that log_to_memory was called with approval update
        self.memory_mock.assert_any_call(self.project_id, {
            "approval_requests": [unittest.mock.ANY]
        })
        
        # Check that log_to_memory was called with loop trace update
        self.memory_mock.assert_any_call(self.project_id, {
            "loop_trace": [unittest.mock.ANY]
        })
        
        # Check that log_to_chat was called with approval message
        self.chat_mock.assert_called()
        # Get the last call arguments
        args, kwargs = self.chat_mock.call_args
        # Check that the message contains the approval confirmation
        self.assertIn("Simulation approved", args[1]["message"])
    
    @patch('orchestrator.modules.dry_run_simulator.FILE_TEMPLATES')
    def test_generate_jsx_preview(self, mock_templates):
        """Test generating a JSX preview."""
        # Create a simplified template for testing
        mock_templates.__getitem__.return_value = """import React from 'react';

function {component_name}() {{
  return <div>Test</div>;
}}

export default {component_name};
"""
        
        # Call the function
        preview = generate_jsx_preview("LoginForm.jsx", "Create a login form component")
        
        # Check the result
        self.assertIn("import React", preview)
        self.assertIn("function LoginForm", preview)
        self.assertIn("export default LoginForm", preview)
    
    @patch('orchestrator.modules.dry_run_simulator.FILE_TEMPLATES')
    def test_generate_json_preview(self, mock_templates):
        """Test generating a JSON preview."""
        # Create a simplified template for testing
        mock_templates.__getitem__.return_value = """{{
  "name": "{model_name}",
  "fields": {{
    "id": "string"
  }}
}}
"""
        
        # Call the function
        preview = generate_json_preview("UserModel.json", "Create a user data model")
        
        # Check the result
        self.assertIn("UserModel", preview)
        self.assertIn("fields", preview)
        
        # Verify it's valid JSON
        parsed = json.loads(preview)
        self.assertEqual(parsed["name"], "UserModel")
    
    def test_generate_md_preview(self):
        """Test generating a Markdown preview."""
        # Call the function
        preview = generate_md_preview("Documentation.md", "Create documentation")
        
        # Check the result
        self.assertIn("# Documentation", preview)
        self.assertIn("## Overview", preview)
        self.assertIn("## Details", preview)
        self.assertIn("## Usage", preview)
        self.assertIn("```javascript", preview)
    
    def test_simulate_validation_valid_jsx(self):
        """Test simulating validation for a valid JSX file."""
        # Create a valid JSX content
        content = """import React from 'react';

function TestComponent() {
  return <div>Test</div>;
}

export default TestComponent;
"""
        
        # Call the function
        is_valid, errors = simulate_validation(self.agent_name, "Test.jsx", content)
        
        # Check the result
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_simulate_validation_invalid_jsx(self):
        """Test simulating validation for an invalid JSX file."""
        # Create an invalid JSX content (missing React import)
        content = """
function testComponent() {
  return <div>Test</div>;
}
"""
        
        # Call the function
        is_valid, errors = simulate_validation(self.agent_name, "Test.jsx", content)
        
        # Check the result
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertIn("must import React", errors[0])


if __name__ == '__main__':
    unittest.main()
