"""
AgentRunner Module

This module provides isolated agent execution functionality, allowing agents to run
independently from the central agent registry, UI, or delegate-stream system.

MODIFIED: Completely removed registry dependencies to ensure standalone operation
"""

import logging
import os
from typing import List, Dict, Any, Optional
import time
import traceback
import sys

# Import OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("❌ OpenAI client import failed")

# Configure logging
logger = logging.getLogger("modules.agent_runner")

class CoreForgeAgent:
    """
    Standalone implementation of CoreForgeAgent with no registry dependencies.
    """
    def __init__(self):
        self.agent_id = "Core.Forge"
        self.name = "Core.Forge"
        self.description = "System orchestrator that routes tasks to appropriate agents"
        self.tone = "professional"
        
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔑 OpenAI API Key loaded: {bool(api_key)}")
        
        # Initialize OpenAI client
        try:
            if not api_key:
                raise ValueError("OpenAI API key is not set in environment variables")
            
            self.client = OpenAI(api_key=api_key)
            print("✅ OpenAI client initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize OpenAI client: {str(e)}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            self.client = None
    
    def run(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run the agent with the given messages.
        
        Args:
            messages: List of message dictionaries with role and content
            
        Returns:
            Dict containing the response and metadata
        """
        try:
            print(f"🤖 CoreForgeAgent.run called with {len(messages)} messages")
            
            if not self.client:
                error_msg = "OpenAI client initialization failed. Unable to process request."
                print(f"❌ {error_msg}")
                return {
                    "content": error_msg,
                    "status": "error"
                }
            
            # Call OpenAI API
            print("📡 Calling OpenAI API...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract content from response
            content = response.choices[0].message.content
            print(f"✅ OpenAI API call successful, received {len(content)} characters")
            
            # Return result with metadata
            return {
                "content": content,
                "status": "success",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "timestamp": time.time()
            }
        except Exception as e:
            error_msg = f"Error in CoreForgeAgent.run: {str(e)}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "content": f"Error processing request: {str(e)}",
                "status": "error"
            }

def run_agent(agent_id: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Run an agent with the given messages, with no registry dependencies.
    
    MODIFIED: Removed all registry dependencies to ensure standalone operation
    
    Args:
        agent_id: The ID of the agent to run
        messages: List of message dictionaries with role and content
        
    Returns:
        Dict containing the response and metadata
    """
    try:
        start_time = time.time()
        print(f"🧠 Starting AgentRunner for: {agent_id}")
        logger.info(f"Starting agent execution: {agent_id}")
        
        # Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔑 OpenAI API Key loaded: {bool(api_key)}")
        logger.info(f"OpenAI API Key available: {bool(api_key)}")
        
        if not api_key:
            error_msg = "OpenAI API key is not set in environment variables"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return {
                "agent_id": agent_id,
                "response": error_msg,
                "status": "error",
                "execution_time": time.time() - start_time
            }
        
        # MODIFIED: Direct CoreForge integration with no registry dependency
        if agent_id.lower() in ["core.forge", "core-forge"]:
            print("🔄 Using direct CoreForgeAgent implementation (no registry)")
            logger.info("Using direct CoreForgeAgent implementation")
            agent = CoreForgeAgent()
        else:
            # No support for other agents in isolated mode
            error_msg = f"Agent {agent_id} not supported in isolated mode. Only Core.Forge is available."
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return {
                "agent_id": agent_id,
                "response": error_msg,
                "status": "error",
                "execution_time": time.time() - start_time
            }
        
        # Check if agent has run method
        if hasattr(agent, "run") and callable(getattr(agent, "run")):
            # Call agent's run method
            print(f"🏃 Calling {agent_id}.run() method")
            result = agent.run(messages)
            
            # Log result
            print(f"✅ Agent {agent_id} execution completed successfully")
            logger.info(f"Agent {agent_id} execution completed successfully")
            
            # Return result
            return {
                "agent_id": agent_id,
                "response": result.get("content", "No content returned"),
                "status": "ok",
                "registry_available": False,  # Always false in isolated mode
                "execution_time": time.time() - start_time,
                "usage": result.get("usage", {})
            }
        
        # This should never happen with our CoreForgeAgent implementation
        error_msg = f"Agent {agent_id} doesn't have run method"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        return {
            "agent_id": agent_id,
            "response": error_msg,
            "status": "error",
            "execution_time": time.time() - start_time
        }
    
    except Exception as e:
        # Handle any unexpected errors
        error_msg = f"Error running agent {agent_id}: {str(e)}"
        print(f"❌ AgentRunner failed: {str(e)}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "agent_id": agent_id,
            "response": error_msg,
            "status": "error",
            "execution_time": time.time() - start_time
        }

def test_core_forge_isolation():
    """
    Test CoreForgeAgent in isolation to verify it works correctly.
    
    Returns:
        Dict containing the test results
    """
    print("\n=== Testing CoreForgeAgent in isolation ===\n")
    
    try:
        # Create test messages
        messages = [
            {"role": "user", "content": "What is 7 + 5?"}
        ]
        
        # Create agent
        print("🔧 Creating CoreForgeAgent instance")
        agent = CoreForgeAgent()
        
        # Run the agent
        print(f"🏃 Running CoreForgeAgent with message: {messages[0]['content']}")
        result = agent.run(messages)
        
        # Print the result
        print(f"\nResult:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Response: {result.get('content', 'No response')}")
        
        if result.get('status') == 'success':
            print("\n✅ Test passed: CoreForgeAgent returned successful response")
        else:
            print("\n❌ Test failed: CoreForgeAgent did not return successful response")
        
        return result
    
    except Exception as e:
        error_msg = f"Error testing CoreForgeAgent in isolation: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "content": error_msg
        }

if __name__ == "__main__":
    # Run the isolation test if this module is executed directly
    test_core_forge_isolation()
