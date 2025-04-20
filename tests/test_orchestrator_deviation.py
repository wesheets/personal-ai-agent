"""
Test Module for Orchestrator Deviation Detection and Reroute Logic

This module provides test cases for verifying the functionality of the
Orchestrator Deviation Detection and Mid-Loop Reroute Logic implementation.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

# Mock PROJECT_MEMORY for testing
PROJECT_MEMORY = {}

# Mock SCHEMA_REGISTRY for testing
SCHEMA_REGISTRY = {
    "agents": {
        "hal": {
            "role": "initial builder",
            "dependencies": [],
            "produces": ["README.md", "requirements.txt"],
            "unlocks": ["nova"]
        },
        "nova": {
            "role": "logic writer",
            "dependencies": ["hal"],
            "produces": ["api_routes", "logic_modules"],
            "unlocks": ["critic"]
        },
        "critic": {
            "role": "code reviewer",
            "dependencies": ["nova"],
            "produces": ["review_report"],
            "unlocks": []
        }
    },
    "loop": {
        "required_agents": ["hal", "nova", "critic"],
        "max_loops": 5,
        "exit_conditions": ["loop_complete == true", "loop_count >= max_loops"]
    }
}

# Import the functions to test (with mocked dependencies)
# In a real implementation, these would be imported from their modules
# For testing purposes, we'll define simplified versions here

def initialize_orchestrator_memory(project_id: str) -> None:
    """Initialize the orchestrator-related memory structures if they don't exist."""
    if project_id not in PROJECT_MEMORY:
        PROJECT_MEMORY[project_id] = {}
    
    memory = PROJECT_MEMORY[project_id]
    
    # Initialize orchestrator decisions array if it doesn't exist
    if "orchestrator_decisions" not in memory:
        memory["orchestrator_decisions"] = []
    
    # Initialize other required fields with defaults if they don't exist
    if "completed_steps" not in memory:
        memory["completed_steps"] = []
    
    if "loop_count" not in memory:
        memory["loop_count"] = 1
    
    if "loop_complete" not in memory:
        memory["loop_complete"] = False
    
    if "next_recommended_agent" not in memory:
        memory["next_recommended_agent"] = None
    
    if "autospawn" not in memory:
        memory["autospawn"] = False
    
    # Initialize reflections array if it doesn't exist
    if "reflections" not in memory:
        memory["reflections"] = []
    
    # Initialize deviation logs array if it doesn't exist
    if "deviation_logs" not in memory:
        memory["deviation_logs"] = []
    
    # Initialize reroute trace array if it doesn't exist
    if "reroute_trace" not in memory:
        memory["reroute_trace"] = []


def detect_deviation(project_id: str) -> Dict[str, Any]:
    """
    Detect deviations in the project state that might require intervention.
    
    Checks for:
    - Missing required files (based on agent output expectations)
    - Incomplete agent steps
    - Reflection score below threshold
    - Drift logs present since last loop
    - Invalid schema state
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Access project memory
    memory = PROJECT_MEMORY[project_id]
    completed = memory.get("completed_steps", [])
    required = SCHEMA_REGISTRY.get("loop", {}).get("required_agents", [])
    
    # Check for missing agents
    missing_agents = list(set(required) - set(completed))
    
    # Check for drift logs
    drift_logs = memory.get("drift_logs", [])[-1:] if memory.get("drift_logs") else []
    
    # Check reflection confidence
    reflection = memory.get("last_reflection", {})
    
    # Initialize issues dict
    issues = {}
    
    # Add issues if found
    if missing_agents:
        issues["missing_agents"] = missing_agents
    
    if drift_logs:
        issues["drift_detected"] = drift_logs
    
    if reflection.get("confidence", 1.0) < 0.5:
        issues["low_confidence"] = reflection
    
    # Check for missing required files
    file_tree = memory.get("file_tree", {})
    files = file_tree.get("files", [])
    
    # Collect expected files from completed agents
    expected_files = []
    for agent_name in completed:
        agent_def = SCHEMA_REGISTRY.get("agents", {}).get(agent_name, {})
        expected_files.extend(agent_def.get("produces", []))
    
    # Check for missing files
    missing_files = [file for file in expected_files if file not in files]
    if missing_files:
        issues["missing_files"] = missing_files
    
    # Log the deviation check
    if issues:
        # Add to deviation logs
        deviation_log = {
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat(),
            "loop_count": memory.get("loop_count", 1)
        }
        memory.setdefault("deviation_logs", []).append(deviation_log)
    
    return issues


def reroute_loop(project_id: str, deviation_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a reroute plan based on detected deviations.
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Access project memory
    memory = PROJECT_MEMORY[project_id]
    
    # Determine appropriate reroute action based on issues
    proposed_next_agent = "critic"  # Default to critic for most issues
    
    # If missing files is the only issue, try to regenerate with the agent that produces them
    if set(deviation_report.keys()) == {"missing_files"} and not memory.get("reroute_attempts", 0):
        missing_files = deviation_report["missing_files"]
        
        # Find agent that produces the missing files
        for agent_name, agent_def in SCHEMA_REGISTRY.get("agents", {}).items():
            produces = agent_def.get("produces", [])
            if any(file in produces for file in missing_files):
                proposed_next_agent = agent_name
                break
    
    # Create reroute plan
    plan = {
        "status": "reroute",
        "trigger": "deviation_detected",
        "issues": deviation_report,
        "proposed_next_agent": proposed_next_agent,
        "timestamp": datetime.utcnow().isoformat(),
        "loop_count": memory.get("loop_count", 1)
    }
    
    # Log the reroute plan
    memory.setdefault("reroute_trace", []).append(plan)
    
    # Update next recommended agent
    memory["next_recommended_agent"] = proposed_next_agent
    
    # Track reroute attempts
    memory["reroute_attempts"] = memory.get("reroute_attempts", 0) + 1
    
    return plan


def get_deviation_logs(project_id: str, limit=None) -> List[Dict[str, Any]]:
    """Retrieve the deviation logs for a project."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    logs = PROJECT_MEMORY[project_id].get("deviation_logs", [])
    
    if limit is not None:
        return logs[-limit:]
    
    return logs


def get_reroute_trace(project_id: str, limit=None) -> List[Dict[str, Any]]:
    """Retrieve the reroute trace for a project."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    traces = PROJECT_MEMORY[project_id].get("reroute_trace", [])
    
    if limit is not None:
        return traces[-limit:]
    
    return traces


class TestOrchestratorDeviation(unittest.TestCase):
    """Test cases for the Orchestrator Deviation Detection and Reroute Logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear the mock PROJECT_MEMORY before each test
        global PROJECT_MEMORY
        PROJECT_MEMORY = {}
        
        # Set up a test project
        self.project_id = "test_project"
        initialize_orchestrator_memory(self.project_id)
        
        # Set up some test data
        PROJECT_MEMORY[self.project_id]["completed_steps"] = ["hal"]
        PROJECT_MEMORY[self.project_id]["file_tree"] = {"files": ["README.md"]}
        PROJECT_MEMORY[self.project_id]["last_reflection"] = {
            "goal": "Test project",
            "summary": "Loop 1 completed",
            "confidence": 0.9,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def test_detect_deviation_no_issues(self):
        """Test that no issues are detected when everything is normal."""
        # Set up a normal state
        PROJECT_MEMORY[self.project_id]["completed_steps"] = ["hal", "nova", "critic"]
        PROJECT_MEMORY[self.project_id]["file_tree"] = {
            "files": ["README.md", "requirements.txt", "api_routes", "logic_modules", "review_report"]
        }
        
        # Detect deviations
        issues = detect_deviation(self.project_id)
        
        # Verify no issues detected
        self.assertEqual(issues, {})
        
        # Verify no deviation logs created
        deviation_logs = PROJECT_MEMORY[self.project_id].get("deviation_logs", [])
        self.assertEqual(len(deviation_logs), 0)
    
    def test_detect_deviation_missing_agents(self):
        """Test detection of missing required agents."""
        # Set up a state with missing agents
        PROJECT_MEMORY[self.project_id]["completed_steps"] = ["hal"]  # Missing nova and critic
        
        # Detect deviations
        issues = detect_deviation(self.project_id)
        
        # Verify missing agents detected
        self.assertIn("missing_agents", issues)
        self.assertIn("nova", issues["missing_agents"])
        self.assertIn("critic", issues["missing_agents"])
        
        # Verify deviation log created
        deviation_logs = PROJECT_MEMORY[self.project_id].get("deviation_logs", [])
        self.assertEqual(len(deviation_logs), 1)
        self.assertIn("missing_agents", deviation_logs[0]["issues"])
    
    def test_detect_deviation_missing_files(self):
        """Test detection of missing required files."""
        # Set up a state with missing files
        PROJECT_MEMORY[self.project_id]["completed_steps"] = ["hal", "nova"]
        PROJECT_MEMORY[self.project_id]["file_tree"] = {
            "files": ["README.md"]  # Missing requirements.txt, api_routes, logic_modules
        }
        
        # Detect deviations
        issues = detect_deviation(self.project_id)
        
        # Verify missing files detected
        self.assertIn("missing_files", issues)
        self.assertIn("requirements.txt", issues["missing_files"])
        self.assertIn("api_routes", issues["missing_files"])
        self.assertIn("logic_modules", issues["missing_files"])
        
        # Verify deviation log created
        deviation_logs = PROJECT_MEMORY[self.project_id].get("deviation_logs", [])
        self.assertEqual(len(deviation_logs), 1)
        self.assertIn("missing_files", deviation_logs[0]["issues"])
    
    def test_detect_deviation_low_confidence(self):
        """Test detection of low reflection confidence."""
        # Set up a state with low confidence reflection
        PROJECT_MEMORY[self.project_id]["last_reflection"] = {
            "goal": "Test project",
            "summary": "Loop 1 completed with issues",
            "confidence": 0.4,  # Below 0.5 threshold
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Detect deviations
        issues = detect_deviation(self.project_id)
        
        # Verify low confidence detected
        self.assertIn("low_confidence", issues)
        self.assertEqual(issues["low_confidence"]["confidence"], 0.4)
        
        # Verify deviation log created
        deviation_logs = PROJECT_MEMORY[self.project_id].get("deviation_logs", [])
        self.assertEqual(len(deviation_logs), 1)
        self.assertIn("low_confidence", deviation_logs[0]["issues"])
    
    def test_detect_deviation_drift_logs(self):
        """Test detection of drift logs."""
        # Set up a state with drift logs
        PROJECT_MEMORY[self.project_id]["drift_logs"] = [
            {
                "type": "schema_drift",
                "details": "Unexpected field in memory",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        # Detect deviations
        issues = detect_deviation(self.project_id)
        
        # Verify drift detected
        self.assertIn("drift_detected", issues)
        self.assertEqual(len(issues["drift_detected"]), 1)
        self.assertEqual(issues["drift_detected"][0]["type"], "schema_drift")
        
        # Verify deviation log created
        deviation_logs = PROJECT_MEMORY[self.project_id].get("deviation_logs", [])
        self.assertEqual(len(deviation_logs), 1)
        self.assertIn("drift_detected", deviation_logs[0]["issues"])
    
    def test_reroute_loop_default(self):
        """Test default reroute to critic."""
        # Set up a state with multiple issues
        issues = {
            "missing_agents": ["nova", "critic"],
            "low_confidence": {"confidence": 0.4}
        }
        
        # Create reroute plan
        plan = reroute_loop(self.project_id, issues)
        
        # Verify plan structure
        self.assertEqual(plan["status"], "reroute")
        self.assertEqual(plan["trigger"], "deviation_detected")
        self.assertEqual(plan["issues"], issues)
        self.assertEqual(plan["proposed_next_agent"], "critic")
        
        # Verify reroute trace created
        reroute_trace = PROJECT_MEMORY[self.project_id].get("reroute_trace", [])
        self.assertEqual(len(reroute_trace), 1)
        self.assertEqual(reroute_trace[0], plan)
        
        # Verify next_recommended_agent updated
        self.assertEqual(PROJECT_MEMORY[self.project_id]["next_recommended_agent"], "critic")
        
        # Verify reroute_attempts incremented
        self.assertEqual(PROJECT_MEMORY[self.project_id]["reroute_attempts"], 1)
    
    def test_reroute_loop_missing_files(self):
        """Test reroute for missing files to the agent that produces them."""
        # Set up a state with only missing files
        issues = {
            "missing_files": ["requirements.txt"]
        }
        
        # Create reroute plan
        plan = reroute_loop(self.project_id, issues)
        
        # Verify plan routes to hal (which produces requirements.txt)
        self.assertEqual(plan["proposed_next_agent"], "hal")
        
        # Verify next_recommended_agent updated
        self.assertEqual(PROJECT_MEMORY[self.project_id]["next_recommended_agent"], "hal")
    
    def test_reroute_loop_multiple_attempts(self):
        """Test that after multiple attempts, always routes to critic."""
        # Set up a state with only missing files but multiple attempts
        issues = {
            "missing_files": ["requirements.txt"]
        }
        PROJECT_MEMORY[self.project_id]["reroute_attempts"] = 1
        
        # Create reroute plan
        plan = reroute_loop(self.project_id, issues)
        
        # Verify plan routes to critic (not hal) due to previous attempts
        self.assertEqual(plan["proposed_next_agent"], "critic")
        
        # Verify next_recommended_agent updated
        self.assertEqual(PROJECT_MEMORY[self.project_id]["next_recommended_agent"], "critic")
        
        # Verify reroute_attempts incremented
        self.assertEqual(PROJECT_MEMORY[self.project_id]["reroute_attempts"], 2)
    
    def test_get_deviation_logs(self):
        """Test retrieving deviation logs."""
        # Create multiple deviation logs
        PROJECT_MEMORY[self.project_id]["deviation_logs"] = [
            {
                "issues": {"missing_agents": ["nova"]},
                "timestamp": "2025-04-20T10:00:00Z",
                "loop_count": 1
            },
            {
                "issues": {"missing_files": ["api_routes"]},
                "timestamp": "2025-04-20T11:00:00Z",
                "loop_count": 2
            }
        ]
        
        # Get all logs
        logs = get_deviation_logs(self.project_id)
        
        # Verify logs
        self.assertEqual(len(logs), 2)
        self.assertIn("missing_agents", logs[0]["issues"])
        self.assertIn("missing_files", logs[1]["issues"])
        
        # Test with limit
        limited_logs = get_deviation_logs(self.project_id, 1)
        self.assertEqual(len(limited_logs), 1)
        self.assertIn("missing_files", limited_logs[0]["issues"])
    
    def test_get_reroute_trace(self):
        """Test retrieving reroute trace."""
        # Create multiple reroute traces
        PROJECT_MEMORY[self.project_id]["reroute_trace"] = [
            {
                "status": "reroute",
                "trigger": "deviation_detected",
                "issues": {"missing_agents": ["nova"]},
                "proposed_next_agent": "hal",
                "timestamp": "2025-04-20T10:00:00Z",
                "loop_count": 1
            },
            {
                "status": "reroute",
                "trigger": "deviation_detected",
                "issues": {"missing_files": ["api_routes"]},
                "proposed_next_agent": "nova",
                "timestamp": "2025-04-20T11:00:00Z",
                "loop_count": 2
            }
        ]
        
        # Get all traces
        traces = get_reroute_trace(self.project_id)
        
        # Verify traces
        self.assertEqual(len(traces), 2)
        self.assertEqual(traces[0]["proposed_next_agent"], "hal")
        self.assertEqual(traces[1]["proposed_next_agent"], "nova")
        
        # Test with limit
        limited_traces = get_reroute_trace(self.project_id, 1)
        self.assertEqual(len(limited_traces), 1)
        self.assertEqual(limited_traces[0]["proposed_next_agent"], "nova")


if __name__ == "__main__":
    unittest.main()
