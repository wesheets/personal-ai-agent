"""
Tests for the nested comments module.

This module contains tests for the nested_comments.py module, which provides
functionality for creating and managing nested comment threads.
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
from orchestrator.modules.nested_comments import (
    create_thread,
    reply_to_thread,
    get_thread_messages,
    get_threads_for_loop,
    update_thread_status,
    mark_thread_for_plan_revision,
    find_similar_threads,
    integrate_thread_with_plan
)

class TestNestedComments(unittest.TestCase):
    """Test cases for the nested comments module."""

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
                    "thread_summaries": []
                }
            },
            "chat_messages": []
        }

    def test_create_thread(self):
        """Test creating a new thread."""
        # Create a thread
        thread_id = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="This is a test thread",
            timestamp="2025-04-20T12:00:00Z"
        )

        # Check that thread was created
        self.assertIsNotNone(thread_id)
        self.assertIn(1, self.memory["thread_history"])
        self.assertIn(thread_id, self.memory["thread_history"][1])
        self.assertIn(thread_id, self.memory["thread_messages"])
        
        # Check thread metadata
        thread_meta = self.memory["thread_history"][1][thread_id]
        self.assertEqual(thread_meta["status"], "open")
        self.assertEqual(thread_meta["creator"], "hal")
        self.assertEqual(thread_meta["reply_count"], 0)
        self.assertEqual(thread_meta["participants"], ["hal"])
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][thread_id]
        self.assertEqual(len(thread_messages), 1)
        self.assertEqual(thread_messages[0]["message"], "This is a test thread")
        self.assertEqual(thread_messages[0]["agent"], "hal")
        self.assertEqual(thread_messages[0]["role"], "agent")
        self.assertEqual(thread_messages[0]["loop_id"], 1)
        self.assertEqual(thread_messages[0]["timestamp"], "2025-04-20T12:00:00Z")
        self.assertEqual(thread_messages[0]["depth"], 0)
        self.assertEqual(thread_messages[0]["status"], "open")
        
        # Check loop trace
        self.assertEqual(len(self.memory["loop_trace"][1]["thread_activity"]), 1)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][0]["action"], "thread_created")
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][0]["thread_id"], thread_id)

    def test_reply_to_thread(self):
        """Test replying to a thread."""
        # Create a thread
        thread_id = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="This is a test thread",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        # Reply to thread
        reply_id = reply_to_thread(
            memory=self.memory,
            thread_id=thread_id,
            parent_id=self.memory["thread_messages"][thread_id][0]["message_id"],
            agent="nova",
            role="agent",
            message="This is a reply",
            timestamp="2025-04-20T12:05:00Z"
        )
        
        # Check that reply was created
        self.assertIsNotNone(reply_id)
        
        # Check thread metadata
        thread_meta = self.memory["thread_history"][1][thread_id]
        self.assertEqual(thread_meta["reply_count"], 1)
        self.assertEqual(set(thread_meta["participants"]), set(["hal", "nova"]))
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][thread_id]
        self.assertEqual(len(thread_messages), 2)
        self.assertEqual(thread_messages[1]["message"], "This is a reply")
        self.assertEqual(thread_messages[1]["agent"], "nova")
        self.assertEqual(thread_messages[1]["role"], "agent")
        self.assertEqual(thread_messages[1]["parent_id"], thread_messages[0]["message_id"])
        self.assertEqual(thread_messages[1]["depth"], 1)
        
        # Check loop trace
        self.assertEqual(len(self.memory["loop_trace"][1]["thread_activity"]), 2)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["action"], "reply_created")
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["thread_id"], thread_id)

    def test_get_thread_messages(self):
        """Test getting thread messages."""
        # Create a thread
        thread_id = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="This is a test thread",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        # Reply to thread
        reply_to_thread(
            memory=self.memory,
            thread_id=thread_id,
            parent_id=self.memory["thread_messages"][thread_id][0]["message_id"],
            agent="nova",
            role="agent",
            message="This is a reply",
            timestamp="2025-04-20T12:05:00Z"
        )
        
        # Get thread messages
        messages = get_thread_messages(self.memory, thread_id)
        
        # Check messages
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["message"], "This is a test thread")
        self.assertEqual(messages[1]["message"], "This is a reply")

    def test_get_threads_for_loop(self):
        """Test getting threads for a loop."""
        # Create threads
        thread_id1 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="Thread 1",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        thread_id2 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="nova",
            role="agent",
            message="Thread 2",
            timestamp="2025-04-20T12:10:00Z"
        )
        
        # Create thread in different loop
        create_thread(
            memory=self.memory,
            loop_id=2,
            agent="ash",
            role="agent",
            message="Thread 3",
            timestamp="2025-04-20T12:20:00Z"
        )
        
        # Get threads for loop 1
        threads = get_threads_for_loop(self.memory, 1)
        
        # Check threads
        self.assertEqual(len(threads), 2)
        thread_ids = [thread["thread_id"] for thread in threads]
        self.assertIn(thread_id1, thread_ids)
        self.assertIn(thread_id2, thread_ids)

    def test_update_thread_status(self):
        """Test updating thread status."""
        # Create a thread
        thread_id = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="This is a test thread",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        # Update thread status
        result = update_thread_status(
            memory=self.memory,
            thread_id=thread_id,
            status="closed",
            summary="Thread closed for testing",
            agent="orchestrator"
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread metadata
        thread_meta = self.memory["thread_history"][1][thread_id]
        self.assertEqual(thread_meta["status"], "closed")
        self.assertEqual(thread_meta["summary"], "Thread closed for testing")
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][thread_id]
        self.assertEqual(thread_messages[0]["status"], "closed")
        self.assertEqual(thread_messages[0]["summary"], "Thread closed for testing")
        
        # Check loop trace
        self.assertEqual(len(self.memory["loop_trace"][1]["thread_activity"]), 2)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["action"], "thread_status_updated")
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["thread_id"], thread_id)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["status"], "closed")

    def test_mark_thread_for_plan_revision(self):
        """Test marking a thread for plan revision."""
        # Create a thread
        thread_id = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="This is a test thread",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        # Mark thread for plan revision
        result = mark_thread_for_plan_revision(
            memory=self.memory,
            thread_id=thread_id,
            agent="orchestrator"
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread metadata
        thread_meta = self.memory["thread_history"][1][thread_id]
        self.assertTrue(thread_meta["actionable"])
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][thread_id]
        self.assertTrue(thread_messages[0]["actionable"])
        
        # Check loop trace
        self.assertEqual(len(self.memory["loop_trace"][1]["thread_activity"]), 2)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["action"], "thread_marked_actionable")
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["thread_id"], thread_id)

    def test_find_similar_threads(self):
        """Test finding similar threads."""
        # Create threads with similar topics
        thread_id1 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="Discussion about Python error handling",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        thread_id2 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="nova",
            role="agent",
            message="Python exception handling best practices",
            timestamp="2025-04-20T12:10:00Z"
        )
        
        # Create thread with different topic
        thread_id3 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="ash",
            role="agent",
            message="JavaScript async/await patterns",
            timestamp="2025-04-20T12:20:00Z"
        )
        
        # Find similar threads to thread 1
        similar_threads = find_similar_threads(
            memory=self.memory,
            thread_id=thread_id1,
            max_results=5
        )
        
        # Check similar threads
        self.assertEqual(len(similar_threads), 1)
        self.assertEqual(similar_threads[0]["thread_id"], thread_id2)
        
        # Find similar threads to thread 3
        similar_threads = find_similar_threads(
            memory=self.memory,
            thread_id=thread_id3,
            max_results=5
        )
        
        # Check similar threads (should be empty)
        self.assertEqual(len(similar_threads), 0)

    def test_integrate_thread_with_plan(self):
        """Test integrating a thread with a plan."""
        # Create a thread
        thread_id = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="This is a test thread",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        # Add plan to loop trace
        self.memory["loop_trace"][1]["plan"] = {
            "steps": ["Step 1", "Step 2", "Step 3"]
        }
        
        # Integrate thread with plan
        result = integrate_thread_with_plan(
            memory=self.memory,
            thread_id=thread_id,
            plan_step=1,
            integration_type="addition",
            integration_summary="Added thread insights to step 2",
            agent="orchestrator"
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread metadata
        thread_meta = self.memory["thread_history"][1][thread_id]
        self.assertEqual(thread_meta["status"], "integrated")
        self.assertEqual(thread_meta["summary"], "Added thread insights to step 2")
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][thread_id]
        self.assertEqual(thread_messages[0]["status"], "integrated")
        self.assertEqual(thread_messages[0]["summary"], "Added thread insights to step 2")
        self.assertIsNotNone(thread_messages[0]["plan_integration"])
        self.assertEqual(thread_messages[0]["plan_integration"]["plan_step"], 1)
        self.assertEqual(thread_messages[0]["plan_integration"]["integration_type"], "addition")
        
        # Check loop trace
        self.assertEqual(len(self.memory["loop_trace"][1]["thread_activity"]), 2)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["action"], "thread_integrated")
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["thread_id"], thread_id)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["integration_type"], "addition")

if __name__ == "__main__":
    unittest.main()
