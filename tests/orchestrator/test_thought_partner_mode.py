"""
Unit tests for the Orchestrator Thought Partner Mode.

This module tests the functionality of the Thought Partner Mode, including:
- Prompt analysis
- Reflection question generation
- Memory storage and retrieval
- Mode dispatcher integration
"""

import unittest
import datetime
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

from orchestrator.modes.thought_partner import (
    analyze_prompt,
    generate_reflection_questions,
    store_prompt_analysis,
    get_last_prompt_analysis
)
from orchestrator.mode_dispatcher import ModeDispatcher, MODE_THOUGHT_PARTNER, MODE_ARCHITECT, MODE_SAGE


class TestThoughtPartnerMode(unittest.TestCase):
    """Test cases for the Orchestrator Thought Partner Mode."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory = {
            "loop_trace": {},
            "prompt_analysis": {}
        }
        self.project_id = "test-project"
        self.loop_id = 123
        
        # Sample prompts for testing
        self.clear_prompt = "Create a user authentication system with secure password hashing and JWT token generation."
        self.ambiguous_prompt = "Build a simple dashboard with some filters for the data."
        self.empty_prompt = ""
        self.excited_prompt = "I'm so excited to build an amazing new interface for our users!"
        self.complex_prompt = """
            I need a comprehensive data analytics platform that can ingest data from multiple sources,
            process it in real-time, and display it in an intuitive dashboard with various visualization
            options. The system should support filtering, sorting, and exporting of data.
        """

    def test_analyze_prompt_with_clear_prompt(self):
        """Test analyze_prompt with a clear, specific prompt."""
        analysis = analyze_prompt(self.clear_prompt)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn("interpreted_intent", analysis)
        self.assertIn("confidence_score", analysis)
        self.assertIn("emotional_tone", analysis)
        self.assertIn("ambiguous_phrases", analysis)
        
        self.assertGreaterEqual(analysis["confidence_score"], 0.5)
        self.assertEqual(analysis["interpreted_intent"], "Create a user authentication system with secure password hashing and jwt token generation")

    def test_analyze_prompt_with_ambiguous_prompt(self):
        """Test analyze_prompt with an ambiguous prompt."""
        analysis = analyze_prompt(self.ambiguous_prompt)
        
        self.assertIsInstance(analysis, dict)
        self.assertGreater(len(analysis["ambiguous_phrases"]), 0)
        self.assertIn("simple", analysis["ambiguous_phrases"])
        self.assertIn("dashboard", analysis["ambiguous_phrases"])
        self.assertIn("filter", analysis["ambiguous_phrases"])
        self.assertIn("data", analysis["ambiguous_phrases"])
        self.assertLess(analysis["confidence_score"], 0.5)

    def test_analyze_prompt_with_empty_prompt(self):
        """Test analyze_prompt with an empty prompt."""
        analysis = analyze_prompt(self.empty_prompt)
        
        self.assertIsInstance(analysis, dict)
        self.assertEqual(analysis["confidence_score"], 0.0)
        self.assertEqual(analysis["interpreted_intent"], "")
        self.assertEqual(analysis["emotional_tone"], "neutral")
        self.assertEqual(analysis["ambiguous_phrases"], [])

    def test_analyze_prompt_detects_emotional_tone(self):
        """Test that analyze_prompt correctly detects emotional tone."""
        analysis = analyze_prompt(self.excited_prompt)
        
        self.assertEqual(analysis["emotional_tone"], "excited")

    def test_generate_reflection_questions_with_ambiguous_prompt(self):
        """Test generate_reflection_questions with an ambiguous prompt analysis."""
        analysis = analyze_prompt(self.ambiguous_prompt)
        questions = generate_reflection_questions(analysis)
        
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)
        self.assertLessEqual(len(questions), 3)  # Default max_questions is 3

    def test_generate_reflection_questions_with_clear_prompt(self):
        """Test generate_reflection_questions with a clear prompt analysis."""
        analysis = analyze_prompt(self.clear_prompt)
        questions = generate_reflection_questions(analysis)
        
        self.assertIsInstance(questions, list)
        # Even with a clear prompt, we should get at least one question
        self.assertGreater(len(questions), 0)

    def test_generate_reflection_questions_with_custom_max(self):
        """Test generate_reflection_questions with a custom max_questions value."""
        analysis = analyze_prompt(self.ambiguous_prompt)
        questions = generate_reflection_questions(analysis, max_questions=1)
        
        self.assertIsInstance(questions, list)
        self.assertEqual(len(questions), 1)

    def test_store_prompt_analysis(self):
        """Test store_prompt_analysis stores data correctly in memory."""
        analysis = analyze_prompt(self.clear_prompt)
        updated_memory = store_prompt_analysis(self.project_id, self.loop_id, analysis, self.memory)
        
        self.assertIn("prompt_analysis", updated_memory)
        self.assertIn(str(self.loop_id), updated_memory["prompt_analysis"])
        
        stored_analysis = updated_memory["prompt_analysis"][str(self.loop_id)]
        self.assertEqual(stored_analysis["project_id"], self.project_id)
        self.assertEqual(stored_analysis["loop_id"], self.loop_id)
        self.assertIn("timestamp", stored_analysis)
        self.assertIn("reflection_questions", stored_analysis)

    def test_store_prompt_analysis_with_loop_trace(self):
        """Test store_prompt_analysis also stores in loop_trace if it exists."""
        # Set up loop_trace for this test
        self.memory["loop_trace"][str(self.loop_id)] = {}
        
        analysis = analyze_prompt(self.clear_prompt)
        updated_memory = store_prompt_analysis(self.project_id, self.loop_id, analysis, self.memory)
        
        self.assertIn("prompt_analysis", updated_memory["loop_trace"][str(self.loop_id)])
        self.assertEqual(
            updated_memory["loop_trace"][str(self.loop_id)]["prompt_analysis"]["interpreted_intent"],
            analysis["interpreted_intent"]
        )

    def test_get_last_prompt_analysis(self):
        """Test get_last_prompt_analysis retrieves the latest analysis."""
        # Store multiple analyses with different timestamps
        analysis1 = analyze_prompt(self.clear_prompt)
        analysis2 = analyze_prompt(self.ambiguous_prompt)
        
        # Store with older timestamp
        analysis1_with_meta = analysis1.copy()
        analysis1_with_meta["timestamp"] = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat()
        analysis1_with_meta["project_id"] = self.project_id
        analysis1_with_meta["loop_id"] = self.loop_id
        self.memory["prompt_analysis"]["1"] = analysis1_with_meta
        
        # Store with newer timestamp
        analysis2_with_meta = analysis2.copy()
        analysis2_with_meta["timestamp"] = datetime.datetime.now().isoformat()
        analysis2_with_meta["project_id"] = self.project_id
        analysis2_with_meta["loop_id"] = self.loop_id + 1
        self.memory["prompt_analysis"]["2"] = analysis2_with_meta
        
        # Get the latest analysis
        latest_analysis = get_last_prompt_analysis(self.project_id, self.memory)
        
        self.assertIsNotNone(latest_analysis)
        self.assertEqual(latest_analysis["loop_id"], self.loop_id + 1)
        self.assertEqual(latest_analysis["interpreted_intent"], analysis2["interpreted_intent"])

    def test_get_last_prompt_analysis_with_empty_memory(self):
        """Test get_last_prompt_analysis with empty memory."""
        latest_analysis = get_last_prompt_analysis(self.project_id, {})
        
        self.assertIsNone(latest_analysis)

    def test_get_last_prompt_analysis_with_different_project(self):
        """Test get_last_prompt_analysis with a different project ID."""
        analysis = analyze_prompt(self.clear_prompt)
        analysis_with_meta = analysis.copy()
        analysis_with_meta["timestamp"] = datetime.datetime.now().isoformat()
        analysis_with_meta["project_id"] = "other-project"
        analysis_with_meta["loop_id"] = self.loop_id
        self.memory["prompt_analysis"]["1"] = analysis_with_meta
        
        latest_analysis = get_last_prompt_analysis(self.project_id, self.memory)
        
        self.assertIsNone(latest_analysis)

    def test_mode_dispatcher_initialization(self):
        """Test ModeDispatcher initialization."""
        dispatcher = ModeDispatcher()
        
        self.assertEqual(dispatcher.active_mode, MODE_ARCHITECT)
        self.assertTrue(dispatcher.sage_mode_enabled)
        
        # Test with custom config
        config = {
            "default_mode": MODE_THOUGHT_PARTNER,
            "sage_mode_enabled": False
        }
        dispatcher = ModeDispatcher(config)
        
        self.assertEqual(dispatcher.active_mode, MODE_THOUGHT_PARTNER)
        self.assertFalse(dispatcher.sage_mode_enabled)

    def test_mode_dispatcher_set_mode(self):
        """Test ModeDispatcher.set_mode."""
        dispatcher = ModeDispatcher()
        
        # Test setting valid modes
        dispatcher.set_mode(MODE_THOUGHT_PARTNER)
        self.assertEqual(dispatcher.active_mode, MODE_THOUGHT_PARTNER)
        
        dispatcher.set_mode(MODE_SAGE)
        self.assertEqual(dispatcher.active_mode, MODE_SAGE)
        
        # Test setting invalid mode
        dispatcher.set_mode("invalid_mode")
        self.assertEqual(dispatcher.active_mode, MODE_ARCHITECT)  # Should default to ARCHITECT

    def test_mode_dispatcher_toggle_sage_mode(self):
        """Test ModeDispatcher.toggle_sage_mode."""
        dispatcher = ModeDispatcher()
        
        # Test disabling Sage Mode
        dispatcher.toggle_sage_mode(False)
        self.assertFalse(dispatcher.sage_mode_enabled)
        
        # Test enabling Sage Mode (should also set mode to THOUGHT_PARTNER)
        dispatcher.toggle_sage_mode(True)
        self.assertTrue(dispatcher.sage_mode_enabled)
        self.assertEqual(dispatcher.active_mode, MODE_THOUGHT_PARTNER)

    def test_mode_dispatcher_should_analyze_prompt(self):
        """Test ModeDispatcher.should_analyze_prompt."""
        dispatcher = ModeDispatcher()
        
        # Test in ARCHITECT mode with short prompt
        dispatcher.set_mode(MODE_ARCHITECT)
        self.assertFalse(dispatcher.should_analyze_prompt("Short prompt"))
        
        # Test in ARCHITECT mode with long prompt
        long_prompt = " ".join(["word"] * 51)  # 51 words
        self.assertTrue(dispatcher.should_analyze_prompt(long_prompt))
        
        # Test in THOUGHT_PARTNER mode (should always analyze)
        dispatcher.set_mode(MODE_THOUGHT_PARTNER)
        self.assertTrue(dispatcher.should_analyze_prompt("Short prompt"))
        
        # Test in SAGE mode with sage_mode_enabled=True
        dispatcher.set_mode(MODE_SAGE)
        dispatcher.sage_mode_enabled = True
        self.assertTrue(dispatcher.should_analyze_prompt("Short prompt"))
        
        # Test in SAGE mode with sage_mode_enabled=False
        dispatcher.sage_mode_enabled = False
        self.assertFalse(dispatcher.should_analyze_prompt("Short prompt"))

    def test_mode_dispatcher_process_prompt(self):
        """Test ModeDispatcher.process_prompt."""
        dispatcher = ModeDispatcher()
        dispatcher.set_mode(MODE_THOUGHT_PARTNER)
        
        result = dispatcher.process_prompt(self.ambiguous_prompt, self.project_id, self.loop_id, self.memory)
        
        self.assertEqual(result["mode"], MODE_THOUGHT_PARTNER)
        self.assertTrue(result["prompt_analyzed"])
        self.assertIsNotNone(result["analysis"])
        self.assertIsNotNone(result["reflection_questions"])
        
        # Check that analysis was stored in memory
        self.assertIn(str(self.loop_id), self.memory["prompt_analysis"])

    def test_mode_dispatcher_get_previous_analysis(self):
        """Test ModeDispatcher.get_previous_analysis."""
        dispatcher = ModeDispatcher()
        
        # Store an analysis
        analysis = analyze_prompt(self.clear_prompt)
        self.memory = store_prompt_analysis(self.project_id, self.loop_id, analysis, self.memory)
        
        # Get the previous analysis
        previous_analysis = dispatcher.get_previous_analysis(self.project_id, self.memory)
        
        self.assertIsNotNone(previous_analysis)
        self.assertEqual(previous_analysis["project_id"], self.project_id)
        self.assertEqual(previous_analysis["loop_id"], self.loop_id)

    def test_integration_with_low_confidence(self):
        """Test integration with a prompt that has low confidence."""
        dispatcher = ModeDispatcher()
        dispatcher.set_mode(MODE_THOUGHT_PARTNER)
        
        result = dispatcher.process_prompt(self.ambiguous_prompt, self.project_id, self.loop_id, self.memory)
        
        self.assertTrue(result["prompt_analyzed"])
        self.assertLess(result["analysis"]["confidence_score"], 0.7)
        self.assertIsNotNone(result["reflection_questions"])
        self.assertGreater(len(result["reflection_questions"]), 0)

    def test_integration_with_high_confidence(self):
        """Test integration with a prompt that has high confidence."""
        dispatcher = ModeDispatcher()
        dispatcher.set_mode(MODE_THOUGHT_PARTNER)
        
        # Use a more specific prompt that should have higher confidence
        specific_prompt = "Create a REST API with Node.js and Express that has endpoints for user authentication, product management, and order processing."
        
        result = dispatcher.process_prompt(specific_prompt, self.project_id, self.loop_id, self.memory)
        
        self.assertTrue(result["prompt_analyzed"])
        # Even with high confidence, we might still generate questions
        if result["analysis"]["confidence_score"] >= 0.7 and not result["analysis"]["ambiguous_phrases"]:
            # If confidence is high and no ambiguity, reflection questions might be None
            pass
        else:
            # Otherwise, we should have reflection questions
            self.assertIsNotNone(result["reflection_questions"])


if __name__ == "__main__":
    unittest.main()
