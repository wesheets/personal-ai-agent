"""
Unit tests for the Historian Agent implementation.

This module tests the Historian Agent's ability to detect memory drift
by comparing loop summaries against system beliefs.
"""

import unittest
import json
from datetime import datetime
from unittest.mock import patch, mock_open

from agents.historian_agent import (
    generate_belief_alignment_score,
    detect_forgotten_beliefs,
    generate_historian_alert,
    analyze_loop_summary
)
from memory.belief_reference import (
    extract_belief_keywords,
    scan_text_for_belief,
    get_belief_references_over_time
)

class TestHistorianAgent(unittest.TestCase):
    """Test cases for the Historian Agent implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample beliefs for testing
        self.beliefs = [
            "The system should prioritize user safety above all else",
            "The system should be transparent about its capabilities and limitations",
            "The system should respect user privacy and data confidentiality",
            "The system should provide accurate and helpful information"
        ]
        
        # Sample loop summaries for testing
        self.loop_summaries = [
            {
                "loop_id": "loop-001",
                "summary": "The agent provided accurate information about climate change while respecting user privacy.",
                "timestamp": "2025-04-01T10:00:00Z"
            },
            {
                "loop_id": "loop-002",
                "summary": "The agent was transparent about its limitations when asked about quantum physics.",
                "timestamp": "2025-04-02T11:00:00Z"
            },
            {
                "loop_id": "loop-003",
                "summary": "The agent completed the task efficiently but did not explicitly consider safety implications.",
                "timestamp": "2025-04-03T12:00:00Z"
            }
        ]
        
        # Sample memory for testing
        self.memory = {
            "loops": self.loop_summaries,
            "historian_alerts": []
        }
    
    def test_belief_alignment_score_high(self):
        """Test belief alignment score calculation with high alignment."""
        loop_summary = "The agent was transparent about its limitations and provided accurate information while respecting user privacy."
        score = generate_belief_alignment_score(loop_summary, self.beliefs)
        
        # Should have high alignment (>0.7) as it references 3 of 4 beliefs
        self.assertGreater(score, 0.7)
    
    def test_belief_alignment_score_medium(self):
        """Test belief alignment score calculation with medium alignment."""
        loop_summary = "The agent provided accurate information but didn't mention limitations or privacy."
        score = generate_belief_alignment_score(loop_summary, self.beliefs)
        
        # Should have medium alignment (0.3-0.7) as it references 1 of 4 beliefs
        self.assertGreater(score, 0.3)
        self.assertLess(score, 0.7)
    
    def test_belief_alignment_score_low(self):
        """Test belief alignment score calculation with low alignment."""
        loop_summary = "The agent completed the task without any issues."
        score = generate_belief_alignment_score(loop_summary, self.beliefs)
        
        # Should have low alignment (<0.3) as it doesn't reference any beliefs
        self.assertLess(score, 0.3)
    
    def test_detect_forgotten_beliefs(self):
        """Test detection of forgotten beliefs across multiple loops."""
        forgotten = detect_forgotten_beliefs(self.loop_summaries, self.beliefs)
        
        # Should detect that the safety belief is forgotten (not referenced in any loop)
        self.assertIn("The system should prioritize user safety above all else", forgotten)
        
        # Should not include beliefs that are referenced
        self.assertNotIn("The system should provide accurate and helpful information", forgotten)
    
    def test_generate_historian_alert_with_missing_beliefs(self):
        """Test generation of historian alert with missing beliefs."""
        missing_beliefs = ["The system should prioritize user safety above all else"]
        alignment_score = 0.75
        
        updated_memory = generate_historian_alert("loop-004", missing_beliefs, alignment_score, self.memory)
        
        # Should add a historian alert to memory
        self.assertIn("historian_alerts", updated_memory)
        self.assertEqual(len(updated_memory["historian_alerts"]), 1)
        
        # Alert should have correct properties
        alert = updated_memory["historian_alerts"][0]
        self.assertEqual(alert["loop_id"], "loop-004")
        self.assertEqual(alert["alert_type"], "belief_drift_detected")
        self.assertEqual(alert["missing_beliefs"], missing_beliefs)
        self.assertEqual(alert["loop_belief_alignment_score"], alignment_score)
        self.assertIn("suggestion", alert)
        self.assertIn("timestamp", alert)
    
    def test_generate_historian_alert_with_low_alignment(self):
        """Test generation of historian alert with low alignment score."""
        missing_beliefs = ["The system should prioritize user safety above all else", 
                          "The system should be transparent about its capabilities and limitations"]
        alignment_score = 0.2  # Very low alignment
        
        updated_memory = generate_historian_alert("loop-004", missing_beliefs, alignment_score, self.memory)
        
        # Should add a CTO warning due to low alignment
        self.assertIn("cto_warnings", updated_memory)
        self.assertEqual(len(updated_memory["cto_warnings"]), 1)
        
        # Warning should have correct properties
        warning = updated_memory["cto_warnings"][0]
        self.assertEqual(warning["type"], "belief_drift")
        self.assertEqual(warning["loop_id"], "loop-004")
        self.assertIn("message", warning)
        self.assertIn("timestamp", warning)
    
    def test_analyze_loop_summary(self):
        """Test the main analyze_loop_summary function."""
        loop_summary = "The agent provided accurate information but didn't mention safety or privacy."
        
        updated_memory = analyze_loop_summary("loop-004", loop_summary, self.loop_summaries, self.beliefs, self.memory)
        
        # Should add a historian alert to memory
        self.assertIn("historian_alerts", updated_memory)
        self.assertGreaterEqual(len(updated_memory["historian_alerts"]), 1)
        
        # Get the latest alert
        latest_alert = updated_memory["historian_alerts"][-1]
        
        # Alert should have correct properties
        self.assertEqual(latest_alert["loop_id"], "loop-004")
        self.assertIn("missing_beliefs", latest_alert)
        self.assertIn("loop_belief_alignment_score", latest_alert)
    
    def test_extract_belief_keywords(self):
        """Test extraction of significant keywords from beliefs."""
        belief = "The system should prioritize user safety above all else"
        keywords = extract_belief_keywords(belief)
        
        # Should extract significant keywords
        self.assertIn("system", keywords)
        self.assertIn("prioritize", keywords)
        self.assertIn("safety", keywords)
        
        # Should not include stop words
        self.assertNotIn("the", keywords)
        self.assertNotIn("should", keywords)
        self.assertNotIn("all", keywords)
    
    def test_scan_text_for_belief(self):
        """Test scanning text for references to a belief."""
        belief = "The system should respect user privacy and data confidentiality"
        
        # Text with exact match
        text1 = "The agent ensured that the system should respect user privacy and data confidentiality."
        score1 = scan_text_for_belief(text1, belief)
        self.assertEqual(score1, 1.0)
        
        # Text with partial match
        text2 = "The agent respected user privacy when handling sensitive data."
        score2 = scan_text_for_belief(text2, belief)
        self.assertGreater(score2, 0.3)
        self.assertLess(score2, 1.0)
        
        # Text with no match
        text3 = "The agent completed the task efficiently."
        score3 = scan_text_for_belief(text3, belief)
        self.assertLess(score3, 0.3)
    
    def test_get_belief_references_over_time(self):
        """Test tracking belief references over time."""
        references = get_belief_references_over_time(self.loop_summaries, self.beliefs)
        
        # Should return a dictionary with all beliefs
        self.assertEqual(len(references), len(self.beliefs))
        
        # Each belief should have a list of boolean values
        for belief, referenced in references.items():
            self.assertEqual(len(referenced), len(self.loop_summaries))
        
        # Safety belief should not be referenced in any loop
        safety_belief = "The system should prioritize user safety above all else"
        self.assertFalse(any(references[safety_belief]))
        
        # Accuracy belief should be referenced in at least one loop
        accuracy_belief = "The system should provide accurate and helpful information"
        self.assertTrue(any(references[accuracy_belief]))

if __name__ == '__main__':
    unittest.main()
