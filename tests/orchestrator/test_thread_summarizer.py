"""
Tests for the thread summarizer module.

This module contains tests for the thread_summarizer.py module, which provides
functionality for generating summaries of nested comment threads.
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
from orchestrator.modules.thread_summarizer import (
    generate_thread_summary,
    close_thread_with_summary,
    get_thread_summaries_for_loop,
    get_actionable_threads,
    batch_summarize_threads
)

# Import nested_comments for setup
from orchestrator.modules.nested_comments import (
    create_thread,
    reply_to_thread
)

class TestThreadSummarizer(unittest.TestCase):
    """Test cases for the thread summarizer module."""

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
        
        # Create test threads
        self.thread_id1 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="Discussion about Python error handling",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        # Add replies to thread 1
        self.reply_id1 = reply_to_thread(
            memory=self.memory,
            thread_id=self.thread_id1,
            parent_id=self.memory["thread_messages"][self.thread_id1][0]["message_id"],
            agent="nova",
            role="agent",
            message="I think we should use try-except blocks more consistently",
            timestamp="2025-04-20T12:05:00Z"
        )
        
        self.reply_id2 = reply_to_thread(
            memory=self.memory,
            thread_id=self.thread_id1,
            parent_id=self.memory["thread_messages"][self.thread_id1][0]["message_id"],
            agent="ash",
            role="agent",
            message="We should also consider adding custom exception classes",
            timestamp="2025-04-20T12:10:00Z"
        )
        
        # Create another thread
        self.thread_id2 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="critic",
            role="agent",
            message="Performance concerns with current implementation",
            timestamp="2025-04-20T12:15:00Z"
        )
        
        # Mark thread 2 as actionable
        self.memory["thread_messages"][self.thread_id2][0]["actionable"] = True
        if 1 not in self.memory["thread_history"]:
            self.memory["thread_history"][1] = {}
        self.memory["thread_history"][1][self.thread_id2] = {
            "status": "open",
            "creator": "critic",
            "created_at": "2025-04-20T12:15:00Z",
            "last_updated_at": "2025-04-20T12:15:00Z",
            "reply_count": 0,
            "participants": ["critic"],
            "actionable": True
        }

    @patch('orchestrator.modules.thread_summarizer.generate_summary_with_llm')
    def test_generate_thread_summary(self, mock_generate_summary):
        """Test generating a thread summary."""
        # Mock the LLM summary generation
        mock_generate_summary.return_value = "Thread discusses Python error handling with suggestions for try-except blocks and custom exception classes."
        
        # Generate summary
        summary = generate_thread_summary(
            memory=self.memory,
            thread_id=self.thread_id1,
            max_length=200
        )
        
        # Check summary
        self.assertIsNotNone(summary)
        self.assertEqual(summary, "Thread discusses Python error handling with suggestions for try-except blocks and custom exception classes.")
        
        # Verify LLM was called with correct messages
        mock_generate_summary.assert_called_once()
        call_args = mock_generate_summary.call_args[0]
        self.assertEqual(len(call_args[0]), 3)  # Should include all 3 messages

    @patch('orchestrator.modules.thread_summarizer.generate_summary_with_llm')
    def test_close_thread_with_summary(self, mock_generate_summary):
        """Test closing a thread with a summary."""
        # Mock the LLM summary generation
        mock_generate_summary.return_value = "Thread discusses Python error handling with suggestions for try-except blocks and custom exception classes."
        
        # Close thread with summary
        result = close_thread_with_summary(
            memory=self.memory,
            thread_id=self.thread_id1,
            agent="orchestrator",
            max_summary_length=200
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread status and summary
        thread_meta = self.memory["thread_history"][1][self.thread_id1]
        self.assertEqual(thread_meta["status"], "closed")
        self.assertEqual(thread_meta["summary"], "Thread discusses Python error handling with suggestions for try-except blocks and custom exception classes.")
        
        # Check thread messages
        thread_messages = self.memory["thread_messages"][self.thread_id1]
        self.assertEqual(thread_messages[0]["status"], "closed")
        self.assertEqual(thread_messages[0]["summary"], "Thread discusses Python error handling with suggestions for try-except blocks and custom exception classes.")
        
        # Check thread summaries
        self.assertIn(1, self.memory["thread_summaries"])
        self.assertIn(self.thread_id1, self.memory["thread_summaries"][1])
        self.assertEqual(self.memory["thread_summaries"][1][self.thread_id1]["summary"], "Thread discusses Python error handling with suggestions for try-except blocks and custom exception classes.")
        
        # Check loop trace
        thread_activity = self.memory["loop_trace"][1]["thread_activity"]
        summary_activities = [a for a in thread_activity if a["action"] == "summary_stored"]
        self.assertEqual(len(summary_activities), 1)
        self.assertEqual(summary_activities[0]["thread_id"], self.thread_id1)
        self.assertEqual(summary_activities[0]["summary"], "Thread discusses Python error handling with suggestions for try-except blocks and custom exception classes.")

    def test_get_thread_summaries_for_loop(self):
        """Test getting thread summaries for a loop."""
        # Add summaries to threads
        if 1 not in self.memory["thread_summaries"]:
            self.memory["thread_summaries"][1] = {}
        
        self.memory["thread_summaries"][1][self.thread_id1] = {
            "thread_id": self.thread_id1,
            "summary": "Thread discusses Python error handling",
            "created_at": "2025-04-20T12:30:00Z",
            "agent": "orchestrator",
            "status": "closed"
        }
        
        self.memory["thread_summaries"][1][self.thread_id2] = {
            "thread_id": self.thread_id2,
            "summary": "Performance concerns with current implementation",
            "created_at": "2025-04-20T12:35:00Z",
            "agent": "orchestrator",
            "status": "open"
        }
        
        # Get summaries
        summaries = get_thread_summaries_for_loop(self.memory, 1)
        
        # Check summaries
        self.assertEqual(len(summaries), 2)
        thread_ids = [s["thread_id"] for s in summaries]
        self.assertIn(self.thread_id1, thread_ids)
        self.assertIn(self.thread_id2, thread_ids)
        
        # Check filtering by status
        closed_summaries = get_thread_summaries_for_loop(self.memory, 1, status="closed")
        self.assertEqual(len(closed_summaries), 1)
        self.assertEqual(closed_summaries[0]["thread_id"], self.thread_id1)

    def test_get_actionable_threads(self):
        """Test getting actionable threads."""
        # Get actionable threads
        actionable_threads = get_actionable_threads(self.memory, 1)
        
        # Check actionable threads
        self.assertEqual(len(actionable_threads), 1)
        self.assertEqual(actionable_threads[0]["thread_id"], self.thread_id2)
        self.assertTrue(actionable_threads[0]["actionable"])

    @patch('orchestrator.modules.thread_summarizer.generate_summary_with_llm')
    def test_batch_summarize_threads(self, mock_generate_summary):
        """Test batch summarizing threads."""
        # Mock the LLM summary generation
        mock_generate_summary.return_value = "Batch generated summary"
        
        # Batch summarize threads
        result = batch_summarize_threads(
            memory=self.memory,
            loop_id=1,
            agent="orchestrator",
            max_threads=5,
            max_summary_length=200
        )
        
        # Check result
        self.assertTrue(result["success"])
        self.assertEqual(result["summarized"], 2)
        self.assertEqual(result["failed"], 0)
        
        # Check thread summaries
        self.assertIn(1, self.memory["thread_summaries"])
        self.assertIn(self.thread_id1, self.memory["thread_summaries"][1])
        self.assertIn(self.thread_id2, self.memory["thread_summaries"][1])
        self.assertEqual(self.memory["thread_summaries"][1][self.thread_id1]["summary"], "Batch generated summary")
        self.assertEqual(self.memory["thread_summaries"][1][self.thread_id2]["summary"], "Batch generated summary")

if __name__ == "__main__":
    unittest.main()
