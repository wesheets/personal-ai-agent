import os
from typing import Dict, Any, List, Optional
import time
import json
from openai import AsyncOpenAI
from app.providers.model_router import ModelProvider

class OpenAIProvider(ModelProvider):
    """
    Provider for OpenAI models
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.available_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ]
        self.default_model = "gpt-4"
    
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
        
        # Get the model from the prompt chain or use default
        model = prompt_chain.get("model", self.default_model)
        
        # Call the OpenAI API
        response = await self.client.chat.completions.create(
            model=model,
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
            "timestamp": time.time(),
            "model": model,
            "provider": "openai"
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
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available OpenAI models
        
        Returns:
            List of model identifiers
        """
        return self.available_models
    
    def get_default_model(self) -> str:
        """
        Get the default OpenAI model
        
        Returns:
            Default model identifier
        """
        return self.default_model
