"""
AgentRunner Module

This module provides isolated agent execution functionality, allowing agents to run
independently from the central agent registry, UI, or delegate-stream system.

It implements a robust mechanism for executing agent cognition with proper fallbacks
when the registry fails or specific agents are missing.
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
    from app.core.openai_client import get_openai_client
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("❌ OpenAI client import failed")

# Try to import agent registry
try:
    from app.core.agent_loader import get_agent, get_all_agents
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    print("❌ Agent registry import failed")

# Configure logging
logger = logging.getLogger("modules.agent_runner")

class CoreForgeAgent:
    """
    Fallback implementation of CoreForgeAgent when the registry is not available.
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
    Run an agent with the given messages, with fallback mechanisms for registry failures.
    
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
        
        # Try to get agent from registry first
        agent = None
        registry_available = False
        
        try:
            # Check if agent registry is available
            if REGISTRY_AVAILABLE:
                print(f"🔍 Looking for agent in registry: {agent_id}")
                agent = get_agent(agent_id)
                registry_available = True
                
                if agent:
                    print(f"✅ Found agent in registry: {agent_id}")
                    logger.info(f"Found agent in registry: {agent_id}")
                else:
                    print(f"⚠️ Agent not found in registry: {agent_id}")
                    logger.warning(f"Agent not found in registry: {agent_id}")
            else:
                print("⚠️ Agent registry not available")
                logger.warning("Agent registry not available")
        except Exception as e:
            error_msg = f"Agent registry access failed: {str(e)}"
            print(f"⚠️ {error_msg}")
            logger.warning(error_msg)
        
        # If agent not found in registry or registry not available, use fallback
        if not agent:
            # Special case for Core.Forge
            if agent_id.lower() in ["core.forge", "core-forge"]:
                print("⚠️ Using fallback CoreForgeAgent (registry unavailable)")
                logger.info("Using fallback CoreForgeAgent")
                agent = CoreForgeAgent()
            else:
                # No fallback available for other agents
                error_msg = f"Agent {agent_id} not found and no fallback available"
                print(f"❌ {error_msg}")
                logger.error(error_msg)
                return {
                    "agent_id": agent_id,
                    "response": error_msg,
                    "status": "error",
                    "registry_available": registry_available,
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
                "registry_available": registry_available,
                "execution_time": time.time() - start_time,
                "usage": result.get("usage", {})
            }
        
        # If agent doesn't have run method, use fallback with OpenAI
        print(f"⚠️ Agent {agent_id} doesn't have run method, using OpenAI fallback")
        logger.warning(f"Agent {agent_id} doesn't have run method, using OpenAI fallback")
        
        # Get agent metadata for system prompt
        agent_name = getattr(agent, "name", agent_id)
        agent_description = getattr(agent, "description", "")
        agent_tone = getattr(agent, "tone", "professional")
        
        # Create system prompt
        system_prompt = f"You are {agent_name}, an AI assistant with a {agent_tone} tone. {agent_description}"
        
        # Add system message to messages if not already present
        has_system_message = any(msg.get("role") == "system" for msg in messages)
        if not has_system_message:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Use OpenAI client directly
        try:
            print("📡 Using direct OpenAI client")
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            print(f"✅ OpenAI API call successful, received {len(content)} characters")
            
            # Log result
            logger.info(f"Agent {agent_id} execution completed with OpenAI fallback")
            
            # Return result
            return {
                "agent_id": agent_id,
                "response": content,
                "status": "ok",
                "registry_available": registry_available,
                "execution_time": time.time() - start_time,
                "fallback_used": True,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            error_msg = f"OpenAI fallback failed: {str(e)}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "agent_id": agent_id,
                "response": f"OpenAI fallback failed: {str(e)}",
                "status": "error",
                "registry_available": registry_available,
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
