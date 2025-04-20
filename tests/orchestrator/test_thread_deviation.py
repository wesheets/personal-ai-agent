"""
Tests for the thread deviation module.

This module contains tests for the thread_deviation.py module, which provides
functionality for tracking historical deviations in threads and analyzing patterns.
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
from orchestrator.modules.thread_deviation import (
    initialize_deviation_memory,
    record_thread_deviation,
    resolve_thread_deviation,
    update_deviation_patterns,
    get_thread_deviations,
    get_deviation_patterns,
    detect_potential_deviations,
    generate_deviation_report
)

# Import nested_comments for setup
from orchestrator.modules.nested_comments import create_thread, reply_to_thread

class TestThreadDeviation(unittest.TestCase):
    """Test cases for the thread deviation module."""

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
                    "plan_deviations": []
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
            message="We should consider a different approach to authentication",
            timestamp="2025-04-20T12:00:00Z"
        )
        
        # Add reply to thread 1
        self.reply_id1 = reply_to_thread(
            memory=self.memory,
            thread_id=self.thread_id1,
            parent_id=self.memory["thread_messages"][self.thread_id1][0]["message_id"],
            agent="nova",
            role="agent",
            message="I think OAuth would be better than the current JWT implementation",
            timestamp="2025-04-20T12:05:00Z"
        )
        
        # Create another thread
        self.thread_id2 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="ash",
            role="agent",
            message="The current database schema needs optimization",
            timestamp="2025-04-20T12:10:00Z"
        )
        
        # Initialize deviation memory
        initialize_deviation_memory(self.memory)

    def test_initialize_deviation_memory(self):
        """Test initializing deviation memory."""
        # Create a fresh memory dictionary
        memory = {}
        
        # Initialize deviation memory
        result = initialize_deviation_memory(memory)
        
        # Check result
        self.assertTrue(result)
        
        # Check memory structures
        self.assertIn("thread_deviations", memory)
        self.assertIn("deviation_patterns", memory)
        
        # Check that structures are empty dictionaries
        self.assertEqual(memory["thread_deviations"], {})
        self.assertEqual(memory["deviation_patterns"], {})

    def test_record_thread_deviation(self):
        """Test recording a thread deviation."""
        # Record deviation
        result = record_thread_deviation(
            memory=self.memory,
            thread_id=self.thread_id1,
            deviation_type="scope_expansion",
            agent="orchestrator",
            description="Thread proposes changing authentication mechanism which is out of scope",
            severity="high",
            related_plan_step=2
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check thread deviations
        self.assertIn(1, self.memory["thread_deviations"])
        self.assertIn(self.thread_id1, self.memory["thread_deviations"][1])
        self.assertEqual(len(self.memory["thread_deviations"][1][self.thread_id1]), 1)
        
        # Check deviation details
        deviation = self.memory["thread_deviations"][1][self.thread_id1][0]
        self.assertEqual(deviation["deviation_type"], "scope_expansion")
        self.assertEqual(deviation["agent"], "orchestrator")
        self.assertEqual(deviation["description"], "Thread proposes changing authentication mechanism which is out of scope")
        self.assertEqual(deviation["severity"], "high")
        self.assertEqual(deviation["related_plan_step"], 2)
        self.assertEqual(deviation["message_count"], 2)
        self.assertEqual(set(deviation["participants"]), set(["hal", "nova"]))
        self.assertFalse(deviation["resolved"])
        
        # Check loop trace
        thread_activity = self.memory["loop_trace"][1]["thread_activity"]
        deviation_activities = [a for a in thread_activity if a["action"] == "thread_deviation_recorded"]
        self.assertEqual(len(deviation_activities), 1)
        self.assertEqual(deviation_activities[0]["thread_id"], self.thread_id1)
        self.assertEqual(deviation_activities[0]["deviation_type"], "scope_expansion")
        
        # Check plan deviations
        plan_deviations = self.memory["loop_trace"][1]["plan_deviations"]
        thread_deviations = [d for d in plan_deviations if d["type"] == "thread_deviation" and d["thread_id"] == self.thread_id1]
        self.assertEqual(len(thread_deviations), 1)
        self.assertEqual(thread_deviations[0]["deviation_type"], "scope_expansion")

    def test_resolve_thread_deviation(self):
        """Test resolving a thread deviation."""
        # First record a deviation
        record_thread_deviation(
            memory=self.memory,
            thread_id=self.thread_id1,
            deviation_type="scope_expansion",
            agent="orchestrator",
            description="Thread proposes changing authentication mechanism which is out of scope",
            severity="high"
        )
        
        # Resolve deviation
        result = resolve_thread_deviation(
            memory=self.memory,
            thread_id=self.thread_id1,
            deviation_index=0,
            agent="orchestrator",
            resolution_description="Decided to keep current authentication mechanism and document reasons"
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check deviation status
        deviation = self.memory["thread_deviations"][1][self.thread_id1][0]
        self.assertTrue(deviation["resolved"])
        self.assertEqual(deviation["resolution_description"], "Decided to keep current authentication mechanism and document reasons")
        self.assertEqual(deviation["resolved_by"], "orchestrator")
        self.assertIn("resolved_at", deviation)
        
        # Check loop trace
        thread_activity = self.memory["loop_trace"][1]["thread_activity"]
        resolution_activities = [a for a in thread_activity if a["action"] == "thread_deviation_resolved"]
        self.assertEqual(len(resolution_activities), 1)
        self.assertEqual(resolution_activities[0]["thread_id"], self.thread_id1)
        self.assertEqual(resolution_activities[0]["deviation_type"], "scope_expansion")
        self.assertEqual(resolution_activities[0]["resolution_description"], "Decided to keep current authentication mechanism and document reasons")

    def test_update_deviation_patterns(self):
        """Test updating deviation patterns."""
        # Get thread messages
        thread_messages = self.memory["thread_messages"][self.thread_id1]
        
        # Update patterns
        result = update_deviation_patterns(
            memory=self.memory,
            deviation_type="scope_expansion",
            thread_messages=thread_messages
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check patterns
        self.assertIn("scope_expansion", self.memory["deviation_patterns"])
        pattern = self.memory["deviation_patterns"]["scope_expansion"]
        
        # Check pattern details
        self.assertEqual(pattern["count"], 1)
        self.assertIn("hal", pattern["common_agents"])
        self.assertIn("nova", pattern["common_agents"])
        self.assertIn("authentication", pattern["common_words"])
        self.assertIn("oauth", pattern["common_words"])
        self.assertIn("2", pattern["message_count_distribution"])
        self.assertIn("2", pattern["participant_count_distribution"])

    def test_get_thread_deviations(self):
        """Test getting thread deviations."""
        # Record deviations for multiple threads
        record_thread_deviation(
            memory=self.memory,
            thread_id=self.thread_id1,
            deviation_type="scope_expansion",
            agent="orchestrator",
            description="Thread proposes changing authentication mechanism which is out of scope",
            severity="high"
        )
        
        record_thread_deviation(
            memory=self.memory,
            thread_id=self.thread_id2,
            deviation_type="technical_concern",
            agent="orchestrator",
            description="Thread raises concerns about database schema that weren't in original plan",
            severity="medium"
        )
        
        # Get all deviations
        deviations = get_thread_deviations(self.memory)
        
        # Check deviations
        self.assertEqual(len(deviations), 2)
        
        # Get deviations by thread ID
        thread1_deviations = get_thread_deviations(self.memory, thread_id=self.thread_id1)
        self.assertEqual(len(thread1_deviations), 1)
        self.assertEqual(thread1_deviations[0]["thread_id"], self.thread_id1)
        self.assertEqual(thread1_deviations[0]["deviation_type"], "scope_expansion")
        
        # Get deviations by loop ID
        loop_deviations = get_thread_deviations(self.memory, loop_id=1)
        self.assertEqual(len(loop_deviations), 2)
        
        # Get deviations by type
        scope_deviations = get_thread_deviations(self.memory, deviation_type="scope_expansion")
        self.assertEqual(len(scope_deviations), 1)
        self.assertEqual(scope_deviations[0]["deviation_type"], "scope_expansion")
        
        # Get deviations by resolved status
        unresolved_deviations = get_thread_deviations(self.memory, resolved=False)
        self.assertEqual(len(unresolved_deviations), 2)
        
        # Resolve one deviation
        resolve_thread_deviation(
            memory=self.memory,
            thread_id=self.thread_id1,
            deviation_index=0,
            agent="orchestrator",
            resolution_description="Resolved"
        )
        
        # Get resolved deviations
        resolved_deviations = get_thread_deviations(self.memory, resolved=True)
        self.assertEqual(len(resolved_deviations), 1)
        self.assertEqual(resolved_deviations[0]["thread_id"], self.thread_id1)

    def test_get_deviation_patterns(self):
        """Test getting deviation patterns."""
        # Create patterns for multiple deviation types
        thread_messages1 = self.memory["thread_messages"][self.thread_id1]
        update_deviation_patterns(
            memory=self.memory,
            deviation_type="scope_expansion",
            thread_messages=thread_messages1
        )
        
        thread_messages2 = self.memory["thread_messages"][self.thread_id2]
        update_deviation_patterns(
            memory=self.memory,
            deviation_type="technical_concern",
            thread_messages=thread_messages2
        )
        
        # Get all patterns
        patterns = get_deviation_patterns(self.memory)
        
        # Check patterns
        self.assertEqual(len(patterns), 2)
        self.assertIn("scope_expansion", patterns)
        self.assertIn("technical_concern", patterns)
        
        # Get patterns by type
        scope_patterns = get_deviation_patterns(self.memory, deviation_type="scope_expansion")
        self.assertEqual(len(scope_patterns), 1)
        self.assertIn("scope_expansion", scope_patterns)
        
        # Get patterns with minimum count
        update_deviation_patterns(
            memory=self.memory,
            deviation_type="scope_expansion",
            thread_messages=thread_messages1
        )
        
        min_count_patterns = get_deviation_patterns(self.memory, min_count=2)
        self.assertEqual(len(min_count_patterns), 1)
        self.assertIn("scope_expansion", min_count_patterns)
        self.assertEqual(min_count_patterns["scope_expansion"]["count"], 2)

    @patch('datetime.datetime')
    def test_detect_potential_deviations(self, mock_datetime):
        """Test detecting potential deviations."""
        # Mock current time
        mock_datetime.now.return_value = datetime.datetime.fromisoformat("2025-04-20T13:00:00Z")
        mock_datetime.fromisoformat = datetime.datetime.fromisoformat
        
        # Create patterns from existing threads
        thread_messages1 = self.memory["thread_messages"][self.thread_id1]
        update_deviation_patterns(
            memory=self.memory,
            deviation_type="scope_expansion",
            thread_messages=thread_messages1
        )
        
        # Create a new thread with similar content
        thread_id3 = create_thread(
            memory=self.memory,
            loop_id=1,
            agent="hal",
            role="agent",
            message="I think we should replace the current authentication system with SAML",
            timestamp="2025-04-20T12:30:00Z"
        )
        
        reply_to_thread(
            memory=self.memory,
            thread_id=thread_id3,
            parent_id=self.memory["thread_messages"][thread_id3][0]["message_id"],
            agent="nova",
            role="agent",
            message="Yes, SAML would provide better enterprise integration than JWT",
            timestamp="2025-04-20T12:35:00Z"
        )
        
        # Update pattern count to meet threshold
        update_deviation_patterns(
            memory=self.memory,
            deviation_type="scope_expansion",
            thread_messages=thread_messages1
        )
        update_deviation_patterns(
            memory=self.memory,
            deviation_type="scope_expansion",
            thread_messages=thread_messages1
        )
        
        # Detect potential deviations
        potential_deviations = detect_potential_deviations(
            memory=self.memory,
            loop_id=1,
            threshold=0.5
        )
        
        # Check potential deviations
        self.assertGreaterEqual(len(potential_deviations), 1)
        
        # Check that the new thread is detected
        thread3_deviations = [d for d in potential_deviations if d["thread_id"] == thread_id3]
        self.assertEqual(len(thread3_deviations), 1)
        self.assertEqual(thread3_deviations[0]["deviation_type"], "scope_expansion")
        self.assertGreaterEqual(thread3_deviations[0]["similarity_score"], 0.5)

    def test_generate_deviation_report(self):
        """Test generating a deviation report."""
        # Record deviations
        record_thread_deviation(
            memory=self.memory,
            thread_id=self.thread_id1,
            deviation_type="scope_expansion",
            agent="orchestrator",
            description="Thread proposes changing authentication mechanism which is out of scope",
            severity="high"
        )
        
        record_thread_deviation(
            memory=self.memory,
            thread_id=self.thread_id2,
            deviation_type="technical_concern",
            agent="orchestrator",
            description="Thread raises concerns about database schema that weren't in original plan",
            severity="medium"
        )
        
        # Resolve one deviation
        resolve_thread_deviation(
            memory=self.memory,
            thread_id=self.thread_id1,
            deviation_index=0,
            agent="orchestrator",
            resolution_description="Decided to keep current authentication mechanism"
        )
        
        # Generate report with all deviations
        report = generate_deviation_report(
            memory=self.memory,
            loop_id=1,
            include_patterns=True,
            include_unresolved=True,
            include_resolved=True
        )
        
        # Check report
        self.assertIn("summary", report)
        self.assertIn("deviations", report)
        self.assertIn("patterns", report)
        
        # Check summary
        self.assertEqual(report["summary"]["total_deviations"], 2)
        self.assertEqual(report["summary"]["resolved_deviations"], 1)
        self.assertEqual(report["summary"]["unresolved_deviations"], 1)
        
        # Check deviation types
        self.assertEqual(len(report["summary"]["deviation_types"]), 2)
        self.assertIn("scope_expansion", report["summary"]["deviation_types"])
        self.assertIn("technical_concern", report["summary"]["deviation_types"])
        
        # Check deviations
        self.assertEqual(len(report["deviations"]), 2)
        
        # Generate report with only unresolved deviations
        unresolved_report = generate_deviation_report(
            memory=self.memory,
            loop_id=1,
            include_patterns=False,
            include_unresolved=True,
            include_resolved=False
        )
        
        # Check unresolved report
        self.assertEqual(unresolved_report["summary"]["total_deviations"], 1)
        self.assertEqual(len(unresolved_report["deviations"]), 1)
        self.assertEqual(unresolved_report["deviations"][0]["thread_id"], self.thread_id2)
        self.assertNotIn("patterns", unresolved_report)

    def test_error_handling(self):
        """Test error handling for edge cases."""
        # Test with non-existent thread
        result = record_thread_deviation(
            memory=self.memory,
            thread_id="non-existent-thread",
            deviation_type="scope_expansion",
            agent="orchestrator",
            description="Test description"
        )
        self.assertFalse(result)
        
        # Test resolving non-existent deviation
        result = resolve_thread_deviation(
            memory=self.memory,
            thread_id=self.thread_id1,
            deviation_index=999,  # Non-existent index
            agent="orchestrator",
            resolution_description="Test resolution"
        )
        self.assertFalse(result)
        
        # Test with non-existent loop
        potential_deviations = detect_potential_deviations(
            memory=self.memory,
            loop_id=999,  # Non-existent loop
            threshold=0.5
        )
        self.assertEqual(len(potential_deviations), 0)

if __name__ == "__main__":
    unittest.main()
