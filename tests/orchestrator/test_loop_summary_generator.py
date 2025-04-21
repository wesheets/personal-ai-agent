"""
Tests for the loop summary generator module.

This module contains tests for the loop summary generator module to ensure it correctly
generates, stores, and retrieves summaries of completed loops.
"""

import unittest
import json
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.loop_summary_generator import (
    generate_loop_summary,
    store_loop_summary,
    get_loop_summary,
    _get_status_emoji,
    _extract_key_events,
    _loop_exists
)

class TestLoopSummaryGenerator(unittest.TestCase):
    """Test cases for the loop summary generator module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample loop data for testing
        self.project_id = "test_project_001"
        self.loop_id = 42
        
        # Sample memory with loop data
        self.memory = {
            "loop_trace": {
                "42": {
                    "status": "completed",
                    "start_time": "2025-04-20T10:00:00Z",
                    "end_time": "2025-04-20T10:30:00Z",
                    "operator_feedback": {
                        "status": "accepted",
                        "timestamp": "2025-04-20T10:35:00Z"
                    }
                }
            },
            "agent_actions": {
                "42": [
                    {
                        "agent": "hal",
                        "action_type": "code_generation",
                        "timestamp": "2025-04-20T10:05:00Z",
                        "details": {
                            "file": "LoginForm.jsx",
                            "language": "jsx"
                        }
                    },
                    {
                        "agent": "critic",
                        "action_type": "rejection",
                        "timestamp": "2025-04-20T10:15:00Z",
                        "details": {
                            "reason": "logic bug",
                            "file": "LoginForm.jsx"
                        }
                    },
                    {
                        "agent": "hal",
                        "action_type": "fix",
                        "timestamp": "2025-04-20T10:20:00Z",
                        "details": {
                            "file": "LoginForm.jsx",
                            "fix_type": "logic correction"
                        }
                    }
                ]
            },
            "loop_plans": [
                {
                    "loop_id": 42,
                    "goals": ["Refactor login interface"],
                    "agents": ["nova", "hal", "critic"],
                    "planned_files": ["LoginForm.jsx", "authUtils.js"],
                    "confirmed": True,
                    "agent_selection_trace": [
                        {
                            "agent": "nova",
                            "trust_score": 0.92,
                            "reason": "UI design expertise"
                        },
                        {
                            "agent": "hal",
                            "trust_score": 0.85,
                            "reason": "validation and logic implementation"
                        },
                        {
                            "agent": "critic",
                            "trust_score": 0.75,
                            "reason": "Critical agent added for validation purposes"
                        }
                    ]
                }
            ]
        }
        
        # Memory with rerouted loop
        self.rerouted_memory = {
            "loop_trace": {
                "43": {
                    "status": "rerouted",
                    "start_time": "2025-04-20T11:00:00Z",
                    "end_time": "2025-04-20T11:30:00Z",
                    "rerouted_from": 42
                }
            },
            "agent_actions": {
                "43": [
                    {
                        "agent": "nova",
                        "action_type": "code_generation",
                        "timestamp": "2025-04-20T11:05:00Z",
                        "details": {
                            "file": "LoginForm.jsx",
                            "language": "jsx"
                        }
                    }
                ]
            },
            "loop_plans": [
                {
                    "loop_id": 43,
                    "goals": ["Improve login interface accessibility"],
                    "agents": ["nova", "critic"],
                    "planned_files": ["LoginForm.jsx"],
                    "confirmed": True
                }
            ]
        }
        
        # Memory with rejected loop
        self.rejected_memory = {
            "loop_trace": {
                "44": {
                    "status": "rejected",
                    "start_time": "2025-04-20T12:00:00Z",
                    "end_time": "2025-04-20T12:30:00Z",
                    "operator_feedback": {
                        "status": "rejected",
                        "reason": "Does not meet accessibility requirements",
                        "timestamp": "2025-04-20T12:35:00Z"
                    }
                }
            },
            "agent_actions": {
                "44": [
                    {
                        "agent": "nova",
                        "action_type": "code_generation",
                        "timestamp": "2025-04-20T12:05:00Z",
                        "details": {
                            "file": "ProfilePage.jsx",
                            "language": "jsx"
                        }
                    }
                ]
            },
            "loop_plans": [
                {
                    "loop_id": 44,
                    "goals": ["Create user profile page"],
                    "agents": ["nova", "critic"],
                    "planned_files": ["ProfilePage.jsx", "profileStyles.css"],
                    "confirmed": True
                }
            ]
        }
        
        # Empty memory for edge cases
        self.empty_memory = {}
    
    def test_generate_loop_summary_with_multiple_agents(self):
        """Test generating a summary with multiple agents."""
        summary = generate_loop_summary(self.project_id, self.loop_id, self.memory)
        
        # Verify summary structure and content
        self.assertIn(f"Loop {self.loop_id} Summary:", summary)
        self.assertIn("• Plan: \"Refactor login interface\"", summary)
        self.assertIn("nova", summary)
        self.assertIn("hal", summary)
        self.assertIn("• Files: LoginForm.jsx, authUtils.js", summary)
        self.assertIn("CRITIC flagged a logic bug, fixed by HAL", summary)
        self.assertIn("• Operator accepted the result", summary)
    
    def test_generate_loop_summary_with_rerouted_loop(self):
        """Test generating a summary for a rerouted loop."""
        summary = generate_loop_summary(self.project_id, 43, self.rerouted_memory)
        
        # Verify summary structure and content
        self.assertIn("Loop 43 Summary:", summary)
        self.assertIn("🔄", summary)  # Rerouted emoji
        self.assertIn("• Plan: \"Improve login interface accessibility\"", summary)
        self.assertIn("• Rerouted from Loop 42", summary)
    
    def test_generate_loop_summary_with_rejection(self):
        """Test generating a summary for a rejected loop."""
        summary = generate_loop_summary(self.project_id, 44, self.rejected_memory)
        
        # Verify summary structure and content
        self.assertIn("Loop 44 Summary:", summary)
        self.assertIn("❌", summary)  # Rejected emoji
        self.assertIn("• Operator rejected the result", summary)
        self.assertIn("Does not meet accessibility requirements", summary)
    
    def test_store_loop_summary(self):
        """Test storing a loop summary in memory."""
        # Create a test summary
        test_summary = "Loop 42 Summary:\n• Test summary content"
        
        # Create a copy of memory to avoid modifying the original
        memory_copy = json.loads(json.dumps(self.memory))
        
        # Store the summary
        store_loop_summary(self.project_id, self.loop_id, test_summary, memory_copy)
        
        # Verify summary is stored in loop_summaries
        self.assertIn("loop_summaries", memory_copy)
        self.assertIn(str(self.loop_id), memory_copy["loop_summaries"])
        self.assertEqual(test_summary, memory_copy["loop_summaries"][str(self.loop_id)]["summary"])
        
        # Verify summary is stored in loop_trace
        self.assertEqual(test_summary, memory_copy["loop_trace"][str(self.loop_id)]["summary"]["text"])
        
        # Verify summary is added to chat_messages
        self.assertIn("chat_messages", memory_copy)
        chat_message = memory_copy["chat_messages"][-1]
        self.assertEqual("orchestrator", chat_message["role"])
        self.assertIn(test_summary, chat_message["message"])
        self.assertEqual(self.loop_id, chat_message["loop_id"])
    
    def test_get_loop_summary_existing(self):
        """Test retrieving an existing loop summary."""
        # Create a test summary and store it
        test_summary = "Loop 42 Summary:\n• Test summary content"
        memory_copy = json.loads(json.dumps(self.memory))
        store_loop_summary(self.project_id, self.loop_id, test_summary, memory_copy)
        
        # Retrieve the summary
        retrieved_summary = get_loop_summary(self.project_id, self.loop_id, memory_copy)
        
        # Verify retrieved summary matches stored summary
        self.assertEqual(test_summary, retrieved_summary)
    
    def test_get_loop_summary_nonexistent(self):
        """Test retrieving a nonexistent loop summary."""
        # Try to retrieve a summary for a nonexistent loop
        retrieved_summary = get_loop_summary(self.project_id, 999, self.memory)
        
        # Verify no summary is returned
        self.assertIsNone(retrieved_summary)
    
    def test_get_loop_summary_generate_if_missing(self):
        """Test retrieving a summary that doesn't exist but can be generated."""
        # Create a copy of memory without loop_summaries
        memory_copy = json.loads(json.dumps(self.memory))
        if "loop_summaries" in memory_copy:
            del memory_copy["loop_summaries"]
        
        # Retrieve the summary (should generate a new one)
        retrieved_summary = get_loop_summary(self.project_id, self.loop_id, memory_copy)
        
        # Verify a summary was generated and returned
        self.assertIsNotNone(retrieved_summary)
        self.assertIn(f"Loop {self.loop_id} Summary:", retrieved_summary)
    
    def test_get_status_emoji(self):
        """Test getting status emojis for different loop statuses."""
        self.assertEqual("✅", _get_status_emoji("completed"))
        self.assertEqual("✅", _get_status_emoji("accepted"))
        self.assertEqual("❌", _get_status_emoji("rejected"))
        self.assertEqual("🔄", _get_status_emoji("rerouted"))
        self.assertEqual("🔄", _get_status_emoji("modified"))
        self.assertEqual("⏳", _get_status_emoji("in_progress"))
        self.assertEqual("ℹ️", _get_status_emoji("unknown"))
    
    def test_extract_key_events(self):
        """Test extracting key events from agent actions."""
        agent_actions = self.memory["agent_actions"]["42"]
        loop_trace = self.memory["loop_trace"]["42"]
        
        key_events = _extract_key_events(agent_actions, loop_trace)
        
        # Verify key events extraction
        self.assertEqual(1, len(key_events))
        self.assertIn("CRITIC flagged a logic bug, fixed by HAL", key_events[0])
    
    def test_loop_exists(self):
        """Test checking if a loop exists in memory."""
        # Test existing loop
        self.assertTrue(_loop_exists(self.loop_id, self.memory))
        
        # Test nonexistent loop
        self.assertFalse(_loop_exists(999, self.memory))
        
        # Test with empty memory
        self.assertFalse(_loop_exists(self.loop_id, self.empty_memory))
    
    def test_empty_loop_edge_case(self):
        """Test handling of empty loop edge case."""
        # Create memory with minimal loop data
        minimal_memory = {
            "loop_trace": {
                "45": {
                    "status": "completed"
                }
            },
            "loop_plans": [
                {
                    "loop_id": 45,
                    "goals": [],
                    "agents": [],
                    "planned_files": []
                }
            ]
        }
        
        # Generate summary for minimal loop
        summary = generate_loop_summary(self.project_id, 45, minimal_memory)
        
        # Verify summary is generated despite minimal data
        self.assertIn("Loop 45 Summary:", summary)
    
    def test_memory_injection_safety(self):
        """Test that the module safely handles memory injection attempts."""
        # Create memory with potentially dangerous content
        dangerous_memory = {
            "loop_trace": {
                "46": {
                    "status": "completed",
                    "operator_feedback": {
                        "status": "<script>alert('XSS')</script>",
                        "reason": "function() { return malicious_code(); }"
                    }
                }
            },
            "loop_plans": [
                {
                    "loop_id": 46,
                    "goals": ["<img src=x onerror=alert('XSS')>"],
                    "agents": ["nova; DROP TABLE users;--"]
                }
            ]
        }
        
        # Generate summary for dangerous memory
        summary = generate_loop_summary(self.project_id, 46, dangerous_memory)
        
        # Verify summary is generated without executing dangerous content
        self.assertIn("Loop 46 Summary:", summary)
        self.assertNotIn("alert('XSS')", summary)  # Content should be treated as text, not code

if __name__ == "__main__":
    unittest.main()
