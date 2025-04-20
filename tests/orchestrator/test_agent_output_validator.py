"""
Tests for the agent output validator module.

This module contains tests for the agent output validator module to ensure it correctly
validates agent file outputs against predefined schemas.
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.agent_output_validator import (
    get_schema_for_file,
    validate_agent_file_output,
    validate_and_log_output,
    extract_metadata,
    validate_file_content,
    handle_rejected_file
)

class TestAgentOutputValidator(unittest.TestCase):
    """Test cases for the agent output validator module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Sample file contents for testing
        self.valid_jsx_content = """
import React from 'react';

function UserProfile(props) {
    const [name, setName] = React.useState('');
    
    return (
        <div className="user-profile">
            <h1>User Profile</h1>
            <input 
                type="text" 
                value={name} 
                onChange={(e) => setName(e.target.value)} 
            />
        </div>
    );
}

export default UserProfile;
"""
        
        self.invalid_jsx_content = """
function UserProfile(props) {
    // Missing React import
    return (
        <div className="user-profile">
            <h1>User Profile</h1>
        </div>
    );
}
// Missing export
"""
        
        self.valid_json_content = """
{
    "name": "UserModel",
    "fields": {
        "id": "string",
        "name": "string",
        "email": "string",
        "age": "number"
    },
    "relationships": {
        "posts": {
            "type": "hasMany",
            "model": "Post",
            "foreignKey": "userId"
        }
    }
}
"""
        
        self.invalid_json_content = """
{
    "name": "UserModel",
    "fields": {
        "id": "string",
        "name": "string",
        "email": "string",
        "age": "number",
    }, // Invalid trailing comma
    "relationships": {
        "posts": {
            "type": "hasMany",
            "model": "Post",
            "foreignKey": "userId"
        }
    }
}
"""
        
        self.valid_md_content = """
# User Guide

## Introduction
This is a user guide for the application.

## Getting Started
Here's how to get started with the application.

```javascript
import { App } from './app';
const app = new App();
app.start();
```

## Troubleshooting
If you encounter any issues, please contact support.
"""
        
        self.invalid_md_content = """
This is a user guide for the application.

Getting Started
Here's how to get started with the application.

Troubleshooting
If you encounter any issues, please contact support.
"""
        
        # Create test files
        self.valid_jsx_file = os.path.join(self.test_dir, "UserProfile.jsx")
        with open(self.valid_jsx_file, "w") as f:
            f.write(self.valid_jsx_content)
        
        self.invalid_jsx_file = os.path.join(self.test_dir, "InvalidComponent.jsx")
        with open(self.invalid_jsx_file, "w") as f:
            f.write(self.invalid_jsx_content)
        
        self.valid_json_file = os.path.join(self.test_dir, "UserModel.json")
        with open(self.valid_json_file, "w") as f:
            f.write(self.valid_json_content)
        
        self.invalid_json_file = os.path.join(self.test_dir, "InvalidModel.json")
        with open(self.invalid_json_file, "w") as f:
            f.write(self.invalid_json_content)
        
        self.valid_md_file = os.path.join(self.test_dir, "UserGuide.md")
        with open(self.valid_md_file, "w") as f:
            f.write(self.valid_md_content)
        
        self.invalid_md_file = os.path.join(self.test_dir, "InvalidGuide.md")
        with open(self.invalid_md_file, "w") as f:
            f.write(self.invalid_md_content)
        
        self.unknown_ext_file = os.path.join(self.test_dir, "unknown.xyz")
        with open(self.unknown_ext_file, "w") as f:
            f.write("This file has an unknown extension")
        
        # Mock project ID
        self.project_id = "test_project_001"
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory and all its contents
        shutil.rmtree(self.test_dir)
    
    def test_get_schema_for_file_valid_extensions(self):
        """Test getting schema for files with valid extensions."""
        # Test JSX file
        jsx_schema = get_schema_for_file(self.valid_jsx_file, "hal")
        self.assertIn("component_ui.schema.json", jsx_schema, "Should get component UI schema for JSX file")
        
        # Test JSON file
        json_schema = get_schema_for_file(self.valid_json_file, "nova")
        self.assertIn("data_model.schema.json", json_schema, "Should get data model schema for JSON file")
        
        # Test MD file
        md_schema = get_schema_for_file(self.valid_md_file, "critic")
        self.assertIn("doc_template.schema.json", md_schema, "Should get doc template schema for MD file")
    
    def test_get_schema_for_file_unknown_extension(self):
        """Test getting schema for files with unknown extensions."""
        # Test with HAL agent
        with self.assertRaises(ValueError):
            get_schema_for_file(self.unknown_ext_file, "unknown_agent")
        
        # Test with known agents
        hal_schema = get_schema_for_file(self.unknown_ext_file, "hal")
        self.assertIn("component_ui.schema.json", hal_schema, "Should get component UI schema for HAL")
        
        nova_schema = get_schema_for_file(self.unknown_ext_file, "nova")
        self.assertIn("data_model.schema.json", nova_schema, "Should get data model schema for NOVA")
        
        critic_schema = get_schema_for_file(self.unknown_ext_file, "critic")
        self.assertIn("doc_template.schema.json", critic_schema, "Should get doc template schema for CRITIC")
    
    @patch('orchestrator.modules.agent_output_validator.validate_file_content')
    def test_validate_agent_file_output_valid_files(self, mock_validate_content):
        """Test validating valid agent file outputs."""
        # Mock validate_file_content to return no errors
        mock_validate_content.return_value = []
        
        # Test valid JSX file
        jsx_result = validate_agent_file_output("hal", self.valid_jsx_file)
        self.assertTrue(jsx_result["valid"], "Valid JSX file should pass validation")
        self.assertEqual(len(jsx_result["errors"]), 0, "Valid JSX file should have no errors")
        
        # Test valid JSON file
        json_result = validate_agent_file_output("nova", self.valid_json_file)
        self.assertTrue(json_result["valid"], "Valid JSON file should pass validation")
        self.assertEqual(len(json_result["errors"]), 0, "Valid JSON file should have no errors")
        
        # Test valid MD file
        md_result = validate_agent_file_output("critic", self.valid_md_file)
        self.assertTrue(md_result["valid"], "Valid MD file should pass validation")
        self.assertEqual(len(md_result["errors"]), 0, "Valid MD file should have no errors")
    
    def test_validate_agent_file_output_invalid_files(self):
        """Test validating invalid agent file outputs."""
        # Test invalid JSX file
        jsx_result = validate_agent_file_output("hal", self.invalid_jsx_file)
        self.assertFalse(jsx_result["valid"], "Invalid JSX file should fail validation")
        self.assertGreater(len(jsx_result["errors"]), 0, "Invalid JSX file should have errors")
        
        # Test invalid JSON file
        json_result = validate_agent_file_output("nova", self.invalid_json_file)
        self.assertFalse(json_result["valid"], "Invalid JSON file should fail validation")
        self.assertGreater(len(json_result["errors"]), 0, "Invalid JSON file should have errors")
        
        # Test invalid MD file
        md_result = validate_agent_file_output("critic", self.invalid_md_file)
        self.assertFalse(md_result["valid"], "Invalid MD file should fail validation")
        self.assertGreater(len(md_result["errors"]), 0, "Invalid MD file should have errors")
    
    def test_validate_agent_file_output_nonexistent_file(self):
        """Test validating a nonexistent file."""
        result = validate_agent_file_output("hal", "/nonexistent/file.jsx")
        self.assertFalse(result["valid"], "Nonexistent file should fail validation")
        self.assertIn("File not found", result["errors"][0], "Error should mention file not found")
    
    def test_extract_metadata_jsx(self):
        """Test extracting metadata from JSX files."""
        metadata = extract_metadata(self.valid_jsx_file, self.valid_jsx_content, "hal")
        self.assertEqual(metadata["componentName"], "UserProfile", "Should extract correct component name")
        self.assertTrue(metadata["hasProps"], "Should detect props usage")
        self.assertTrue(metadata["hasState"], "Should detect state usage")
        self.assertIn("react", [dep.lower() for dep in metadata["dependencies"]], "Should detect React dependency")
    
    def test_extract_metadata_json(self):
        """Test extracting metadata from JSON files."""
        metadata = extract_metadata(self.valid_json_file, self.valid_json_content, "nova")
        self.assertEqual(metadata["modelName"], "UserModel", "Should extract correct model name")
        self.assertIn("name", metadata["fields"], "Should extract fields")
        self.assertIn("posts", metadata["relationships"], "Should extract relationships")
    
    def test_extract_metadata_md(self):
        """Test extracting metadata from MD files."""
        metadata = extract_metadata(self.valid_md_file, self.valid_md_content, "critic")
        self.assertEqual(metadata["title"], "User Guide", "Should extract correct title")
        self.assertIn("Introduction", metadata["sections"], "Should extract sections")
        self.assertTrue(metadata["hasCodeExamples"], "Should detect code examples")
    
    def test_validate_file_content_jsx(self):
        """Test validating JSX file content."""
        # Test valid JSX
        valid_errors = validate_file_content(self.valid_jsx_file, self.valid_jsx_content, "hal")
        self.assertEqual(len(valid_errors), 0, "Valid JSX should have no errors")
        
        # Test invalid JSX
        invalid_errors = validate_file_content(self.invalid_jsx_file, self.invalid_jsx_content, "hal")
        self.assertGreater(len(invalid_errors), 0, "Invalid JSX should have errors")
        self.assertTrue(any("import React" in error for error in invalid_errors), "Should detect missing React import")
        self.assertTrue(any("export" in error for error in invalid_errors), "Should detect missing export")
    
    def test_validate_file_content_json(self):
        """Test validating JSON file content."""
        # Test valid JSON
        valid_errors = validate_file_content(self.valid_json_file, self.valid_json_content, "nova")
        self.assertEqual(len(valid_errors), 0, "Valid JSON should have no errors")
        
        # Test invalid JSON
        invalid_errors = validate_file_content(self.invalid_json_file, self.invalid_json_content, "nova")
        self.assertGreater(len(invalid_errors), 0, "Invalid JSON should have errors")
        self.assertTrue(any("Invalid JSON" in error for error in invalid_errors), "Should detect invalid JSON")
    
    def test_validate_file_content_md(self):
        """Test validating MD file content."""
        # Test valid MD
        valid_errors = validate_file_content(self.valid_md_file, self.valid_md_content, "critic")
        self.assertEqual(len(valid_errors), 0, "Valid MD should have no errors")
        
        # Test invalid MD
        invalid_errors = validate_file_content(self.invalid_md_file, self.invalid_md_content, "critic")
        self.assertGreater(len(invalid_errors), 0, "Invalid MD should have errors")
        self.assertTrue(any("title" in error for error in invalid_errors), "Should detect missing title")
    
    @patch('orchestrator.modules.agent_output_validator.log_to_memory')
    @patch('orchestrator.modules.agent_output_validator.log_to_chat')
    @patch('orchestrator.modules.agent_output_validator.handle_rejected_file')
    @patch('orchestrator.modules.agent_output_validator.notify_critic')
    def test_validate_and_log_output_valid_file(self, mock_notify_critic, mock_handle_rejected, mock_log_chat, mock_log_memory):
        """Test validating and logging output for a valid file."""
        # Mock validate_agent_file_output to return valid result
        with patch('orchestrator.modules.agent_output_validator.validate_agent_file_output') as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "errors": []
            }
            
            # Validate and log output
            result = validate_and_log_output(self.project_id, "hal", self.valid_jsx_file)
            
            # Verify result
            self.assertTrue(result["valid"], "Should return valid result")
            
            # Verify logging calls
            self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
            self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
            
            # Verify no rejection handling
            mock_handle_rejected.assert_not_called()
            mock_notify_critic.assert_not_called()
    
    @patch('orchestrator.modules.agent_output_validator.log_to_memory')
    @patch('orchestrator.modules.agent_output_validator.log_to_chat')
    @patch('orchestrator.modules.agent_output_validator.handle_rejected_file')
    @patch('orchestrator.modules.agent_output_validator.notify_critic')
    def test_validate_and_log_output_invalid_file(self, mock_notify_critic, mock_handle_rejected, mock_log_chat, mock_log_memory):
        """Test validating and logging output for an invalid file."""
        # Mock validate_agent_file_output to return invalid result
        with patch('orchestrator.modules.agent_output_validator.validate_agent_file_output') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "errors": ["Test error"]
            }
            
            # Validate and log output
            result = validate_and_log_output(self.project_id, "hal", self.invalid_jsx_file)
            
            # Verify result
            self.assertFalse(result["valid"], "Should return invalid result")
            
            # Verify logging calls
            self.assertEqual(mock_log_memory.call_count, 3, "Should log to memory three times")
            self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
            
            # Verify rejection handling
            mock_handle_rejected.assert_called_once()
            mock_notify_critic.assert_called_once()
    
    def test_handle_rejected_file(self):
        """Test handling a rejected file."""
        # Create a test file to reject
        test_file = os.path.join(self.test_dir, "test_reject.jsx")
        with open(test_file, "w") as f:
            f.write("Test content")
        
        # Handle rejected file
        handle_rejected_file(test_file)
        
        # Verify file was moved
        self.assertFalse(os.path.exists(test_file), "Original file should be moved")
        
        # Verify rejected_output directory was created
        rejected_dir = os.path.join(self.test_dir, "rejected_output")
        self.assertTrue(os.path.exists(rejected_dir), "Rejected output directory should be created")
        
        # Verify a file was created in the rejected directory
        rejected_files = os.listdir(rejected_dir)
        self.assertEqual(len(rejected_files), 1, "One file should be in rejected directory")
        self.assertTrue(any("test_reject.jsx" in f for f in rejected_files), "Rejected file should have original name")

if __name__ == "__main__":
    unittest.main()
