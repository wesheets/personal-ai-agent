"""
Test Module for Operator Override Console

This module provides test cases for verifying the functionality of the
Operator Override Console implementation.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

# Mock PROJECT_MEMORY for testing
PROJECT_MEMORY = {}

# Import the functions to test (with mocked dependencies)
# In a real implementation, these would be imported from their modules
# For testing purposes, we'll define simplified versions here

def initialize_orchestrator_memory(project_id):
    """Initialize the orchestrator-related memory structures if they don't exist."""
    if project_id not in PROJECT_MEMORY:
        PROJECT_MEMORY[project_id] = {}
    
    memory = PROJECT_MEMORY[project_id]
    
    # Initialize required fields
    if "orchestrator_decisions" not in memory:
        memory["orchestrator_decisions"] = []
    
    if "completed_steps" not in memory:
        memory["completed_steps"] = []
    
    if "loop_count" not in memory:
        memory["loop_count"] = 1
    
    if "loop_complete" not in memory:
        memory["loop_complete"] = False
    
    if "next_recommended_agent" not in memory:
        memory["next_recommended_agent"] = None
    
    if "operator_actions" not in memory:
        memory["operator_actions"] = []


def set_next_agent(project_id, agent, reason):
    """Override the next recommended agent for a project."""
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    action = {
        "type": "override_next_agent",
        "agent": agent,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
        "loop_count": memory.get("loop_count", 1)
    }
    
    memory["next_recommended_agent"] = agent
    memory.setdefault("operator_actions", []).append(action)
    
    return action


def force_loop_complete(project_id, status):
    """Override the loop complete status for a project."""
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    action = {
        "type": "set_loop_complete",
        "value": status,
        "timestamp": datetime.utcnow().isoformat(),
        "loop_count": memory.get("loop_count", 1)
    }
    
    memory["loop_complete"] = status
    memory.setdefault("operator_actions", []).append(action)
    
    return action


def force_loop_skip(project_id, reason):
    """Force a loop skip by marking the current loop as complete and starting a new one."""
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    action = {
        "type": "force_loop_skip",
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
        "loop_count": memory.get("loop_count", 1)
    }
    
    memory.setdefault("operator_actions", []).append(action)
    memory["loop_complete"] = True
    
    # Simulate starting a new loop
    memory["loop_count"] += 1
    memory["completed_steps"] = []
    memory["loop_complete"] = False
    
    action["new_loop_count"] = memory["loop_count"]
    
    return action


def force_loop_reroute(project_id, agent, reason):
    """Force a loop reroute by setting the next recommended agent and creating a reroute trace."""
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    action = {
        "type": "force_loop_reroute",
        "agent": agent,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
        "loop_count": memory.get("loop_count", 1)
    }
    
    memory.setdefault("operator_actions", []).append(action)
    memory["next_recommended_agent"] = agent
    
    # Create reroute plan
    plan = {
        "status": "reroute",
        "trigger": "operator_override",
        "issues": {"operator_override": True},
        "proposed_next_agent": agent,
        "timestamp": datetime.utcnow().isoformat(),
        "loop_count": memory.get("loop_count", 1)
    }
    
    memory.setdefault("reroute_trace", []).append(plan)
    
    return action


def get_operator_actions(project_id, limit=None):
    """Retrieve the operator actions for a project."""
    initialize_orchestrator_memory(project_id)
    
    actions = PROJECT_MEMORY[project_id].get("operator_actions", [])
    
    if limit is not None:
        return actions[-limit:]
    
    return actions


class TestOperatorOverride(unittest.TestCase):
    """Test cases for the Operator Override Console functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear the mock PROJECT_MEMORY before each test
        global PROJECT_MEMORY
        PROJECT_MEMORY = {}
        
        # Set up a test project
        self.project_id = "test_project"
        initialize_orchestrator_memory(self.project_id)
    
    def test_set_next_agent(self):
        """Test setting the next recommended agent."""
        # Set next agent
        agent = "hal"
        reason = "manual override for testing"
        action = set_next_agent(self.project_id, agent, reason)
        
        # Verify action record
        self.assertEqual(action["type"], "override_next_agent")
        self.assertEqual(action["agent"], agent)
        self.assertEqual(action["reason"], reason)
        
        # Verify memory update
        self.assertEqual(PROJECT_MEMORY[self.project_id]["next_recommended_agent"], agent)
        
        # Verify action logged
        actions = PROJECT_MEMORY[self.project_id]["operator_actions"]
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0], action)
    
    def test_force_loop_complete(self):
        """Test forcing the loop complete status."""
        # Force loop complete
        status = True
        action = force_loop_complete(self.project_id, status)
        
        # Verify action record
        self.assertEqual(action["type"], "set_loop_complete")
        self.assertEqual(action["value"], status)
        
        # Verify memory update
        self.assertEqual(PROJECT_MEMORY[self.project_id]["loop_complete"], status)
        
        # Verify action logged
        actions = PROJECT_MEMORY[self.project_id]["operator_actions"]
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0], action)
        
        # Test setting to False
        status = False
        action = force_loop_complete(self.project_id, status)
        self.assertEqual(PROJECT_MEMORY[self.project_id]["loop_complete"], status)
        self.assertEqual(len(PROJECT_MEMORY[self.project_id]["operator_actions"]), 2)
    
    def test_force_loop_skip(self):
        """Test forcing a loop skip."""
        # Set initial state
        PROJECT_MEMORY[self.project_id]["loop_count"] = 2
        PROJECT_MEMORY[self.project_id]["completed_steps"] = ["hal", "nova"]
        
        # Force loop skip
        reason = "skipping problematic loop"
        action = force_loop_skip(self.project_id, reason)
        
        # Verify action record
        self.assertEqual(action["type"], "force_loop_skip")
        self.assertEqual(action["reason"], reason)
        self.assertEqual(action["new_loop_count"], 3)
        
        # Verify memory updates
        self.assertEqual(PROJECT_MEMORY[self.project_id]["loop_count"], 3)
        self.assertEqual(PROJECT_MEMORY[self.project_id]["completed_steps"], [])
        self.assertEqual(PROJECT_MEMORY[self.project_id]["loop_complete"], False)
        
        # Verify action logged
        actions = PROJECT_MEMORY[self.project_id]["operator_actions"]
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0], action)
    
    def test_force_loop_reroute(self):
        """Test forcing a loop reroute."""
        # Force loop reroute
        agent = "critic"
        reason = "manual intervention needed"
        action = force_loop_reroute(self.project_id, agent, reason)
        
        # Verify action record
        self.assertEqual(action["type"], "force_loop_reroute")
        self.assertEqual(action["agent"], agent)
        self.assertEqual(action["reason"], reason)
        
        # Verify memory updates
        self.assertEqual(PROJECT_MEMORY[self.project_id]["next_recommended_agent"], agent)
        
        # Verify action logged
        actions = PROJECT_MEMORY[self.project_id]["operator_actions"]
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0], action)
        
        # Verify reroute trace
        reroute_trace = PROJECT_MEMORY[self.project_id]["reroute_trace"]
        self.assertEqual(len(reroute_trace), 1)
        self.assertEqual(reroute_trace[0]["trigger"], "operator_override")
        self.assertEqual(reroute_trace[0]["proposed_next_agent"], agent)
    
    def test_get_operator_actions(self):
        """Test retrieving operator actions."""
        # Create multiple actions
        set_next_agent(self.project_id, "hal", "first override")
        force_loop_complete(self.project_id, True)
        force_loop_skip(self.project_id, "skip loop")
        
        # Get all actions
        actions = get_operator_actions(self.project_id)
        
        # Verify actions
        self.assertEqual(len(actions), 3)
        self.assertEqual(actions[0]["type"], "override_next_agent")
        self.assertEqual(actions[1]["type"], "set_loop_complete")
        self.assertEqual(actions[2]["type"], "force_loop_skip")
        
        # Test with limit
        limited_actions = get_operator_actions(self.project_id, 2)
        self.assertEqual(len(limited_actions), 2)
        self.assertEqual(limited_actions[0]["type"], "set_loop_complete")
        self.assertEqual(limited_actions[1]["type"], "force_loop_skip")
    
    def test_multiple_overrides(self):
        """Test multiple overrides in sequence."""
        # Perform multiple overrides
        set_next_agent(self.project_id, "hal", "initial agent")
        force_loop_reroute(self.project_id, "nova", "change direction")
        force_loop_complete(self.project_id, True)
        
        # Verify final state
        self.assertEqual(PROJECT_MEMORY[self.project_id]["next_recommended_agent"], "nova")
        self.assertEqual(PROJECT_MEMORY[self.project_id]["loop_complete"], True)
        
        # Verify all actions logged
        actions = PROJECT_MEMORY[self.project_id]["operator_actions"]
        self.assertEqual(len(actions), 3)
        
        # Verify reroute trace
        reroute_trace = PROJECT_MEMORY[self.project_id]["reroute_trace"]
        self.assertEqual(len(reroute_trace), 1)


if __name__ == "__main__":
    unittest.main()
