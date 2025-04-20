"""
Test cases for the Agent Performance Audit + Trust Score System.

Tests the ability to track agent performance across loops and compute dynamic trust scores.
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.agent_performance_tracker import (
    update_agent_performance,
    calculate_trust_score,
    get_agent_report,
    get_agent_performance_history,
    get_current_trust_score
)

class TestAgentPerformanceTracker(unittest.TestCase):
    """Test cases for the Agent Performance Audit + Trust Score System."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample project and agent data
        self.project_id = "test_project_001"
        self.agent_name = "hal"
        self.loop_id = 33
        
        # Patch the log_to_memory and log_to_chat functions
        self.memory_patch = patch('orchestrator.modules.agent_performance_tracker.log_to_memory')
        self.chat_patch = patch('orchestrator.modules.agent_performance_tracker.log_to_chat')
        self.memory_mock = self.memory_patch.start()
        self.chat_mock = self.chat_patch.start()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Stop all patches
        self.memory_patch.stop()
        self.chat_patch.stop()
    
    def test_update_agent_performance_success(self):
        """Test updating agent performance with successful metrics."""
        # Create a sample result with successful metrics
        result = {
            "schema_passed": True,
            "was_rerouted": False,
            "operator_approved": True,
            "files_created": 1,
            "rejections": 0
        }
        
        # Call the function
        performance_data = update_agent_performance(self.project_id, self.agent_name, self.loop_id, result)
        
        # Check the performance data
        self.assertEqual(performance_data["agent"], self.agent_name)
        self.assertEqual(performance_data["loop_id"], self.loop_id)
        self.assertTrue(performance_data["schema_passed"])
        self.assertFalse(performance_data["was_rerouted"])
        self.assertTrue(performance_data["operator_approved"])
        self.assertEqual(performance_data["files_created"], 1)
        self.assertEqual(performance_data["rejections"], 0)
        
        # Check that log_to_memory was called with the expected arguments
        self.memory_mock.assert_any_call(self.project_id, {
            "agent_performance": {
                self.agent_name: [unittest.mock.ANY]
            }
        })
        self.memory_mock.assert_any_call(self.project_id, {
            "loop_trace": [unittest.mock.ANY]
        })
        
        # Check that log_to_chat was called
        self.chat_mock.assert_called()
    
    def test_update_agent_performance_failure(self):
        """Test updating agent performance with failure metrics."""
        # Create a sample result with failure metrics
        result = {
            "schema_passed": False,
            "was_rerouted": True,
            "operator_approved": False,
            "files_created": 0,
            "rejections": 2
        }
        
        # Call the function
        performance_data = update_agent_performance(self.project_id, self.agent_name, self.loop_id, result)
        
        # Check the performance data
        self.assertEqual(performance_data["agent"], self.agent_name)
        self.assertEqual(performance_data["loop_id"], self.loop_id)
        self.assertFalse(performance_data["schema_passed"])
        self.assertTrue(performance_data["was_rerouted"])
        self.assertFalse(performance_data["operator_approved"])
        self.assertEqual(performance_data["files_created"], 0)
        self.assertEqual(performance_data["rejections"], 2)
        
        # Check that log_to_memory was called with the expected arguments
        self.memory_mock.assert_any_call(self.project_id, {
            "agent_performance": {
                self.agent_name: [unittest.mock.ANY]
            }
        })
        
        # Check that log_to_chat was called with warning emoji
        self.chat_mock.assert_called()
        args, kwargs = self.chat_mock.call_args
        self.assertIn("⚠️", args[1]["message"])
    
    def test_update_agent_performance_missing_fields(self):
        """Test updating agent performance with missing fields."""
        # Create a sample result with missing fields
        result = {
            "schema_passed": True
        }
        
        # Call the function
        performance_data = update_agent_performance(self.project_id, self.agent_name, self.loop_id, result)
        
        # Check the performance data has default values for missing fields
        self.assertEqual(performance_data["agent"], self.agent_name)
        self.assertEqual(performance_data["loop_id"], self.loop_id)
        self.assertTrue(performance_data["schema_passed"])
        self.assertFalse(performance_data["was_rerouted"])  # Default
        self.assertFalse(performance_data["operator_approved"])  # Default
        self.assertEqual(performance_data["files_created"], 0)  # Default
        self.assertEqual(performance_data["rejections"], 0)  # Default
    
    @patch('orchestrator.modules.agent_performance_tracker.get_agent_performance_history')
    def test_calculate_trust_score_no_history(self, mock_get_history):
        """Test calculating trust score with no performance history."""
        # Set up the mock to return an empty list
        mock_get_history.return_value = []
        
        # Call the function
        trust_score = calculate_trust_score(self.project_id, self.agent_name)
        
        # Check the result
        self.assertEqual(trust_score, 0.5)  # Default trust score
        
        # Check that log_to_memory was called with the expected arguments
        self.memory_mock.assert_called_with(self.project_id, {
            "agent_status": {
                self.agent_name: {
                    "trust_score": 0.5,
                    "last_updated": unittest.mock.ANY
                }
            }
        })
    
    @patch('orchestrator.modules.agent_performance_tracker.get_agent_performance_history')
    def test_calculate_trust_score_perfect_history(self, mock_get_history):
        """Test calculating trust score with perfect performance history."""
        # Create a sample performance history with perfect metrics
        history = [
            {
                "agent": self.agent_name,
                "loop_id": 30,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 1,
                "rejections": 0,
                "timestamp": "2025-04-20T12:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 31,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 2,
                "rejections": 0,
                "timestamp": "2025-04-20T13:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 32,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 1,
                "rejections": 0,
                "timestamp": "2025-04-20T14:00:00Z"
            }
        ]
        
        # Set up the mock to return our history
        mock_get_history.return_value = history
        
        # Call the function
        trust_score = calculate_trust_score(self.project_id, self.agent_name)
        
        # Check the result is very high (close to 1.0)
        self.assertGreaterEqual(trust_score, 0.95)
        
        # Check that log_to_memory was called with the expected arguments
        self.memory_mock.assert_called_with(self.project_id, {
            "agent_status": {
                self.agent_name: {
                    "trust_score": unittest.mock.ANY,
                    "last_updated": unittest.mock.ANY
                }
            }
        })
    
    @patch('orchestrator.modules.agent_performance_tracker.get_agent_performance_history')
    def test_calculate_trust_score_poor_history(self, mock_get_history):
        """Test calculating trust score with poor performance history."""
        # Create a sample performance history with poor metrics
        history = [
            {
                "agent": self.agent_name,
                "loop_id": 30,
                "schema_passed": False,
                "was_rerouted": True,
                "operator_approved": False,
                "files_created": 0,
                "rejections": 2,
                "timestamp": "2025-04-20T12:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 31,
                "schema_passed": False,
                "was_rerouted": True,
                "operator_approved": False,
                "files_created": 1,
                "rejections": 1,
                "timestamp": "2025-04-20T13:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 32,
                "schema_passed": False,
                "was_rerouted": True,
                "operator_approved": False,
                "files_created": 0,
                "rejections": 3,
                "timestamp": "2025-04-20T14:00:00Z"
            }
        ]
        
        # Set up the mock to return our history
        mock_get_history.return_value = history
        
        # Call the function
        trust_score = calculate_trust_score(self.project_id, self.agent_name)
        
        # Check the result is very low (close to 0.0)
        self.assertLessEqual(trust_score, 0.2)
    
    @patch('orchestrator.modules.agent_performance_tracker.get_agent_performance_history')
    def test_calculate_trust_score_mixed_history(self, mock_get_history):
        """Test calculating trust score with mixed performance history."""
        # Create a sample performance history with mixed metrics
        history = [
            {
                "agent": self.agent_name,
                "loop_id": 30,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 1,
                "rejections": 0,
                "timestamp": "2025-04-20T12:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 31,
                "schema_passed": False,
                "was_rerouted": True,
                "operator_approved": False,
                "files_created": 0,
                "rejections": 2,
                "timestamp": "2025-04-20T13:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 32,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 1,
                "rejections": 0,
                "timestamp": "2025-04-20T14:00:00Z"
            }
        ]
        
        # Set up the mock to return our history
        mock_get_history.return_value = history
        
        # Call the function
        trust_score = calculate_trust_score(self.project_id, self.agent_name)
        
        # Check the result is moderate (around 0.5-0.7)
        self.assertGreaterEqual(trust_score, 0.5)
        self.assertLessEqual(trust_score, 0.7)
    
    @patch('orchestrator.modules.agent_performance_tracker.get_agent_performance_history')
    @patch('orchestrator.modules.agent_performance_tracker.get_current_trust_score')
    def test_get_agent_report_no_history(self, mock_get_score, mock_get_history):
        """Test getting agent report with no performance history."""
        # Set up the mocks
        mock_get_history.return_value = []
        mock_get_score.return_value = (0.5, "2025-04-20T15:00:00Z")
        
        # Call the function
        report = get_agent_report(self.project_id, self.agent_name)
        
        # Check the report
        self.assertEqual(report["agent"], self.agent_name)
        self.assertEqual(report["trust_score"], 0.5)
        self.assertEqual(report["loops_participated"], 0)
        self.assertEqual(report["validation_pass_rate"], 0.0)
        self.assertEqual(report["reroute_count"], 0)
        self.assertEqual(report["operator_rejections"], 0)
        self.assertEqual(report["files_created"], 0)
    
    @patch('orchestrator.modules.agent_performance_tracker.get_agent_performance_history')
    @patch('orchestrator.modules.agent_performance_tracker.get_current_trust_score')
    def test_get_agent_report_with_history(self, mock_get_score, mock_get_history):
        """Test getting agent report with performance history."""
        # Create a sample performance history
        history = [
            {
                "agent": self.agent_name,
                "loop_id": 30,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 1,
                "rejections": 0,
                "timestamp": "2025-04-20T12:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 31,
                "schema_passed": False,
                "was_rerouted": True,
                "operator_approved": False,
                "files_created": 0,
                "rejections": 2,
                "timestamp": "2025-04-20T13:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 32,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 1,
                "rejections": 0,
                "timestamp": "2025-04-20T14:00:00Z"
            }
        ]
        
        # Set up the mocks
        mock_get_history.return_value = history
        mock_get_score.return_value = (0.65, "2025-04-20T15:00:00Z")
        
        # Call the function
        report = get_agent_report(self.project_id, self.agent_name)
        
        # Check the report
        self.assertEqual(report["agent"], self.agent_name)
        self.assertEqual(report["trust_score"], 0.65)
        self.assertEqual(report["loops_participated"], 3)
        self.assertAlmostEqual(report["validation_pass_rate"], 2/3)
        self.assertEqual(report["reroute_count"], 1)
        self.assertEqual(report["operator_rejections"], 2)
        self.assertEqual(report["files_created"], 2)
        self.assertEqual(len(report["recent_performance"]), 3)
        self.assertIn("trend", report)
    
    @patch('orchestrator.modules.agent_performance_tracker.get_agent_performance_history')
    @patch('orchestrator.modules.agent_performance_tracker.get_current_trust_score')
    def test_get_agent_report_trend_improving(self, mock_get_score, mock_get_history):
        """Test getting agent report with improving trend."""
        # Create a sample performance history with improving trend
        history = [
            {
                "agent": self.agent_name,
                "loop_id": 30,
                "schema_passed": False,
                "was_rerouted": True,
                "operator_approved": False,
                "files_created": 0,
                "rejections": 2,
                "timestamp": "2025-04-20T12:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 31,
                "schema_passed": False,
                "was_rerouted": True,
                "operator_approved": False,
                "files_created": 1,
                "rejections": 1,
                "timestamp": "2025-04-20T13:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 32,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 1,
                "rejections": 0,
                "timestamp": "2025-04-20T14:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 33,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 2,
                "rejections": 0,
                "timestamp": "2025-04-20T15:00:00Z"
            }
        ]
        
        # Set up the mocks
        mock_get_history.return_value = history
        mock_get_score.return_value = (0.6, "2025-04-20T16:00:00Z")
        
        # Call the function
        report = get_agent_report(self.project_id, self.agent_name)
        
        # Check the trend
        self.assertEqual(report["trend"], "improving")
    
    @patch('orchestrator.modules.agent_performance_tracker.get_agent_performance_history')
    @patch('orchestrator.modules.agent_performance_tracker.get_current_trust_score')
    def test_get_agent_report_trend_declining(self, mock_get_score, mock_get_history):
        """Test getting agent report with declining trend."""
        # Create a sample performance history with declining trend
        history = [
            {
                "agent": self.agent_name,
                "loop_id": 30,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 1,
                "rejections": 0,
                "timestamp": "2025-04-20T12:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 31,
                "schema_passed": True,
                "was_rerouted": False,
                "operator_approved": True,
                "files_created": 1,
                "rejections": 0,
                "timestamp": "2025-04-20T13:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 32,
                "schema_passed": False,
                "was_rerouted": True,
                "operator_approved": False,
                "files_created": 0,
                "rejections": 2,
                "timestamp": "2025-04-20T14:00:00Z"
            },
            {
                "agent": self.agent_name,
                "loop_id": 33,
                "schema_passed": False,
                "was_rerouted": True,
                "operator_approved": False,
                "files_created": 0,
                "rejections": 1,
                "timestamp": "2025-04-20T15:00:00Z"
            }
        ]
        
        # Set up the mocks
        mock_get_history.return_value = history
        mock_get_score.return_value = (0.4, "2025-04-20T16:00:00Z")
        
        # Call the function
        report = get_agent_report(self.project_id, self.agent_name)
        
        # Check the trend
        self.assertEqual(report["trend"], "declining")
    
    def test_trust_score_bounds(self):
        """Test that trust score is always within bounds (0.0 - 1.0)."""
        # Create a patch for get_agent_performance_history to return custom history
        with patch('orchestrator.modules.agent_performance_tracker.get_agent_performance_history') as mock_get_history:
            # Test lower bound (extremely poor performance)
            history_poor = [
                {
                    "agent": self.agent_name,
                    "loop_id": 30,
                    "schema_passed": False,
                    "was_rerouted": True,
                    "operator_approved": False,
                    "files_created": 0,
                    "rejections": 100,  # Extremely high rejections
                    "timestamp": "2025-04-20T12:00:00Z"
                }
            ]
            mock_get_history.return_value = history_poor
            trust_score_poor = calculate_trust_score(self.project_id, self.agent_name)
            self.assertGreaterEqual(trust_score_poor, 0.0)
            
            # Test upper bound (extremely good performance)
            history_good = [
                {
                    "agent": self.agent_name,
                    "loop_id": 30,
                    "schema_passed": True,
                    "was_rerouted": False,
                    "operator_approved": True,
                    "files_created": 100,  # Extremely high file count
                    "rejections": 0,
                    "timestamp": "2025-04-20T12:00:00Z"
                }
            ]
            mock_get_history.return_value = history_good
            trust_score_good = calculate_trust_score(self.project_id, self.agent_name)
            self.assertLessEqual(trust_score_good, 1.0)


if __name__ == '__main__':
    unittest.main()
