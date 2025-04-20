"""
Tests for the plan validator module.

This module contains tests for the plan validator to ensure it correctly validates
loop plans against the schema.
"""

import unittest
import json
import os
import sys

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.plan_validator import validate_loop_plan, validate_and_log

class TestPlanValidator(unittest.TestCase):
    """Test cases for the plan validator module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Valid test plan with all required fields
        self.valid_plan = {
            "loop_id": 26,
            "agents": ["hal", "nova", "critic"],
            "goals": ["implement UI component", "add validation logic"],
            "planned_files": ["src/components/Button.jsx", "src/utils/validators.js"],
            "confirmed": True,
            "confirmed_by": "operator",
            "confirmed_at": "2025-04-22T18:20:03Z"
        }
        
        # Plan with missing required field
        self.missing_field_plan = {
            "loop_id": 27,
            "agents": ["hal", "nova"],
            "goals": ["fix bug in validation"],
            # Missing planned_files
            "confirmed": True,
            "confirmed_by": "operator",
            "confirmed_at": "2025-04-22T19:15:00Z"
        }
        
        # Plan with wrong data type
        self.wrong_type_plan = {
            "loop_id": "28",  # Should be a number, not a string
            "agents": ["hal", "nova"],
            "goals": ["refactor code"],
            "planned_files": ["src/utils/helpers.js"],
            "confirmed": True,
            "confirmed_by": "operator",
            "confirmed_at": "2025-04-22T20:30:00Z"
        }
    
    def test_valid_plan(self):
        """Test that a valid plan passes validation."""
        errors = validate_loop_plan(self.valid_plan)
        self.assertEqual(len(errors), 0, "Valid plan should have no validation errors")
        
        # Test the combined validate_and_log function
        is_valid, errors, trace = validate_and_log(self.valid_plan)
        self.assertTrue(is_valid, "Valid plan should be marked as valid")
        self.assertEqual(len(errors), 0, "Valid plan should have no validation errors")
        self.assertEqual(trace["status"], "passed", "Trace should indicate validation passed")
    
    def test_missing_field(self):
        """Test that a plan with a missing required field fails validation."""
        errors = validate_loop_plan(self.missing_field_plan)
        self.assertGreater(len(errors), 0, "Plan with missing field should have validation errors")
        
        # Check if the error message mentions the missing field
        has_missing_field_error = any("planned_files" in error for error in errors)
        self.assertTrue(has_missing_field_error, "Error should mention the missing field")
        
        # Test the combined validate_and_log function
        is_valid, errors, trace = validate_and_log(self.missing_field_plan)
        self.assertFalse(is_valid, "Plan with missing field should be marked as invalid")
        self.assertGreater(len(errors), 0, "Plan with missing field should have validation errors")
        self.assertEqual(trace["status"], "failed", "Trace should indicate validation failed")
    
    def test_wrong_data_type(self):
        """Test that a plan with a wrong data type fails validation."""
        errors = validate_loop_plan(self.wrong_type_plan)
        self.assertGreater(len(errors), 0, "Plan with wrong data type should have validation errors")
        
        # Check if the error message mentions the field with the wrong type
        has_wrong_type_error = any("loop_id" in error for error in errors)
        self.assertTrue(has_wrong_type_error, "Error should mention the field with wrong type")
        
        # Test the combined validate_and_log function
        is_valid, errors, trace = validate_and_log(self.wrong_type_plan)
        self.assertFalse(is_valid, "Plan with wrong data type should be marked as invalid")
        self.assertGreater(len(errors), 0, "Plan with wrong data type should have validation errors")
        self.assertEqual(trace["status"], "failed", "Trace should indicate validation failed")

if __name__ == "__main__":
    unittest.main()
