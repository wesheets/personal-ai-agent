# /app/modules/llm_infer.py

import os
import json
import requests
from typing import Dict, Any, Optional

# Import the prompt_cleaner function
from app.utils.prompt_cleaner import clean_prompt

class LLMInferenceModule:
    """
    Module for handling LLM inference requests to external providers.
    
    This module sanitizes prompts before sending them to external LLM providers
    to protect privacy and abstract internal agent architecture.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM inference module.
        
        Args:
            api_key (str, optional): API key for the LLM provider. 
                                    If not provided, will attempt to load from environment.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as OPENAI_API_KEY environment variable")
    
    def infer(self, prompt: str, model: str = "gpt-4", **kwargs) -> Dict[str, Any]:
        """
        Send a prompt to the LLM provider and return the response.
        
        This method sanitizes the prompt using the prompt_cleaner utility
        before sending it to the LLM provider.
        
        Args:
            prompt (str): The prompt to send to the LLM
            model (str): The model to use for inference
            **kwargs: Additional parameters to pass to the LLM provider
            
        Returns:
            Dict[str, Any]: The response from the LLM provider
        """
        # Clean the prompt before sending to external LLM provider
        sanitized_prompt = clean_prompt(prompt)
        
        # Prepare the request payload
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": sanitized_prompt}],
            **kwargs
        }
        
        # Make the API request to OpenAI
        try:
            response = self._call_openai_api(payload)
            return response
        except Exception as e:
            # Log the error and re-raise
            print(f"Error calling LLM API: {str(e)}")
            raise
    
    def _call_openai_api(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make the actual API call to OpenAI.
        
        Args:
            payload (Dict[str, Any]): The request payload
            
        Returns:
            Dict[str, Any]: The response from OpenAI
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
        
        return response.json()


# Function to be used directly in the /llm/infer endpoint
def infer_with_llm(prompt: str, model: str = "gpt-4", api_key: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for the /llm/infer endpoint to make LLM API calls.
    
    This function sanitizes the prompt using the prompt_cleaner utility
    before sending it to the LLM provider.
    
    Args:
        prompt (str): The prompt to send to the LLM
        model (str): The model to use for inference
        api_key (str, optional): API key for the LLM provider
        **kwargs: Additional parameters to pass to the LLM provider
        
    Returns:
        Dict[str, Any]: The response from the LLM provider
    """
    # Create an instance of the LLMInferenceModule
    llm_module = LLMInferenceModule(api_key)
    
    # Use the module to make the inference call with the sanitized prompt
    return llm_module.infer(prompt, model, **kwargs)
