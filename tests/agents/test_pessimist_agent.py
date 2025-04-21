"""
Unit tests for the Pessimist Agent.

This module tests the functionality of the Pessimist Agent, including:
- Tone evaluation
- Bias detection
- Alert generation
- Memory injection
"""

import unittest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any

from agents.pessimist_agent import (
    evaluate_summary_tone,
    detect_optimism_bias,
    detect_vague_summary,
    detect_confidence_mismatch,
    generate_pessimist_alert,
    inject_memory_alert,
    process_loop_summary
)
from memory.tags import get_bias_tag_list, get_bias_tag_info


class TestPessimistAgent(unittest.TestCase):
    """Test cases for the Pessimist Agent."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory = {
            "loop_trace": {},
            "loop_summaries": {}
        }
        self.loop_id = "123"
        
        # Sample summaries for testing
        self.optimistic_summary = """
            Loop 123 Summary: ✅
            • Plan: "Create a user authentication system"
            • Agents: hal (validation), nova (UI), ash (backend)
            • Files: auth.js, UserLogin.jsx, authService.js
            • Successfully implemented a flawless authentication system with perfect security
            • Easily integrated with the existing backend without any issues
            • Operator accepted the result.
        """
        
        self.vague_summary = """
            Loop 123 Summary: ✅
            • Plan: "Create a user authentication system"
            • Agents: hal (validation), nova (UI), ash (backend)
            • Files: auth.js, UserLogin.jsx, authService.js
            • Made progress on the authentication implementation
            • Worked on integrating with the backend
            • Continued development of the UI components
            • Operator accepted the result.
        """
        
        self.balanced_summary = """
            Loop 123 Summary: ✅
            • Plan: "Create a user authentication system"
            • Agents: hal (validation), nova (UI), ash (backend)
            • Files: auth.js, UserLogin.jsx, authService.js
            • Implemented JWT-based authentication with password hashing
            • Created login and registration forms with validation
            • Fixed CORS issues during API integration
            • Operator accepted the result.
        """
        
        # Sample feedback for testing
        self.positive_feedback = [
            {"text": "Good work on the authentication system.", "rating": 4}
        ]
        
        self.negative_feedback = [
            {"text": "The authentication system has security issues.", "rating": 2}
        ]
        
        self.mixed_feedback = [
            {"text": "Good UI implementation but the backend has issues.", "rating": 3}
        ]

    def test_evaluate_summary_tone_with_optimistic_summary(self):
        """Test evaluate_summary_tone with an optimistic summary."""
        result = evaluate_summary_tone(self.optimistic_summary, [])
        
        self.assertIsInstance(result, dict)
        self.assertIn("tone_score", result)
        self.assertIn("optimism_score", result)
        self.assertIn("vagueness_score", result)
        self.assertIn("detected_phrases", result)
        
        # Optimistic summary should have high tone and optimism scores
        self.assertGreater(result["tone_score"], 0.6)
        self.assertGreater(result["optimism_score"], 0.6)
        
        # Should detect optimistic phrases
        self.assertGreater(len(result["detected_phrases"]["optimistic"]), 0)
        self.assertIn("successfully", result["detected_phrases"]["optimistic"])
        self.assertIn("flawless", result["detected_phrases"]["optimistic"])

    def test_evaluate_summary_tone_with_vague_summary(self):
        """Test evaluate_summary_tone with a vague summary."""
        result = evaluate_summary_tone(self.vague_summary, [])
        
        self.assertIsInstance(result, dict)
        
        # Vague summary should have medium tone score and high vagueness score
        self.assertLess(result["optimism_score"], 0.6)
        self.assertGreater(result["vagueness_score"], 0.3)
        
        # Should detect vague phrases
        self.assertGreater(len(result["detected_phrases"]["vague"]), 0)
        self.assertIn("made progress", result["detected_phrases"]["vague"])
        self.assertIn("worked on", result["detected_phrases"]["vague"])

    def test_evaluate_summary_tone_with_balanced_summary(self):
        """Test evaluate_summary_tone with a balanced summary."""
        result = evaluate_summary_tone(self.balanced_summary, [])
        
        self.assertIsInstance(result, dict)
        
        # Balanced summary should have moderate tone score
        self.assertLess(result["tone_score"], 0.6)
        self.assertLess(result["optimism_score"], 0.6)
        self.assertLess(result["vagueness_score"], 0.3)
        
        # Should not detect many optimistic or vague phrases
        self.assertLessEqual(len(result["detected_phrases"]["optimistic"]), 1)
        self.assertLessEqual(len(result["detected_phrases"]["vague"]), 1)

    def test_evaluate_summary_tone_with_feedback(self):
        """Test evaluate_summary_tone with feedback."""
        # Optimistic summary with negative feedback should increase optimism score
        result = evaluate_summary_tone(self.optimistic_summary, self.negative_feedback)
        
        self.assertIsInstance(result, dict)
        self.assertGreater(result["optimism_score"], 0.6)
        
        # Vague summary with positive feedback should not change much
        result_vague = evaluate_summary_tone(self.vague_summary, self.positive_feedback)
        self.assertGreater(result_vague["vagueness_score"], 0.3)

    def test_detect_optimism_bias(self):
        """Test detect_optimism_bias function."""
        # Create tone evaluations with different scores
        high_optimism = {
            "tone_score": 0.8,
            "optimism_score": 0.7,
            "detected_phrases": {
                "optimistic": ["successfully", "perfectly"],
                "vague": []
            }
        }
        
        medium_optimism = {
            "tone_score": 0.6,
            "optimism_score": 0.5,
            "detected_phrases": {
                "optimistic": ["successfully"],
                "vague": []
            }
        }
        
        low_optimism = {
            "tone_score": 0.4,
            "optimism_score": 0.3,
            "detected_phrases": {
                "optimistic": [],
                "vague": []
            }
        }
        
        # Test detection
        self.assertTrue(detect_optimism_bias(high_optimism))
        self.assertFalse(detect_optimism_bias(low_optimism))
        
        # Edge case: medium tone score but multiple optimistic phrases
        self.assertTrue(detect_optimism_bias(medium_optimism))

    def test_detect_vague_summary(self):
        """Test detect_vague_summary function."""
        # Create tone evaluations with different vagueness scores
        high_vagueness = {
            "tone_score": 0.6,
            "vagueness_score": 0.5,
            "detected_phrases": {
                "optimistic": [],
                "vague": ["made progress", "worked on", "continued"]
            }
        }
        
        medium_vagueness = {
            "tone_score": 0.5,
            "vagueness_score": 0.3,
            "detected_phrases": {
                "optimistic": [],
                "vague": ["made progress", "worked on"]
            }
        }
        
        low_vagueness = {
            "tone_score": 0.4,
            "vagueness_score": 0.1,
            "detected_phrases": {
                "optimistic": [],
                "vague": []
            }
        }
        
        # Test detection
        self.assertTrue(detect_vague_summary(high_vagueness))
        self.assertTrue(detect_vague_summary(medium_vagueness))
        self.assertFalse(detect_vague_summary(low_vagueness))

    def test_detect_confidence_mismatch(self):
        """Test detect_confidence_mismatch function."""
        # Test with low plan confidence but optimistic summary
        self.assertTrue(detect_confidence_mismatch(
            "Successfully implemented all features perfectly.",
            0.3  # Low plan confidence
        ))
        
        # Test with high plan confidence and optimistic summary (no mismatch)
        self.assertFalse(detect_confidence_mismatch(
            "Successfully implemented all features.",
            0.8  # High plan confidence
        ))
        
        # Test with low plan confidence but balanced summary (no mismatch)
        self.assertFalse(detect_confidence_mismatch(
            "Implemented the required features with some challenges.",
            0.4  # Low plan confidence
        ))
        
        # Test with None plan confidence (should not detect mismatch)
        self.assertFalse(detect_confidence_mismatch(
            "Successfully implemented all features.",
            None
        ))

    def test_generate_pessimist_alert_with_optimistic_summary(self):
        """Test generate_pessimist_alert with an optimistic summary."""
        alert = generate_pessimist_alert(self.loop_id, self.optimistic_summary, [], 0.7)
        
        self.assertIsInstance(alert, dict)
        self.assertEqual(alert["loop_id"], self.loop_id)
        self.assertIn("bias_tags", alert)
        self.assertIn("alert_type", alert)
        self.assertIn("suggestion", alert)
        self.assertIn("details", alert)
        
        # Should detect optimism bias
        self.assertIn("optimism_bias", alert["bias_tags"])
        
        # Should have appropriate alert type
        self.assertEqual(alert["alert_type"], "excessive_confidence")
        
        # Should include detected phrases in details
        self.assertIn("detected_phrases", alert["details"])
        self.assertGreater(len(alert["details"]["detected_phrases"]["optimistic"]), 0)

    def test_generate_pessimist_alert_with_vague_summary(self):
        """Test generate_pessimist_alert with a vague summary."""
        alert = generate_pessimist_alert(self.loop_id, self.vague_summary, [], 0.7)
        
        self.assertIsInstance(alert, dict)
        self.assertEqual(alert["loop_id"], self.loop_id)
        
        # Should detect vague summary
        self.assertIn("vague_summary", alert["bias_tags"])
        
        # Should have appropriate alert type
        self.assertEqual(alert["alert_type"], "vague_accomplishment")
        
        # Should include detected phrases in details
        self.assertIn("detected_phrases", alert["details"])
        self.assertGreater(len(alert["details"]["detected_phrases"]["vague"]), 0)

    def test_generate_pessimist_alert_with_balanced_summary(self):
        """Test generate_pessimist_alert with a balanced summary."""
        alert = generate_pessimist_alert(self.loop_id, self.balanced_summary, [], 0.7)
        
        # Should not generate an alert for balanced summary
        self.assertIsNone(alert)

    def test_generate_pessimist_alert_with_confidence_mismatch(self):
        """Test generate_pessimist_alert with confidence mismatch."""
        alert = generate_pessimist_alert(self.loop_id, self.optimistic_summary, [], 0.3)
        
        self.assertIsInstance(alert, dict)
        
        # Should detect confidence mismatch
        self.assertIn("overconfidence", alert["bias_tags"])
        
        # Should have appropriate alert type
        self.assertEqual(alert["alert_type"], "excessive_confidence")

    def test_inject_memory_alert(self):
        """Test inject_memory_alert function."""
        # Create a test alert
        alert = {
            "loop_id": self.loop_id,
            "alert_type": "excessive_confidence",
            "bias_tags": ["optimism_bias", "overconfidence"],
            "suggestion": "Adjust tone to reflect actual accomplishments",
            "details": {
                "detected_phrases": {
                    "optimistic": ["successfully", "perfectly"],
                    "vague": []
                },
                "tone_score": 0.8
            },
            "severity": "medium",
            "confidence": 0.9,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Set up memory with loop summary
        self.memory["loop_summaries"][self.loop_id] = {
            "summary": self.optimistic_summary,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {}
        }
        
        # Inject alert into memory
        updated_memory = inject_memory_alert(self.memory, alert)
        
        # Check that pessimist_alerts section was created
        self.assertIn("pessimist_alerts", updated_memory)
        self.assertEqual(len(updated_memory["pessimist_alerts"]), 1)
        self.assertEqual(updated_memory["pessimist_alerts"][0], alert)
        
        # Check that bias_tags were added to loop summary metadata
        self.assertIn("bias_tags", updated_memory["loop_summaries"][self.loop_id]["metadata"])
        self.assertEqual(
            set(updated_memory["loop_summaries"][self.loop_id]["metadata"]["bias_tags"]),
            set(["optimism_bias", "overconfidence"])
        )

    def test_process_loop_summary(self):
        """Test process_loop_summary function."""
        # Set up memory with loop summary
        self.memory["loop_summaries"][self.loop_id] = {
            "summary": self.optimistic_summary,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {}
        }
        
        # Process the loop summary
        updated_memory = process_loop_summary(
            self.loop_id,
            self.optimistic_summary,
            self.negative_feedback,
            self.memory,
            0.7
        )
        
        # Check that pessimist_alerts section was created
        self.assertIn("pessimist_alerts", updated_memory)
        self.assertGreater(len(updated_memory["pessimist_alerts"]), 0)
        
        # Check that bias_tags were added to loop summary metadata
        self.assertIn("bias_tags", updated_memory["loop_summaries"][self.loop_id]["metadata"])
        self.assertGreater(len(updated_memory["loop_summaries"][self.loop_id]["metadata"]["bias_tags"]), 0)
        
        # Process a balanced summary (should not add alerts)
        balanced_memory = self.memory.copy()
        balanced_memory["loop_summaries"][self.loop_id]["summary"] = self.balanced_summary
        
        updated_balanced_memory = process_loop_summary(
            self.loop_id,
            self.balanced_summary,
            self.positive_feedback,
            balanced_memory,
            0.7
        )
        
        # Check that no alerts were added
        self.assertNotIn("pessimist_alerts", updated_balanced_memory)

    def test_memory_tags_integration(self):
        """Test integration with memory tags."""
        # Get all bias tags
        bias_tags = get_bias_tag_list()
        
        # Check that required tags exist
        required_tags = ["optimism_bias", "vague_summary", "overconfidence"]
        for tag in required_tags:
            self.assertIn(tag, bias_tags)
        
        # Check tag info
        optimism_info = get_bias_tag_info("optimism_bias")
        self.assertIn("description", optimism_info)
        self.assertIn("indicators", optimism_info)
        self.assertIn("severity", optimism_info)
        
        # Check that indicators match what's used in the agent
        self.assertIn("successfully", optimism_info["indicators"])


if __name__ == "__main__":
    unittest.main()
