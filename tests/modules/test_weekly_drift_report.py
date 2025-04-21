"""
Unit tests for Weekly Drift Report Generator

This module contains tests for the Weekly Drift Report Generator functionality.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from orchestrator.modules.weekly_drift_report import (
    generate_weekly_drift_report,
    store_weekly_drift_report,
    handle_critical_drift_pattern,
    process_loop_with_weekly_drift_report,
    should_generate_weekly_report,
    _extract_drift_summaries,
    _extract_ceo_insights,
    _extract_cto_reports,
    _extract_historian_alerts,
    _calculate_drift_summary_stats,
    _calculate_belief_engagement,
    _calculate_trust_trend,
    _calculate_mode_usage,
    _generate_recommendation
)

class TestWeeklyDriftReportGenerator(unittest.TestCase):
    """Test cases for Weekly Drift Report Generator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.loop_range = ["loop_0096", "loop_0097", "loop_0098", "loop_0099", "loop_0100", "loop_0101", "loop_0102"]
        self.memory = {
            "drift_summaries": [
                {
                    "loop_id": "loop_0096",
                    "drift_severity": "low",
                    "alignment_score": 0.75,
                    "belief_alignment_score": 0.78,
                    "health_score": 0.82,
                    "bias_tags": [],
                    "timestamp": "2025-04-26T05:10:00Z"
                },
                {
                    "loop_id": "loop_0097",
                    "drift_severity": "moderate",
                    "alignment_score": 0.62,
                    "belief_alignment_score": 0.65,
                    "health_score": 0.70,
                    "bias_tags": ["optimism_bias"],
                    "timestamp": "2025-04-26T05:20:00Z"
                },
                {
                    "loop_id": "loop_0098",
                    "drift_severity": "moderate",
                    "alignment_score": 0.58,
                    "belief_alignment_score": 0.60,
                    "health_score": 0.65,
                    "bias_tags": ["optimism_bias", "vague_summary"],
                    "timestamp": "2025-04-26T05:30:00Z"
                },
                {
                    "loop_id": "loop_0099",
                    "drift_severity": "critical",
                    "alignment_score": 0.35,
                    "belief_alignment_score": 0.38,
                    "health_score": 0.45,
                    "trust_decay": 0.22,
                    "bias_tags": ["optimism_bias", "vague_summary"],
                    "timestamp": "2025-04-26T05:40:00Z"
                },
                {
                    "loop_id": "loop_0100",
                    "drift_severity": "moderate",
                    "alignment_score": 0.55,
                    "belief_alignment_score": 0.58,
                    "health_score": 0.62,
                    "trust_decay": 0.15,
                    "bias_tags": ["optimism_bias"],
                    "timestamp": "2025-04-26T05:50:00Z"
                },
                {
                    "loop_id": "loop_0101",
                    "drift_severity": "low",
                    "alignment_score": 0.72,
                    "belief_alignment_score": 0.75,
                    "health_score": 0.80,
                    "trust_decay": 0.08,
                    "bias_tags": [],
                    "timestamp": "2025-04-26T06:00:00Z"
                },
                {
                    "loop_id": "loop_0102",
                    "drift_severity": "critical",
                    "alignment_score": 0.38,
                    "belief_alignment_score": 0.40,
                    "health_score": 0.48,
                    "trust_decay": 0.25,
                    "bias_tags": ["optimism_bias", "overconfidence"],
                    "timestamp": "2025-04-26T06:10:00Z"
                }
            ],
            "ceo_insights": [
                {
                    "loop_id": "loop_0096",
                    "insight_type": "alignment_improvement_needed",
                    "alignment_score": 0.75,
                    "missing_beliefs": ["belief3"],
                    "timestamp": "2025-04-26T05:10:00Z"
                },
                {
                    "loop_id": "loop_0099",
                    "insight_type": "belief_omission_alert",
                    "alignment_score": 0.35,
                    "missing_beliefs": ["belief1", "belief2", "belief3"],
                    "timestamp": "2025-04-26T05:40:00Z"
                }
            ],
            "cto_reports": [
                {
                    "loop_id": "loop_0096",
                    "health_score": 0.82,
                    "trust_decay": 0.05,
                    "timestamp": "2025-04-26T05:10:00Z"
                },
                {
                    "loop_id": "loop_0097",
                    "health_score": 0.70,
                    "trust_decay": 0.10,
                    "timestamp": "2025-04-26T05:20:00Z"
                },
                {
                    "loop_id": "loop_0098",
                    "health_score": 0.65,
                    "trust_decay": 0.12,
                    "timestamp": "2025-04-26T05:30:00Z"
                },
                {
                    "loop_id": "loop_0099",
                    "health_score": 0.45,
                    "trust_decay": 0.22,
                    "timestamp": "2025-04-26T05:40:00Z"
                },
                {
                    "loop_id": "loop_0100",
                    "health_score": 0.62,
                    "trust_decay": 0.15,
                    "timestamp": "2025-04-26T05:50:00Z"
                },
                {
                    "loop_id": "loop_0101",
                    "health_score": 0.80,
                    "trust_decay": 0.08,
                    "timestamp": "2025-04-26T06:00:00Z"
                },
                {
                    "loop_id": "loop_0102",
                    "health_score": 0.48,
                    "trust_decay": 0.25,
                    "timestamp": "2025-04-26T06:10:00Z"
                }
            ],
            "historian_alerts": [
                {
                    "loop_id": "loop_0096",
                    "alert_type": "belief_alignment_check",
                    "missing_beliefs": ["belief3"],
                    "loop_belief_alignment_score": 0.78,
                    "timestamp": "2025-04-26T05:10:00Z"
                },
                {
                    "loop_id": "loop_0097",
                    "alert_type": "belief_alignment_check",
                    "missing_beliefs": ["belief2"],
                    "loop_belief_alignment_score": 0.65,
                    "timestamp": "2025-04-26T05:20:00Z"
                },
                {
                    "loop_id": "loop_0098",
                    "alert_type": "belief_alignment_check",
                    "missing_beliefs": ["belief1", "belief3"],
                    "loop_belief_alignment_score": 0.60,
                    "timestamp": "2025-04-26T05:30:00Z"
                },
                {
                    "loop_id": "loop_0099",
                    "alert_type": "belief_drift_detected",
                    "missing_beliefs": ["belief1", "belief2", "belief3"],
                    "loop_belief_alignment_score": 0.38,
                    "timestamp": "2025-04-26T05:40:00Z"
                },
                {
                    "loop_id": "loop_0100",
                    "alert_type": "belief_alignment_check",
                    "missing_beliefs": ["belief2", "belief3"],
                    "loop_belief_alignment_score": 0.58,
                    "timestamp": "2025-04-26T05:50:00Z"
                },
                {
                    "loop_id": "loop_0101",
                    "alert_type": "belief_alignment_check",
                    "missing_beliefs": ["belief3"],
                    "loop_belief_alignment_score": 0.75,
                    "timestamp": "2025-04-26T06:00:00Z"
                },
                {
                    "loop_id": "loop_0102",
                    "alert_type": "belief_drift_detected",
                    "missing_beliefs": ["belief1", "belief2"],
                    "loop_belief_alignment_score": 0.40,
                    "timestamp": "2025-04-26T06:10:00Z"
                }
            ],
            "loops": [
                {
                    "loop_id": "loop_0096",
                    "mode": "RESEARCHER",
                    "timestamp": "2025-04-26T05:10:00Z"
                },
                {
                    "loop_id": "loop_0097",
                    "mode": "RESEARCHER",
                    "timestamp": "2025-04-26T05:20:00Z"
                },
                {
                    "loop_id": "loop_0098",
                    "mode": "BUILDER",
                    "timestamp": "2025-04-26T05:30:00Z"
                },
                {
                    "loop_id": "loop_0099",
                    "mode": "SAGE",
                    "timestamp": "2025-04-26T05:40:00Z"
                },
                {
                    "loop_id": "loop_0100",
                    "mode": "RESEARCHER",
                    "timestamp": "2025-04-26T05:50:00Z"
                },
                {
                    "loop_id": "loop_0101",
                    "mode": "RESEARCHER",
                    "timestamp": "2025-04-26T06:00:00Z"
                },
                {
                    "loop_id": "loop_0102",
                    "mode": "RESEARCHER",
                    "timestamp": "2025-04-26T06:10:00Z"
                }
            ]
        }

    def test_extract_drift_summaries(self):
        """Test extraction of drift summaries."""
        # Test with existing drift summaries
        drift_summaries = _extract_drift_summaries(self.loop_range, self.memory)
        self.assertEqual(len(drift_summaries), 7)
        
        # Test with non-existent loop IDs
        drift_summaries = _extract_drift_summaries(["loop_9999"], self.memory)
        self.assertEqual(len(drift_summaries), 0)
        
        # Test with empty memory
        drift_summaries = _extract_drift_summaries(self.loop_range, {})
        self.assertEqual(len(drift_summaries), 0)

    def test_extract_ceo_insights(self):
        """Test extraction of CEO insights."""
        # Test with existing CEO insights
        ceo_insights = _extract_ceo_insights(self.loop_range, self.memory)
        self.assertEqual(len(ceo_insights), 2)
        
        # Test with non-existent loop IDs
        ceo_insights = _extract_ceo_insights(["loop_9999"], self.memory)
        self.assertEqual(len(ceo_insights), 0)
        
        # Test with empty memory
        ceo_insights = _extract_ceo_insights(self.loop_range, {})
        self.assertEqual(len(ceo_insights), 0)

    def test_extract_cto_reports(self):
        """Test extraction of CTO reports."""
        # Test with existing CTO reports
        cto_reports = _extract_cto_reports(self.loop_range, self.memory)
        self.assertEqual(len(cto_reports), 7)
        
        # Test with non-existent loop IDs
        cto_reports = _extract_cto_reports(["loop_9999"], self.memory)
        self.assertEqual(len(cto_reports), 0)
        
        # Test with empty memory
        cto_reports = _extract_cto_reports(self.loop_range, {})
        self.assertEqual(len(cto_reports), 0)

    def test_extract_historian_alerts(self):
        """Test extraction of historian alerts."""
        # Test with existing historian alerts
        historian_alerts = _extract_historian_alerts(self.loop_range, self.memory)
        self.assertEqual(len(historian_alerts), 7)
        
        # Test with non-existent loop IDs
        historian_alerts = _extract_historian_alerts(["loop_9999"], self.memory)
        self.assertEqual(len(historian_alerts), 0)
        
        # Test with empty memory
        historian_alerts = _extract_historian_alerts(self.loop_range, {})
        self.assertEqual(len(historian_alerts), 0)

    def test_calculate_drift_summary_stats(self):
        """Test calculation of drift summary statistics."""
        # Test with existing drift summaries
        drift_summaries = _extract_drift_summaries(self.loop_range, self.memory)
        stats = _calculate_drift_summary_stats(drift_summaries)
        
        # Check that the stats have the expected structure
        self.assertIn("avg_drift_score", stats)
        self.assertIn("critical_drift_count", stats)
        self.assertIn("common_biases", stats)
        
        # Check that the values are correct
        self.assertEqual(stats["critical_drift_count"], 2)
        self.assertIn("optimism_bias", stats["common_biases"])
        
        # Test with empty drift summaries
        stats = _calculate_drift_summary_stats([])
        self.assertEqual(stats["avg_drift_score"], 0.0)
        self.assertEqual(stats["critical_drift_count"], 0)
        self.assertEqual(stats["common_biases"], [])

    def test_calculate_belief_engagement(self):
        """Test calculation of belief engagement metrics."""
        # Test with existing historian alerts
        historian_alerts = _extract_historian_alerts(self.loop_range, self.memory)
        config = {"belief_reference_threshold": 0.3}
        engagement = _calculate_belief_engagement(historian_alerts, config)
        
        # Check that the engagement has the expected structure
        self.assertIn("most_referenced", engagement)
        self.assertIn("least_referenced", engagement)
        
        # Test with empty historian alerts
        engagement = _calculate_belief_engagement([], config)
        self.assertIsNone(engagement["most_referenced"])
        self.assertIsNone(engagement["least_referenced"])

    def test_calculate_trust_trend(self):
        """Test calculation of trust trend metrics."""
        # Test with existing CTO reports
        cto_reports = _extract_cto_reports(self.loop_range, self.memory)
        trend = _calculate_trust_trend(cto_reports)
        
        # Check that the trend has the expected structure
        self.assertIn("avg_health_score", trend)
        self.assertIn("avg_trust_decay", trend)
        
        # Check that the values are reasonable
        self.assertGreater(trend["avg_health_score"], 0.0)
        self.assertLess(trend["avg_health_score"], 1.0)
        self.assertGreater(trend["avg_trust_decay"], 0.0)
        self.assertLess(trend["avg_trust_decay"], 1.0)
        
        # Test with empty CTO reports
        trend = _calculate_trust_trend([])
        self.assertEqual(trend["avg_health_score"], 0.0)
        self.assertEqual(trend["avg_trust_decay"], 0.0)

    def test_calculate_mode_usage(self):
        """Test calculation of mode usage statistics."""
        # Test with existing loops
        mode_usage = _calculate_mode_usage(self.loop_range, self.memory)
        
        # Check that the mode usage has the expected structure
        self.assertIn("RESEARCHER", mode_usage)
        self.assertIn("SAGE", mode_usage)
        self.assertIn("BUILDER", mode_usage)
        
        # Check that the values are correct
        self.assertEqual(mode_usage["RESEARCHER"], 5)
        self.assertEqual(mode_usage["SAGE"], 1)
        self.assertEqual(mode_usage["BUILDER"], 1)
        
        # Test with non-existent loop IDs
        mode_usage = _calculate_mode_usage(["loop_9999"], self.memory)
        self.assertEqual(len(mode_usage), 0)
        
        # Test with empty memory
        mode_usage = _calculate_mode_usage(self.loop_range, {})
        self.assertEqual(len(mode_usage), 0)

    def test_generate_recommendation(self):
        """Test generation of recommendations."""
        # Test with critical conditions
        drift_summary_stats = {
            "avg_drift_score": 0.65,
            "critical_drift_count": 3,
            "common_biases": ["optimism_bias", "vague_summary"]
        }
        belief_engagement = {
            "most_referenced": "belief1",
            "least_referenced": "belief3"
        }
        trust_trend = {
            "avg_health_score": 0.45,
            "avg_trust_decay": 0.20
        }
        config = {
            "critical_drift_threshold": 0.6,
            "critical_count_threshold": 2
        }
        
        recommendation = _generate_recommendation(
            drift_summary_stats,
            belief_engagement,
            trust_trend,
            config
        )
        
        # Check that the recommendation mentions pausing and SAGE mode
        self.assertIn("Pause building", recommendation)
        self.assertIn("SAGE mode", recommendation)
        
        # Test with moderate conditions
        drift_summary_stats = {
            "avg_drift_score": 0.45,
            "critical_drift_count": 1,
            "common_biases": ["optimism_bias"]
        }
        trust_trend = {
            "avg_health_score": 0.65,
            "avg_trust_decay": 0.12
        }
        
        recommendation = _generate_recommendation(
            drift_summary_stats,
            belief_engagement,
            trust_trend,
            config
        )
        
        # Check that the recommendation mentions emotional tone
        self.assertIn("emotional tone", recommendation)
        
        # Test with healthy system
        drift_summary_stats = {
            "avg_drift_score": 0.25,
            "critical_drift_count": 0,
            "common_biases": []
        }
        trust_trend = {
            "avg_health_score": 0.85,
            "avg_trust_decay": 0.05
        }
        
        recommendation = _generate_recommendation(
            drift_summary_stats,
            belief_engagement,
            trust_trend,
            config
        )
        
        # Check that the recommendation mentions continuing normal operation
        self.assertIn("Continue normal operation", recommendation)

    def test_generate_weekly_drift_report(self):
        """Test generation of weekly drift report."""
        # Test with complete memory
        report = generate_weekly_drift_report(self.loop_range, self.memory)
        
        # Check that the report has the expected structure
        self.assertIn("report_id", report)
        self.assertIn("loop_range", report)
        self.assertIn("drift_summary_stats", report)
        self.assertIn("belief_engagement", report)
        self.assertIn("trust_trend", report)
        self.assertIn("mode_usage", report)
        self.assertIn("recommendation", report)
        self.assertIn("timestamp", report)
        
        # Check that the values are correct
        self.assertEqual(report["loop_range"], self.loop_range)
        self.assertEqual(report["drift_summary_stats"]["critical_drift_count"], 2)
        self.assertEqual(report["mode_usage"]["RESEARCHER"], 5)
        
        # Test with empty memory
        report = generate_weekly_drift_report(self.loop_range, {})
        self.assertEqual(report["loop_range"], self.loop_range)
        self.assertEqual(report["drift_summary_stats"]["critical_drift_count"], 0)
        self.assertEqual(len(report["mode_usage"]), 0)

    def test_store_weekly_drift_report(self):
        """Test storing weekly drift report in memory."""
        # Create a report
        report = {
            "report_id": "drift_week_014",
            "loop_range": self.loop_range,
            "drift_summary_stats": {
                "avg_drift_score": 0.58,
                "critical_drift_count": 2,
                "common_biases": ["optimism_bias", "vague_summary"]
            },
            "belief_engagement": {
                "most_referenced": "belief1",
                "least_referenced": "belief3"
            },
            "trust_trend": {
                "avg_health_score": 0.65,
                "avg_trust_decay": 0.14
            },
            "mode_usage": {
                "RESEARCHER": 5,
                "SAGE": 1,
                "BUILDER": 1
            },
            "recommendation": "Pause building. Enter SAGE mode and reflect on emotional alignment.",
            "timestamp": "2025-04-26T06:22:00Z"
        }
        
        # Test with empty memory
        updated_memory = store_weekly_drift_report({}, report)
        self.assertIn("weekly_drift_reports", updated_memory)
        self.assertEqual(len(updated_memory["weekly_drift_reports"]), 1)
        self.assertEqual(updated_memory["weekly_drift_reports"][0], report)
        
        # Test with existing weekly drift reports
        memory_with_reports = {
            "weekly_drift_reports": [
                {
                    "report_id": "drift_week_013",
                    "loop_range": ["loop_0089", "loop_0090", "loop_0091", "loop_0092", "loop_0093", "loop_0094", "loop_0095"],
                    "timestamp": "2025-04-19T06:22:00Z"
                }
            ]
        }
        updated_memory = store_weekly_drift_report(memory_with_reports, report)
        self.assertEqual(len(updated_memory["weekly_drift_reports"]), 2)
        self.assertEqual(updated_memory["weekly_drift_reports"][1], report)

    def test_handle_critical_drift_pattern(self):
        """Test handling of critical drift pattern."""
        # Create a critical report
        critical_report = {
            "report_id": "drift_week_014",
            "loop_range": self.loop_range,
            "drift_summary_stats": {
                "avg_drift_score": 0.65,
                "critical_drift_count": 3,
                "common_biases": ["optimism_bias", "vague_summary"]
            },
            "recommendation": "Pause building. Enter SAGE mode and reflect on system alignment.",
            "timestamp": "2025-04-26T06:22:00Z"
        }
        
        # Test with empty memory
        updated_memory = handle_critical_drift_pattern({}, critical_report)
        self.assertIn("cto_warnings", updated_memory)
        self.assertEqual(len(updated_memory["cto_warnings"]), 1)
        self.assertEqual(updated_memory["cto_warnings"][0]["type"], "critical_drift_pattern")
        self.assertEqual(updated_memory["cto_warnings"][0]["report_id"], "drift_week_014")
        
        # Test with existing warnings
        memory_with_warnings = {
            "cto_warnings": [
                {
                    "type": "belief_drift",
                    "loop_id": "loop_0095",
                    "timestamp": "2025-04-19T06:22:00Z"
                }
            ]
        }
        updated_memory = handle_critical_drift_pattern(memory_with_warnings, critical_report)
        self.assertEqual(len(updated_memory["cto_warnings"]), 2)
        self.assertEqual(updated_memory["cto_warnings"][1]["type"], "critical_drift_pattern")
        
        # Test with non-critical report
        moderate_report = {
            "report_id": "drift_week_014",
            "loop_range": self.loop_range,
            "drift_summary_stats": {
                "avg_drift_score": 0.45,
                "critical_drift_count": 1,
                "common_biases": ["optimism_bias"]
            },
            "timestamp": "2025-04-26T06:22:00Z"
        }
        updated_memory = handle_critical_drift_pattern({}, moderate_report)
        self.assertNotIn("cto_warnings", updated_memory)

    def test_should_generate_weekly_report(self):
        """Test determination of when to generate weekly report."""
        # Test with loop ID that should trigger report
        should_generate, loop_range = should_generate_weekly_report("loop_0105", self.memory)
        self.assertTrue(should_generate)
        self.assertEqual(len(loop_range), 7)
        self.assertEqual(loop_range[0], "loop_0099")
        self.assertEqual(loop_range[-1], "loop_0105")
        
        # Test with loop ID that should not trigger report
        should_generate, loop_range = should_generate_weekly_report("loop_0103", self.memory)
        self.assertFalse(should_generate)
        
        # Test with invalid loop ID
        should_generate, loop_range = should_generate_weekly_report("invalid_loop_id", self.memory)
        self.assertFalse(should_generate)
        
        # Test with custom report frequency
        config = {"report_frequency": 5, "min_loops_required": 3}
        should_generate, loop_range = should_generate_weekly_report("loop_0105", self.memory, config)
        self.assertTrue(should_generate)
        self.assertEqual(len(loop_range), 5)

    def test_process_loop_with_weekly_drift_report(self):
        """Test the main weekly drift report processing function."""
        # Test with loop ID that should trigger report
        updated_memory = process_loop_with_weekly_drift_report("loop_0105", self.memory)
        
        # Check that weekly drift reports were added
        self.assertIn("weekly_drift_reports", updated_memory)
        self.assertEqual(updated_memory["weekly_drift_reports"][0]["report_id"], "drift_week_015")
        
        # Test with loop ID that should not trigger report
        unchanged_memory = process_loop_with_weekly_drift_report("loop_0103", self.memory)
        self.assertEqual(unchanged_memory, self.memory)
        
        # Test with disabled config
        config = {"enabled": False}
        unchanged_memory = process_loop_with_weekly_drift_report("loop_0105", self.memory, config)
        self.assertEqual(unchanged_memory, self.memory)
        
        # Test with manual trigger
        updated_memory = process_loop_with_weekly_drift_report("loop_0103", self.memory, manual_trigger=True)
        self.assertIn("weekly_drift_reports", updated_memory)

if __name__ == '__main__':
    unittest.main()
