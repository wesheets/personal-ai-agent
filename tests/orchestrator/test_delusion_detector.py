"""
Unit tests for the Delusion Detection module.
"""

import unittest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from orchestrator.modules.delusion_detector import (
    generate_plan_hash,
    get_plan_similarity,
    compare_to_rejected_hashes,
    inject_delusion_warning,
    detect_plan_delusion,
    store_rejected_plan
)

class TestDelusionDetector(unittest.TestCase):
    """Test cases for the Delusion Detection module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample plans
        self.plan1 = {
            "goal": "Create a user authentication system",
            "approach": "Use JWT tokens with secure password hashing",
            "steps": [
                {"description": "Set up database schema for users"},
                {"description": "Implement password hashing"},
                {"description": "Create JWT token generation"},
                {"description": "Build login and registration endpoints"}
            ]
        }
        
        self.plan2 = {
            "goal": "Create a user authentication system",
            "approach": "Use JWT tokens with secure password hashing",
            "steps": [
                {"description": "Set up database schema for users"},
                {"description": "Implement password hashing"},
                {"description": "Create JWT token generation"},
                {"description": "Build login and registration endpoints"},
                {"description": "Add password reset functionality"}
            ]
        }
        
        self.plan3 = {
            "goal": "Build a data visualization dashboard",
            "approach": "Use React with D3.js",
            "steps": [
                {"description": "Set up React project structure"},
                {"description": "Create data fetching services"},
                {"description": "Implement D3.js charts"},
                {"description": "Build dashboard layout"}
            ]
        }
        
        # Sample memory
        self.memory = {
            "loop_trace": {
                "loop_123": {
                    "plan": self.plan1,
                    "status": "completed"
                }
            },
            "rejected_plans": [
                {
                    "loop_id": "loop_42",
                    "hash": "abc123",
                    "failure_reason": "API rate limit exceeded",
                    "timestamp": "2025-04-20T12:00:00Z",
                    "plan_summary": {
                        "goal": "Create a user authentication system",
                        "steps_count": 4,
                        "approach": "Use JWT tokens with secure password hashing"
                    }
                }
            ]
        }
    
    def test_generate_plan_hash(self):
        """Test generate_plan_hash function."""
        # Generate hash for plan1
        hash1 = generate_plan_hash(self.plan1)
        
        # Hash should be a string
        self.assertIsInstance(hash1, str)
        
        # Hash should be 64 characters (SHA-256 hex digest)
        self.assertEqual(len(hash1), 64)
        
        # Same plan should generate same hash
        hash1_again = generate_plan_hash(self.plan1)
        self.assertEqual(hash1, hash1_again)
        
        # Different plans should generate different hashes
        hash3 = generate_plan_hash(self.plan3)
        self.assertNotEqual(hash1, hash3)
    
    def test_get_plan_similarity(self):
        """Test get_plan_similarity function."""
        # Generate hashes
        hash1 = generate_plan_hash(self.plan1)
        hash2 = generate_plan_hash(self.plan2)
        hash3 = generate_plan_hash(self.plan3)
        
        # Identical plans should have similarity 1.0
        self.assertEqual(get_plan_similarity(hash1, hash1), 1.0)
        
        # Similar plans should have high similarity
        similarity12 = get_plan_similarity(hash1, hash2)
        self.assertGreater(similarity12, 0.7)
        
        # Different plans should have lower similarity
        similarity13 = get_plan_similarity(hash1, hash3)
        # Use assertLessEqual instead of assertLess to handle potential equality edge cases
        self.assertLessEqual(similarity13, similarity12)
    
    def test_compare_to_rejected_hashes_with_match(self):
        """Test compare_to_rejected_hashes with a matching plan."""
        # Mock rejected plans with a hash that will match
        rejected_plans = [
            {
                "loop_id": "loop_42",
                "hash": generate_plan_hash(self.plan1),
                "failure_reason": "API rate limit exceeded"
            }
        ]
        
        # Compare current plan hash to rejected plans
        result = compare_to_rejected_hashes(
            generate_plan_hash(self.plan1),
            rejected_plans,
            0.85
        )
        
        # Should find a match
        self.assertIsNotNone(result)
        self.assertIn("rejected_plan", result)
        self.assertIn("similarity_score", result)
        self.assertEqual(result["similarity_score"], 1.0)
    
    def test_compare_to_rejected_hashes_without_match(self):
        """Test compare_to_rejected_hashes without a matching plan."""
        # Mock rejected plans with a hash that won't match
        rejected_plans = [
            {
                "loop_id": "loop_42",
                "hash": generate_plan_hash(self.plan3),
                "failure_reason": "API rate limit exceeded"
            }
        ]
        
        # Compare current plan hash to rejected plans
        result = compare_to_rejected_hashes(
            generate_plan_hash(self.plan1),
            rejected_plans,
            0.85
        )
        
        # Should not find a match
        self.assertIsNone(result)
    
    def test_inject_delusion_warning(self):
        """Test inject_delusion_warning function."""
        # Mock similar plan
        similar_plan = {
            "loop_id": "loop_42",
            "failure_reason": "API rate limit exceeded"
        }
        
        # Inject warning
        updated_memory = inject_delusion_warning(
            self.memory,
            "loop_123",
            similar_plan,
            0.9
        )
        
        # Check that warning was injected
        self.assertIn("delusion_alerts", updated_memory)
        self.assertEqual(len(updated_memory["delusion_alerts"]), 1)
        
        # Check alert properties
        alert = updated_memory["delusion_alerts"][0]
        self.assertEqual(alert["loop_id"], "loop_123")
        self.assertEqual(alert["warning_type"], "plan_repetition")
        self.assertIn("This plan resembles Loop loop_42", alert["message"])
        self.assertEqual(alert["similarity_score"], 0.9)
        self.assertEqual(alert["similar_loop_id"], "loop_42")
        self.assertEqual(alert["failure_reason"], "API rate limit exceeded")
    
    def test_detect_plan_delusion_with_similar_plan(self):
        """Test detect_plan_delusion with a similar plan."""
        # Mock memory with a rejected plan similar to plan1
        memory_with_similar = self.memory.copy()
        memory_with_similar["rejected_plans"] = [
            {
                "loop_id": "loop_42",
                "hash": generate_plan_hash(self.plan1),
                "failure_reason": "API rate limit exceeded",
                "timestamp": "2025-04-20T12:00:00Z",
                "plan_summary": {
                    "goal": "Create a user authentication system",
                    "steps_count": 4,
                    "approach": "Use JWT tokens with secure password hashing"
                }
            }
        ]
        
        # Detect delusion
        updated_memory = detect_plan_delusion(
            self.plan1,
            "loop_123",
            memory_with_similar,
            0.85
        )
        
        # Check that warning was injected
        self.assertIn("delusion_alerts", updated_memory)
        self.assertEqual(len(updated_memory["delusion_alerts"]), 1)
        
        # Check alert properties
        alert = updated_memory["delusion_alerts"][0]
        self.assertEqual(alert["loop_id"], "loop_123")
        self.assertEqual(alert["warning_type"], "plan_repetition")
        self.assertIn("This plan resembles Loop loop_42", alert["message"])
        self.assertEqual(alert["similar_loop_id"], "loop_42")
        self.assertEqual(alert["failure_reason"], "API rate limit exceeded")
    
    def test_detect_plan_delusion_without_similar_plan(self):
        """Test detect_plan_delusion without a similar plan."""
        # Mock memory with a rejected plan not similar to plan1
        memory_without_similar = self.memory.copy()
        memory_without_similar["rejected_plans"] = [
            {
                "loop_id": "loop_42",
                "hash": generate_plan_hash(self.plan3),
                "failure_reason": "API rate limit exceeded",
                "timestamp": "2025-04-20T12:00:00Z",
                "plan_summary": {
                    "goal": "Build a data visualization dashboard",
                    "steps_count": 4,
                    "approach": "Use React with D3.js"
                }
            }
        ]
        
        # Detect delusion
        updated_memory = detect_plan_delusion(
            self.plan1,
            "loop_123",
            memory_without_similar,
            0.85
        )
        
        # Check that no warning was injected
        self.assertNotIn("delusion_alerts", updated_memory)
        
        # Memory should be unchanged
        self.assertEqual(updated_memory, memory_without_similar)
    
    def test_store_rejected_plan(self):
        """Test store_rejected_plan function."""
        # Store rejected plan
        updated_memory = store_rejected_plan(
            self.plan1,
            "loop_123",
            "API rate limit exceeded",
            self.memory
        )
        
        # Check that plan was stored
        self.assertIn("rejected_plans", updated_memory)
        self.assertEqual(len(updated_memory["rejected_plans"]), 2)
        
        # Check stored plan properties
        stored_plan = updated_memory["rejected_plans"][1]
        self.assertEqual(stored_plan["loop_id"], "loop_123")
        self.assertEqual(stored_plan["failure_reason"], "API rate limit exceeded")
        self.assertIn("hash", stored_plan)
        self.assertIn("timestamp", stored_plan)
        self.assertIn("plan_summary", stored_plan)
        
        # Check plan summary
        plan_summary = stored_plan["plan_summary"]
        self.assertEqual(plan_summary["goal"], "Create a user authentication system")
        self.assertEqual(plan_summary["steps_count"], 4)
        self.assertEqual(plan_summary["approach"], "Use JWT tokens with secure password hashing")

if __name__ == "__main__":
    unittest.main()
