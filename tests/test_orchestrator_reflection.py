"""
Test Module for Orchestrator Reflection Logic

This module provides test cases for verifying the functionality of the
Orchestrator Reflection implementation.
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
        }
    },
    "loop": {
        "required_agents": ["hal", "nova"],
        "max_loops": 5,
        "exit_conditions": ["loop_complete == true", "loop_count >= max_loops"]
    },
    "reflection": {
        "goal": str,
        "summary": str,
        "confidence": float,
        "tags": list
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


def reflect_on_last_loop(project_id: str) -> Dict[str, Any]:
    """Reflect on the last loop cycle and write a structured memory object summarizing what happened."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Access project memory
    memory = PROJECT_MEMORY[project_id]
    loop_count = memory.get("loop_count", 0)
    completed = memory.get("completed_steps", [])
    files = memory.get("file_tree", {}).get("files", [])
    
    # Create summary text
    summary = f"Loop {loop_count} completed. Agents executed: {', '.join(completed)}. " \
              f"{len(files)} files present in file tree."
    
    # Create reflection record
    reflection = {
        "goal": memory.get("project_goal", "Autonomous loop execution"),
        "summary": summary,
        "confidence": 0.9,  # (optional: computed based on loop result quality)
        "tags": ["reflection", f"loop:{loop_count}", "orchestrator"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Log the reflection
    memory.setdefault("reflections", []).append(reflection)
    memory["last_reflection"] = reflection
    
    return reflection


def get_reflections(project_id: str, limit: int = None) -> List[Dict[str, Any]]:
    """Retrieve the reflection history for a project."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    reflections = PROJECT_MEMORY[project_id].get("reflections", [])
    
    if limit is not None:
        return reflections[-limit:]
    
    return reflections


def get_last_reflection(project_id: str) -> Dict[str, Any]:
    """Retrieve the most recent reflection for a project."""
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    return PROJECT_MEMORY[project_id].get("last_reflection")


class TestOrchestratorReflection(unittest.TestCase):
    """Test cases for the Orchestrator Reflection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear the mock PROJECT_MEMORY before each test
        global PROJECT_MEMORY
        PROJECT_MEMORY = {}
        
        # Set up a test project
        self.project_id = "test_project"
        initialize_orchestrator_memory(self.project_id)
        
        # Set up some test data
        PROJECT_MEMORY[self.project_id]["completed_steps"] = ["hal", "nova"]
        PROJECT_MEMORY[self.project_id]["loop_count"] = 2
        PROJECT_MEMORY[self.project_id]["project_goal"] = "Build a test project"
        PROJECT_MEMORY[self.project_id]["file_tree"] = {
            "files": ["README.md", "requirements.txt", "app.py"]
        }
    
    def test_reflect_on_last_loop(self):
        """Test that reflection on the last loop creates the expected record."""
        # Create a reflection
        reflection = reflect_on_last_loop(self.project_id)
        
        # Verify reflection structure
        self.assertIn("goal", reflection)
        self.assertIn("summary", reflection)
        self.assertIn("confidence", reflection)
        self.assertIn("tags", reflection)
        self.assertIn("timestamp", reflection)
        
        # Verify reflection content
        self.assertEqual(reflection["goal"], "Build a test project")
        self.assertIn("Loop 2 completed", reflection["summary"])
        self.assertIn("hal, nova", reflection["summary"])
        self.assertIn("3 files", reflection["summary"])
        self.assertEqual(reflection["confidence"], 0.9)
        self.assertIn("reflection", reflection["tags"])
        self.assertIn("loop:2", reflection["tags"])
        self.assertIn("orchestrator", reflection["tags"])
        
        # Verify reflection was added to memory
        reflections = PROJECT_MEMORY[self.project_id]["reflections"]
        self.assertEqual(len(reflections), 1)
        self.assertEqual(reflections[0], reflection)
        
        # Verify last_reflection was set
        self.assertEqual(PROJECT_MEMORY[self.project_id]["last_reflection"], reflection)
    
    def test_get_reflections(self):
        """Test retrieving reflections from memory."""
        # Create multiple reflections
        reflection1 = reflect_on_last_loop(self.project_id)
        
        # Change some data and create another reflection
        PROJECT_MEMORY[self.project_id]["loop_count"] = 3
        PROJECT_MEMORY[self.project_id]["completed_steps"] = ["hal", "nova", "critic"]
        reflection2 = reflect_on_last_loop(self.project_id)
        
        # Test getting all reflections
        all_reflections = get_reflections(self.project_id)
        self.assertEqual(len(all_reflections), 2)
        self.assertEqual(all_reflections[0], reflection1)
        self.assertEqual(all_reflections[1], reflection2)
        
        # Test getting limited reflections
        limited_reflections = get_reflections(self.project_id, 1)
        self.assertEqual(len(limited_reflections), 1)
        self.assertEqual(limited_reflections[0], reflection2)
    
    def test_get_last_reflection(self):
        """Test retrieving the last reflection from memory."""
        # With no reflections
        last_reflection = get_last_reflection(self.project_id)
        self.assertIsNone(last_reflection)
        
        # Create a reflection
        reflection1 = reflect_on_last_loop(self.project_id)
        
        # Get last reflection
        last_reflection = get_last_reflection(self.project_id)
        self.assertEqual(last_reflection, reflection1)
        
        # Create another reflection
        PROJECT_MEMORY[self.project_id]["loop_count"] = 3
        reflection2 = reflect_on_last_loop(self.project_id)
        
        # Get last reflection again
        last_reflection = get_last_reflection(self.project_id)
        self.assertEqual(last_reflection, reflection2)
    
    def test_reflection_schema_compliance(self):
        """Test that reflections comply with the schema registry."""
        # Create a reflection
        reflection = reflect_on_last_loop(self.project_id)
        
        # Verify schema compliance
        reflection_schema = SCHEMA_REGISTRY["reflection"]
        
        # Check that all required fields are present and of the correct type
        for field, field_type in reflection_schema.items():
            self.assertIn(field, reflection)
            if field == "goal":
                self.assertIsInstance(reflection["goal"], str)
            elif field == "summary":
                self.assertIsInstance(reflection["summary"], str)
            elif field == "confidence":
                self.assertIsInstance(reflection["confidence"], float)
            elif field == "tags":
                self.assertIsInstance(reflection["tags"], list)


if __name__ == "__main__":
    unittest.main()
