import os
from typing import Dict, Any, Optional
import time
import json
from openai import AsyncOpenAI

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def process_with_prompt_chain(
        self, 
        prompt_chain: Dict[str, Any], 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user input through a prompt chain using OpenAI's API
        
        Args:
            prompt_chain: The prompt chain configuration
            user_input: The user's input text
            context: Optional context information
            
        Returns:
            Dict containing the response and metadata
        """
        # Prepare the messages based on the prompt chain
        messages = self._prepare_messages(prompt_chain, user_input, context)
        
        # Call the OpenAI API
        response = await self.client.chat.completions.create(
            model=prompt_chain.get("model", "gpt-4"),
            messages=messages,
            temperature=prompt_chain.get("temperature", 0.7),
            max_tokens=prompt_chain.get("max_tokens", 1000),
        )
        
        # Extract the content from the response
        content = response.choices[0].message.content
        
        # Return the result with metadata
        return {
            "content": content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "timestamp": time.time()
        }
    
    def _prepare_messages(
        self, 
        prompt_chain: Dict[str, Any], 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Prepare the messages for the OpenAI API based on the prompt chain
        
        Args:
            prompt_chain: The prompt chain configuration
            user_input: The user's input text
            context: Optional context information
            
        Returns:
            List of message dictionaries for the OpenAI API
        """
        messages = []
        
        # Add system message if present
        if "system" in prompt_chain:
            messages.append({"role": "system", "content": prompt_chain["system"]})
        
        # Add examples if present
        if "examples" in prompt_chain:
            for example in prompt_chain["examples"]:
                if "user" in example:
                    messages.append({"role": "user", "content": example["user"]})
                if "assistant" in example:
                    messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add context if provided
        if context:
            context_str = json.dumps(context)
            messages.append({"role": "system", "content": f"Additional context: {context_str}"})
        
        # Add user input
        messages.append({"role": "user", "content": user_input})
        
        return messages

def get_openai_client():
    """
    Dependency to get the OpenAI client
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    return OpenAIClient(api_key=api_key)
