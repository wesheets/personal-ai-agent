"""
Tests for the agent plan injector module.

This module contains tests for the agent plan injector module to ensure it correctly
creates and injects execution contracts to agents.
"""

import unittest
import json
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.agent_plan_injector import (
    generate_agent_contract,
    inject_agent_contract,
    check_agent_execution_readiness
)

class TestAgentPlanInjector(unittest.TestCase):
    """Test cases for the agent plan injector module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample loop plans for testing
        self.valid_plan = {
            "loop_id": 31,
            "agents": ["hal", "nova", "critic"],
            "goals": ["Add form logic to ContactForm.jsx", "Implement validation"],
            "planned_files": ["ContactForm.jsx", "validation.js"],
            "tool_requirements": ["form_validator", "component_builder"],
            "confirmed": True,
            "confirmed_by": "operator",
            "confirmed_at": "2025-04-23T20:18:00Z"
        }
        
        self.unconfirmed_plan = {
            "loop_id": 32,
            "agents": ["hal", "nova", "critic"],
            "goals": ["Add form logic to ContactForm.jsx", "Implement validation"],
            "planned_files": ["ContactForm.jsx", "validation.js"],
            "tool_requirements": ["form_validator", "component_builder"],
            "confirmed": False,
            "confirmed_by": "",
            "confirmed_at": "2025-04-23T20:18:00Z"
        }
        
        self.missing_tools_plan = {
            "loop_id": 33,
            "agents": ["hal", "nova", "critic"],
            "goals": ["Add form logic to ContactForm.jsx", "Implement validation"],
            "planned_files": ["ContactForm.jsx", "validation.js"],
            "tool_requirements": ["missing_tool_1", "missing_tool_2"],
            "confirmed": True,
            "confirmed_by": "operator",
            "confirmed_at": "2025-04-23T20:18:00Z"
        }
        
        # Mock project ID
        self.project_id = "test_project_001"
        
    def test_generate_agent_contract_valid_plan(self):
        """Test generating a contract from a valid plan."""
        # Generate a contract for NOVA
        contract = generate_agent_contract("nova", self.valid_plan)
        
        # Verify contract structure
        self.assertEqual(contract["loop_id"], self.valid_plan["loop_id"], "Contract should have correct loop_id")
        self.assertEqual(contract["agent"], "nova", "Contract should have correct agent")
        self.assertEqual(contract["goal"], self.valid_plan["goals"][0], "Contract should have a goal from the plan")
        self.assertEqual(contract["file"], self.valid_plan["planned_files"][0], "Contract should have a file from the plan")
        self.assertEqual(contract["tools"], self.valid_plan["tool_requirements"], "Contract should have tools from the plan")
        self.assertEqual(contract["confirmed"], self.valid_plan["confirmed"], "Contract should have correct confirmation status")
        self.assertIn("received_at", contract, "Contract should have a received_at timestamp")
        self.assertEqual(contract["trace_id"], f"loop_{self.valid_plan['loop_id']}_nova_contract", "Contract should have correct trace_id")
        
    def test_generate_agent_contract_invalid_inputs(self):
        """Test generating a contract with invalid inputs."""
        # Test with invalid loop plan
        with self.assertRaises(ValueError):
            generate_agent_contract("nova", None)
        
        # Test with invalid agent
        with self.assertRaises(ValueError):
            generate_agent_contract("", self.valid_plan)
        
        # Test with plan missing loop_id
        invalid_plan = self.valid_plan.copy()
        invalid_plan.pop("loop_id")
        with self.assertRaises(ValueError):
            generate_agent_contract("nova", invalid_plan)
        
        # Test with plan missing goals
        invalid_plan = self.valid_plan.copy()
        invalid_plan.pop("goals")
        with self.assertRaises(ValueError):
            generate_agent_contract("nova", invalid_plan)
        
        # Test with plan missing planned_files
        invalid_plan = self.valid_plan.copy()
        invalid_plan.pop("planned_files")
        with self.assertRaises(ValueError):
            generate_agent_contract("nova", invalid_plan)
    
    @patch('orchestrator.modules.agent_plan_injector.log_to_memory')
    @patch('orchestrator.modules.agent_plan_injector.log_to_chat')
    def test_inject_agent_contract_valid_plan(self, mock_log_chat, mock_log_memory):
        """Test injecting contracts to all agents in a valid plan."""
        # Inject contracts
        agent_contracts = inject_agent_contract(self.project_id, self.valid_plan)
        
        # Verify contracts were created for all agents
        self.assertEqual(len(agent_contracts), len(self.valid_plan["agents"]), "Should create contracts for all agents")
        
        # Verify each agent has a valid contract
        for agent in self.valid_plan["agents"]:
            self.assertIn(agent, agent_contracts, f"Should create contract for {agent}")
            contract = agent_contracts[agent]
            self.assertEqual(contract["agent"], agent, f"Contract should be for {agent}")
            self.assertEqual(contract["loop_id"], self.valid_plan["loop_id"], "Contract should have correct loop_id")
        
        # Verify logging calls
        expected_memory_calls = len(self.valid_plan["agents"]) * 2  # agent_contracts + loop_trace for each agent
        self.assertEqual(mock_log_memory.call_count, expected_memory_calls, "Should log to memory for each agent")
        
        expected_chat_calls = len(self.valid_plan["agents"])  # One chat message per agent
        self.assertEqual(mock_log_chat.call_count, expected_chat_calls, "Should log to chat for each agent")
    
    @patch('orchestrator.modules.agent_plan_injector.log_to_memory')
    @patch('orchestrator.modules.agent_plan_injector.log_to_chat')
    def test_inject_agent_contract_unconfirmed_plan(self, mock_log_chat, mock_log_memory):
        """Test injecting contracts with an unconfirmed plan."""
        # Inject contracts
        agent_contracts = inject_agent_contract(self.project_id, self.unconfirmed_plan)
        
        # Verify no contracts were created
        self.assertEqual(len(agent_contracts), 0, "Should not create contracts for unconfirmed plan")
        
        # Verify warning was logged to chat
        self.assertEqual(mock_log_chat.call_count, 1, "Should log warning to chat")
        chat_message = mock_log_chat.call_args[0][1]["message"]
        self.assertIn("not confirmed", chat_message, "Chat message should mention plan not confirmed")
    
    @patch('orchestrator.modules.agent_plan_injector.log_to_memory')
    @patch('orchestrator.modules.agent_plan_injector.log_to_chat')
    def test_inject_agent_contract_invalid_inputs(self, mock_log_chat, mock_log_memory):
        """Test injecting contracts with invalid inputs."""
        # Test with invalid loop plan
        with self.assertRaises(ValueError):
            inject_agent_contract(self.project_id, None)
        
        # Test with plan missing loop_id
        invalid_plan = self.valid_plan.copy()
        invalid_plan.pop("loop_id")
        with self.assertRaises(ValueError):
            inject_agent_contract(self.project_id, invalid_plan)
        
        # Test with plan missing agents
        invalid_plan = self.valid_plan.copy()
        invalid_plan.pop("agents")
        with self.assertRaises(ValueError):
            inject_agent_contract(self.project_id, invalid_plan)
    
    @patch('orchestrator.modules.agent_plan_injector.generate_agent_contract')
    @patch('orchestrator.modules.agent_plan_injector.log_to_memory')
    @patch('orchestrator.modules.agent_plan_injector.log_to_chat')
    def test_inject_agent_contract_error_handling(self, mock_log_chat, mock_log_memory, mock_generate_contract):
        """Test error handling during contract injection."""
        # Mock generate_agent_contract to raise an error
        mock_generate_contract.side_effect = ValueError("Test error")
        
        # Inject contracts
        agent_contracts = inject_agent_contract(self.project_id, self.valid_plan)
        
        # Verify no contracts were created
        self.assertEqual(len(agent_contracts), 0, "Should not create contracts when errors occur")
        
        # Verify errors were logged
        expected_memory_calls = len(self.valid_plan["agents"])  # One orchestrator_warnings entry per agent
        self.assertEqual(mock_log_memory.call_count, expected_memory_calls, "Should log errors to memory")
        
        expected_chat_calls = len(self.valid_plan["agents"])  # One chat message per agent
        self.assertEqual(mock_log_chat.call_count, expected_chat_calls, "Should log errors to chat")
    
    def test_check_agent_execution_readiness(self):
        """Test checking if an agent is ready for execution."""
        # This is a placeholder test since the function just returns mock data for now
        is_ready, reason = check_agent_execution_readiness(self.project_id, self.valid_plan["loop_id"], "nova")
        self.assertTrue(is_ready, "Should return ready for execution")
        self.assertEqual(reason, "All conditions met", "Should return correct reason")
    
    def test_trace_id_format(self):
        """Test that trace IDs follow the required format."""
        # Generate contracts for different agents
        hal_contract = generate_agent_contract("hal", self.valid_plan)
        nova_contract = generate_agent_contract("nova", self.valid_plan)
        critic_contract = generate_agent_contract("critic", self.valid_plan)
        
        # Verify trace ID format
        self.assertEqual(hal_contract["trace_id"], f"loop_{self.valid_plan['loop_id']}_hal_contract", "HAL trace ID should follow format")
        self.assertEqual(nova_contract["trace_id"], f"loop_{self.valid_plan['loop_id']}_nova_contract", "NOVA trace ID should follow format")
        self.assertEqual(critic_contract["trace_id"], f"loop_{self.valid_plan['loop_id']}_critic_contract", "CRITIC trace ID should follow format")
    
    @patch('orchestrator.modules.agent_plan_injector.predict_required_tools')
    def test_tool_prediction_fallback(self, mock_predict_tools):
        """Test that tool prediction is used when tool_requirements is not in the plan."""
        # Create a plan without tool_requirements
        plan_without_tools = self.valid_plan.copy()
        plan_without_tools.pop("tool_requirements")
        
        # Mock predict_required_tools to return some tools
        mock_predict_tools.return_value = ["predicted_tool_1", "predicted_tool_2"]
        
        # Generate a contract
        contract = generate_agent_contract("nova", plan_without_tools)
        
        # Verify tools were predicted
        self.assertEqual(contract["tools"], ["predicted_tool_1", "predicted_tool_2"], "Contract should use predicted tools")
        self.assertEqual(mock_predict_tools.call_count, 1, "Should call predict_required_tools")
    
    @patch('orchestrator.modules.agent_plan_injector.log_to_memory')
    @patch('orchestrator.modules.agent_plan_injector.log_to_chat')
    def test_loop_trace_integration(self, mock_log_chat, mock_log_memory):
        """Test integration with loop trace logging."""
        # Inject contracts
        agent_contracts = inject_agent_contract(self.project_id, self.valid_plan)
        
        # Verify loop trace entries were created
        loop_trace_calls = [call for call in mock_log_memory.call_args_list if "loop_trace" in call[0][1]]
        self.assertEqual(len(loop_trace_calls), len(self.valid_plan["agents"]), "Should create loop trace entry for each agent")
        
        # Verify trace entry format
        for call in loop_trace_calls:
            trace_entry = call[0][1]["loop_trace"][0]
            self.assertEqual(trace_entry["type"], "agent_contract_delivered", "Trace entry should have correct type")
            self.assertIn("trace_id", trace_entry, "Trace entry should have trace_id")
            self.assertIn("loop_id", trace_entry, "Trace entry should have loop_id")
            self.assertIn("agent", trace_entry, "Trace entry should have agent")
            self.assertIn("file", trace_entry, "Trace entry should have file")
            self.assertIn("timestamp", trace_entry, "Trace entry should have timestamp")

if __name__ == "__main__":
    unittest.main()
