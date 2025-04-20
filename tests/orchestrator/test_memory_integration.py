"""
Tests for the memory integration module.

This module contains tests for the memory_integration.py module, which provides
functionality for integrating nested comments with the memory system.
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
from orchestrator.modules.memory_integration import (
    initialize_thread_memory,
    store_thread_in_memory,
    store_reply_in_memory,
    store_thread_summary_in_memory,
    retrieve_threads_from_memory,
    retrieve_thread_messages_from_memory,
    retrieve_thread_summaries_from_memory,
    export_threads_to_chat_messages,
    import_chat_messages_to_threads
)

class TestMemoryIntegration(unittest.TestCase):
    """Test cases for the memory integration module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock memory dictionary
        self.memory = {}
        
        # Initialize thread memory
        initialize_thread_memory(self.memory)
        
        # Create test thread data
        self.thread_id = "thread-123"
        self.thread_data = {
            "message_id": "msg-123",
            "loop_id": 1,
            "thread_id": self.thread_id,
            "parent_id": None,
            "agent": "hal",
            "role": "agent",
            "message": "This is a test thread",
            "timestamp": "2025-04-20T12:00:00Z",
            "depth": 0,
            "status": "open",
            "file": None,
            "summary": None,
            "actionable": False,
            "tags": ["test"],
            "topic_hash": None,
            "plan_integration": None,
            "thread_metadata": {
                "created_at": "2025-04-20T12:00:00Z",
                "last_updated_at": "2025-04-20T12:00:00Z",
                "reply_count": 0,
                "participants": ["hal"]
            }
        }
        
        # Create test reply data
        self.reply_data = {
            "message_id": "msg-456",
            "loop_id": 1,
            "thread_id": self.thread_id,
            "parent_id": "msg-123",
            "agent": "nova",
            "role": "agent",
            "message": "This is a reply",
            "timestamp": "2025-04-20T12:05:00Z",
            "depth": 1,
            "status": "open",
            "file": None,
            "summary": None,
            "actionable": False,
            "tags": [],
            "topic_hash": None,
            "plan_integration": None,
            "thread_metadata": None
        }
        
        # Initialize loop trace
        self.memory["loop_trace"] = {
            1: {
                "thread_activity": [],
                "thread_summaries": []
            }
        }

    def test_initialize_thread_memory(self):
        """Test initializing thread memory."""
        # Create a fresh memory dictionary
        memory = {}
        
        # Initialize thread memory
        result = initialize_thread_memory(memory)
        
        # Check result
        self.assertTrue(result)
        
        # Check memory structures
        self.assertIn("thread_history", memory)
        self.assertIn("thread_messages", memory)
        self.assertIn("thread_summaries", memory)
        
        # Check that structures are empty dictionaries
        self.assertEqual(memory["thread_history"], {})
        self.assertEqual(memory["thread_messages"], {})
        self.assertEqual(memory["thread_summaries"], {})

    def test_store_thread_in_memory(self):
        """Test storing a thread in memory."""
        # Store thread in memory
        result = store_thread_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            thread_data=self.thread_data
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread history
        self.assertIn(1, self.memory["thread_history"])
        self.assertIn(self.thread_id, self.memory["thread_history"][1])
        
        # Check thread metadata
        thread_meta = self.memory["thread_history"][1][self.thread_id]
        self.assertEqual(thread_meta["status"], "open")
        self.assertEqual(thread_meta["creator"], "hal")
        self.assertEqual(thread_meta["reply_count"], 0)
        self.assertEqual(thread_meta["participants"], ["hal"])
        
        # Check thread messages
        self.assertIn(self.thread_id, self.memory["thread_messages"])
        self.assertEqual(len(self.memory["thread_messages"][self.thread_id]), 1)
        self.assertEqual(self.memory["thread_messages"][self.thread_id][0]["message"], "This is a test thread")
        
        # Check loop trace
        self.assertEqual(len(self.memory["loop_trace"][1]["thread_activity"]), 1)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][0]["action"], "thread_stored")
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][0]["thread_id"], self.thread_id)

    def test_store_reply_in_memory(self):
        """Test storing a reply in memory."""
        # First store the thread
        store_thread_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            thread_data=self.thread_data
        )
        
        # Store reply in memory
        result = store_reply_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            reply_data=self.reply_data
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread metadata
        thread_meta = self.memory["thread_history"][1][self.thread_id]
        self.assertEqual(thread_meta["reply_count"], 1)
        self.assertEqual(set(thread_meta["participants"]), set(["hal", "nova"]))
        
        # Check thread messages
        self.assertEqual(len(self.memory["thread_messages"][self.thread_id]), 2)
        self.assertEqual(self.memory["thread_messages"][self.thread_id][1]["message"], "This is a reply")
        self.assertEqual(self.memory["thread_messages"][self.thread_id][1]["parent_id"], "msg-123")
        
        # Check loop trace
        self.assertEqual(len(self.memory["loop_trace"][1]["thread_activity"]), 2)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["action"], "reply_stored")
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["thread_id"], self.thread_id)

    def test_store_thread_summary_in_memory(self):
        """Test storing a thread summary in memory."""
        # First store the thread
        store_thread_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            thread_data=self.thread_data
        )
        
        # Store thread summary
        result = store_thread_summary_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            summary="This is a test summary",
            agent="orchestrator"
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread metadata
        thread_meta = self.memory["thread_history"][1][self.thread_id]
        self.assertEqual(thread_meta["summary"], "This is a test summary")
        
        # Check thread messages
        self.assertEqual(self.memory["thread_messages"][self.thread_id][0]["summary"], "This is a test summary")
        
        # Check thread summaries
        self.assertIn(1, self.memory["thread_summaries"])
        self.assertIn(self.thread_id, self.memory["thread_summaries"][1])
        self.assertEqual(self.memory["thread_summaries"][1][self.thread_id]["summary"], "This is a test summary")
        
        # Check loop trace
        self.assertEqual(len(self.memory["loop_trace"][1]["thread_activity"]), 2)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["action"], "summary_stored")
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["thread_id"], self.thread_id)
        self.assertEqual(self.memory["loop_trace"][1]["thread_activity"][1]["summary"], "This is a test summary")

    def test_retrieve_threads_from_memory(self):
        """Test retrieving threads from memory."""
        # Store multiple threads
        store_thread_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            thread_data=self.thread_data
        )
        
        thread_id2 = "thread-456"
        thread_data2 = self.thread_data.copy()
        thread_data2["thread_id"] = thread_id2
        thread_data2["message_id"] = "msg-789"
        thread_data2["message"] = "Another test thread"
        thread_data2["agent"] = "nova"
        thread_data2["thread_metadata"]["participants"] = ["nova"]
        
        store_thread_in_memory(
            memory=self.memory,
            thread_id=thread_id2,
            thread_data=thread_data2
        )
        
        # Retrieve all threads
        threads = retrieve_threads_from_memory(self.memory)
        
        # Check threads
        self.assertEqual(len(threads), 2)
        thread_ids = [thread["thread_id"] for thread in threads]
        self.assertIn(self.thread_id, thread_ids)
        self.assertIn(thread_id2, thread_ids)
        
        # Retrieve threads by loop ID
        threads = retrieve_threads_from_memory(self.memory, loop_id=1)
        self.assertEqual(len(threads), 2)
        
        # Retrieve threads by agent
        threads = retrieve_threads_from_memory(self.memory, agent="hal")
        self.assertEqual(len(threads), 1)
        self.assertEqual(threads[0]["thread_id"], self.thread_id)
        
        threads = retrieve_threads_from_memory(self.memory, agent="nova")
        self.assertEqual(len(threads), 1)
        self.assertEqual(threads[0]["thread_id"], thread_id2)

    def test_retrieve_thread_messages_from_memory(self):
        """Test retrieving thread messages from memory."""
        # Store thread and reply
        store_thread_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            thread_data=self.thread_data
        )
        
        store_reply_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            reply_data=self.reply_data
        )
        
        # Retrieve thread messages
        messages = retrieve_thread_messages_from_memory(
            memory=self.memory,
            thread_id=self.thread_id
        )
        
        # Check messages
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["message"], "This is a test thread")
        self.assertEqual(messages[1]["message"], "This is a reply")

    def test_retrieve_thread_summaries_from_memory(self):
        """Test retrieving thread summaries from memory."""
        # Store thread and summary
        store_thread_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            thread_data=self.thread_data
        )
        
        store_thread_summary_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            summary="This is a test summary",
            agent="orchestrator"
        )
        
        # Store another thread and summary
        thread_id2 = "thread-456"
        thread_data2 = self.thread_data.copy()
        thread_data2["thread_id"] = thread_id2
        thread_data2["message_id"] = "msg-789"
        thread_data2["message"] = "Another test thread"
        
        store_thread_in_memory(
            memory=self.memory,
            thread_id=thread_id2,
            thread_data=thread_data2
        )
        
        store_thread_summary_in_memory(
            memory=self.memory,
            thread_id=thread_id2,
            summary="Another test summary",
            agent="orchestrator"
        )
        
        # Retrieve all summaries
        summaries = retrieve_thread_summaries_from_memory(self.memory)
        
        # Check summaries
        self.assertEqual(len(summaries), 2)
        summary_threads = [s["thread_id"] for s in summaries]
        self.assertIn(self.thread_id, summary_threads)
        self.assertIn(thread_id2, summary_threads)
        
        # Retrieve summaries by loop ID
        summaries = retrieve_thread_summaries_from_memory(self.memory, loop_id=1)
        self.assertEqual(len(summaries), 2)

    def test_export_threads_to_chat_messages(self):
        """Test exporting threads to chat messages."""
        # Store thread and reply
        store_thread_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            thread_data=self.thread_data
        )
        
        store_reply_in_memory(
            memory=self.memory,
            thread_id=self.thread_id,
            reply_data=self.reply_data
        )
        
        # Export threads to chat messages
        result = export_threads_to_chat_messages(
            memory=self.memory,
            loop_id=1
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check chat messages
        self.assertIn("chat_messages", self.memory)
        self.assertEqual(len(self.memory["chat_messages"]), 2)
        
        # Check root message
        root_message = self.memory["chat_messages"][0]
        self.assertEqual(root_message["message"], "This is a test thread")
        self.assertEqual(root_message["agent"], "hal")
        self.assertEqual(root_message["role"], "agent")
        self.assertEqual(root_message["thread_id"], self.thread_id)
        self.assertEqual(root_message["message_id"], "msg-123")
        
        # Check reply
        reply = self.memory["chat_messages"][1]
        self.assertEqual(reply["message"], "This is a reply")
        self.assertEqual(reply["agent"], "nova")
        self.assertEqual(reply["role"], "agent")
        self.assertEqual(reply["thread_id"], self.thread_id)
        self.assertEqual(reply["message_id"], "msg-456")
        self.assertEqual(reply["parent_id"], "msg-123")
        self.assertEqual(reply["depth"], 1)

    def test_import_chat_messages_to_threads(self):
        """Test importing chat messages to threads."""
        # Create chat messages
        self.memory["chat_messages"] = [
            {
                "role": "agent",
                "agent": "hal",
                "message": "This is a test thread",
                "loop": 1,
                "timestamp": "2025-04-20T12:00:00Z",
                "thread_id": self.thread_id,
                "message_id": "msg-123",
                "status": "open"
            },
            {
                "role": "agent",
                "agent": "nova",
                "message": "This is a reply",
                "loop": 1,
                "timestamp": "2025-04-20T12:05:00Z",
                "thread_id": self.thread_id,
                "message_id": "msg-456",
                "parent_id": "msg-123",
                "depth": 1
            }
        ]
        
        # Import chat messages to threads
        result = import_chat_messages_to_threads(
            memory=self.memory,
            loop_id=1
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread history
        self.assertIn(1, self.memory["thread_history"])
        self.assertIn(self.thread_id, self.memory["thread_history"][1])
        
        # Check thread messages
        self.assertIn(self.thread_id, self.memory["thread_messages"])
        self.assertEqual(len(self.memory["thread_messages"][self.thread_id]), 2)
        
        # Check root message
        root_message = self.memory["thread_messages"][self.thread_id][0]
        self.assertEqual(root_message["message"], "This is a test thread")
        self.assertEqual(root_message["agent"], "hal")
        self.assertEqual(root_message["role"], "agent")
        self.assertEqual(root_message["message_id"], "msg-123")
        
        # Check reply
        reply = self.memory["thread_messages"][self.thread_id][1]
        self.assertEqual(reply["message"], "This is a reply")
        self.assertEqual(reply["agent"], "nova")
        self.assertEqual(reply["role"], "agent")
        self.assertEqual(reply["message_id"], "msg-456")
        self.assertEqual(reply["parent_id"], "msg-123")
        self.assertEqual(reply["depth"], 1)

if __name__ == "__main__":
    unittest.main()
