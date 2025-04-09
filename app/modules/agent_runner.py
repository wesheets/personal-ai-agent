"""
AgentRunner Module

This module provides isolated agent execution functionality, allowing agents to run
independently from the central agent registry, UI, or delegate-stream system.

MODIFIED: Added full runtime logging and error protection to prevent 502 errors
"""

import logging
import os
from typing import List, Dict, Any, Optional
import time
import traceback
import sys
from fastapi.responses import JSONResponse

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

def run_agent(agent_id: str, messages: List[Dict[str, Any]]):
    """
    Run an agent with the given messages, with no registry dependencies.
    
    MODIFIED: Added full runtime logging and error protection to prevent 502 errors
    
    Args:
        agent_id: The ID of the agent to run
        messages: List of message dictionaries with role and content
        
    Returns:
        Dict containing the response and metadata or JSONResponse with error details
    """
    # ADDED: Entry confirmation logging
    print("🔥 AgentRunner route invoked")
    logger.info("🔥 AgentRunner route invoked")
    
    # MODIFIED: Wrapped all logic in global try/except
    try:
        print("🧠 Attempting to run CoreForgeAgent fallback")
        logger.info("Attempting to run CoreForgeAgent fallback")
        
        # Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔑 OpenAI API Key loaded: {bool(api_key)}")
        logger.info(f"OpenAI API Key available: {bool(api_key)}")
        
        if not api_key:
            error_msg = "OpenAI API key is not set in environment variables"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return JSONResponse(
                status_code=500,
                content={
                    "agent_id": agent_id,
                    "response": error_msg,
                    "status": "error"
                }
            )
        
        # Create CoreForgeAgent instance
        print(f"🔄 Creating CoreForgeAgent instance for: {agent_id}")
        agent = CoreForgeAgent()
        
        # Call agent's run method
        print(f"🏃 Calling CoreForgeAgent.run() method with {len(messages)} messages")
        result = agent.run(messages)
        
        # Check if agent execution was successful
        if result.get("status") == "error":
            error_msg = f"CoreForgeAgent execution failed: {result.get('content')}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return JSONResponse(
                status_code=500,
                content={
                    "agent_id": "Core.Forge",
                    "response": result.get("content", "Unknown error"),
                    "status": "error"
                }
            )
        
        # Log success
        print("✅ AgentRunner success, returning response")
        logger.info("AgentRunner success, returning response")
        
        # Return successful response
        return {
            "agent_id": "Core.Forge",
            "response": result.get("content", ""),
            "status": "ok",
            "usage": result.get("usage", {})
        }
    
    except Exception as e:
        # Handle any unexpected errors
        error_msg = f"Error running agent {agent_id}: {str(e)}"
        print(f"❌ AgentRunner failed: {str(e)}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Return structured error response
        return JSONResponse(
            status_code=500,
            content={
                "agent_id": agent_id,
                "response": error_msg,
                "status": "error",
                "message": str(e)
            }
        )

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
