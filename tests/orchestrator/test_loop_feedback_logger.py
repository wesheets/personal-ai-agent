"""
Tests for the Loop Feedback Logger module.

This test suite verifies the functionality for tracking when a completed loop is rejected, 
revised, or rescored by the Operator after the fact.
"""

import unittest
import datetime
from unittest.mock import patch, MagicMock
import json
import logging
from orchestrator.modules.loop_feedback_logger import (
    record_loop_feedback,
    invalidate_loop_reflection,
    log_feedback_to_agent_performance
)

class TestLoopFeedbackLogger(unittest.TestCase):
    """Test cases for the Loop Feedback Logger module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a fresh memory dictionary for each test
        self.memory = {
            "loop_trace": {
                1: {
                    "reflection": {
                        "content": "This was a successful loop",
                        "status": "active"
                    }
                }
            },
            "reflection": {
                1: {
                    "content": "This was a successful loop",
                    "status": "active"
                }
            }
        }
        
        # Sample feedback data
        self.valid_feedback = {
            "status": "rejected",
            "reason": "Output drifted from intent",
            "reflection_invalidated": True,
            "operator_notes": "This wasn't what I meant. Plan missed emotional tone."
        }
    
    def test_record_loop_feedback_valid(self):
        """Test recording valid feedback."""
        result = record_loop_feedback(
            self.memory, 
            "test-project", 
            1, 
            self.valid_feedback
        )
        
        # Check that feedback was recorded in memory
        self.assertIn("loop_feedback", self.memory)
        self.assertEqual(len(self.memory["loop_feedback"]), 1)
        
        # Check that feedback was recorded in loop trace
        self.assertIn("feedback", self.memory["loop_trace"][1])
        self.assertEqual(len(self.memory["loop_trace"][1]["feedback"]), 1)
        
        # Check that feedback entry has all required fields
        feedback_entry = self.memory["loop_feedback"][0]
        self.assertEqual(feedback_entry["loop_id"], 1)
        self.assertEqual(feedback_entry["status"], "rejected")
        self.assertEqual(feedback_entry["reason"], "Output drifted from intent")
        self.assertTrue(feedback_entry["reflection_invalidated"])
        self.assertEqual(feedback_entry["operator_notes"], "This wasn't what I meant. Plan missed emotional tone.")
        self.assertIn("timestamp", feedback_entry)
        
        # Check that CTO warning was added
        self.assertIn("cto_warnings", self.memory)
        self.assertEqual(len(self.memory["cto_warnings"]), 1)
        self.assertEqual(self.memory["cto_warnings"][0]["type"], "summary_rejection")
        self.assertEqual(self.memory["cto_warnings"][0]["loop_id"], 1)
    
    def test_record_loop_feedback_missing_fields(self):
        """Test recording feedback with missing required fields."""
        invalid_feedback = {
            "status": "rejected"
            # Missing "reason" field
        }
        
        with self.assertRaises(ValueError) as context:
            record_loop_feedback(self.memory, "test-project", 1, invalid_feedback)
        
        self.assertIn("Missing required field", str(context.exception))
    
    def test_record_loop_feedback_invalid_status(self):
        """Test recording feedback with invalid status."""
        invalid_feedback = {
            "status": "invalid_status",
            "reason": "Some reason"
        }
        
        with self.assertRaises(ValueError) as context:
            record_loop_feedback(self.memory, "test-project", 1, invalid_feedback)
        
        self.assertIn("Invalid status", str(context.exception))
    
    def test_record_loop_feedback_with_custom_timestamp(self):
        """Test recording feedback with a custom timestamp."""
        feedback_with_timestamp = self.valid_feedback.copy()
        custom_timestamp = "2025-04-24T00:41:00Z"
        feedback_with_timestamp["timestamp"] = custom_timestamp
        
        result = record_loop_feedback(
            self.memory, 
            "test-project", 
            1, 
            feedback_with_timestamp
        )
        
        self.assertEqual(result["timestamp"], custom_timestamp)
    
    def test_invalidate_loop_reflection(self):
        """Test invalidating a loop reflection."""
        result = invalidate_loop_reflection(self.memory, 1)
        
        # Check that reflection was invalidated
        self.assertTrue(result)
        self.assertEqual(self.memory["reflection"][1]["status"], "retracted")
        self.assertIn("retraction_timestamp", self.memory["reflection"][1])
        
        # Check that loop trace reflection was also invalidated
        self.assertEqual(self.memory["loop_trace"][1]["reflection"]["status"], "retracted")
        self.assertIn("retraction_timestamp", self.memory["loop_trace"][1]["reflection"])
    
    def test_invalidate_nonexistent_reflection(self):
        """Test invalidating a reflection that doesn't exist."""
        result = invalidate_loop_reflection(self.memory, 999)
        
        # Should return False for non-existent reflection
        self.assertFalse(result)
    
    def test_log_feedback_to_agent_performance_negative(self):
        """Test logging negative feedback to agent performance."""
        result = log_feedback_to_agent_performance(
            self.memory,
            "hal",
            1,
            -0.5  # Negative impact
        )
        
        # Check that agent performance was updated
        self.assertIn("agent_performance", self.memory)
        self.assertIn("hal", self.memory["agent_performance"])
        
        # Check that rejection count was incremented
        self.assertEqual(self.memory["agent_performance"]["hal"]["rejection_count"], 1)
        
        # Check that trust score was decreased
        self.assertLess(self.memory["agent_performance"]["hal"]["trust_score"], 0.5)
        
        # Check that feedback history was updated
        self.assertEqual(len(self.memory["agent_performance"]["hal"]["feedback_history"]), 1)
        self.assertEqual(self.memory["agent_performance"]["hal"]["feedback_history"][0]["loop_id"], 1)
        self.assertEqual(self.memory["agent_performance"]["hal"]["feedback_history"][0]["impact"], -0.5)
    
    def test_log_feedback_to_agent_performance_positive(self):
        """Test logging positive feedback to agent performance."""
        result = log_feedback_to_agent_performance(
            self.memory,
            "hal",
            1,
            0.5  # Positive impact
        )
        
        # Check that success count was incremented
        self.assertEqual(self.memory["agent_performance"]["hal"]["success_count"], 1)
        
        # Check that trust score was increased
        self.assertGreater(self.memory["agent_performance"]["hal"]["trust_score"], 0.5)
    
    def test_log_feedback_to_agent_performance_neutral(self):
        """Test logging neutral feedback to agent performance."""
        result = log_feedback_to_agent_performance(
            self.memory,
            "hal",
            1,
            0.0  # Neutral impact
        )
        
        # Check that revision count was incremented
        self.assertEqual(self.memory["agent_performance"]["hal"]["revision_count"], 1)
        
        # Check that trust score remained the same
        self.assertEqual(self.memory["agent_performance"]["hal"]["trust_score"], 0.5)
    
    def test_log_feedback_to_agent_performance_invalid_impact(self):
        """Test logging feedback with invalid impact value."""
        with self.assertRaises(ValueError) as context:
            log_feedback_to_agent_performance(
                self.memory,
                "hal",
                1,
                1.5  # Invalid impact (outside -1.0 to 1.0 range)
            )
        
        self.assertIn("Impact must be between -1.0 and 1.0", str(context.exception))
    
    def test_log_feedback_to_agent_performance_multiple_updates(self):
        """Test multiple feedback updates to the same agent."""
        # First update (negative)
        log_feedback_to_agent_performance(self.memory, "hal", 1, -0.3)
        first_trust = self.memory["agent_performance"]["hal"]["trust_score"]
        
        # Second update (positive)
        log_feedback_to_agent_performance(self.memory, "hal", 2, 0.2)
        second_trust = self.memory["agent_performance"]["hal"]["trust_score"]
        
        # Check that history has two entries
        self.assertEqual(len(self.memory["agent_performance"]["hal"]["feedback_history"]), 2)
        
        # Check that trust score was first decreased, then increased
        self.assertLess(first_trust, 0.5)
        self.assertGreater(second_trust, first_trust)
    
    def test_full_feedback_workflow(self):
        """Test the complete feedback workflow."""
        # Record feedback that invalidates reflection
        record_loop_feedback(
            self.memory, 
            "test-project", 
            1, 
            self.valid_feedback
        )
        
        # Check that reflection was invalidated automatically
        self.assertEqual(self.memory["reflection"][1]["status"], "retracted")
        
        # Log negative feedback to agent performance
        log_feedback_to_agent_performance(
            self.memory,
            "hal",
            1,
            -0.7
        )
        
        # Check that all memory structures were updated correctly
        self.assertIn("loop_feedback", self.memory)
        self.assertIn("cto_warnings", self.memory)
        self.assertIn("agent_performance", self.memory)
        self.assertEqual(self.memory["reflection"][1]["status"], "retracted")
        self.assertEqual(self.memory["loop_trace"][1]["reflection"]["status"], "retracted")
        self.assertGreater(self.memory["agent_performance"]["hal"]["rejection_count"], 0)
        self.assertLess(self.memory["agent_performance"]["hal"]["trust_score"], 0.5)

if __name__ == "__main__":
    unittest.main()
