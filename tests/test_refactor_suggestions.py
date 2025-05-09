import unittest
import os
import json

# Assuming the refactor_monitor.py is in the same directory or accessible in PYTHONPATH
from app.validators.refactor_monitor import generate_refactor_suggestion, REFACTOR_SUGGESTION_LOG_PATH

class TestRefactorSuggestions(unittest.TestCase):

    def setUp(self):
        # Ensure the log file is empty before each test
        if os.path.exists(REFACTOR_SUGGESTION_LOG_PATH):
            os.remove(REFACTOR_SUGGESTION_LOG_PATH)

    def tearDown(self):
        # Clean up the log file after each test
        if os.path.exists(REFACTOR_SUGGESTION_LOG_PATH):
            os.remove(REFACTOR_SUGGESTION_LOG_PATH)

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

        self.assertTrue(os.path.exists(REFACTOR_SUGGESTION_LOG_PATH))
        with open(REFACTOR_SUGGESTION_LOG_PATH, 'r') as f:
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

        self.assertTrue(os.path.exists(REFACTOR_SUGGESTION_LOG_PATH))
        with open(REFACTOR_SUGGESTION_LOG_PATH, 'r') as f:
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

        self.assertTrue(os.path.exists(REFACTOR_SUGGESTION_LOG_PATH))
        with open(REFACTOR_SUGGESTION_LOG_PATH, 'r') as f:
            log_data = json.load(f)
        self.assertEqual(len(log_data), 2)
        self.assertEqual(log_data[0]["loop_id"], "loop1")
        self.assertEqual(log_data[1]["loop_id"], "loop2")

if __name__ == '__main__':
    unittest.main()

