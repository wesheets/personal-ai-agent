import os
from typing import Dict, Any, List, Optional
import time
import json
import anthropic
from app.providers.model_router import ModelProvider

class ClaudeProvider(ModelProvider):
    """
    Provider for Anthropic Claude models
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY environment variable is not set")
        
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        self.available_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        # Use Claude 3 Sonnet as default per user requirements
        self.default_model = "claude-3-sonnet-20240229"
    
    async def process_with_prompt_chain(
        self, 
        prompt_chain: Dict[str, Any], 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user input through a prompt chain using Claude's API
        
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
        if model == "claude-3-opus":
            model = "claude-3-opus-20240229"
        elif model == "claude-3-sonnet":
            model = "claude-3-sonnet-20240229"
        elif model == "claude-3-haiku":
            model = "claude-3-haiku-20240307"
        
        # Call the Claude API
        response = await self.client.messages.create(
            model=model,
            messages=messages,
            temperature=prompt_chain.get("temperature", 0.7),
            max_tokens=prompt_chain.get("max_tokens", 1000),
        )
        
        # Extract the content from the response
        content = response.content[0].text
        
        # Return the result with metadata
        return {
            "content": content,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            "timestamp": time.time(),
            "model": model,
            "provider": "claude"
        }
    
    def _prepare_messages(
        self, 
        prompt_chain: Dict[str, Any], 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Prepare the messages for the Claude API based on the prompt chain
        
        Args:
            prompt_chain: The prompt chain configuration
            user_input: The user's input text
            context: Optional context information
            
        Returns:
            List of message dictionaries for the Claude API
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
            if messages and messages[0]["role"] == "system":
                # Append to existing system message
                messages[0]["content"] += f"\n\nAdditional context: {context_str}"
            else:
                # Add as new system message
                messages.insert(0, {"role": "system", "content": f"Additional context: {context_str}"})
        
        # Add user input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available Claude models
        
        Returns:
            List of model identifiers
        """
        return self.available_models
    
    def get_default_model(self) -> str:
        """
        Get the default Claude model
        
        Returns:
            Default model identifier
        """
        return self.default_model
