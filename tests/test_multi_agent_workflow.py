import os
import sys
import json
import asyncio
import unittest
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.orchestrator import get_orchestrator
from app.api.agent import AgentRequest
from app.core.execution_chain_logger import get_execution_chain_logger

class TestMultiAgentWorkflow(unittest.TestCase):
    """Test the multi-agent workflow orchestration functionality"""
    
    async def test_orchestration_with_auto_orchestrate(self):
        """Test orchestration with auto_orchestrate enabled"""
        # Get the orchestrator
        orchestrator = get_orchestrator()
        
        # Create a test request
        request = AgentRequest(
            input="I need to create a REST API for a blog with users, posts, and comments, and then deploy it to production.",
            context={},
            save_to_memory=True,
            auto_orchestrate=True
        )
        
        # Orchestrate the workflow
        chain = await orchestrator.orchestrate(
            initial_agent="builder",
            initial_input=request.input,
            context=request.context,
            auto_orchestrate=request.auto_orchestrate,
            max_steps=3  # Limit to 3 steps for testing
        )
        
        # Verify the chain was created
        self.assertIsNotNone(chain)
        self.assertIsNotNone(chain.chain_id)
        
        # Verify at least one step was executed
        self.assertGreater(len(chain.steps), 0)
        
        # Verify the first step was executed by the builder agent
        self.assertEqual(chain.steps[0].agent_name, "builder")
        
        # If auto_orchestrate worked and there's a suggested next step,
        # there should be more than one step
        if len(chain.steps) > 1:
            # The second step should be executed by a different agent
            self.assertNotEqual(chain.steps[1].agent_name, chain.steps[0].agent_name)
            
            # Print the chain details for debugging
            print(f"Chain ID: {chain.chain_id}")
            print(f"Number of steps: {len(chain.steps)}")
            for i, step in enumerate(chain.steps):
                print(f"Step {i+1}: {step.agent_name}")
                print(f"  Input: {step.input_text[:100]}...")
                print(f"  Output: {step.output_text[:100]}...")
                if step.metadata.get("suggested_next_step"):
                    print(f"  Suggested next step: {step.metadata.get('suggested_next_step')}")
        
        # Verify the chain was completed
        self.assertEqual(chain.status, "completed")
        
        # Verify the chain was logged
        chain_logger = get_execution_chain_logger()
        logged_chain = await chain_logger.get_chain(chain.chain_id)
        self.assertIsNotNone(logged_chain)
        self.assertEqual(logged_chain.chain_id, chain.chain_id)
        
        return chain
    
    async def test_orchestration_with_manual_control(self):
        """Test orchestration with manual control (auto_orchestrate disabled)"""
        # Get the orchestrator
        orchestrator = get_orchestrator()
        
        # Create a test request
        request = AgentRequest(
            input="I need to research the latest trends in AI and machine learning for 2025.",
            context={},
            save_to_memory=True,
            auto_orchestrate=False
        )
        
        # Orchestrate the workflow
        chain = await orchestrator.orchestrate(
            initial_agent="research",
            initial_input=request.input,
            context=request.context,
            auto_orchestrate=request.auto_orchestrate,
            max_steps=3  # Limit to 3 steps for testing
        )
        
        # Verify the chain was created
        self.assertIsNotNone(chain)
        self.assertIsNotNone(chain.chain_id)
        
        # Verify exactly one step was executed (since auto_orchestrate is False)
        self.assertEqual(len(chain.steps), 1)
        
        # Verify the step was executed by the research agent
        self.assertEqual(chain.steps[0].agent_name, "research")
        
        # Verify the chain was completed
        self.assertEqual(chain.status, "completed")
        
        # Verify the chain was logged
        chain_logger = get_execution_chain_logger()
        logged_chain = await chain_logger.get_chain(chain.chain_id)
        self.assertIsNotNone(logged_chain)
        self.assertEqual(logged_chain.chain_id, chain.chain_id)
        
        return chain
    
    async def test_agent_routing_based_on_keywords(self):
        """Test agent routing based on handoff keywords"""
        # Get the orchestrator
        orchestrator = get_orchestrator()
        
        # Create a test request with a keyword that should trigger the ops agent
        request = AgentRequest(
            input="I need to deploy my application to production.",
            context={},
            save_to_memory=True,
            auto_orchestrate=True
        )
        
        # Orchestrate the workflow starting with the builder agent
        chain = await orchestrator.orchestrate(
            initial_agent="builder",
            initial_input=request.input,
            context=request.context,
            auto_orchestrate=request.auto_orchestrate,
            max_steps=3  # Limit to 3 steps for testing
        )
        
        # Verify the chain was created
        self.assertIsNotNone(chain)
        
        # If the routing worked correctly and there's more than one step,
        # the second agent should be the ops agent (since "deploy" is a handoff keyword for ops)
        if len(chain.steps) > 1:
            self.assertEqual(chain.steps[1].agent_name, "ops")
        
        return chain
    
    async def test_agent_routing_based_on_task_category(self):
        """Test agent routing based on task category"""
        # Get the orchestrator
        orchestrator = get_orchestrator()
        
        # Create a context with a task category that should be accepted by the research agent
        context = {
            "task_category": "research"
        }
        
        # Create a test request
        request = AgentRequest(
            input="I need information about the latest developments in quantum computing.",
            context=context,
            save_to_memory=True,
            auto_orchestrate=True
        )
        
        # Orchestrate the workflow starting with the builder agent
        chain = await orchestrator.orchestrate(
            initial_agent="builder",
            initial_input=request.input,
            context=request.context,
            auto_orchestrate=request.auto_orchestrate,
            max_steps=3  # Limit to 3 steps for testing
        )
        
        # Verify the chain was created
        self.assertIsNotNone(chain)
        
        # If the routing worked correctly and there's more than one step,
        # the second agent should be the research agent (since "research" is in its accepts_tasks)
        if len(chain.steps) > 1:
            self.assertEqual(chain.steps[1].agent_name, "research")
        
        return chain

async def run_tests():
    """Run the tests"""
    # Create a test instance
    test = TestMultiAgentWorkflow()
    
    # Run the tests
    print("Testing orchestration with auto_orchestrate enabled...")
    auto_chain = await test.test_orchestration_with_auto_orchestrate()
    
    print("\nTesting orchestration with manual control...")
    manual_chain = await test.test_orchestration_with_manual_control()
    
    print("\nTesting agent routing based on keywords...")
    keyword_chain = await test.test_agent_routing_based_on_keywords()
    
    print("\nTesting agent routing based on task category...")
    category_chain = await test.test_agent_routing_based_on_task_category()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Auto-orchestrate chain: {auto_chain.chain_id} - {len(auto_chain.steps)} steps")
    print(f"Manual control chain: {manual_chain.chain_id} - {len(manual_chain.steps)} steps")
    print(f"Keyword routing chain: {keyword_chain.chain_id} - {len(keyword_chain.steps)} steps")
    print(f"Category routing chain: {category_chain.chain_id} - {len(category_chain.steps)} steps")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_tests())
