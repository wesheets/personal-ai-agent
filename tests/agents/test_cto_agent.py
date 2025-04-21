"""
Unit tests for CTO Agent

This module contains tests for the CTO Agent functionality.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from agents.cto_agent import (
    score_loop_health,
    check_plan_summary_divergence,
    track_trust_decay,
    generate_cto_report,
    analyze_loop_with_cto_agent
)

class TestCTOAgent(unittest.TestCase):
    """Test cases for CTO Agent functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.loop_id = "loop_0094"
        self.plan = {
            "objective": "Implement feature X with comprehensive tests",
            "steps": [
                {"description": "Create directory structure"},
                {"description": "Implement core functionality"},
                {"description": "Write unit tests"},
                {"description": "Update documentation"}
            ]
        }
        self.summary = "Successfully implemented feature X with comprehensive tests. Created directory structure, implemented core functionality, wrote unit tests, and updated documentation."
        self.loop = {
            "loop_id": self.loop_id,
            "plan_rerouted": False,
            "called_agents": ["core-forge", "critic", "hal", "nova"],
            "status": "completed",
            "error": False
        }
        self.agent_logs = [
            {
                "agent_name": "core-forge",
                "status": "success",
                "timestamp": "2025-04-26T04:10:00Z"
            },
            {
                "agent_name": "critic",
                "status": "success",
                "timestamp": "2025-04-26T04:12:00Z"
            },
            {
                "agent_name": "hal",
                "status": "success",
                "timestamp": "2025-04-26T04:13:00Z"
            },
            {
                "agent_name": "nova",
                "status": "success",
                "timestamp": "2025-04-26T04:14:00Z"
            },
            {
                "agent_name": "system",
                "status": "success",
                "trust_score": 0.95,
                "timestamp": "2025-04-26T04:15:00Z"
            }
        ]
        self.memory = {
            "loops": [
                {
                    "loop_id": "loop_0093",
                    "summary": "Previous loop summary",
                    "timestamp": "2025-04-25T04:15:00Z"
                }
            ]
        }

    def test_score_loop_health(self):
        """Test scoring of loop health."""
        # Test healthy loop
        healthy_score = score_loop_health(self.loop)
        self.assertGreaterEqual(healthy_score, 0.0)
        self.assertLessEqual(healthy_score, 1.0)
        self.assertGreaterEqual(healthy_score, 0.9)  # Should be high for a healthy loop
        
        # Test unhealthy loop - plan rerouted
        unhealthy_loop = self.loop.copy()
        unhealthy_loop["plan_rerouted"] = True
        unhealthy_score = score_loop_health(unhealthy_loop)
        self.assertLess(unhealthy_score, healthy_score)
        
        # Test unhealthy loop - missing critic
        no_critic_loop = self.loop.copy()
        no_critic_loop["called_agents"] = ["core-forge", "hal", "nova"]
        no_critic_score = score_loop_health(no_critic_loop)
        self.assertLess(no_critic_score, healthy_score)
        
        # Test unhealthy loop - error
        error_loop = self.loop.copy()
        error_loop["error"] = True
        error_score = score_loop_health(error_loop)
        self.assertLess(error_score, healthy_score)

    def test_check_plan_summary_divergence(self):
        """Test checking of plan-summary divergence."""
        # Test aligned plan and summary
        aligned_divergence = check_plan_summary_divergence(self.plan, self.summary)
        self.assertGreaterEqual(aligned_divergence, 0.0)
        self.assertLessEqual(aligned_divergence, 1.0)
        self.assertLessEqual(aligned_divergence, 0.7)  # Should be relatively low for aligned plan and summary
        
        # Test divergent plan and summary
        divergent_summary = "Implemented feature Y with basic functionality. Created directory structure but skipped tests."
        divergent_divergence = check_plan_summary_divergence(self.plan, divergent_summary)
        self.assertGreater(divergent_divergence, aligned_divergence)
        
        # Test completely different plan and summary
        unrelated_summary = "Fixed bugs in the authentication system. Updated user login flow."
        unrelated_divergence = check_plan_summary_divergence(self.plan, unrelated_summary)
        self.assertGreater(unrelated_divergence, divergent_divergence)

    def test_track_trust_decay(self):
        """Test tracking of trust decay."""
        # Test with successful agents
        successful_decay = track_trust_decay(self.agent_logs)
        self.assertIn("agent_failure_rate", successful_decay)
        self.assertIn("avg_loop_trust_decay", successful_decay)
        
        # All agents should have 0.0 failure rate
        for agent, rate in successful_decay["agent_failure_rate"].items():
            self.assertEqual(rate, 0.0)
        
        # Test with failing agents
        failing_logs = self.agent_logs.copy()
        failing_logs.append({
            "agent_name": "nova",
            "status": "failed",
            "timestamp": "2025-04-26T04:16:00Z"
        })
        failing_logs.append({
            "agent_name": "nova",
            "status": "failed",
            "timestamp": "2025-04-26T04:17:00Z"
        })
        
        failing_decay = track_trust_decay(failing_logs)
        self.assertGreater(failing_decay["agent_failure_rate"].get("nova", 0), 0.0)
        
        # Test with trust decay
        decaying_logs = self.agent_logs.copy()
        decaying_logs.append({
            "agent_name": "system",
            "status": "success",
            "trust_score": 0.85,
            "timestamp": "2025-04-26T04:16:00Z"
        })
        decaying_logs.append({
            "agent_name": "system",
            "status": "success",
            "trust_score": 0.75,
            "timestamp": "2025-04-26T04:17:00Z"
        })
        
        decaying_trust = track_trust_decay(decaying_logs)
        self.assertGreater(decaying_trust["avg_loop_trust_decay"], 0.0)

    def test_generate_cto_report(self):
        """Test generation of CTO reports."""
        report = generate_cto_report(
            self.loop_id,
            self.loop,
            self.plan,
            self.summary,
            self.agent_logs
        )
        
        # Check that the report has the expected structure
        self.assertEqual(report["loop_id"], self.loop_id)
        self.assertIn("health_score", report)
        self.assertIn("plan_summary_alignment_score", report)
        self.assertIn("trust_decay", report)
        self.assertIn("recommendation", report)
        self.assertIn("timestamp", report)
        
        # Check that scores are within expected ranges
        self.assertGreaterEqual(report["health_score"], 0.0)
        self.assertLessEqual(report["health_score"], 1.0)
        self.assertGreaterEqual(report["plan_summary_alignment_score"], 0.0)
        self.assertLessEqual(report["plan_summary_alignment_score"], 1.0)
        
        # Test with unhealthy loop
        unhealthy_loop = self.loop.copy()
        unhealthy_loop["plan_rerouted"] = True
        unhealthy_loop["error"] = True
        unhealthy_loop["called_agents"] = ["core-forge", "hal"]
        
        unhealthy_report = generate_cto_report(
            self.loop_id,
            unhealthy_loop,
            self.plan,
            self.summary,
            self.agent_logs
        )
        
        self.assertLess(unhealthy_report["health_score"], report["health_score"])
        self.assertNotEqual(unhealthy_report["recommendation"], "No specific recommendations; system operating within normal parameters")

    def test_analyze_loop_with_cto_agent(self):
        """Test the main CTO Agent analysis function."""
        # Test with default config
        updated_memory = analyze_loop_with_cto_agent(
            self.loop_id,
            self.loop,
            self.plan,
            self.summary,
            self.agent_logs,
            self.memory
        )
        
        # Check that the memory was updated
        self.assertIn("cto_reports", updated_memory)
        self.assertEqual(updated_memory["cto_reports"][0]["loop_id"], self.loop_id)
        
        # Check that the loop health score was added to the loop
        self.assertIn("loop_health_score", self.loop)
        
        # Test with disabled config
        config = {"enabled": False}
        unchanged_memory = analyze_loop_with_cto_agent(
            self.loop_id,
            self.loop,
            self.plan,
            self.summary,
            self.agent_logs,
            self.memory,
            config
        )
        
        # Check that the memory was not changed when disabled
        self.assertEqual(unchanged_memory, self.memory)
        
        # Test with unhealthy loop that should generate warnings
        unhealthy_loop = self.loop.copy()
        unhealthy_loop["plan_rerouted"] = True
        unhealthy_loop["error"] = True
        unhealthy_loop["called_agents"] = ["core-forge"]
        
        warning_config = {
            "enabled": True,
            "warning_threshold": 0.9  # High threshold to ensure warning is generated
        }
        
        warning_memory = analyze_loop_with_cto_agent(
            self.loop_id,
            unhealthy_loop,
            self.plan,
            self.summary,
            self.agent_logs,
            self.memory,
            warning_config
        )
        
        # Check that warnings were generated
        self.assertIn("cto_warnings", warning_memory)
        self.assertEqual(warning_memory["cto_warnings"][0]["loop_id"], self.loop_id)
        self.assertIn("health_score", warning_memory["cto_warnings"][0])

if __name__ == '__main__':
    unittest.main()
