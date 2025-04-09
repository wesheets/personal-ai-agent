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

# Import OpenAI client
try:
    from openai import OpenAI
    from app.core.openai_client import get_openai_client
except ImportError:
    # Fallback for when OpenAI client is not available
    pass

# Try to import agent registry
try:
    from app.core.agent_loader import get_agent, get_all_agents
except ImportError:
    # Fallback for when agent registry is not available
    pass

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
        
        # Initialize OpenAI client
        try:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.client = None
    
    def run(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run the agent with the given messages.
        
        Args:
            messages: List of message dictionaries with role and content
            
        Returns:
            Dict containing the response and metadata
        """
        if not self.client:
            return {
                "content": "OpenAI client initialization failed. Unable to process request.",
                "status": "error"
            }
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract content from response
            content = response.choices[0].message.content
            
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
            logger.error(f"Error in CoreForgeAgent.run: {str(e)}")
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
    start_time = time.time()
    logger.info(f"Starting agent execution: {agent_id}")
    
    try:
        # Try to get agent from registry first
        agent = None
        registry_available = False
        
        try:
            # Check if agent registry is available
            agent = get_agent(agent_id)
            registry_available = True
            
            if agent:
                logger.info(f"Found agent in registry: {agent_id}")
            else:
                logger.warning(f"Agent not found in registry: {agent_id}")
        except Exception as e:
            logger.warning(f"Agent registry not available: {str(e)}")
        
        # If agent not found in registry or registry not available, use fallback
        if not agent:
            # Special case for Core.Forge
            if agent_id.lower() in ["core.forge", "core-forge"]:
                logger.info("Using fallback CoreForgeAgent")
                agent = CoreForgeAgent()
            else:
                # No fallback available for other agents
                error_msg = f"Agent {agent_id} not found and no fallback available"
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
            result = agent.run(messages)
            
            # Log result
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
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
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
            logger.error(f"OpenAI fallback failed: {str(e)}")
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
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "agent_id": agent_id,
            "response": error_msg,
            "status": "error",
            "execution_time": time.time() - start_time
        }
