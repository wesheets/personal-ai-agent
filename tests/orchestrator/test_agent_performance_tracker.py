"""
Tests for the Agent Performance Tracker module.

This test suite verifies the functionality for tracking agent performance,
calculating trust scores, and generating agent reports.
"""

import unittest
import datetime
from unittest.mock import patch, MagicMock
import json
import logging
from orchestrator.modules.agent_performance_tracker import (
    update_agent_performance,
    calculate_trust_score,
    get_agent_report,
    get_all_agent_reports,
    get_agent_history,
    reset_agent_performance
)

class TestAgentPerformanceTracker(unittest.TestCase):
    """Test cases for the Agent Performance Tracker module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a fresh memory dictionary for each test
        self.memory = {}
        
        # Sample outcome data
        self.valid_outcome = {
            "loop_id": 37,
            "status": "approved",
            "schema_valid": True,
            "reflection_passed": True,
            "rejected_by_operator": False,
            "critic_override": False
        }
    
    def test_update_agent_performance_valid(self):
        """Test updating agent performance with valid outcome."""
        result = update_agent_performance(
            self.memory, 
            "nova", 
            self.valid_outcome
        )
        
        # Check that agent performance was recorded in memory
        self.assertIn("agent_performance", self.memory)
        self.assertIn("nova", self.memory["agent_performance"])
        
        # Check that agent performance entry has all required fields
        agent_perf = self.memory["agent_performance"]["nova"]
        self.assertIn("trust_score", agent_perf)
        self.assertIn("loops_participated", agent_perf)
        self.assertIn("schema_validations", agent_perf)
        self.assertIn("reflection_validations", agent_perf)
        self.assertIn("critic_rejections", agent_perf)
        self.assertIn("operator_rejections", agent_perf)
        self.assertIn("history", agent_perf)
        self.assertIn("last_updated", agent_perf)
        
        # Check that participation count was incremented
        self.assertEqual(agent_perf["loops_participated"], 1)
        
        # Check that schema validation was recorded
        self.assertEqual(agent_perf["schema_validations"]["passed"], 1)
        self.assertEqual(agent_perf["schema_validations"]["failed"], 0)
        
        # Check that reflection validation was recorded
        self.assertEqual(agent_perf["reflection_validations"]["passed"], 1)
        self.assertEqual(agent_perf["reflection_validations"]["failed"], 0)
        
        # Check that history was updated
        self.assertEqual(len(agent_perf["history"]), 1)
        self.assertEqual(agent_perf["history"][0]["loop_id"], 37)
        self.assertEqual(agent_perf["history"][0]["status"], "approved")
    
    def test_update_agent_performance_missing_fields(self):
        """Test updating agent performance with missing required fields."""
        invalid_outcome = {
            "status": "approved"
            # Missing "loop_id" field
        }
        
        with self.assertRaises(ValueError) as context:
            update_agent_performance(self.memory, "nova", invalid_outcome)
        
        self.assertIn("Missing required field", str(context.exception))
    
    def test_update_agent_performance_invalid_status(self):
        """Test updating agent performance with invalid status."""
        invalid_outcome = {
            "loop_id": 37,
            "status": "invalid_status"
        }
        
        with self.assertRaises(ValueError) as context:
            update_agent_performance(self.memory, "nova", invalid_outcome)
        
        self.assertIn("Invalid status", str(context.exception))
    
    def test_update_agent_performance_rejection(self):
        """Test updating agent performance with rejection outcome."""
        rejection_outcome = {
            "loop_id": 38,
            "status": "rejected",
            "schema_valid": True,
            "reflection_passed": False,
            "rejected_by_operator": True,
            "critic_override": True
        }
        
        result = update_agent_performance(
            self.memory, 
            "nova", 
            rejection_outcome
        )
        
        # Check that rejection counts were incremented
        agent_perf = self.memory["agent_performance"]["nova"]
        self.assertEqual(agent_perf["operator_rejections"], 1)
        self.assertEqual(agent_perf["critic_rejections"], 1)
        
        # Check that reflection validation failure was recorded
        self.assertEqual(agent_perf["reflection_validations"]["failed"], 1)
    
    def test_calculate_trust_score_new_agent(self):
        """Test calculating trust score for a new agent."""
        # Calculate trust score for non-existent agent
        score = calculate_trust_score(self.memory, "new_agent")
        
        # Should return default score for new agents
        self.assertEqual(score, 0.5)
    
    def test_calculate_trust_score_perfect_agent(self):
        """Test calculating trust score for an agent with perfect performance."""
        # Create an agent with perfect performance
        self.memory["agent_performance"] = {
            "perfect_agent": {
                "trust_score": 0.5,
                "loops_participated": 10,
                "schema_validations": {
                    "passed": 10,
                    "failed": 0
                },
                "reflection_validations": {
                    "passed": 10,
                    "failed": 0
                },
                "critic_rejections": 0,
                "operator_rejections": 0,
                "history": [],
                "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # Calculate trust score
        score = calculate_trust_score(self.memory, "perfect_agent")
        
        # Should be close to maximum (0.9)
        self.assertGreater(score, 0.8)
    
    def test_calculate_trust_score_poor_agent(self):
        """Test calculating trust score for an agent with poor performance."""
        # Create an agent with poor performance
        self.memory["agent_performance"] = {
            "poor_agent": {
                "trust_score": 0.5,
                "loops_participated": 10,
                "schema_validations": {
                    "passed": 2,
                    "failed": 8
                },
                "reflection_validations": {
                    "passed": 3,
                    "failed": 7
                },
                "critic_rejections": 5,
                "operator_rejections": 4,
                "history": [],
                "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # Calculate trust score
        score = calculate_trust_score(self.memory, "poor_agent")
        
        # Should be significantly lower than default
        self.assertLess(score, 0.4)
    
    def test_calculate_trust_score_time_decay(self):
        """Test trust score time decay for inactive agents."""
        # Create an agent with old last_updated timestamp
        old_date = (datetime.datetime.utcnow() - datetime.timedelta(days=20)).isoformat() + "Z"
        self.memory["agent_performance"] = {
            "inactive_agent": {
                "trust_score": 0.8,
                "loops_participated": 10,
                "schema_validations": {
                    "passed": 10,
                    "failed": 0
                },
                "reflection_validations": {
                    "passed": 10,
                    "failed": 0
                },
                "critic_rejections": 0,
                "operator_rejections": 0,
                "history": [],
                "last_updated": old_date
            }
        }
        
        # Calculate trust score
        score = calculate_trust_score(self.memory, "inactive_agent")
        
        # Should be lower than the stored score due to time decay
        self.assertLess(score, 0.8)
    
    def test_get_agent_report(self):
        """Test generating an agent report."""
        # Create an agent with some performance data
        self.memory["agent_performance"] = {
            "nova": {
                "trust_score": 0.72,
                "loops_participated": 9,
                "schema_validations": {
                    "passed": 8,
                    "failed": 1
                },
                "reflection_validations": {
                    "passed": 7,
                    "failed": 2
                },
                "critic_rejections": 2,
                "operator_rejections": 1,
                "history": [],
                "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # Get agent report
        report = get_agent_report(self.memory, "nova")
        
        # Check that report has all required fields
        self.assertEqual(report["agent"], "nova")
        self.assertIn("trust_score", report)
        self.assertEqual(report["loops_participated"], 9)
        self.assertEqual(report["critic_rejections"], 2)
        self.assertEqual(report["operator_rejections"], 1)
        self.assertAlmostEqual(report["schema_pass_rate"], 0.88, places=2)
        self.assertAlmostEqual(report["reflection_pass_rate"], 0.77, places=2)
        self.assertIn("last_updated", report)
    
    def test_get_agent_report_nonexistent(self):
        """Test generating a report for a non-existent agent."""
        with self.assertRaises(ValueError) as context:
            get_agent_report(self.memory, "nonexistent_agent")
        
        self.assertIn("No performance data found", str(context.exception))
    
    def test_get_all_agent_reports(self):
        """Test generating reports for all agents."""
        # Create multiple agents with performance data
        self.memory["agent_performance"] = {
            "nova": {
                "trust_score": 0.72,
                "loops_participated": 9,
                "schema_validations": {
                    "passed": 8,
                    "failed": 1
                },
                "reflection_validations": {
                    "passed": 7,
                    "failed": 2
                },
                "critic_rejections": 2,
                "operator_rejections": 1,
                "history": [],
                "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
            },
            "hal": {
                "trust_score": 0.85,
                "loops_participated": 12,
                "schema_validations": {
                    "passed": 11,
                    "failed": 1
                },
                "reflection_validations": {
                    "passed": 10,
                    "failed": 2
                },
                "critic_rejections": 1,
                "operator_rejections": 0,
                "history": [],
                "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # Get all agent reports
        reports = get_all_agent_reports(self.memory)
        
        # Check that reports were generated for both agents
        self.assertEqual(len(reports), 2)
        self.assertIn("nova", reports)
        self.assertIn("hal", reports)
        self.assertEqual(reports["nova"]["agent"], "nova")
        self.assertEqual(reports["hal"]["agent"], "hal")
    
    def test_get_agent_history(self):
        """Test retrieving agent history."""
        # Create an agent with history
        self.memory["agent_performance"] = {
            "nova": {
                "trust_score": 0.72,
                "loops_participated": 3,
                "schema_validations": {
                    "passed": 2,
                    "failed": 1
                },
                "reflection_validations": {
                    "passed": 2,
                    "failed": 1
                },
                "critic_rejections": 1,
                "operator_rejections": 1,
                "history": [
                    {
                        "loop_id": 35,
                        "status": "approved",
                        "trust_before": 0.5,
                        "trust_after": 0.6,
                        "timestamp": "2025-04-23T00:00:00Z"
                    },
                    {
                        "loop_id": 36,
                        "status": "rejected",
                        "trust_before": 0.6,
                        "trust_after": 0.5,
                        "timestamp": "2025-04-24T00:00:00Z"
                    },
                    {
                        "loop_id": 37,
                        "status": "approved",
                        "trust_before": 0.5,
                        "trust_after": 0.72,
                        "timestamp": "2025-04-25T00:00:00Z"
                    }
                ],
                "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # Get agent history
        history = get_agent_history(self.memory, "nova")
        
        # Check that history is returned in reverse chronological order
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["loop_id"], 37)  # Most recent first
        self.assertEqual(history[1]["loop_id"], 36)
        self.assertEqual(history[2]["loop_id"], 35)
        
        # Test with limit
        limited_history = get_agent_history(self.memory, "nova", limit=2)
        self.assertEqual(len(limited_history), 2)
        self.assertEqual(limited_history[0]["loop_id"], 37)
        self.assertEqual(limited_history[1]["loop_id"], 36)
    
    def test_reset_agent_performance(self):
        """Test resetting agent performance."""
        # Create an agent with some performance data
        self.memory["agent_performance"] = {
            "nova": {
                "trust_score": 0.72,
                "loops_participated": 9,
                "schema_validations": {
                    "passed": 8,
                    "failed": 1
                },
                "reflection_validations": {
                    "passed": 7,
                    "failed": 2
                },
                "critic_rejections": 2,
                "operator_rejections": 1,
                "history": [{"loop_id": 1}],
                "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # Reset agent performance
        result = reset_agent_performance(self.memory, "nova")
        
        # Check that reset was successful
        self.assertTrue(result)
        
        # Check that performance was reset to default values
        agent_perf = self.memory["agent_performance"]["nova"]
        self.assertEqual(agent_perf["trust_score"], 0.5)
        self.assertEqual(agent_perf["loops_participated"], 0)
        self.assertEqual(agent_perf["schema_validations"]["passed"], 0)
        self.assertEqual(agent_perf["schema_validations"]["failed"], 0)
        self.assertEqual(agent_perf["reflection_validations"]["passed"], 0)
        self.assertEqual(agent_perf["reflection_validations"]["failed"], 0)
        self.assertEqual(agent_perf["critic_rejections"], 0)
        self.assertEqual(agent_perf["operator_rejections"], 0)
        self.assertEqual(len(agent_perf["history"]), 0)
    
    def test_full_agent_lifecycle(self):
        """Test the complete agent performance lifecycle."""
        # Update agent performance multiple times with different outcomes
        update_agent_performance(
            self.memory,
            "nova",
            {
                "loop_id": 35,
                "status": "approved",
                "schema_valid": True,
                "reflection_passed": True
            }
        )
        
        update_agent_performance(
            self.memory,
            "nova",
            {
                "loop_id": 36,
                "status": "rejected",
                "schema_valid": False,
                "reflection_passed": False,
                "rejected_by_operator": True
            }
        )
        
        update_agent_performance(
            self.memory,
            "nova",
            {
                "loop_id": 37,
                "status": "revised",
                "schema_valid": True,
                "reflection_passed": False,
                "critic_override": True
            }
        )
        
        # Get agent report
        report = get_agent_report(self.memory, "nova")
        
        # Check that report reflects all updates
        self.assertEqual(report["loops_participated"], 3)
        self.assertEqual(report["critic_rejections"], 1)
        self.assertEqual(report["operator_rejections"], 1)
        self.assertAlmostEqual(report["schema_pass_rate"], 2/3, places=2)
        self.assertAlmostEqual(report["reflection_pass_rate"], 1/3, places=2)
        
        # Check that trust score is lower than default due to rejections
        self.assertLess(report["trust_score"], 0.5)
        
        # Get agent history
        history = get_agent_history(self.memory, "nova")
        self.assertEqual(len(history), 3)

if __name__ == "__main__":
    unittest.main()
