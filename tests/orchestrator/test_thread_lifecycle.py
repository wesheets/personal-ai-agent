"""
Tests for the thread lifecycle module.

This module contains tests for the thread_lifecycle.py module, which provides
functionality for managing the lifecycle of nested comment threads.
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
from orchestrator.modules.thread_lifecycle import (
    close_thread,
    integrate_thread,
    discard_thread,
    reopen_thread,
    batch_close_inactive_threads,
    get_thread_lifecycle_history
)

# Import nested_comments for setup
from orchestrator.modules.nested_comments import create_thread, reply_to_thread

class TestThreadLifecycle(unittest.TestCase):
    """Test cases for the thread lifecycle module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock memory dictionary
        self.memory = {
            "thread_history": {},
            "thread_messages": {},
            "thread_summaries": {},
            "loop_trace": {
                1: {
                    "thread_activity": [],
                    "thread_summaries": [],
                    "plan": {
                        "steps": ["Step 1", "Step 2", "Step 3"]
                    }
                }
            },
            "chat_messages": []
        }
        
        # Create test thread
        self.thread_id = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="This is a test thread",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        # Add reply to thread
        self.reply_id = reply_to_thread(
            memory=self.memory,
            thread_id=self.thread_id,
            parent_id=self.memory["thread_messages"][self.thread_id][0]["message_id"],
            agent="nova",
            role="agent",
            message="This is a reply",
            timestamp="2025-04-20T12:05:00Z"
        )

    def test_close_thread(self):
        """Test closing a thread."""
        # Close thread
        result = close_thread(
            memory=self.memory,
            thread_id=self.thread_id,
            agent="orchestrator",
            auto_summarize=True,
            summary="Thread closed for testing"
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread status
        thread_meta = self.memory["thread_history"][1][self.thread_id]
        self.assertEqual(thread_meta["status"], "closed")
        self.assertEqual(thread_meta["summary"], "Thread closed for testing")
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][self.thread_id]
        self.assertEqual(thread_messages[0]["status"], "closed")
        self.assertEqual(thread_messages[0]["summary"], "Thread closed for testing")
        
        # Check loop trace
        thread_activity = self.memory["loop_trace"][1]["thread_activity"]
        close_activities = [a for a in thread_activity if a["action"] == "thread_closed"]
        self.assertEqual(len(close_activities), 1)
        self.assertEqual(close_activities[0]["thread_id"], self.thread_id)
        self.assertEqual(close_activities[0]["agent"], "orchestrator")

    def test_integrate_thread(self):
        """Test integrating a thread into the plan."""
        # Integrate thread
        result = integrate_thread(
            memory=self.memory,
            thread_id=self.thread_id,
            agent="orchestrator",
            plan_step=1,
            integration_type="addition",
            integration_summary="Added thread insights to step 2"
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread status
        thread_meta = self.memory["thread_history"][1][self.thread_id]
        self.assertEqual(thread_meta["status"], "integrated")
        self.assertEqual(thread_meta["summary"], "Added thread insights to step 2")
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][self.thread_id]
        self.assertEqual(thread_messages[0]["status"], "integrated")
        self.assertEqual(thread_messages[0]["summary"], "Added thread insights to step 2")
        self.assertIsNotNone(thread_messages[0]["plan_integration"])
        self.assertEqual(thread_messages[0]["plan_integration"]["plan_step"], 1)
        self.assertEqual(thread_messages[0]["plan_integration"]["integration_type"], "addition")
        
        # Check loop trace
        thread_activity = self.memory["loop_trace"][1]["thread_activity"]
        integrate_activities = [a for a in thread_activity if a["action"] == "thread_integrated"]
        self.assertEqual(len(integrate_activities), 1)
        self.assertEqual(integrate_activities[0]["thread_id"], self.thread_id)
        self.assertEqual(integrate_activities[0]["agent"], "orchestrator")
        self.assertEqual(integrate_activities[0]["plan_step"], 1)
        self.assertEqual(integrate_activities[0]["integration_type"], "addition")

    def test_discard_thread(self):
        """Test discarding a thread."""
        # Discard thread
        result = discard_thread(
            memory=self.memory,
            thread_id=self.thread_id,
            agent="orchestrator",
            reason="Thread is no longer relevant"
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread status
        thread_meta = self.memory["thread_history"][1][self.thread_id]
        self.assertEqual(thread_meta["status"], "discarded")
        self.assertIn("Thread is no longer relevant", thread_meta["summary"])
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][self.thread_id]
        self.assertEqual(thread_messages[0]["status"], "discarded")
        self.assertIn("Thread is no longer relevant", thread_messages[0]["summary"])
        
        # Check loop trace
        thread_activity = self.memory["loop_trace"][1]["thread_activity"]
        discard_activities = [a for a in thread_activity if a["action"] == "thread_discarded"]
        self.assertEqual(len(discard_activities), 1)
        self.assertEqual(discard_activities[0]["thread_id"], self.thread_id)
        self.assertEqual(discard_activities[0]["agent"], "orchestrator")
        self.assertEqual(discard_activities[0]["reason"], "Thread is no longer relevant")

    def test_reopen_thread(self):
        """Test reopening a thread."""
        # First close the thread
        close_thread(
            memory=self.memory,
            thread_id=self.thread_id,
            agent="orchestrator",
            summary="Thread closed for testing"
        )
        
        # Reopen thread
        result = reopen_thread(
            memory=self.memory,
            thread_id=self.thread_id,
            agent="orchestrator",
            reason="Further discussion needed"
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread status
        thread_meta = self.memory["thread_history"][1][self.thread_id]
        self.assertEqual(thread_meta["status"], "open")
        self.assertIsNone(thread_meta["summary"])  # Summary should be cleared
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][self.thread_id]
        self.assertEqual(thread_messages[0]["status"], "open")
        self.assertIsNone(thread_messages[0]["summary"])  # Summary should be cleared
        
        # Check loop trace
        thread_activity = self.memory["loop_trace"][1]["thread_activity"]
        reopen_activities = [a for a in thread_activity if a["action"] == "thread_reopened"]
        self.assertEqual(len(reopen_activities), 1)
        self.assertEqual(reopen_activities[0]["thread_id"], self.thread_id)
        self.assertEqual(reopen_activities[0]["agent"], "orchestrator")
        self.assertEqual(reopen_activities[0]["previous_status"], "closed")
        self.assertEqual(reopen_activities[0]["reason"], "Further discussion needed")

    def test_batch_close_inactive_threads(self):
        """Test batch closing inactive threads."""
        # Create additional threads
        thread_id2 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="nova",
            role="agent",
            message="Another test thread",
            timestamp="2025-04-20T11:00:00Z"  # Older timestamp to make it inactive
        )
        
        thread_id3 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="ash",
            role="agent",
            message="Yet another test thread",
            timestamp="2025-04-20T11:30:00Z"  # Older timestamp to make it inactive
        )
        
        # Batch close inactive threads
        with patch('datetime.datetime') as mock_datetime:
            # Mock current time to be 1 hour after thread creation
            mock_datetime.now.return_value = datetime.datetime.fromisoformat("2025-04-20T13:00:00Z")
            mock_datetime.fromisoformat = datetime.datetime.fromisoformat
            
            result = batch_close_inactive_threads(
                memory=self.memory,
                loop_id=1,
                agent="orchestrator",
                inactivity_threshold_minutes=30,
                max_threads=10
            )
        
        # Check result
        self.assertTrue(result["success"])
        self.assertEqual(result["closed"], 3)  # All 3 threads should be closed
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["skipped"], 0)
        
        # Check thread statuses
        self.assertEqual(self.memory["thread_history"][1][self.thread_id]["status"], "closed")
        self.assertEqual(self.memory["thread_history"][1][thread_id2]["status"], "closed")
        self.assertEqual(self.memory["thread_history"][1][thread_id3]["status"], "closed")

    def test_get_thread_lifecycle_history(self):
        """Test getting thread lifecycle history."""
        # Create a thread with multiple lifecycle events
        thread_id = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="Lifecycle test thread",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        # Close thread
        close_thread(
            memory=self.memory,
            thread_id=thread_id,
            agent="orchestrator",
            summary="Thread closed for testing"
        )
        
        # Reopen thread
        reopen_thread(
            memory=self.memory,
            thread_id=thread_id,
            agent="orchestrator",
            reason="Further discussion needed"
        )
        
        # Integrate thread
        integrate_thread(
            memory=self.memory,
            thread_id=thread_id,
            agent="orchestrator",
            plan_step=1,
            integration_type="addition"
        )
        
        # Get lifecycle history
        history = get_thread_lifecycle_history(
            memory=self.memory,
            thread_id=thread_id
        )
        
        # Check history
        self.assertEqual(len(history), 4)  # Created, closed, reopened, integrated
        
        # Check event types
        event_actions = [event["action"] for event in history]
        self.assertIn("thread_created", event_actions)
        self.assertIn("thread_status_updated", event_actions)  # or thread_closed
        self.assertIn("thread_reopened", event_actions)
        self.assertIn("thread_integrated", event_actions)
        
        # Check chronological order
        timestamps = [event.get("timestamp", "") for event in history]
        self.assertEqual(timestamps, sorted(timestamps))

if __name__ == "__main__":
    unittest.main()
