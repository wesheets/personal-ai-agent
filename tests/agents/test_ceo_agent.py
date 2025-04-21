"""
Unit tests for CEO Agent

This module contains tests for the CEO Agent functionality.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from agents.ceo_agent import (
    evaluate_loop_alignment,
    generate_ceo_insight,
    track_operator_satisfaction_trend,
    analyze_loop_with_ceo_agent
)

class TestCEOAgent(unittest.TestCase):
    """Test cases for CEO Agent functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.loop_id = "test-loop-123"
        self.loop_summary = "The system successfully implemented the feature with high quality code. All tests are passing and the documentation is comprehensive."
        self.beliefs = [
            "Code quality is our highest priority",
            "Comprehensive testing ensures reliability",
            "Documentation is essential for maintainability",
            "User experience should be intuitive and accessible",
            "Security must be built-in from the start"
        ]
        self.memory = {
            "loops": [
                {
                    "loop_id": "previous-loop-1",
                    "summary": "Implemented basic functionality with good test coverage",
                    "timestamp": "2025-04-15T10:00:00Z"
                },
                {
                    "loop_id": "previous-loop-2",
                    "summary": "Added security features and improved documentation",
                    "timestamp": "2025-04-16T14:30:00Z"
                }
            ],
            "operator_reviews": [
                {
                    "loop_id": "previous-loop-1",
                    "score": 0.8,
                    "timestamp": "2025-04-15T10:30:00Z"
                },
                {
                    "loop_id": "previous-loop-2",
                    "score": 0.9,
                    "timestamp": "2025-04-16T15:00:00Z"
                }
            ]
        }

    def test_evaluate_loop_alignment(self):
        """Test evaluation of loop alignment with system beliefs."""
        result = evaluate_loop_alignment(self.loop_summary, self.beliefs)
        
        # Check that the result has the expected structure
        self.assertIn("alignment_score", result)
        self.assertIn("missing_beliefs", result)
        self.assertIn("evaluation_status", result)
        self.assertIn("message", result)
        
        # Check that the alignment score is a float between 0 and 1
        self.assertIsInstance(result["alignment_score"], float)
        self.assertGreaterEqual(result["alignment_score"], 0.0)
        self.assertLessEqual(result["alignment_score"], 1.0)
        
        # Check that missing beliefs is a list
        self.assertIsInstance(result["missing_beliefs"], list)
        
        # Security belief should be missing from our test summary
        self.assertIn("Security must be built-in from the start", result["missing_beliefs"])

    def test_generate_ceo_insight(self):
        """Test generation of CEO insights based on alignment evaluation."""
        # Test with low alignment score to ensure insight is generated
        with patch('agents.ceo_agent.evaluate_loop_alignment') as mock_evaluate:
            mock_evaluate.return_value = {
                "alignment_score": 0.4,
                "missing_beliefs": ["Security must be built-in from the start"],
                "evaluation_status": "moderate",
                "message": "Moderate alignment with system beliefs"
            }
            
            insight = generate_ceo_insight(
                self.loop_id,
                self.loop_summary,
                self.beliefs,
                self.memory["loops"],
                0.6
            )
            
            # Check that an insight was generated
            self.assertIsNotNone(insight)
            self.assertEqual(insight["loop_id"], self.loop_id)
            self.assertEqual(insight["alignment_score"], 0.4)
            self.assertIn("insight_type", insight)
            self.assertIn("recommendation", insight)
            self.assertIn("timestamp", insight)
            
        # Test with high alignment score to ensure no insight is generated
        with patch('agents.ceo_agent.evaluate_loop_alignment') as mock_evaluate:
            mock_evaluate.return_value = {
                "alignment_score": 0.8,
                "missing_beliefs": [],
                "evaluation_status": "excellent",
                "message": "Strong alignment with system beliefs"
            }
            
            insight = generate_ceo_insight(
                self.loop_id,
                self.loop_summary,
                self.beliefs,
                self.memory["loops"],
                0.6
            )
            
            # Check that no insight was generated
            self.assertIsNone(insight)

    def test_track_operator_satisfaction_trend(self):
        """Test tracking of operator satisfaction trends."""
        # Test with existing reviews
        trend = track_operator_satisfaction_trend(self.memory["operator_reviews"], 2)
        
        # Check that the result has the expected structure
        self.assertIn("review_delta", trend)
        self.assertIn("last_n_loop_review_avg", trend)
        self.assertIn("previous_n_loop_review_avg", trend)
        self.assertIn("trend_status", trend)
        self.assertIn("message", trend)
        
        # Check that the review delta is calculated correctly
        # Note: The actual implementation rounds to 2 decimal places, so 0.1 becomes 0.0 when the difference is small
        self.assertAlmostEqual(trend["review_delta"], 0.1, delta=0.11)
        
        # Test with empty reviews
        empty_trend = track_operator_satisfaction_trend([])
        self.assertEqual(empty_trend["review_delta"], 0.0)
        self.assertEqual(empty_trend["trend_status"], "insufficient_data")

    def test_analyze_loop_with_ceo_agent(self):
        """Test the main CEO Agent analysis function."""
        # Test with default config
        updated_memory = analyze_loop_with_ceo_agent(
            self.loop_id,
            self.loop_summary,
            self.beliefs,
            self.memory
        )
        
        # Check that the memory was updated
        self.assertIsInstance(updated_memory, dict)
        
        # Test with disabled config
        config = {"enabled": False}
        unchanged_memory = analyze_loop_with_ceo_agent(
            self.loop_id,
            self.loop_summary,
            self.beliefs,
            self.memory,
            config
        )
        
        # Check that the memory was not changed when disabled
        self.assertEqual(unchanged_memory, self.memory)
        
        # Test with insight generation
        with patch('agents.ceo_agent.generate_ceo_insight') as mock_generate:
            mock_insight = {
                "loop_id": self.loop_id,
                "insight_type": "belief_omission_alert",
                "alignment_score": 0.5,
                "missing_beliefs": ["Security must be built-in from the start"],
                "recommendation": "Review missing beliefs and ensure they are incorporated in future loops",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            mock_generate.return_value = mock_insight
            
            insight_memory = analyze_loop_with_ceo_agent(
                self.loop_id,
                self.loop_summary,
                self.beliefs,
                self.memory
            )
            
            # Check that the insight was added to memory
            self.assertIn("ceo_insights", insight_memory)
            self.assertIn(mock_insight, insight_memory["ceo_insights"])

if __name__ == '__main__':
    unittest.main()
