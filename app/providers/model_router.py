import os
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ModelProvider(ABC):
    """
    Abstract base class for model providers
    """
    @abstractmethod
    async def process_with_prompt_chain(
        self, 
        prompt_chain: Dict[str, Any], 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user input through a prompt chain
        
        Args:
            prompt_chain: The prompt chain configuration
            user_input: The user's input text
            context: Optional context information
            
        Returns:
            Dict containing the response and metadata
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from this provider
        
        Returns:
            List of model identifiers
        """
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """
        Get the default model for this provider
        
        Returns:
            Default model identifier
        """
        pass

class ModelRouter:
    """
    Routes requests to the appropriate model provider
    """
    def __init__(self):
        self.providers = {}
        self.model_to_provider_map = {}
        self.fallback_order = []
    
    def register_provider(self, provider_name: str, provider: ModelProvider, models: List[str], is_fallback: bool = False):
        """
        Register a model provider
        
        Args:
            provider_name: Name of the provider
            provider: Provider instance
            models: List of models supported by this provider
            is_fallback: Whether this provider should be used as a fallback
        """
        self.providers[provider_name] = provider
        
        # Map each model to this provider
        for model in models:
            self.model_to_provider_map[model] = provider_name
        
        # Add to fallback order if specified
        if is_fallback:
            self.fallback_order.append(provider_name)
    
    def get_provider_for_model(self, model: str) -> Optional[ModelProvider]:
        """
        Get the appropriate provider for a model
        
        Args:
            model: Model identifier
            
        Returns:
            Provider instance or None if not found
        """
        provider_name = self.model_to_provider_map.get(model)
        if provider_name:
            return self.providers.get(provider_name)
        return None
    
    async def process_with_model(
        self, 
        model: str, 
        prompt_chain: Dict[str, Any], 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None,
        use_fallbacks: bool = True
    ) -> Dict[str, Any]:
        """
        Process a request with the specified model, falling back if necessary
        
        Args:
            model: Model identifier
            prompt_chain: The prompt chain configuration
            user_input: The user's input text
            context: Optional context information
            use_fallbacks: Whether to try fallback providers if the primary fails
            
        Returns:
            Dict containing the response and metadata
        """
        # Override the model in the prompt chain
        prompt_chain = prompt_chain.copy()
        prompt_chain["model"] = model
        
        # Get the provider for this model
        provider = self.get_provider_for_model(model)
        if not provider:
            raise ValueError(f"No provider found for model: {model}")
        
        try:
            # Try the primary provider
            return await provider.process_with_prompt_chain(prompt_chain, user_input, context)
        except Exception as e:
            if not use_fallbacks or not self.fallback_order:
                # No fallbacks or fallbacks disabled
                raise
            
            # Try fallbacks in order
            last_error = e
            for provider_name in self.fallback_order:
                if provider_name != self.model_to_provider_map.get(model):  # Skip the one that already failed
                    try:
                        fallback_provider = self.providers[provider_name]
                        # Use the default model for this fallback provider
                        fallback_model = fallback_provider.get_default_model()
                        prompt_chain["model"] = fallback_model
                        
                        result = await fallback_provider.process_with_prompt_chain(prompt_chain, user_input, context)
                        
                        # Add fallback information to the result
                        if "metadata" not in result:
                            result["metadata"] = {}
                        result["metadata"]["fallback"] = True
                        result["metadata"]["original_model"] = model
                        result["metadata"]["fallback_model"] = fallback_model
                        
                        return result
                    except Exception as fallback_error:
                        last_error = fallback_error
                        continue
            
            # If we get here, all fallbacks failed
            raise last_error
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """
        Get all available models grouped by provider
        
        Returns:
            Dict mapping provider names to lists of model identifiers
        """
        result = {}
        for provider_name, provider in self.providers.items():
            result[provider_name] = provider.get_available_models()
        return result

# Singleton instance
_model_router = None

def get_model_router() -> ModelRouter:
    """
    Get the singleton ModelRouter instance
    """
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter()
    return _model_router
