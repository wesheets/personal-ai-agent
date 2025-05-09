#!/usr/bin/env python3
import sys
import os
import json # Added import for json module

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.validators.refactor_monitor import generate_refactor_suggestion
from unittest.mock import patch, mock_open
import unittest

# Define the path to the log file for testing purposes
TEST_REFACTOR_SUGGESTION_LOG_PATH = os.path.join(project_root, "tests", "test_refactor_suggestion_log.json")

class TestRefactorSuggestionsStandalone(unittest.TestCase):

    def setUp(self):
        # Ensure the log file is empty before each test
        if os.path.exists(TEST_REFACTOR_SUGGESTION_LOG_PATH):
            os.remove(TEST_REFACTOR_SUGGESTION_LOG_PATH)
        # Override the REFACTOR_SUGGESTION_LOG_PATH in refactor_monitor for testing
        self.patcher = patch('app.validators.refactor_monitor.REFACTOR_SUGGESTION_LOG_PATH', TEST_REFACTOR_SUGGESTION_LOG_PATH)
        self.patcher.start()

    def tearDown(self):
        # Clean up the log file after each test
        if os.path.exists(TEST_REFACTOR_SUGGESTION_LOG_PATH):
            os.remove(TEST_REFACTOR_SUGGESTION_LOG_PATH)
        self.patcher.stop()

    def test_generate_refactor_suggestion_high_regret(self):
        """Test that a refactor suggestion is logged for high regret score."""
        loop_id = "loop_regret_test"
        component = "TestComponentRegret"
        recommended_action = "Review logic for regret calculation."
        confidence_score = 0.9

        generate_refactor_suggestion(
            trigger_reason="High Regret Score",
            loop_id=loop_id,
            component=component,
            recommended_action=recommended_action,
            confidence_score=confidence_score
        )

        self.assertTrue(os.path.exists(TEST_REFACTOR_SUGGESTION_LOG_PATH))
        with open(TEST_REFACTOR_SUGGESTION_LOG_PATH, 'r') as f:
            log_data = json.load(f)
        self.assertEqual(len(log_data), 1)
        suggestion = log_data[0]
        self.assertEqual(suggestion["trigger_reason"], "High Regret Score")
        self.assertEqual(suggestion["loop_id"], loop_id)
        self.assertEqual(suggestion["component"], component)
        self.assertEqual(suggestion["recommended_action"], recommended_action)
        self.assertEqual(suggestion["confidence_score"], confidence_score)

    def test_generate_refactor_suggestion_high_sadness(self):
        """Test that a refactor suggestion is logged for high sadness score."""
        loop_id = "loop_sadness_test"
        component = "TestComponentSadness"
        recommended_action = "Investigate causes of high sadness."
        confidence_score = 0.88

        generate_refactor_suggestion(
            trigger_reason="High Sadness Score",
            loop_id=loop_id,
            component=component,
            recommended_action=recommended_action,
            confidence_score=confidence_score
        )

        self.assertTrue(os.path.exists(TEST_REFACTOR_SUGGESTION_LOG_PATH))
        with open(TEST_REFACTOR_SUGGESTION_LOG_PATH, 'r') as f:
            log_data = json.load(f)
        self.assertEqual(len(log_data), 1)
        suggestion = log_data[0]
        self.assertEqual(suggestion["trigger_reason"], "High Sadness Score")
        self.assertEqual(suggestion["loop_id"], loop_id)
        self.assertEqual(suggestion["component"], component)
        self.assertEqual(suggestion["recommended_action"], recommended_action)
        self.assertEqual(suggestion["confidence_score"], confidence_score)

    def test_multiple_suggestions_logged_correctly(self):
        """Test that multiple suggestions are logged correctly in the same file."""
        generate_refactor_suggestion(
            trigger_reason="High Regret Score",
            loop_id="loop1",
            component="CompA",
            recommended_action="Action A",
            confidence_score=0.7
        )
        generate_refactor_suggestion(
            trigger_reason="High Sadness Score",
            loop_id="loop2",
            component="CompB",
            recommended_action="Action B",
            confidence_score=0.9
        )

        self.assertTrue(os.path.exists(TEST_REFACTOR_SUGGESTION_LOG_PATH))
        with open(TEST_REFACTOR_SUGGESTION_LOG_PATH, 'r') as f:
            log_data = json.load(f)
        self.assertEqual(len(log_data), 2)
        self.assertEqual(log_data[0]["loop_id"], "loop1")
        self.assertEqual(log_data[1]["loop_id"], "loop2")

if __name__ == '__main__':
    unittest.main()

