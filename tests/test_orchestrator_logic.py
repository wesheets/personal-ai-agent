"""
Test Module for Orchestrator Logic

This module provides test cases for verifying the functionality of the
Orchestrator Next Agent Planner implementation.
"""

import unittest
from datetime import datetime
from typing import Dict, Any, List
import logging

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
            "role": "review + logic auditor",
            "dependencies": ["nova"],
            "produces": ["feedback_log", "next_agent_recommendation"],
            "unlocks": ["ash", "orchestrator"]
        },
        "ash": {
            "role": "documenter",
            "dependencies": ["critic"],
            "produces": ["README updates", "documentation"],
            "unlocks": ["sage"]
        },
        "sage": {
            "role": "reflection + loop closer",
            "dependencies": ["ash"],
            "produces": ["summary", "final reflections"],
            "unlocks": ["hal"]
        }
    },
    "loop": {
        "required_agents": ["hal", "nova", "critic", "ash", "sage"],
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


def log_orchestrator_decision(
    project_id: str, 
    last_agent: str, 
    next_agent: str, 
    reason: str
) -> Dict[str, Any]:
    """Log an orchestrator decision to the project memory."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Get the current loop count
    memory = PROJECT_MEMORY[project_id]
    loop_count = memory.get("loop_count", 1)
    
    # Create the decision record
    decision = {
        "loop_count": loop_count,
        "last_agent": last_agent,
        "next_agent": next_agent,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Log the decision
    memory["orchestrator_decisions"].append(decision)
    
    # Update the next recommended agent
    memory["next_recommended_agent"] = next_agent
    
    return decision


def get_orchestrator_decisions(
    project_id: str, 
    limit: int = None
) -> List[Dict[str, Any]]:
    """Retrieve the orchestrator decision history for a project."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    decisions = PROJECT_MEMORY[project_id].get("orchestrator_decisions", [])
    
    if limit is not None:
        return decisions[-limit:]
    
    return decisions


def get_last_orchestrator_decision(project_id: str) -> Dict[str, Any]:
    """Retrieve the most recent orchestrator decision for a project."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    decisions = PROJECT_MEMORY[project_id].get("orchestrator_decisions", [])
    
    if decisions:
        return decisions[-1]
    
    return None


def mark_agent_completed(project_id: str, agent_name: str) -> None:
    """Mark an agent as completed in the project memory."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    # Add to completed steps if not already there
    if agent_name not in memory.get("completed_steps", []):
        memory.setdefault("completed_steps", []).append(agent_name)


def check_loop_completion(project_id: str) -> bool:
    """Check if all required agents for the current loop have completed."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    completed_steps = set(memory.get("completed_steps", []))
    
    # Get required agents from loop schema
    loop_schema = SCHEMA_REGISTRY.get("loop", {})
    required_agents = set(loop_schema.get("required_agents", []))
    
    # Check if all required agents are in completed steps
    return required_agents.issubset(completed_steps)


def start_new_loop(project_id: str) -> int:
    """Start a new loop for the project by incrementing loop count and resetting completed steps."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    # Increment loop count
    memory["loop_count"] = memory.get("loop_count", 1) + 1
    
    # Reset completed steps for new loop
    memory["completed_steps"] = []
    
    # Reset loop complete flag
    memory["loop_complete"] = False
    
    # Log the loop transition
    log_orchestrator_decision(
        project_id,
        None,
        None,
        f"Starting new loop {memory['loop_count']}"
    )
    
    return memory["loop_count"]


def mark_loop_complete(project_id: str) -> None:
    """Mark the current loop as complete."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    # Set loop complete flag
    memory["loop_complete"] = True
    
    # Log the loop completion
    log_orchestrator_decision(
        project_id,
        get_last_completed_agent(project_id),
        None,
        f"Loop {memory.get('loop_count', 1)} marked as complete"
    )


def get_last_completed_agent(project_id: str) -> str:
    """Get the most recently completed agent for a project."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    completed_steps = PROJECT_MEMORY[project_id].get("completed_steps", [])
    return completed_steps[-1] if completed_steps else None


def determine_next_agent(project_id: str):
    """Determine which agent should run next based on project memory state."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Access project memory
    memory = PROJECT_MEMORY[project_id]
    completed_steps = memory.get("completed_steps", [])
    loop_count = memory.get("loop_count", 1)
    loop_complete = memory.get("loop_complete", False)
    autospawn = memory.get("autospawn", False)
    
    # Get the last completed agent (if any)
    last_agent = get_last_completed_agent(project_id)
    
    # Access schema registry
    agents_schema = SCHEMA_REGISTRY.get("agents", {})
    loop_schema = SCHEMA_REGISTRY.get("loop", {})
    
    # Check if loop is complete or max loops reached
    if loop_complete:
        return None, "loop is marked as complete"
    
    if loop_count >= loop_schema.get("max_loops", 5):
        return None, f"maximum loop count reached ({loop_count})"
    
    # Check if all required agents for this loop are completed
    required_agents = set(loop_schema.get("required_agents", []))
    completed_in_loop = set(completed_steps)
    
    # If all required agents are completed, suggest starting a new loop
    if required_agents.issubset(completed_in_loop):
        return "hal", "all agents in current loop completed, starting new loop"
    
    # Find eligible agents (not completed and dependencies satisfied)
    eligible_agents = []
    
    for agent_name, agent_def in agents_schema.items():
        # Skip if agent is already completed in this loop
        if agent_name in completed_steps:
            continue
        
        # Check if all dependencies are met
        dependencies = agent_def.get("dependencies", [])
        missing_deps = [dep for dep in dependencies if dep not in completed_steps]
        
        if not missing_deps:
            # All dependencies satisfied
            eligible_agents.append((agent_name, agent_def))
    
    # If no eligible agents, report the issue
    if not eligible_agents:
        return None, "no eligible agents found"
    
    # If multiple eligible agents, prioritize based on order in required_agents
    if len(eligible_agents) > 1:
        # Sort by order in required_agents list
        ordered_required = loop_schema.get("required_agents", [])
        eligible_agents.sort(key=lambda x: ordered_required.index(x[0]) if x[0] in ordered_required else float('inf'))
    
    # Select the first eligible agent
    next_agent, agent_def = eligible_agents[0]
    
    # Construct reason based on dependencies and last agent
    if not agent_def.get("dependencies", []):
        reason = f"{next_agent} has no dependencies and is ready to run"
    else:
        deps_str = ", ".join(agent_def.get("dependencies", []))
        reason = f"{next_agent} dependencies satisfied ({deps_str})"
    
    # Add context about last agent if available
    if last_agent:
        # Check if last agent directly unlocks this one
        if next_agent in agents_schema.get(last_agent, {}).get("unlocks", []):
            reason += f", directly unlocked by {last_agent}"
    
    # Consider autospawn if relevant
    if autospawn:
        reason += ", autospawn enabled"
    
    return next_agent, reason


def validate_agent_action(agent_name, project_memory):
    """Mock function for validate_agent_action."""
    return {}


def validate_next_agent_selection(project_id: str, next_agent: str):
    """Validate that the selected next agent is valid according to schema."""
    # Skip validation if no agent selected
    if next_agent is None:
        return True, ""
    
    # Check if agent exists in schema
    if next_agent not in SCHEMA_REGISTRY.get("agents", {}):
        return False, f"Agent '{next_agent}' not found in schema registry"
    
    # Validate agent action using existing utility
    errors = validate_agent_action(next_agent, PROJECT_MEMORY[project_id])
    
    if errors:
        error_msg = "; ".join([f"{k}: {v}" for k, v in errors.items()])
        return False, error_msg
    
    return True, ""


class TestOrchestratorLogic(unittest.TestCase):
    """Test cases for the Orchestrator Logic module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear the mock PROJECT_MEMORY before each test
        global PROJECT_MEMORY
        PROJECT_MEMORY = {}
        
        # Set up a test project
        self.project_id = "test_project"
        initialize_orchestrator_memory(self.project_id)
    
    def test_memory_initialization(self):
        """Test that memory initialization creates the expected structure."""
        # Verify that the project exists in memory
        self.assertIn(self.project_id, PROJECT_MEMORY)
        
        # Verify that required fields are initialized
        memory = PROJECT_MEMORY[self.project_id]
        self.assertIn("orchestrator_decisions", memory)
        self.assertIn("completed_steps", memory)
        self.assertIn("loop_count", memory)
        self.assertIn("loop_complete", memory)
        self.assertIn("next_recommended_agent", memory)
        self.assertIn("autospawn", memory)
        
        # Verify default values
        self.assertEqual(memory["completed_steps"], [])
        self.assertEqual(memory["loop_count"], 1)
        self.assertEqual(memory["loop_complete"], False)
        self.assertEqual(memory["next_recommended_agent"], None)
        self.assertEqual(memory["autospawn"], False)
    
    def test_decision_logging(self):
        """Test that decisions are properly logged."""
        # Log a decision
        decision = log_orchestrator_decision(
            self.project_id,
            "hal",
            "nova",
            "HAL completed, NOVA dependencies satisfied"
        )
        
        # Verify decision structure
        self.assertEqual(decision["loop_count"], 1)
        self.assertEqual(decision["last_agent"], "hal")
        self.assertEqual(decision["next_agent"], "nova")
        self.assertEqual(decision["reason"], "HAL completed, NOVA dependencies satisfied")
        self.assertIn("timestamp", decision)
        
        # Verify decision was added to memory
        decisions = PROJECT_MEMORY[self.project_id]["orchestrator_decisions"]
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0], decision)
        
        # Verify next_recommended_agent was updated
        self.assertEqual(PROJECT_MEMORY[self.project_id]["next_recommended_agent"], "nova")
    
    def test_get_decisions(self):
        """Test retrieving decisions from memory."""
        # Log multiple decisions
        decision1 = log_orchestrator_decision(
            self.project_id, "hal", "nova", "First decision"
        )
        decision2 = log_orchestrator_decision(
            self.project_id, "nova", "critic", "Second decision"
        )
        decision3 = log_orchestrator_decision(
            self.project_id, "critic", "ash", "Third decision"
        )
        
        # Test getting all decisions
        all_decisions = get_orchestrator_decisions(self.project_id)
        self.assertEqual(len(all_decisions), 3)
        self.assertEqual(all_decisions[0], decision1)
        self.assertEqual(all_decisions[1], decision2)
        self.assertEqual(all_decisions[2], decision3)
        
        # Test getting limited decisions
        limited_decisions = get_orchestrator_decisions(self.project_id, 2)
        self.assertEqual(len(limited_decisions), 2)
        self.assertEqual(limited_decisions[0], decision2)
        self.assertEqual(limited_decisions[1], decision3)
        
        # Test getting last decision
        last_decision = get_last_orchestrator_decision(self.project_id)
        self.assertEqual(last_decision, decision3)
    
    def test_mark_agent_completed(self):
        """Test marking an agent as completed."""
        # Mark an agent as completed
        mark_agent_completed(self.project_id, "hal")
        
        # Verify agent was added to completed_steps
        completed_steps = PROJECT_MEMORY[self.project_id]["completed_steps"]
        self.assertEqual(len(completed_steps), 1)
        self.assertEqual(completed_steps[0], "hal")
        
        # Mark another agent as completed
        mark_agent_completed(self.project_id, "nova")
        
        # Verify second agent was added
        completed_steps = PROJECT_MEMORY[self.project_id]["completed_steps"]
        self.assertEqual(len(completed_steps), 2)
        self.assertEqual(completed_steps[1], "nova")
        
        # Mark the same agent again (should not duplicate)
        mark_agent_completed(self.project_id, "nova")
        
        # Verify no duplication
        completed_steps = PROJECT_MEMORY[self.project_id]["completed_steps"]
        self.assertEqual(len(completed_steps), 2)
    
    def test_get_last_completed_agent(self):
        """Test getting the last completed agent."""
        # With no completed agents
        last_agent = get_last_completed_agent(self.project_id)
        self.assertIsNone(last_agent)
        
        # Mark agents as completed
        mark_agent_completed(self.project_id, "hal")
        mark_agent_completed(self.project_id, "nova")
        
        # Get last completed agent
        last_agent = get_last_completed_agent(self.project_id)
        self.assertEqual(last_agent, "nova")
    
    def test_determine_next_agent_no_completed(self):
        """Test determining next agent when no agents have completed."""
        # Determine next agent
        next_agent, reason = determine_next_agent(self.project_id)
        
        # Verify HAL is selected (no dependencies)
        self.assertEqual(next_agent, "hal")
        self.assertIn("no dependencies", reason.lower())
    
    def test_determine_next_agent_with_completed(self):
        """Test determining next agent when some agents have completed."""
        # Mark HAL as completed
        mark_agent_completed(self.project_id, "hal")
        
        # Determine next agent
        next_agent, reason = determine_next_agent(self.project_id)
        
        # Verify NOVA is selected (HAL dependency satisfied)
        self.assertEqual(next_agent, "nova")
        self.assertIn("dependencies satisfied", reason.lower())
        
        # Mark NOVA as completed
        mark_agent_completed(self.project_id, "nova")
        
        # Determine next agent again
        next_agent, reason = determine_next_agent(self.project_id)
        
        # Verify CRITIC is selected (NOVA dependency satisfied)
        self.assertEqual(next_agent, "critic")
        self.assertIn("dependencies satisfied", reason.lower())
    
    def test_determine_next_agent_loop_complete(self):
        """Test determining next agent when loop is marked complete."""
        # Mark loop as complete
        PROJECT_MEMORY[self.project_id]["loop_complete"] = True
        
        # Determine next agent
        next_agent, reason = determine_next_agent(self.project_id)
        
        # Verify no agent is selected
        self.assertIsNone(next_agent)
        self.assertIn("loop is marked as complete", reason.lower())
    
    def test_determine_next_agent_max_loops(self):
        """Test determining next agent when max loops reached."""
        # Set loop count to max
        PROJECT_MEMORY[self.project_id]["loop_count"] = 5
        
        # Determine next agent
        next_agent, reason = determine_next_agent(self.project_id)
        
        # Verify no agent is selected
        self.assertIsNone(next_agent)
        self.assertIn("maximum loop count reached", reason.lower())
    
    def test_check_loop_completion(self):
        """Test checking if a loop is complete."""
        # With no completed agents
        is_complete = check_loop_completion(self.project_id)
        self.assertFalse(is_complete)
        
        # With some completed agents
        mark_agent_completed(self.project_id, "hal")
        mark_agent_completed(self.project_id, "nova")
        is_complete = check_loop_completion(self.project_id)
        self.assertFalse(is_complete)
        
        # With all required agents completed
        mark_agent_completed(self.project_id, "critic")
        mark_agent_completed(self.project_id, "ash")
        mark_agent_completed(self.project_id, "sage")
        is_complete = check_loop_completion(self.project_id)
        self.assertTrue(is_complete)
    
    def test_start_new_loop(self):
        """Test starting a new loop."""
        # Mark some agents as completed
        mark_agent_completed(self.project_id, "hal")
        mark_agent_completed(self.project_id, "nova")
        
        # Start a new loop
        new_loop_count = start_new_loop(self.project_id)
        
        # Verify loop count was incremented
        self.assertEqual(new_loop_count, 2)
        self.assertEqual(PROJECT_MEMORY[self.project_id]["loop_count"], 2)
        
        # Verify completed steps were reset
        self.assertEqual(PROJECT_MEMORY[self.project_id]["completed_steps"], [])
        
        # Verify loop complete flag was reset
        self.assertFalse(PROJECT_MEMORY[self.project_id]["loop_complete"])
        
        # Verify a decision was logged
        decisions = PROJECT_MEMORY[self.project_id]["orchestrator_decisions"]
        self.assertGreaterEqual(len(decisions), 1)
        last_decision = decisions[-1]
        self.assertIn("starting new loop", last_decision["reason"].lower())
    
    def test_mark_loop_complete(self):
        """Test marking a loop as complete."""
        # Mark loop as complete
        mark_loop_complete(self.project_id)
        
        # Verify loop complete flag was set
        self.assertTrue(PROJECT_MEMORY[self.project_id]["loop_complete"])
        
        # Verify a decision was logged
        decisions = PROJECT_MEMORY[self.project_id]["orchestrator_decisions"]
        self.assertEqual(len(decisions), 1)
        self.assertIn("loop", decisions[0]["reason"].lower())
        self.assertIn("complete", decisions[0]["reason"].lower())


if __name__ == "__main__":
    unittest.main()
