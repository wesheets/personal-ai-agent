import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the rebuilder module
from app.plugins.agents.rebuilder.rebuilder import (
    run_agent,
    scan_project_manifest,
    detect_belief_mismatches,
    detect_failing_agents,
    detect_ci_drift,
    calculate_stability_score,
    determine_rebuild_needs,
    generate_recommendations,
    trigger_rebuild,
    update_project_manifest,
    log_rebuild_events
)

class TestRebuilderAgent(unittest.TestCase):
    """Test cases for the Rebuilder Agent."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test manifests
        self.test_dir = tempfile.mkdtemp()
        self.original_manifest_dir = os.environ.get('PROJECT_MANIFEST_DIR')
        os.environ['PROJECT_MANIFEST_DIR'] = self.test_dir
        
        # Create a sample project manifest
        self.project_id = "test-project"
        self.manifest_path = os.path.join(self.test_dir, f"{self.project_id}.json")
        self.sample_manifest = {
            "project_id": self.project_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "modules": {
                "module1": {
                    "module_name": "module1",
                    "loop_id_created": "loop-123",
                    "agent_created_by": "agent-456",
                    "belief_version": "1.0.0",
                    "last_audited_loop_id": "loop-789",
                    "last_ci_result": {
                        "status": "passed",
                        "ci_score": 0.95,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "needs_rebuild": False
                },
                "module2": {
                    "module_name": "module2",
                    "loop_id_created": "loop-234",
                    "agent_created_by": "agent-567",
                    "belief_version": "1.0.0",
                    "last_audited_loop_id": "loop-890",
                    "last_ci_result": {
                        "status": "passed",
                        "ci_score": 0.85,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "needs_rebuild": False
                }
            }
        }
        
        with open(self.manifest_path, 'w') as f:
            json.dump(self.sample_manifest, f, indent=2)

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        
        # Restore original environment variable
        if self.original_manifest_dir:
            os.environ['PROJECT_MANIFEST_DIR'] = self.original_manifest_dir
        else:
            del os.environ['PROJECT_MANIFEST_DIR']

    def test_scan_project_manifest_success(self):
        """Test scanning project manifest with no issues."""
        manifest_data, issues = scan_project_manifest(self.project_id)
        
        self.assertEqual(manifest_data["project_id"], self.project_id)
        self.assertEqual(len(manifest_data["modules"]), 2)
        self.assertEqual(len(issues), 0)

    def test_scan_project_manifest_with_issues(self):
        """Test scanning project manifest with issues."""
        # Create a manifest with issues
        manifest_with_issues = self.sample_manifest.copy()
        manifest_with_issues["modules"]["module3"] = {
            "module_name": "module3",
            "loop_id_created": "loop-345",
            "agent_created_by": "agent-678",
            # Missing belief_version
            "last_audited_loop_id": "loop-901",
            "last_ci_result": {
                "status": "failed",
                "ci_score": 0.3,
                "timestamp": datetime.utcnow().isoformat(),
                "failure_reason": "Test failures"
            },
            "needs_rebuild": True
        }
        
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest_with_issues, f, indent=2)
        
        manifest_data, issues = scan_project_manifest(self.project_id)
        
        self.assertEqual(manifest_data["project_id"], self.project_id)
        self.assertEqual(len(manifest_data["modules"]), 3)
        self.assertGreater(len(issues), 0)
        
        # Check for specific issues
        module_needs_rebuild_issues = [issue for issue in issues if issue["type"] == "module_needs_rebuild"]
        failed_ci_issues = [issue for issue in issues if issue["type"] == "failed_ci"]
        missing_belief_version_issues = [issue for issue in issues if issue["type"] == "missing_belief_version"]
        
        self.assertEqual(len(module_needs_rebuild_issues), 1)
        self.assertEqual(len(failed_ci_issues), 1)
        self.assertEqual(len(missing_belief_version_issues), 1)

    def test_detect_belief_mismatches(self):
        """Test detecting belief mismatches."""
        # Create a manifest with belief mismatches
        manifest_with_mismatches = self.sample_manifest.copy()
        manifest_with_mismatches["modules"]["module2"]["belief_version"] = "2.0.0"
        manifest_with_mismatches["modules"]["module3"] = {
            "module_name": "module3",
            "loop_id_created": "loop-345",
            "agent_created_by": "agent-678",
            # Missing belief_version
            "last_audited_loop_id": "loop-901",
            "last_ci_result": {
                "status": "passed",
                "ci_score": 0.9,
                "timestamp": datetime.utcnow().isoformat()
            },
            "needs_rebuild": False
        }
        
        issues = detect_belief_mismatches(self.project_id, manifest_with_mismatches)
        
        self.assertGreater(len(issues), 0)
        
        # Check for specific issues
        multiple_belief_versions_issues = [issue for issue in issues if issue["type"] == "multiple_belief_versions"]
        missing_belief_versions_issues = [issue for issue in issues if issue["type"] == "missing_belief_versions"]
        
        self.assertEqual(len(multiple_belief_versions_issues), 1)
        self.assertEqual(len(missing_belief_versions_issues), 1)

    def test_detect_failing_agents(self):
        """Test detecting failing agents."""
        # Create a manifest with failing agents
        manifest_with_failing_agents = self.sample_manifest.copy()
        manifest_with_failing_agents["modules"]["module2"]["agent_type"] = "plugin"
        manifest_with_failing_agents["modules"]["module2"]["status"] = "failing"
        manifest_with_failing_agents["modules"]["module2"]["last_error"] = "Agent crashed"
        
        issues = detect_failing_agents(self.project_id, manifest_with_failing_agents)
        
        self.assertGreater(len(issues), 0)
        
        # Check for specific issues
        failing_agent_issues = [issue for issue in issues if issue["type"] == "failing_agent"]
        
        self.assertEqual(len(failing_agent_issues), 1)
        self.assertEqual(failing_agent_issues[0]["module"], "module2")
        self.assertEqual(failing_agent_issues[0]["last_error"], "Agent crashed")

    def test_detect_ci_drift(self):
        """Test detecting CI drift."""
        # Create a manifest with CI drift
        manifest_with_ci_drift = self.sample_manifest.copy()
        manifest_with_ci_drift["modules"]["module2"]["last_ci_result"]["status"] = "failed"
        manifest_with_ci_drift["modules"]["module2"]["last_ci_result"]["ci_score"] = 0.3
        manifest_with_ci_drift["modules"]["module2"]["last_ci_result"]["failure_reason"] = "Test failures"
        
        issues = detect_ci_drift(self.project_id, manifest_with_ci_drift)
        
        self.assertGreater(len(issues), 0)
        
        # Check for specific issues
        failed_ci_issues = [issue for issue in issues if issue["type"] == "failed_ci"]
        
        self.assertEqual(len(failed_ci_issues), 1)
        self.assertEqual(failed_ci_issues[0]["module"], "module2")
        self.assertEqual(failed_ci_issues[0]["failure_reason"], "Test failures")

    def test_calculate_stability_score(self):
        """Test calculating stability score."""
        # Create sample issues
        manifest_issues = [
            {"type": "module_needs_rebuild", "severity": "high", "module": "module1"}
        ]
        belief_issues = [
            {"type": "multiple_belief_versions", "severity": "high", "versions": {"1.0.0": ["module1"], "2.0.0": ["module2"]}}
        ]
        agent_issues = [
            {"type": "failing_agent", "severity": "high", "module": "module2", "last_error": "Agent crashed"}
        ]
        ci_issues = [
            {"type": "failed_ci", "severity": "high", "module": "module2", "failure_reason": "Test failures"}
        ]
        
        # Test with different orchestrator modes
        for mode in ["FAST", "BALANCED", "THOROUGH", "RESEARCH"]:
            score = calculate_stability_score(
                manifest_issues, belief_issues, agent_issues, ci_issues, mode
            )
            
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_determine_rebuild_needs(self):
        """Test determining rebuild needs."""
        # Create sample issues
        manifest_issues = [
            {"type": "module_needs_rebuild", "severity": "high", "module": "module1", "message": "Module needs rebuild"}
        ]
        belief_issues = [
            {"type": "multiple_belief_versions", "severity": "high", "versions": {"1.0.0": ["module1"], "2.0.0": ["module2"]}, "message": "Multiple belief versions"}
        ]
        agent_issues = [
            {"type": "failing_agent", "severity": "high", "module": "module2", "last_error": "Agent crashed", "message": "Agent is failing"}
        ]
        ci_issues = [
            {"type": "failed_ci", "severity": "high", "module": "module2", "failure_reason": "Test failures", "message": "CI tests failed"}
        ]
        
        # Test with low stability score (should need rebuild)
        needs_rebuild, rebuild_events = determine_rebuild_needs(
            0.3, manifest_issues, belief_issues, agent_issues, ci_issues, "BALANCED"
        )
        
        self.assertTrue(needs_rebuild)
        self.assertGreater(len(rebuild_events), 0)
        
        # Test with high stability score (should not need rebuild)
        needs_rebuild, rebuild_events = determine_rebuild_needs(
            0.9, manifest_issues, belief_issues, agent_issues, ci_issues, "BALANCED"
        )
        
        self.assertFalse(needs_rebuild)
        self.assertEqual(len(rebuild_events), 0)

    def test_generate_recommendations(self):
        """Test generating recommendations."""
        # Create sample issues
        manifest_issues = [
            {"type": "module_needs_rebuild", "severity": "high", "module": "module1", "message": "Module needs rebuild"}
        ]
        belief_issues = [
            {"type": "multiple_belief_versions", "severity": "high", "versions": {"1.0.0": ["module1"], "2.0.0": ["module2"]}, "message": "Multiple belief versions"}
        ]
        agent_issues = [
            {"type": "failing_agent", "severity": "high", "module": "module2", "last_error": "Agent crashed", "message": "Agent is failing"}
        ]
        ci_issues = [
            {"type": "failed_ci", "severity": "high", "module": "module2", "failure_reason": "Test failures", "message": "CI tests failed"}
        ]
        
        # Test with low stability score
        recommendations = generate_recommendations(
            0.3, manifest_issues, belief_issues, agent_issues, ci_issues, "BALANCED"
        )
        
        self.assertGreater(len(recommendations), 0)
        
        # Check for specific recommendations
        critical_stability_recommendations = [rec for rec in recommendations if rec["type"] == "critical_stability"]
        rebuild_module_recommendations = [rec for rec in recommendations if rec["type"] == "rebuild_module"]
        align_belief_versions_recommendations = [rec for rec in recommendations if rec["type"] == "align_belief_versions"]
        fix_agent_recommendations = [rec for rec in recommendations if rec["type"] == "fix_agent"]
        fix_ci_recommendations = [rec for rec in recommendations if rec["type"] == "fix_ci"]
        
        self.assertEqual(len(critical_stability_recommendations), 1)
        self.assertEqual(len(rebuild_module_recommendations), 1)
        self.assertEqual(len(align_belief_versions_recommendations), 1)
        self.assertEqual(len(fix_agent_recommendations), 1)
        self.assertEqual(len(fix_ci_recommendations), 1)

    @patch('app.plugins.agents.rebuilder.rebuilder.logger')
    def test_trigger_rebuild(self, mock_logger):
        """Test triggering rebuild."""
        # Create sample rebuild events
        rebuild_events = [
            {
                "type": "low_stability",
                "timestamp": datetime.utcnow().isoformat(),
                "stability_score": 0.3,
                "threshold": 0.6,
                "orchestrator_mode": "BALANCED",
                "message": "System stability score (0.30) is below threshold (0.60)"
            }
        ]
        
        result = trigger_rebuild(self.project_id, rebuild_events, "BALANCED")
        
        self.assertIn("rebuild_id", result)
        self.assertEqual(result["project_id"], self.project_id)
        self.assertEqual(result["orchestrator_mode"], "BALANCED")
        self.assertEqual(result["status"], "triggered")
        self.assertEqual(len(result["events"]), 1)

    def test_update_project_manifest(self):
        """Test updating project manifest."""
        # Create sample result
        result = {
            "agent_id": "rebuilder",
            "timestamp": datetime.utcnow().isoformat(),
            "project_id": self.project_id,
            "loop_id": "loop-123",
            "stability_score": 0.8,
            "needs_rebuild": False,
            "rebuild_events": [],
            "recommendations": [
                {
                    "type": "good_stability",
                    "priority": "info",
                    "message": "Good stability score (0.80). No action needed.",
                    "action": "none"
                }
            ]
        }
        
        success = update_project_manifest(self.project_id, result)
        
        self.assertTrue(success)
        
        # Check if manifest was updated
        with open(self.manifest_path, 'r') as f:
            updated_manifest = json.load(f)
        
        self.assertEqual(updated_manifest["last_stability_score"], 0.8)
        self.assertIn("last_rebuild_check", updated_manifest)
        self.assertEqual(updated_manifest["last_rebuild_check"]["needs_rebuild"], False)

    @patch('app.plugins.agents.rebuilder.rebuilder.logger')
    def test_log_rebuild_events(self, mock_logger):
        """Test logging rebuild events."""
        # Create sample result
        result = {
            "agent_id": "rebuilder",
            "timestamp": datetime.utcnow().isoformat(),
            "project_id": self.project_id,
            "loop_id": "loop-123",
            "stability_score": 0.3,
            "needs_rebuild": True,
            "rebuild_events": [
                {
                    "type": "low_stability",
                    "timestamp": datetime.utcnow().isoformat(),
                    "stability_score": 0.3,
                    "threshold": 0.6,
                    "orchestrator_mode": "BALANCED",
                    "message": "System stability score (0.30) is below threshold (0.60)"
                }
            ],
            "recommendations": [
                {
                    "type": "critical_stability",
                    "priority": "high",
                    "message": "Critical stability issues detected (score: 0.30). Immediate rebuild recommended.",
                    "action": "rebuild_system"
                }
            ]
        }
        
        success = log_rebuild_events(self.project_id, "loop-123", result)
        
        self.assertTrue(success)
        self.assertTrue(mock_logger.info.called)

    @patch('app.plugins.agents.rebuilder.rebuilder.scan_project_manifest')
    @patch('app.plugins.agents.rebuilder.rebuilder.detect_belief_mismatches')
    @patch('app.plugins.agents.rebuilder.rebuilder.detect_failing_agents')
    @patch('app.plugins.agents.rebuilder.rebuilder.detect_ci_drift')
    @patch('app.plugins.agents.rebuilder.rebuilder.calculate_stability_score')
    @patch('app.plugins.agents.rebuilder.rebuilder.determine_rebuild_needs')
    @patch('app.plugins.agents.rebuilder.rebuilder.generate_recommendations')
    @patch('app.plugins.agents.rebuilder.rebuilder.trigger_rebuild')
    @patch('app.plugins.agents.rebuilder.rebuilder.update_project_manifest')
    @patch('app.plugins.agents.rebuilder.rebuilder.log_rebuild_events')
    def test_run_agent(
        self, mock_log_rebuild_events, mock_update_project_manifest, 
        mock_trigger_rebuild, mock_generate_recommendations, 
        mock_determine_rebuild_needs, mock_calculate_stability_score,
        mock_detect_ci_drift, mock_detect_failing_agents,
        mock_detect_belief_mismatches, mock_scan_project_manifest
    ):
        """Test running the agent."""
        # Set up mocks
        mock_scan_project_manifest.return_value = (self.sample_manifest, [])
        mock_detect_belief_mismatches.return_value = []
        mock_detect_failing_agents.return_value = []
        mock_detect_ci_drift.return_value = []
        mock_calculate_stability_score.return_value = 0.9
        mock_determine_rebuild_needs.return_value = (False, [])
        mock_generate_recommendations.return_value = [
            {
                "type": "good_stability",
                "priority": "info",
                "message": "Good stability score (0.90). No action needed.",
                "action": "none"
            }
        ]
        mock_update_project_manifest.return_value = True
        mock_log_rebuild_events.return_value = True
        
        # Create context
        context = {
            "project_id": self.project_id,
            "orchestrator_mode": "BALANCED",
            "loop_id": "loop-123"
        }
        
        # Run agent
        result = run_agent(context)
        
        # Check result
        self.assertEqual(result["agent_id"], "rebuilder")
        self.assertEqual(result["project_id"], self.project_id)
        self.assertEqual(result["loop_id"], "loop-123")
        self.assertEqual(result["stability_score"], 0.9)
        self.assertEqual(result["needs_rebuild"], False)
        
        # Verify mocks were called
        mock_scan_project_manifest.assert_called_once_with(self.project_id)
        mock_detect_belief_mismatches.assert_called_once()
        mock_detect_failing_agents.assert_called_once()
        mock_detect_ci_drift.assert_called_once()
        mock_calculate_stability_score.assert_called_once()
        mock_determine_rebuild_needs.assert_called_once()
        mock_generate_recommendations.assert_called_once()
        mock_update_project_manifest.assert_called_once()
        mock_log_rebuild_events.assert_called_once()
        
        # Trigger rebuild should not be called when no rebuild is needed
        mock_trigger_rebuild.assert_not_called()

if __name__ == '__main__':
    unittest.main()
