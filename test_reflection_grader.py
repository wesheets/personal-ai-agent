"""
Test Reflection Grader Module

This script tests the functionality of the reflection_grader module,
which evaluates agent reflections and scores their quality.
"""

import unittest
import json
import os
import shutil
from datetime import datetime
from app.modules.reflection_grader import grade_reflection, get_reflection_scores, get_weak_reflections
from app.modules.project_state import read_project_state, update_project_state

class TestReflectionGrader(unittest.TestCase):
    """Test cases for the reflection_grader module."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_id = "test_reflection_grader_001"
        
        # Ensure project states directory exists
        states_dir = os.path.join(os.path.dirname(__file__), "app/modules/project_states")
        os.makedirs(states_dir, exist_ok=True)
        
        # Create test project state
        self.test_state = {
            "project_id": self.project_id,
            "status": "active",
            "loop_count": 2,
            "last_reflection": {
                "goal": "Build a test project",
                "summary": "Successfully implemented core functionality",
                "confidence": 0.8,
                "tags": ["loop:2", "status:success"]
            }
        }
        
        # Write test state to file
        state_file = os.path.join(states_dir, f"{self.project_id}.json")
        with open(state_file, 'w') as f:
            json.dump(self.test_state, f, indent=2)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test project state file
        states_dir = os.path.join(os.path.dirname(__file__), "app/modules/project_states")
        state_file = os.path.join(states_dir, f"{self.project_id}.json")
        if os.path.exists(state_file):
            os.remove(state_file)
    
    def test_grade_reflection_good(self):
        """Test grading a good reflection."""
        result = grade_reflection(self.project_id)
        
        # Check result structure
        self.assertIn("score", result)
        self.assertIn("issues", result)
        self.assertIn("timestamp", result)
        self.assertIn("loop", result)
        
        # Check score is high for good reflection
        self.assertGreaterEqual(result["score"], 0.8)
        
        # Check issues list is empty or small
        self.assertLessEqual(len(result["issues"]), 1)
        
        # Check project state was updated
        updated_state = read_project_state(self.project_id)
        self.assertIn("reflection_scores", updated_state)
        self.assertEqual(len(updated_state["reflection_scores"]), 1)
        
        # Check weak_reflections wasn't created for good reflection
        self.assertNotIn("weak_reflections", updated_state)
    
    def test_grade_reflection_bad(self):
        """Test grading a bad reflection."""
        # Update project state with a bad reflection
        bad_reflection = {
            "goal": "Build a test project",
            "summary": "Did stuff",  # Too brief
            "confidence": 0.3,  # Low confidence
            "tags": []  # Missing tags
        }
        update_project_state(self.project_id, {"last_reflection": bad_reflection})
        
        result = grade_reflection(self.project_id)
        
        # Check score is low for bad reflection
        self.assertLessEqual(result["score"], 0.5)
        
        # Check issues list contains multiple issues
        self.assertGreaterEqual(len(result["issues"]), 2)
        
        # Check project state was updated
        updated_state = read_project_state(self.project_id)
        self.assertIn("reflection_scores", updated_state)
        self.assertEqual(len(updated_state["reflection_scores"]), 1)
        
        # Check weak_reflections was created for bad reflection
        self.assertIn("weak_reflections", updated_state)
        self.assertEqual(len(updated_state["weak_reflections"]), 1)
    
    def test_get_reflection_scores(self):
        """Test getting reflection scores."""
        # Grade a reflection first to create scores
        grade_reflection(self.project_id)
        
        result = get_reflection_scores(self.project_id)
        
        # Check result structure
        self.assertIn("project_id", result)
        self.assertIn("reflection_scores", result)
        self.assertIn("count", result)
        self.assertIn("average_score", result)
        
        # Check values
        self.assertEqual(result["project_id"], self.project_id)
        self.assertEqual(result["count"], 1)
        self.assertGreaterEqual(result["average_score"], 0)
    
    def test_get_weak_reflections(self):
        """Test getting weak reflections."""
        # Update project state with a bad reflection
        bad_reflection = {
            "goal": "Build a test project",
            "summary": "Did stuff",  # Too brief
            "confidence": 0.3,  # Low confidence
            "tags": []  # Missing tags
        }
        update_project_state(self.project_id, {"last_reflection": bad_reflection})
        
        # Grade the reflection to create weak_reflections
        grade_reflection(self.project_id)
        
        result = get_weak_reflections(self.project_id)
        
        # Check result structure
        self.assertIn("project_id", result)
        self.assertIn("weak_reflections", result)
        self.assertIn("count", result)
        
        # Check values
        self.assertEqual(result["project_id"], self.project_id)
        self.assertEqual(result["count"], 1)
        self.assertEqual(len(result["weak_reflections"]), 1)
    
    def test_multiple_reflections(self):
        """Test grading multiple reflections."""
        # Grade initial reflection
        grade_reflection(self.project_id)
        
        # Update project state with a second reflection
        second_reflection = {
            "goal": "Improve test coverage",
            "summary": "Added comprehensive tests for all modules",
            "confidence": 0.9,
            "tags": ["loop:3", "status:success"]
        }
        update_project_state(self.project_id, {"last_reflection": second_reflection, "loop_count": 3})
        
        # Grade second reflection
        grade_reflection(self.project_id)
        
        # Check project state was updated
        updated_state = read_project_state(self.project_id)
        self.assertIn("reflection_scores", updated_state)
        self.assertEqual(len(updated_state["reflection_scores"]), 2)
        
        # Get scores
        scores = get_reflection_scores(self.project_id)
        self.assertEqual(scores["count"], 2)

if __name__ == "__main__":
    unittest.main()
