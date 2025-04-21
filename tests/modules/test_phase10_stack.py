"""
Unit tests for Phase 10 Sage Cognitive Stack modules:
- Thought Variant Generator
- Persona Mode Loader + Switcher
- Intent-Impact Emotional Feedback Analyzer
"""

import unittest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any

# Import modules to test
from orchestrator.modules.variant_generator import (
    generate_plan_variants,
    store_plan_variants,
    process_plan_with_variant_generator
)
from orchestrator.mode_dispatcher import (
    get_available_personas,
    select_persona_for_loop,
    load_persona,
    switch_persona,
    process_loop_with_persona_loader
)
from orchestrator.modules.intent_impact_analyzer import (
    analyze_intent_impact,
    store_intent_impact_analysis,
    process_loop_with_intent_impact_analyzer
)
from orchestrator.modules.loop_controller import (
    handle_loop_execution,
    handle_loop_completion
)

class TestThoughtVariantGenerator(unittest.TestCase):
    """Test cases for the Thought Variant Generator module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loop_id = "test_loop_001"
        self.memory = {}
        self.original_plan = {
            "steps": [
                {"step_id": 1, "description": "Analyze requirements"},
                {"step_id": 2, "description": "Implement solution"},
                {"step_id": 3, "description": "Test implementation"}
            ]
        }
    
    def test_generate_plan_variants(self):
        """Test generating plan variants."""
        config = {
            "enabled": True,
            "variants_count": 2,
            "tone_options": ["safe", "ambitious"],
            "min_belief_score": 0.7
        }
        
        result = generate_plan_variants(
            self.original_plan,
            self.loop_id,
            self.memory,
            config
        )
        
        # Check that the result contains the original plan and variants
        self.assertIn("original_plan", result)
        self.assertIn("variants", result)
        self.assertEqual(result["original_plan"], self.original_plan)
        
        # Check that the correct number of variants were generated
        variants = result["variants"]
        self.assertEqual(len(variants), 2)
        
        # Check that each variant has the required fields
        for variant in variants:
            self.assertIn("plan_id", variant)
            self.assertIn("tone", variant)
            self.assertIn("belief_score", variant)
            self.assertIn("steps", variant)
            
            # Check that the tone is one of the allowed options
            self.assertIn(variant["tone"], ["safe", "ambitious"])
            
            # Check that the belief score is within the expected range
            self.assertGreaterEqual(variant["belief_score"], 0.7)
            self.assertLessEqual(variant["belief_score"], 1.0)
            
            # Check that the steps were modified
            self.assertEqual(len(variant["steps"]), len(self.original_plan["steps"]))
    
    def test_store_plan_variants(self):
        """Test storing plan variants in memory."""
        variants_data = {
            "original_plan": self.original_plan,
            "variants": [
                {
                    "plan_id": "plan_a",
                    "tone": "safe",
                    "belief_score": 0.85,
                    "steps": []
                },
                {
                    "plan_id": "plan_b",
                    "tone": "ambitious",
                    "belief_score": 0.75,
                    "steps": []
                }
            ]
        }
        
        updated_memory = store_plan_variants(
            self.loop_id,
            variants_data,
            self.memory
        )
        
        # Check that the variants were stored in memory
        self.assertIn("loop_variants", updated_memory)
        self.assertEqual(len(updated_memory["loop_variants"]), 1)
        
        # Check that the stored variants have the correct format
        stored_variants = updated_memory["loop_variants"][0]
        self.assertEqual(stored_variants["loop_id"], self.loop_id)
        self.assertEqual(len(stored_variants["loop_variants"]), 2)
        
        # Check that the variants contain the expected data
        self.assertEqual(stored_variants["loop_variants"][0]["plan_id"], "plan_a")
        self.assertEqual(stored_variants["loop_variants"][0]["tone"], "safe")
        self.assertEqual(stored_variants["loop_variants"][0]["belief_score"], 0.85)
        
        self.assertEqual(stored_variants["loop_variants"][1]["plan_id"], "plan_b")
        self.assertEqual(stored_variants["loop_variants"][1]["tone"], "ambitious")
        self.assertEqual(stored_variants["loop_variants"][1]["belief_score"], 0.75)
    
    def test_process_plan_with_variant_generator(self):
        """Test processing a plan with the variant generator."""
        config = {
            "enabled": True,
            "variants_count": 2
        }
        
        result = process_plan_with_variant_generator(
            self.original_plan,
            self.loop_id,
            self.memory,
            config
        )
        
        # Check that the result has the expected fields
        self.assertIn("status", result)
        self.assertIn("memory", result)
        self.assertIn("message", result)
        self.assertIn("variants_count", result)
        self.assertIn("variants_data", result)
        
        # Check that the status is correct
        self.assertEqual(result["status"], "generated")
        
        # Check that the variants count is correct
        self.assertEqual(result["variants_count"], 2)
        
        # Check that the memory was updated
        self.assertIn("loop_variants", result["memory"])
    
    def test_variant_generator_disabled(self):
        """Test that the variant generator can be disabled."""
        config = {
            "enabled": False
        }
        
        result = process_plan_with_variant_generator(
            self.original_plan,
            self.loop_id,
            self.memory,
            config
        )
        
        # Check that the result has the expected fields
        self.assertIn("status", result)
        self.assertIn("memory", result)
        self.assertIn("message", result)
        self.assertIn("variants_count", result)
        
        # Check that the status is correct
        self.assertEqual(result["status"], "skipped")
        
        # Check that no variants were generated
        self.assertEqual(result["variants_count"], 0)
        
        # Check that the memory was not updated
        self.assertNotIn("loop_variants", result["memory"])


class TestPersonaModeLoader(unittest.TestCase):
    """Test cases for the Persona Mode Loader + Switcher module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loop_id = "test_loop_001"
        self.memory = {}
        self.prompt = "Please analyze the data and provide insights."
    
    def test_get_available_personas(self):
        """Test getting available personas."""
        personas = get_available_personas()
        
        # Check that all expected personas are available
        self.assertIn("SAGE", personas)
        self.assertIn("ARCHITECT", personas)
        self.assertIn("RESEARCHER", personas)
        self.assertIn("RITUALIST", personas)
        self.assertIn("INVENTOR", personas)
        
        # Check that each persona has the required fields
        for persona_name, persona_data in personas.items():
            self.assertIn("description", persona_data)
            self.assertIn("strengths", persona_data)
            self.assertIn("ideal_for", persona_data)
    
    def test_select_persona_for_loop(self):
        """Test selecting a persona for a loop based on the prompt."""
        config = {
            "auto_selection": True
        }
        
        # Test with a research-oriented prompt
        research_prompt = "Can you research the latest advancements in AI and analyze the data?"
        persona, details = select_persona_for_loop(
            self.loop_id,
            research_prompt,
            self.memory,
            config
        )
        
        # Check that the RESEARCHER persona was selected
        self.assertEqual(persona, "RESEARCHER")
        
        # Test with a creative prompt
        creative_prompt = "Let's create a new innovative solution to this problem!"
        persona, details = select_persona_for_loop(
            self.loop_id,
            creative_prompt,
            self.memory,
            config
        )
        
        # Check that the INVENTOR persona was selected
        self.assertEqual(persona, "INVENTOR")
    
    def test_load_persona(self):
        """Test loading a persona into memory."""
        persona_mode = "SAGE"
        
        updated_memory = load_persona(
            persona_mode,
            self.loop_id,
            self.memory
        )
        
        # Check that the persona context was stored in memory
        self.assertIn("persona_contexts", updated_memory)
        self.assertEqual(len(updated_memory["persona_contexts"]), 1)
        
        # Check that the stored persona context has the correct format
        stored_context = updated_memory["persona_contexts"][0]
        self.assertEqual(stored_context["loop_id"], self.loop_id)
        self.assertEqual(stored_context["persona_mode"], "SAGE")
        
        # Check that the current orchestrator persona was set
        self.assertEqual(updated_memory["orchestrator_persona"], "SAGE")
    
    def test_switch_persona(self):
        """Test switching from one persona to another."""
        # First load a persona
        memory_with_persona = load_persona(
            "ARCHITECT",
            self.loop_id,
            self.memory
        )
        
        # Then switch to a different persona
        updated_memory = switch_persona(
            "SAGE",
            self.loop_id,
            memory_with_persona,
            "Testing persona switching"
        )
        
        # Check that the persona was switched
        self.assertEqual(updated_memory["orchestrator_persona"], "SAGE")
        
        # Check that the switch event was stored
        self.assertIn("persona_switches", updated_memory)
        self.assertEqual(len(updated_memory["persona_switches"]), 1)
        
        # Check that the switch event has the correct format
        switch_event = updated_memory["persona_switches"][0]
        self.assertEqual(switch_event["loop_id"], self.loop_id)
        self.assertEqual(switch_event["from_persona"], "ARCHITECT")
        self.assertEqual(switch_event["to_persona"], "SAGE")
        self.assertEqual(switch_event["reason"], "Testing persona switching")
    
    def test_process_loop_with_persona_loader(self):
        """Test processing a loop with the persona loader."""
        config = {
            "enabled": True,
            "auto_selection": True
        }
        
        result = process_loop_with_persona_loader(
            self.loop_id,
            self.prompt,
            self.memory,
            config
        )
        
        # Check that the result has the expected fields
        self.assertIn("status", result)
        self.assertIn("memory", result)
        self.assertIn("message", result)
        self.assertIn("persona", result)
        self.assertIn("details", result)
        
        # Check that the status is correct
        self.assertEqual(result["status"], "loaded")
        
        # Check that the memory was updated
        self.assertIn("persona_contexts", result["memory"])
        self.assertIn("orchestrator_persona", result["memory"])
    
    def test_persona_loader_disabled(self):
        """Test that the persona loader can be disabled."""
        config = {
            "enabled": False
        }
        
        result = process_loop_with_persona_loader(
            self.loop_id,
            self.prompt,
            self.memory,
            config
        )
        
        # Check that the result has the expected fields
        self.assertIn("status", result)
        self.assertIn("memory", result)
        self.assertIn("message", result)
        self.assertIn("persona", result)
        
        # Check that the status is correct
        self.assertEqual(result["status"], "skipped")
        
        # Check that the memory was not updated
        self.assertNotIn("persona_contexts", result["memory"])


class TestIntentImpactAnalyzer(unittest.TestCase):
    """Test cases for the Intent-Impact Emotional Feedback Analyzer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loop_id = "test_loop_001"
        self.memory = {}
        self.prompt = "Can you reflect on this problem and provide a thoughtful analysis?"
        self.summary = "I've analyzed the problem from multiple perspectives and considered various factors."
    
    def test_analyze_intent_impact(self):
        """Test analyzing intent versus impact."""
        config = {
            "enabled": True,
            "confidence_delta_threshold": 0.15,
            "tone_mismatch_threshold": 0.6
        }
        
        result = analyze_intent_impact(
            self.loop_id,
            self.prompt,
            self.summary,
            self.memory,
            config
        )
        
        # Check that the result has the expected fields
        self.assertIn("loop_id", result)
        self.assertIn("intent_tone", result)
        self.assertIn("summary_tone", result)
        self.assertIn("intent_confidence", result)
        self.assertIn("summary_confidence", result)
        self.assertIn("impact_confidence_delta", result)
        self.assertIn("has_mismatch", result)
        self.assertIn("analysis_status", result)
        self.assertIn("timestamp", result)
        
        # Check that the analysis status is correct
        self.assertEqual(result["analysis_status"], "completed")
        
        # Check that the loop ID is correct
        self.assertEqual(result["loop_id"], self.loop_id)
    
    def test_intent_impact_mismatch_detection(self):
        """Test detecting a mismatch between intent and impact."""
        # Test with a reflective prompt but a vague summary
        reflective_prompt = "Can you reflect deeply on this complex issue and provide insights?"
        vague_summary = "There are several aspects to consider. It might be worth looking into further."
        
        result = analyze_intent_impact(
            self.loop_id,
            reflective_prompt,
            vague_summary,
            self.memory
        )
        
        # Check that a mismatch was detected
        self.assertTrue(result["has_mismatch"])
        
        # Check that a recommendation was provided
        self.assertIn("recommendation", result)
    
    def test_store_intent_impact_analysis(self):
        """Test storing intent-impact analysis in memory."""
        analysis_result = {
            "loop_id": self.loop_id,
            "intent_tone": "reflective",
            "summary_tone": "analytical",
            "intent_confidence": 0.8,
            "summary_confidence": 0.7,
            "impact_confidence_delta": -0.1,
            "has_mismatch": False,
            "analysis_status": "completed",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        updated_memory = store_intent_impact_analysis(
            analysis_result,
            self.memory
        )
        
        # Check that the analysis was stored in memory
        self.assertIn("intent_impact_analysis", updated_memory)
        self.assertEqual(len(updated_memory["intent_impact_analysis"]), 1)
        
        # Check that the stored analysis has the correct format
        stored_analysis = updated_memory["intent_impact_analysis"][0]
        self.assertEqual(stored_analysis["loop_id"], self.loop_id)
        self.assertEqual(stored_analysis["intent_tone"], "reflective")
        self.assertEqual(stored_analysis["summary_tone"], "analytical")
        
        # Check that no mismatch entry was created (since has_mismatch is False)
        self.assertNotIn("intent_impact_mismatch", updated_memory)
    
    def test_store_intent_impact_mismatch(self):
        """Test storing an intent-impact mismatch in memory."""
        analysis_result = {
            "loop_id": self.loop_id,
            "intent_tone": "reflective",
            "summary_tone": "vague",
            "intent_confidence": 0.8,
            "summary_confidence": 0.5,
            "impact_confidence_delta": -0.3,
            "has_mismatch": True,
            "recommendation": "Rerun SAGE to reclarify loop purpose",
            "analysis_status": "completed",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        updated_memory = store_intent_impact_analysis(
            analysis_result,
            self.memory
        )
        
        # Check that the analysis was stored in memory
        self.assertIn("intent_impact_analysis", updated_memory)
        
        # Check that the mismatch was stored in memory
        self.assertIn("intent_impact_mismatch", updated_memory)
        self.assertEqual(len(updated_memory["intent_impact_mismatch"]), 1)
        
        # Check that the stored mismatch has the correct format
        stored_mismatch = updated_memory["intent_impact_mismatch"][0]
        self.assertEqual(stored_mismatch["loop_id"], self.loop_id)
        self.assertEqual(stored_mismatch["intent_tone"], "reflective")
        self.assertEqual(stored_mismatch["summary_tone"], "vague")
        self.assertEqual(stored_mismatch["recommendation"], "Rerun SAGE to reclarify loop purpose")
    
    def test_process_loop_with_intent_impact_analyzer(self):
        """Test processing a loop with the intent-impact analyzer."""
        config = {
            "enabled": True,
            "confidence_delta_threshold": 0.15,
            "tone_mismatch_threshold": 0.6
        }
        
        result = process_loop_with_intent_impact_analyzer(
            self.loop_id,
            self.prompt,
            self.summary,
            self.memory,
            config
        )
        
        # Check that the result has the expected fields
        self.assertIn("status", result)
        self.assertIn("memory", result)
        self.assertIn("message", result)
        self.assertIn("has_mismatch", result)
        self.assertIn("analysis_result", result)
        
        # Check that the status is correct
        self.assertEqual(result["status"], "analyzed")
        
        # Check that the memory was updated
        self.assertIn("intent_impact_analysis", result["memory"])
    
    def test_intent_impact_analyzer_disabled(self):
        """Test that the intent-impact analyzer can be disabled."""
        config = {
            "enabled": False
        }
        
        result = process_loop_with_intent_impact_analyzer(
            self.loop_id,
            self.prompt,
            self.summary,
            self.memory,
            config
        )
        
        # Check that the result has the expected fields
        self.assertIn("status", result)
        self.assertIn("memory", result)
        self.assertIn("message", result)
        
        # Check that the status is correct
        self.assertEqual(result["status"], "skipped")
        
        # Check that the memory was not updated
        self.assertNotIn("intent_impact_analysis", result["memory"])


class TestLoopControllerIntegration(unittest.TestCase):
    """Test cases for the integration of Phase 10 modules with the loop controller."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loop_id = "test_loop_001"
        self.memory = {}
        self.prompt = "Can you analyze this data and provide insights?"
        self.plan = {
            "steps": [
                {"step_id": 1, "description": "Analyze data"},
                {"step_id": 2, "description": "Generate insights"},
                {"step_id": 3, "description": "Present findings"}
            ]
        }
        self.summary = "I've analyzed the data and found several interesting patterns."
        self.loop = {"status": "completed"}
        self.agent_logs = []
    
    @patch('orchestrator.modules.variant_generator.process_plan_with_variant_generator')
    @patch('orchestrator.mode_dispatcher.process_loop_with_persona_loader')
    @patch('orchestrator.modules.delusion_detector.detect_plan_delusion')
    def test_handle_loop_execution(self, mock_delusion, mock_persona, mock_variant):
        """Test handling loop execution with all Phase 10 modules."""
        # Mock the variant generator
        mock_variant.return_value = {
            "status": "generated",
            "memory": self.memory,
            "message": "Generated 2 plan variants",
            "variants_count": 2,
            "variants_data": {"variants": []}
        }
        
        # Mock the persona loader
        mock_persona.return_value = {
            "status": "loaded",
            "memory": self.memory,
            "message": "Loaded RESEARCHER persona",
            "persona": "RESEARCHER",
            "details": {}
        }
        
        # Mock the delusion detector
        mock_delusion.return_value = {
            "status": "ok",
            "memory": self.memory,
            "message": "No delusions detected"
        }
        
        # Call the function
        result = handle_loop_execution(
            self.plan,
            self.loop_id,
            self.prompt,
            self.memory
        )
        
        # Check that all modules were called
        mock_variant.assert_called_once()
        mock_persona.assert_called_once()
        mock_delusion.assert_called_once()
        
        # Check that the result has the expected fields
        self.assertIn("status", result)
        self.assertIn("memory", result)
        self.assertIn("message", result)
        self.assertIn("variants_count", result)
        self.assertIn("persona", result)
        
        # Check that the status is correct
        self.assertEqual(result["status"], "proceed")
        
        # Check that the variants count is correct
        self.assertEqual(result["variants_count"], 2)
        
        # Check that the persona is correct
        self.assertEqual(result["persona"], "RESEARCHER")
    
    @patch('orchestrator.modules.intent_impact_analyzer.process_loop_with_intent_impact_analyzer')
    @patch('orchestrator.modules.loop_controller.analyze_loop_with_historian_agent')
    @patch('orchestrator.modules.loop_controller.process_loop_with_ceo_agent')
    @patch('orchestrator.modules.loop_controller.process_loop_with_cto_agent')
    @patch('orchestrator.modules.loop_controller.process_loop_with_drift_engine')
    @patch('orchestrator.modules.loop_controller.process_loop_with_weekly_drift_report')
    def test_handle_loop_completion(self, mock_weekly, mock_drift, mock_cto, mock_ceo, mock_historian, mock_intent):
        """Test handling loop completion with all Phase 10 modules."""
        # Mock the intent-impact analyzer
        mock_intent.return_value = {
            "status": "analyzed",
            "memory": self.memory,
            "message": "Intent-impact analysis completed",
            "has_mismatch": False,
            "analysis_result": {}
        }
        
        # Mock the historian agent
        mock_historian.return_value = {
            "status": "analyzed",
            "memory": self.memory,
            "message": "Loop analyzed: alignment score 0.85, 0 missing beliefs"
        }
        
        # Mock the CEO agent
        mock_ceo.return_value = {
            "status": "analyzed",
            "memory": self.memory,
            "message": "Loop analyzed by CEO: insight with alignment score 0.80"
        }
        
        # Mock the CTO agent
        mock_cto.return_value = {
            "status": "analyzed",
            "memory": self.memory,
            "message": "CTO analysis: health score 0.90, alignment score 0.85"
        }
        
        # Mock the drift engine
        mock_drift.return_value = self.memory
        
        # Mock the weekly drift report
        mock_weekly.return_value = self.memory
        
        # Fix the mock setup to ensure intent-impact analyzer is called
        mock_intent.reset_mock()
        
        # Call the function
        result = handle_loop_completion(
            self.loop_id,
            self.summary,
            self.loop,
            self.plan,
            self.prompt,
            self.agent_logs,
            self.memory
        )
        
        # Check that all modules were called
        mock_intent.assert_called_once()
        mock_historian.assert_called_once()
        mock_ceo.assert_called_once()
        mock_cto.assert_called_once()
        mock_drift.assert_called_once()
        mock_weekly.assert_called_once()
        
        # Check that the result has the expected fields
        self.assertIn("status", result)
        self.assertIn("memory", result)
        self.assertIn("message", result)
        self.assertIn("has_intent_impact_mismatch", result)
        
        # Check that the status is correct
        self.assertEqual(result["status"], "completed")
        
        # Check that the intent-impact mismatch flag is correct
        self.assertFalse(result["has_intent_impact_mismatch"])
    
    @patch('orchestrator.modules.intent_impact_analyzer.process_loop_with_intent_impact_analyzer')
    @patch('orchestrator.modules.loop_controller.analyze_loop_with_historian_agent')
    @patch('orchestrator.modules.loop_controller.process_loop_with_ceo_agent')
    @patch('orchestrator.modules.loop_controller.process_loop_with_cto_agent')
    @patch('orchestrator.modules.loop_controller.process_loop_with_drift_engine')
    @patch('orchestrator.modules.loop_controller.process_loop_with_weekly_drift_report')
    def test_handle_loop_completion_with_mismatch(self, mock_weekly, mock_drift, mock_cto, mock_ceo, mock_historian, mock_intent):
        """Test handling loop completion with an intent-impact mismatch."""
        # Mock the intent-impact analyzer with a mismatch
        mock_intent.return_value = {
            "status": "analyzed",
            "memory": self.memory,
            "message": "Intent-impact mismatch detected",
            "has_mismatch": True,
            "analysis_result": {
                "intent_tone": "reflective",
                "summary_tone": "vague",
                "recommendation": "Rerun SAGE to reclarify loop purpose"
            }
        }
        
        # Mock the other modules
        mock_historian.return_value = {"status": "analyzed", "memory": self.memory, "message": "Loop analyzed"}
        mock_ceo.return_value = {"status": "analyzed", "memory": self.memory, "message": "Loop analyzed by CEO"}
        mock_cto.return_value = {"status": "analyzed", "memory": self.memory, "message": "CTO analysis"}
        mock_drift.return_value = self.memory
        mock_weekly.return_value = self.memory
        
        # Call the function
        result = handle_loop_completion(
            self.loop_id,
            self.summary,
            self.loop,
            self.plan,
            self.prompt,
            self.agent_logs,
            self.memory
        )
        
        # Check that the intent-impact mismatch flag is set
        self.assertTrue(result["has_intent_impact_mismatch"])
        
        # Check that the message includes the mismatch information
        self.assertIn("Intent-Impact", result["message"])


if __name__ == '__main__':
    unittest.main()
