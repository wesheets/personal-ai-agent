"""
CoreForgeAgent implementation for handling GPT prompts.

This agent provides a simple interface for processing messages and generating responses
using a basic prompt template system.
"""

import logging
import json

# Configure logging
logger = logging.getLogger("agents.core_forge")

class CoreForgeAgent:
    """
    CoreForgeAgent handles processing of messages and generating responses.
    
    This is a simplified implementation that can be expanded with more advanced
    functionality in the future.
    """
    
    def __init__(self):
        """Initialize the CoreForgeAgent."""
        print("🔧 CoreForgeAgent initialized")
        self.name = "Core.Forge"
    
    def run(self, messages):
        """
        Process the input messages and generate a response.
        
        Args:
            messages (list): List of message objects with 'role' and 'content' keys
            
        Returns:
            str: Generated response
        """
        print(f"🔄 CoreForgeAgent processing {len(messages)} messages")
        
        try:
            # Extract the last user message for simplicity
            last_message = None
            for message in reversed(messages):
                if message.get('role') == 'user':
                    last_message = message.get('content')
                    break
            
            if not last_message:
                return "I didn't receive a valid user message to respond to."
            
            # Simple response generation logic
            # In a real implementation, this would use an LLM or other AI system
            response = f"CoreForgeAgent received: {last_message[:50]}..."
            
            print(f"✅ CoreForgeAgent generated response")
            return response
            
        except Exception as e:
            logger.error(f"Error in CoreForgeAgent.run: {str(e)}")
            print(f"❌ CoreForgeAgent error: {str(e)}")
            return f"Error processing your request: {str(e)}"
