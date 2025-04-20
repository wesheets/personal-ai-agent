"""
Tests for the thread plan integration module.

This module contains tests for the thread_plan_integration.py module, which provides
functionality for integrating thread insights into plans.
"""

import unittest
import os
import sys
import json
import datetime
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import module to test
from orchestrator.modules.thread_plan_integration import (
    mark_thread_actionable,
    get_plan_for_loop,
    update_plan_with_thread_insight,
    process_actionable_threads,
    suggest_plan_modifications_from_threads,
    get_plan_integration_history
)

# Import nested_comments for setup
from orchestrator.modules.nested_comments import create_thread, reply_to_thread

class TestThreadPlanIntegration(unittest.TestCase):
    """Test cases for the thread plan integration module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock memory dictionary
        self.memory = {
            "thread_history": {},
            "thread_messages": {},
            "thread_summaries": {},
            "thread_deviations": {},
            "deviation_patterns": {},
            "loop_trace": {
                1: {
                    "thread_activity": [],
                    "thread_summaries": [],
                    "plan_revisions": [],
                    "plan": {
                        "steps": [
                            "Step 1: Initialize project structure",
                            "Step 2: Implement core functionality",
                            "Step 3: Add error handling",
                            "Step 4: Write documentation"
                        ]
                    }
                }
            },
            "chat_messages": []
        }
        
        # Create test threads
        self.thread_id1 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="We should add more robust error handling",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        # Add reply to thread 1
        self.reply_id1 = reply_to_thread(
            memory=self.memory,
            thread_id=self.thread_id1,
            parent_id=self.memory["thread_messages"][self.thread_id1][0]["message_id"],
            agent="nova",
            role="agent",
            message="I agree, we should use try-except blocks more consistently",
            timestamp="2025-04-20T12:05:00Z"
        )
        
        # Create another thread
        self.thread_id2 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="ash",
            role="agent",
            message="The documentation should include more examples",
            timestamp="2025-04-20T12:10:00Z"
        )

    def test_mark_thread_actionable(self):
        """Test marking a thread as actionable."""
        # Mark thread as actionable
        result = mark_thread_actionable(
            memory=self.memory,
            thread_id=self.thread_id1,
            agent="orchestrator",
            reason="Contains valuable insights for error handling"
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread metadata
        thread_meta = self.memory["thread_history"][1][self.thread_id1]
        self.assertTrue(thread_meta["actionable"])
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][self.thread_id1]
        self.assertTrue(thread_messages[0]["actionable"])
        
        # Check loop trace
        thread_activity = self.memory["loop_trace"][1]["thread_activity"]
        actionable_activities = [a for a in thread_activity if a["action"] == "thread_marked_actionable"]
        self.assertEqual(len(actionable_activities), 1)
        self.assertEqual(actionable_activities[0]["thread_id"], self.thread_id1)
        self.assertEqual(actionable_activities[0]["agent"], "orchestrator")
        
        # Check plan deviations
        if "plan_deviations" in self.memory["loop_trace"][1]:
            plan_deviations = self.memory["loop_trace"][1]["plan_deviations"]
            thread_deviations = [d for d in plan_deviations if d["type"] == "thread_insight" and d["thread_id"] == self.thread_id1]
            self.assertEqual(len(thread_deviations), 1)

    def test_get_plan_for_loop(self):
        """Test getting the plan for a loop."""
        # Get plan
        plan = get_plan_for_loop(
            memory=self.memory,
            loop_id=1
        )
        
        # Check plan
        self.assertIsNotNone(plan)
        self.assertIn("steps", plan)
        self.assertEqual(len(plan["steps"]), 4)
        self.assertEqual(plan["steps"][0], "Step 1: Initialize project structure")
        
        # Test with non-existent loop
        plan = get_plan_for_loop(
            memory=self.memory,
            loop_id=999
        )
        
        # Check result
        self.assertIsNone(plan)

    def test_update_plan_with_thread_insight(self):
        """Test updating a plan with thread insight."""
        # Update plan with thread insight
        result = update_plan_with_thread_insight(
            memory=self.memory,
            thread_id=self.thread_id1,
            plan_step=2,  # Step 3: Add error handling
            agent="orchestrator",
            modification_type="addition",
            modification_content="Ensure consistent use of try-except blocks for all external API calls."
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check plan
        plan = self.memory["loop_trace"][1]["plan"]
        self.assertIn("Ensure consistent use of try-except blocks", plan["steps"][2])
        
        # Check thread status
        thread_meta = self.memory["thread_history"][1][self.thread_id1]
        self.assertEqual(thread_meta["status"], "integrated")
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][self.thread_id1]
        self.assertEqual(thread_messages[0]["status"], "integrated")
        self.assertIsNotNone(thread_messages[0]["plan_integration"])
        self.assertEqual(thread_messages[0]["plan_integration"]["plan_step"], 2)
        self.assertEqual(thread_messages[0]["plan_integration"]["integration_type"], "addition")
        
        # Check plan revisions
        self.assertIn("plan_revisions", self.memory["loop_trace"][1])
        plan_revisions = self.memory["loop_trace"][1]["plan_revisions"]
        self.assertEqual(len(plan_revisions), 1)
        self.assertEqual(plan_revisions[0]["step"], 2)
        self.assertEqual(plan_revisions[0]["modification_type"], "addition")
        self.assertEqual(plan_revisions[0]["thread_id"], self.thread_id1)

    def test_process_actionable_threads(self):
        """Test processing actionable threads."""
        # Mark threads as actionable
        mark_thread_actionable(
            memory=self.memory,
            thread_id=self.thread_id1,
            agent="orchestrator"
        )
        
        mark_thread_actionable(
            memory=self.memory,
            thread_id=self.thread_id2,
            agent="orchestrator"
        )
        
        # Process actionable threads
        result = process_actionable_threads(
            memory=self.memory,
            loop_id=1,
            agent="orchestrator",
            max_threads=5
        )
        
        # Check result
        self.assertTrue(result["success"])
        self.assertEqual(result["processed"], 2)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["skipped"], 0)
        
        # Check thread statuses
        self.assertEqual(self.memory["thread_history"][1][self.thread_id1]["status"], "integrated")
        self.assertEqual(self.memory["thread_history"][1][self.thread_id2]["status"], "integrated")
        
        # Check plan revisions
        self.assertIn("plan_revisions", self.memory["loop_trace"][1])
        plan_revisions = self.memory["loop_trace"][1]["plan_revisions"]
        self.assertEqual(len(plan_revisions), 2)
        
        # Check that the error handling thread was integrated into step 3
        error_handling_revisions = [r for r in plan_revisions if r["thread_id"] == self.thread_id1]
        self.assertEqual(len(error_handling_revisions), 1)
        self.assertEqual(error_handling_revisions[0]["step"], 2)  # Step 3 (index 2)
        
        # Check that the documentation thread was integrated into step 4
        doc_revisions = [r for r in plan_revisions if r["thread_id"] == self.thread_id2]
        self.assertEqual(len(doc_revisions), 1)
        self.assertEqual(doc_revisions[0]["step"], 3)  # Step 4 (index 3)

    def test_suggest_plan_modifications_from_threads(self):
        """Test suggesting plan modifications from threads."""
        # Get suggestions
        suggestions = suggest_plan_modifications_from_threads(
            memory=self.memory,
            loop_id=1,
            max_suggestions=3
        )
        
        # Check suggestions
        self.assertEqual(len(suggestions), 2)
        
        # Check suggestion content
        thread1_suggestions = [s for s in suggestions if s["thread_id"] == self.thread_id1]
        self.assertEqual(len(thread1_suggestions), 1)
        self.assertEqual(thread1_suggestions[0]["plan_step"], 2)  # Should match step 3 (error handling)
        
        thread2_suggestions = [s for s in suggestions if s["thread_id"] == self.thread_id2]
        self.assertEqual(len(thread2_suggestions), 1)
        self.assertEqual(thread2_suggestions[0]["plan_step"], 3)  # Should match step 4 (documentation)

    def test_get_plan_integration_history(self):
        """Test getting plan integration history."""
        # First integrate some threads
        update_plan_with_thread_insight(
            memory=self.memory,
            thread_id=self.thread_id1,
            plan_step=2,
            agent="orchestrator",
            modification_type="addition",
            modification_content="Ensure consistent use of try-except blocks."
        )
        
        update_plan_with_thread_insight(
            memory=self.memory,
            thread_id=self.thread_id2,
            plan_step=3,
            agent="orchestrator",
            modification_type="addition",
            modification_content="Add more examples to documentation."
        )
        
        # Get integration history
        history = get_plan_integration_history(
            memory=self.memory,
            loop_id=1
        )
        
        # Check history
        self.assertEqual(len(history), 2)
        
        # Check history content
        thread1_history = [h for h in history if h["thread_id"] == self.thread_id1]
        self.assertEqual(len(thread1_history), 1)
        self.assertEqual(thread1_history[0]["plan_step"], 2)
        self.assertEqual(thread1_history[0]["integration_type"], "addition")
        
        thread2_history = [h for h in history if h["thread_id"] == self.thread_id2]
        self.assertEqual(len(thread2_history), 1)
        self.assertEqual(thread2_history[0]["plan_step"], 3)
        self.assertEqual(thread2_history[0]["integration_type"], "addition")

    def test_error_handling(self):
        """Test error handling for edge cases."""
        # Test with non-existent thread
        result = mark_thread_actionable(
            memory=self.memory,
            thread_id="non-existent-thread",
            agent="orchestrator"
        )
        self.assertFalse(result)
        
        # Test with non-existent loop
        result = process_actionable_threads(
            memory=self.memory,
            loop_id=999,
            agent="orchestrator"
        )
        self.assertTrue(result["success"])  # Should succeed but process 0 threads
        self.assertEqual(result["processed"], 0)
        
        # Test with invalid plan step
        result = update_plan_with_thread_insight(
            memory=self.memory,
            thread_id=self.thread_id1,
            plan_step=999,  # Invalid step
            agent="orchestrator",
            modification_type="addition"
        )
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
