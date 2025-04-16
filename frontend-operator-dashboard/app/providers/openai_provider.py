import time
import logging
import asyncio
from typing import Dict, Any, List, Optional
import json
from openai import AsyncOpenAI
from app.providers.model_router import ModelProvider
from app.utils.env_manager import EnvManager

logger = logging.getLogger("providers")

class OpenAIProvider(ModelProvider):
    """
    Provider for OpenAI models
    """
    def __init__(self, api_key: Optional[str] = None):
        # Use the EnvManager to get the API key with proper error handling
        self.api_key = api_key or EnvManager.get("OPENAI_API_KEY", required=True)
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.available_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ]
        self.default_model = EnvManager.get("DEFAULT_MODEL", "gpt-4")
        logger.info(f"OpenAI provider initialized with default model: {self.default_model}")
    
    async def run_conversation(self, messages):
        """
        Run a conversation with retry logic and exponential backoff
        
        Args:
            messages: List of message objects with role and content
            
        Returns:
            Trimmed response content from OpenAI
        """
        for attempt in range(4):
            try:
                response = await self.client.chat.completions.create(
                    model=self.default_model,
                    messages=messages,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    # Exponential backoff for rate limits
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limit hit, retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"OpenAI Error: {e}")
                    return "⚠️ GPT failure — fallback message."
        
        # If we've exhausted all retries
        return "⚠️ GPT failure after multiple retries — fallback message."
    
    async def run_with_function_call(self, messages, functions):
        """
        Run a conversation with function calling capability
        
        Args:
            messages: List of message objects with role and content
            functions: List of function definitions
            
        Returns:
            OpenAI response choice with potential function call
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                functions=functions,
                function_call="auto"
            )
            return response.choices[0]
        except Exception as e:
            logger.error(f"Function call error: {e}")
            raise
    
    async def process_with_prompt_chain(
        self, 
        prompt_chain: Dict[str, Any], 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user input through a prompt chain using OpenAI's API
        """
        messages = self._prepare_messages(prompt_chain, user_input, context)
        # Inject HAL's fallback personality if no system message exists
        has_system = any(msg["role"] == "system" for msg in messages)
        if not has_system:
            messages.insert(0, {
                "role": "system",
                "content": (
                    "You are HAL, an emotionally-aware, hyper-intelligent AI assistant. "
                    "You speak calmly, precisely, and always with thoughtful intent."
                )
            })
        model = prompt_chain.get("model", self.default_model)
        temperature = prompt_chain.get("temperature", 0.7)
        max_tokens = prompt_chain.get("max_tokens", 1000)
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
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
        except Exception as e:
            logger.error(f"[ERROR] OpenAI API call failed: {str(e)}")
            raise
    
    def _prepare_messages(
        self, 
        prompt_chain: Dict[str, Any], 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Prepare the messages for the OpenAI API based on the prompt chain
        """
        messages = []
        if "system" in prompt_chain:
            messages.append({"role": "system", "content": prompt_chain["system"]})
        if "examples" in prompt_chain:
            for example in prompt_chain["examples"]:
                if "user" in example:
                    messages.append({"role": "user", "content": example["user"]})
                if "assistant" in example:
                    messages.append({"role": "assistant", "content": example["assistant"]})
        if context:
            context_str = json.dumps(context)
            messages.append({"role": "system", "content": f"Additional context: {context_str}"})
        messages.append({"role": "user", "content": user_input})
        return messages
    
    def get_available_models(self) -> List[str]:
        return self.available_models
    
    def get_default_model(self) -> str:
        return self.default_model
