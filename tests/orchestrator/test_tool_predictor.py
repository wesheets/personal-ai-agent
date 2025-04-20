"""
Tests for the tool predictor module.

This module contains tests for the tool predictor module to ensure it correctly
predicts required tools and checks their availability.
"""

import unittest
import json
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.tool_predictor import (
    predict_required_tools,
    check_tool_availability,
    tool_check_driver,
    MOCK_TOOL_REGISTRY
)

class TestToolPredictor(unittest.TestCase):
    """Test cases for the tool predictor module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample loop plans for testing
        self.frontend_plan = {
            "loop_id": 29,
            "agents": ["hal", "nova", "critic"],
            "goals": ["Create a React component for user profile", "Implement form validation"],
            "planned_files": ["src/components/UserProfile.jsx", "src/utils/validation.js"],
            "confirmed": True,
            "confirmed_by": "operator",
            "confirmed_at": "2025-04-20T12:00:00Z"
        }
        
        self.backend_plan = {
            "loop_id": 30,
            "agents": ["hal", "critic"],
            "goals": ["Create an API endpoint for authentication", "Implement database queries"],
            "planned_files": ["src/api/auth.js", "src/models/user.js", "src/database/queries.sql"],
            "confirmed": True,
            "confirmed_by": "operator",
            "confirmed_at": "2025-04-20T13:00:00Z"
        }
        
        self.empty_plan = {
            "loop_id": 31,
            "agents": [],
            "goals": [],
            "planned_files": [],
            "confirmed": False,
            "confirmed_by": "",
            "confirmed_at": "2025-04-20T14:00:00Z"
        }
        
        # Mock project ID
        self.project_id = "test_project_001"
        
    def test_predict_required_tools_frontend(self):
        """Test that tools are correctly predicted for a frontend-focused plan."""
        tools = predict_required_tools(self.frontend_plan)
        self.assertGreater(len(tools), 0, "Should predict at least one tool")
        
        # Check for expected frontend tools
        frontend_tools = ["component_builder", "ui_renderer", "file_writer"]
        for tool in frontend_tools:
            self.assertIn(tool, tools, f"Frontend plan should require {tool}")
    
    def test_predict_required_tools_backend(self):
        """Test that tools are correctly predicted for a backend-focused plan."""
        tools = predict_required_tools(self.backend_plan)
        self.assertGreater(len(tools), 0, "Should predict at least one tool")
        
        # Check for expected backend tools
        backend_tools = ["api_client", "database_connector", "file_writer"]
        for tool in backend_tools:
            self.assertIn(tool, tools, f"Backend plan should require {tool}")
    
    def test_predict_required_tools_empty(self):
        """Test that no tools are predicted for an empty plan."""
        tools = predict_required_tools(self.empty_plan)
        self.assertEqual(len(tools), 0, "Empty plan should predict no tools")
    
    def test_check_tool_availability_all_available(self):
        """Test checking availability when all tools are available."""
        # Use a subset of tools that are in the mock registry
        available_tools = MOCK_TOOL_REGISTRY[:3]
        availability = check_tool_availability(available_tools)
        
        self.assertEqual(len(availability), len(available_tools), "Should check all tools")
        for tool, status in availability.items():
            self.assertEqual(status, "available", f"Tool {tool} should be available")
    
    def test_check_tool_availability_some_missing(self):
        """Test checking availability when some tools are missing."""
        # Mix of available and non-existent tools
        mixed_tools = MOCK_TOOL_REGISTRY[:2] + ["non_existent_tool_1", "non_existent_tool_2"]
        availability = check_tool_availability(mixed_tools)
        
        self.assertEqual(len(availability), len(mixed_tools), "Should check all tools")
        for tool in MOCK_TOOL_REGISTRY[:2]:
            self.assertEqual(availability[tool], "available", f"Tool {tool} should be available")
        for tool in ["non_existent_tool_1", "non_existent_tool_2"]:
            self.assertEqual(availability[tool], "missing", f"Tool {tool} should be missing")
    
    def test_check_tool_availability_empty(self):
        """Test checking availability with an empty tool list."""
        availability = check_tool_availability([])
        self.assertEqual(availability, {}, "Empty tool list should return empty dict")
    
    @patch('orchestrator.modules.tool_predictor.log_to_memory')
    @patch('orchestrator.modules.tool_predictor.log_to_chat')
    def test_tool_check_driver_all_available(self, mock_log_chat, mock_log_memory):
        """Test the tool_check_driver with all tools available."""
        # Mock predict_required_tools to return only available tools
        with patch('orchestrator.modules.tool_predictor.predict_required_tools', 
                  return_value=MOCK_TOOL_REGISTRY[:3]):
            
            updated_plan = tool_check_driver(self.project_id, self.frontend_plan)
            
            # Verify updated plan
            self.assertIn("tool_requirements", updated_plan, "Plan should have tool_requirements")
            self.assertIn("tools_available", updated_plan, "Plan should have tools_available")
            
            # Verify all tools are available
            for tool, status in updated_plan["tools_available"].items():
                self.assertEqual(status, "available", f"Tool {tool} should be available")
            
            # Verify logging calls
            self.assertGreaterEqual(mock_log_memory.call_count, 2, "Should log to memory at least twice")
            self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
            
            # Verify chat message indicates all tools are available
            chat_message = mock_log_chat.call_args[0][1]["message"]
            self.assertIn("All required tools are available", chat_message, 
                         "Chat message should indicate all tools are available")
    
    @patch('orchestrator.modules.tool_predictor.log_to_memory')
    @patch('orchestrator.modules.tool_predictor.log_to_chat')
    def test_tool_check_driver_missing_tools(self, mock_log_chat, mock_log_memory):
        """Test the tool_check_driver with missing tools."""
        # Mock predict_required_tools to return some non-existent tools
        with patch('orchestrator.modules.tool_predictor.predict_required_tools', 
                  return_value=MOCK_TOOL_REGISTRY[:2] + ["non_existent_tool"]):
            
            updated_plan = tool_check_driver(self.project_id, self.frontend_plan)
            
            # Verify updated plan
            self.assertIn("tool_requirements", updated_plan, "Plan should have tool_requirements")
            self.assertIn("tools_available", updated_plan, "Plan should have tools_available")
            
            # Verify some tools are missing
            missing_tools = [tool for tool, status in updated_plan["tools_available"].items() 
                           if status == "missing"]
            self.assertGreater(len(missing_tools), 0, "Should have missing tools")
            
            # Verify logging calls
            self.assertGreaterEqual(mock_log_memory.call_count, 3, "Should log to memory at least three times")
            self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
            
            # Verify chat message indicates missing tools
            chat_message = mock_log_chat.call_args[0][1]["message"]
            self.assertIn("Missing tools", chat_message, 
                         "Chat message should indicate missing tools")
    
    @patch('orchestrator.modules.tool_predictor.log_to_memory')
    @patch('orchestrator.modules.tool_predictor.log_to_chat')
    def test_tool_check_driver_error(self, mock_log_chat, mock_log_memory):
        """Test the tool_check_driver with an error-causing plan."""
        # Call with invalid plan
        updated_plan = tool_check_driver(self.project_id, None)
        
        # Verify plan is returned unchanged
        self.assertIsNone(updated_plan, "Should return the original plan")
        
        # Verify logging calls
        self.assertEqual(mock_log_memory.call_count, 1, "Should log to memory once")
        self.assertEqual(mock_log_chat.call_count, 1, "Should log to chat once")
        
        # Verify chat message indicates an error
        chat_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("Failed to predict", chat_message, 
                     "Chat message should indicate prediction failure")

if __name__ == "__main__":
    unittest.main()
