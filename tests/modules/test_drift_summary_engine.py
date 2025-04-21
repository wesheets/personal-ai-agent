"""
Unit tests for Drift Summary Engine

This module contains tests for the Drift Summary Engine functionality.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from orchestrator.modules.drift_summary_engine import (
    generate_drift_summary,
    store_drift_summary,
    handle_critical_drift,
    process_loop_with_drift_engine,
    _extract_ceo_alignment_score,
    _extract_historian_alignment_score,
    _extract_cto_health_metrics,
    _extract_pessimist_metrics,
    _calculate_drift_severity,
    _generate_recommendation
)

class TestDriftSummaryEngine(unittest.TestCase):
    """Test cases for Drift Summary Engine functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.loop_id = "loop_0096"
        self.memory = {
            "ceo_insights": [
                {
                    "loop_id": self.loop_id,
                    "insight_type": "alignment_improvement_needed",
                    "alignment_score": 0.52,
                    "missing_beliefs": ["belief1", "belief2"],
                    "recommendation": "Conduct belief reinforcement training",
                    "timestamp": "2025-04-26T05:10:00Z"
                }
            ],
            "historian_alerts": [
                {
                    "loop_id": self.loop_id,
                    "alert_type": "belief_drift_detected",
                    "missing_beliefs": ["belief3"],
                    "loop_belief_alignment_score": 0.45,
                    "suggestion": "Consider reviewing system beliefs for potential updates",
                    "timestamp": "2025-04-26T05:11:00Z"
                }
            ],
            "cto_reports": [
                {
                    "loop_id": self.loop_id,
                    "health_score": 0.67,
                    "plan_summary_alignment_score": 0.72,
                    "trust_decay": 0.13,
                    "recommendation": "Address trust decay issues",
                    "timestamp": "2025-04-26T05:12:00Z"
                }
            ],
            "pessimist_alerts": [
                {
                    "loop_id": self.loop_id,
                    "bias_tags": ["optimism_bias"],
                    "timestamp": "2025-04-26T05:13:00Z",
                    "alert_type": "excessive_confidence",
                    "suggestion": "Adjust tone to reflect actual accomplishments",
                    "details": {
                        "detected_phrases": {
                            "optimistic": ["successfully", "perfectly"],
                            "vague": []
                        },
                        "tone_score": 0.75
                    },
                    "severity": "medium",
                    "confidence": 0.85
                }
            ]
        }

    def test_extract_ceo_alignment_score(self):
        """Test extraction of CEO alignment score."""
        # Test with existing CEO insight
        alignment_score = _extract_ceo_alignment_score(self.loop_id, self.memory)
        self.assertEqual(alignment_score, 0.52)
        
        # Test with non-existent loop ID
        alignment_score = _extract_ceo_alignment_score("non_existent_loop", self.memory)
        self.assertIsNone(alignment_score)
        
        # Test with empty memory
        alignment_score = _extract_ceo_alignment_score(self.loop_id, {})
        self.assertIsNone(alignment_score)

    def test_extract_historian_alignment_score(self):
        """Test extraction of Historian alignment score."""
        # Test with existing Historian alert
        alignment_score = _extract_historian_alignment_score(self.loop_id, self.memory)
        self.assertEqual(alignment_score, 0.45)
        
        # Test with non-existent loop ID
        alignment_score = _extract_historian_alignment_score("non_existent_loop", self.memory)
        self.assertIsNone(alignment_score)
        
        # Test with empty memory
        alignment_score = _extract_historian_alignment_score(self.loop_id, {})
        self.assertIsNone(alignment_score)

    def test_extract_cto_health_metrics(self):
        """Test extraction of CTO health metrics."""
        # Test with existing CTO report
        health_score, trust_decay = _extract_cto_health_metrics(self.loop_id, self.memory)
        self.assertEqual(health_score, 0.67)
        self.assertEqual(trust_decay, 0.13)
        
        # Test with non-existent loop ID
        health_score, trust_decay = _extract_cto_health_metrics("non_existent_loop", self.memory)
        self.assertIsNone(health_score)
        self.assertIsNone(trust_decay)
        
        # Test with empty memory
        health_score, trust_decay = _extract_cto_health_metrics(self.loop_id, {})
        self.assertIsNone(health_score)
        self.assertIsNone(trust_decay)
        
        # Test with health score in loop data
        memory_with_loop = {
            "loops": [
                {
                    "loop_id": self.loop_id,
                    "loop_health_score": 0.75
                }
            ]
        }
        health_score, trust_decay = _extract_cto_health_metrics(self.loop_id, memory_with_loop)
        self.assertEqual(health_score, 0.75)
        self.assertIsNone(trust_decay)

    def test_extract_pessimist_metrics(self):
        """Test extraction of Pessimist metrics."""
        # Test with existing Pessimist alert
        bias_tags, tone_confidence = _extract_pessimist_metrics(self.loop_id, self.memory)
        self.assertEqual(bias_tags, ["optimism_bias"])
        self.assertEqual(tone_confidence, 0.75)
        
        # Test with non-existent loop ID
        bias_tags, tone_confidence = _extract_pessimist_metrics("non_existent_loop", self.memory)
        self.assertEqual(bias_tags, [])
        self.assertIsNone(tone_confidence)
        
        # Test with empty memory
        bias_tags, tone_confidence = _extract_pessimist_metrics(self.loop_id, {})
        self.assertEqual(bias_tags, [])
        self.assertIsNone(tone_confidence)

    def test_calculate_drift_severity(self):
        """Test calculation of drift severity."""
        # Test critical severity
        severity = _calculate_drift_severity(
            alignment_score=0.3,
            belief_alignment_score=0.35,
            health_score=0.45,
            trust_decay=0.25,
            bias_tags=["optimism_bias", "vague_summary"],
            thresholds={
                "critical": {
                    "alignment_score": 0.4,
                    "belief_alignment_score": 0.4,
                    "health_score": 0.5,
                    "trust_decay": 0.2
                },
                "moderate": {
                    "alignment_score": 0.6,
                    "belief_alignment_score": 0.6,
                    "health_score": 0.7,
                    "trust_decay": 0.1
                }
            }
        )
        self.assertEqual(severity, "critical")
        
        # Test moderate severity
        severity = _calculate_drift_severity(
            alignment_score=0.55,
            belief_alignment_score=0.58,
            health_score=0.65,
            trust_decay=0.12,
            bias_tags=["optimism_bias"],
            thresholds={
                "critical": {
                    "alignment_score": 0.4,
                    "belief_alignment_score": 0.4,
                    "health_score": 0.5,
                    "trust_decay": 0.2
                },
                "moderate": {
                    "alignment_score": 0.6,
                    "belief_alignment_score": 0.6,
                    "health_score": 0.7,
                    "trust_decay": 0.1
                }
            }
        )
        self.assertEqual(severity, "moderate")
        
        # Test low severity
        severity = _calculate_drift_severity(
            alignment_score=0.75,
            belief_alignment_score=0.78,
            health_score=0.85,
            trust_decay=0.05,
            bias_tags=[],
            thresholds={
                "critical": {
                    "alignment_score": 0.4,
                    "belief_alignment_score": 0.4,
                    "health_score": 0.5,
                    "trust_decay": 0.2
                },
                "moderate": {
                    "alignment_score": 0.6,
                    "belief_alignment_score": 0.6,
                    "health_score": 0.7,
                    "trust_decay": 0.1
                }
            }
        )
        self.assertEqual(severity, "low")

    def test_generate_recommendation(self):
        """Test generation of recommendations."""
        # Test critical severity recommendation
        recommendation = _generate_recommendation(
            severity="critical",
            alignment_score=0.3,
            belief_alignment_score=0.35,
            health_score=0.45,
            trust_decay=0.25,
            bias_tags=["optimism_bias", "vague_summary"]
        )
        self.assertIn("critical issues", recommendation)
        
        # Test moderate severity recommendation
        recommendation = _generate_recommendation(
            severity="moderate",
            alignment_score=0.55,
            belief_alignment_score=0.58,
            health_score=0.65,
            trust_decay=0.12,
            bias_tags=["optimism_bias"]
        )
        self.assertIn("Adjust tone", recommendation)
        
        # Test low severity recommendation
        recommendation = _generate_recommendation(
            severity="low",
            alignment_score=0.75,
            belief_alignment_score=0.78,
            health_score=0.85,
            trust_decay=0.05,
            bias_tags=[]
        )
        self.assertIn("Continue normal operation", recommendation)

    def test_generate_drift_summary(self):
        """Test generation of drift summary."""
        # Test with complete memory
        drift_summary = generate_drift_summary(self.loop_id, self.memory)
        
        # Check that the summary has the expected structure
        self.assertEqual(drift_summary["loop_id"], self.loop_id)
        self.assertIn("drift_severity", drift_summary)
        self.assertIn("alignment_score", drift_summary)
        self.assertIn("belief_alignment_score", drift_summary)
        self.assertIn("health_score", drift_summary)
        self.assertIn("trust_decay", drift_summary)
        self.assertIn("bias_tags", drift_summary)
        self.assertIn("recommendation", drift_summary)
        self.assertIn("timestamp", drift_summary)
        
        # Check that the values are correct
        self.assertEqual(drift_summary["alignment_score"], 0.52)
        self.assertEqual(drift_summary["belief_alignment_score"], 0.45)
        self.assertEqual(drift_summary["health_score"], 0.67)
        self.assertEqual(drift_summary["trust_decay"], 0.13)
        self.assertEqual(drift_summary["bias_tags"], ["optimism_bias"])
        
        # Test with empty memory
        drift_summary = generate_drift_summary(self.loop_id, {})
        self.assertEqual(drift_summary["loop_id"], self.loop_id)
        self.assertEqual(drift_summary["drift_severity"], "low")
        self.assertIn("recommendation", drift_summary)
        self.assertIn("timestamp", drift_summary)

    def test_store_drift_summary(self):
        """Test storing drift summary in memory."""
        # Create a drift summary
        drift_summary = {
            "loop_id": self.loop_id,
            "drift_severity": "moderate",
            "alignment_score": 0.52,
            "belief_alignment_score": 0.45,
            "health_score": 0.67,
            "trust_decay": 0.13,
            "bias_tags": ["optimism_bias"],
            "recommendation": "Re-engage Thought Partner and rerun Sage",
            "timestamp": "2025-04-26T05:12:00Z"
        }
        
        # Test with empty memory
        updated_memory = store_drift_summary({}, drift_summary)
        self.assertIn("drift_summaries", updated_memory)
        self.assertEqual(len(updated_memory["drift_summaries"]), 1)
        self.assertEqual(updated_memory["drift_summaries"][0], drift_summary)
        
        # Test with existing drift summaries
        memory_with_summaries = {
            "drift_summaries": [
                {
                    "loop_id": "loop_0095",
                    "drift_severity": "low",
                    "timestamp": "2025-04-26T04:12:00Z"
                }
            ]
        }
        updated_memory = store_drift_summary(memory_with_summaries, drift_summary)
        self.assertEqual(len(updated_memory["drift_summaries"]), 2)
        self.assertEqual(updated_memory["drift_summaries"][1], drift_summary)

    def test_handle_critical_drift(self):
        """Test handling of critical drift."""
        # Create a critical drift summary
        critical_drift = {
            "loop_id": self.loop_id,
            "drift_severity": "critical",
            "alignment_score": 0.32,
            "belief_alignment_score": 0.35,
            "health_score": 0.45,
            "trust_decay": 0.25,
            "bias_tags": ["optimism_bias", "vague_summary"],
            "recommendation": "System reset recommended due to critical issues",
            "timestamp": "2025-04-26T05:12:00Z"
        }
        
        # Test with empty memory
        updated_memory = handle_critical_drift({}, critical_drift)
        self.assertIn("cto_warnings", updated_memory)
        self.assertEqual(len(updated_memory["cto_warnings"]), 1)
        self.assertEqual(updated_memory["cto_warnings"][0]["type"], "critical_drift")
        self.assertEqual(updated_memory["cto_warnings"][0]["loop_id"], self.loop_id)
        
        # Test with existing warnings
        memory_with_warnings = {
            "cto_warnings": [
                {
                    "type": "belief_drift",
                    "loop_id": "loop_0095",
                    "timestamp": "2025-04-26T04:12:00Z"
                }
            ]
        }
        updated_memory = handle_critical_drift(memory_with_warnings, critical_drift)
        self.assertEqual(len(updated_memory["cto_warnings"]), 2)
        self.assertEqual(updated_memory["cto_warnings"][1]["type"], "critical_drift")
        
        # Test with non-critical drift
        moderate_drift = {
            "loop_id": self.loop_id,
            "drift_severity": "moderate",
            "timestamp": "2025-04-26T05:12:00Z"
        }
        updated_memory = handle_critical_drift({}, moderate_drift)
        self.assertNotIn("cto_warnings", updated_memory)

    def test_process_loop_with_drift_engine(self):
        """Test the main drift engine processing function."""
        # Test with default config
        updated_memory = process_loop_with_drift_engine(self.loop_id, self.memory)
        
        # Check that drift summaries were added
        self.assertIn("drift_summaries", updated_memory)
        self.assertEqual(updated_memory["drift_summaries"][0]["loop_id"], self.loop_id)
        
        # Test with disabled config
        config = {"enabled": False}
        unchanged_memory = process_loop_with_drift_engine(self.loop_id, self.memory, config)
        self.assertEqual(unchanged_memory, self.memory)
        
        # Test with critical drift
        critical_memory = {
            "ceo_insights": [
                {
                    "loop_id": self.loop_id,
                    "alignment_score": 0.32
                }
            ],
            "historian_alerts": [
                {
                    "loop_id": self.loop_id,
                    "loop_belief_alignment_score": 0.35
                }
            ],
            "cto_reports": [
                {
                    "loop_id": self.loop_id,
                    "health_score": 0.45,
                    "trust_decay": 0.25
                }
            ],
            "pessimist_alerts": [
                {
                    "loop_id": self.loop_id,
                    "bias_tags": ["optimism_bias", "vague_summary"]
                }
            ]
        }
        
        updated_memory = process_loop_with_drift_engine(self.loop_id, critical_memory)
        
        # Check that drift summaries were added
        self.assertIn("drift_summaries", updated_memory)
        
        # Check that CTO warnings were added for critical drift
        self.assertIn("cto_warnings", updated_memory)
        self.assertEqual(updated_memory["cto_warnings"][0]["type"], "critical_drift")

if __name__ == '__main__':
    unittest.main()
