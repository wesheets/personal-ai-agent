import os
from typing import Dict, Any, Optional
from app.providers.model_router import ModelRouter, get_model_router
from app.providers.openai_provider import OpenAIProvider
from app.providers.claude_provider import ClaudeProvider
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_model_providers():
    """
    Initialize and register all model providers with the router
    """
    router = get_model_router()
    
    # Initialize OpenAI provider if API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        try:
            openai_provider = OpenAIProvider(api_key=openai_api_key)
            router.register_provider(
                provider_name="openai",
                provider=openai_provider,
                models=openai_provider.get_available_models(),
                is_fallback=True
            )
            print("OpenAI provider registered successfully")
        except Exception as e:
            print(f"Failed to initialize OpenAI provider: {str(e)}")
    else:
        print("OPENAI_API_KEY not found, OpenAI provider not registered")
    
    # Initialize Claude provider if API key is available
    claude_api_key = os.getenv("CLAUDE_API_KEY")
    if claude_api_key:
        try:
            claude_provider = ClaudeProvider(api_key=claude_api_key)
            router.register_provider(
                provider_name="claude",
                provider=claude_provider,
                models=claude_provider.get_available_models(),
                is_fallback=True
            )
            print("Claude provider registered successfully")
        except Exception as e:
            print(f"Failed to initialize Claude provider: {str(e)}")
    else:
        print("CLAUDE_API_KEY not found, Claude provider not registered")
    
    # Add model aliases for easier reference
    # Map friendly names to actual model identifiers
    model_aliases = {
        # OpenAI aliases
        "gpt-4": "gpt-4",
        "gpt-4-turbo": "gpt-4-turbo",
        "gpt-3.5-turbo": "gpt-3.5-turbo",
        
        # Claude aliases
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
        "claude-opus": "claude-3-opus-20240229",
        "claude-sonnet": "claude-3-sonnet-20240229",
        "claude-haiku": "claude-3-haiku-20240307"
    }
    
    # Register aliases
    for alias, model_id in model_aliases.items():
        provider_name = router.model_to_provider_map.get(model_id)
        if provider_name:
            router.model_to_provider_map[alias] = provider_name
    
    return router

async def process_with_model(
    model: str, 
    prompt_chain: Dict[str, Any], 
    user_input: str, 
    context: Optional[Dict[str, Any]] = None,
    use_fallbacks: bool = True
) -> Dict[str, Any]:
    """
    Process a request with the specified model
    
    Args:
        model: Model identifier
        prompt_chain: The prompt chain configuration
        user_input: The user's input text
        context: Optional context information
        use_fallbacks: Whether to try fallback providers if the primary fails
        
    Returns:
        Dict containing the response and metadata
    """
    router = get_model_router()
    return await router.process_with_model(
        model=model,
        prompt_chain=prompt_chain,
        user_input=user_input,
        context=context,
        use_fallbacks=use_fallbacks
    )

def get_available_models() -> Dict[str, Any]:
    """
    Get all available models
    
    Returns:
        Dict with available models information
    """
    router = get_model_router()
    return {
        "providers": router.get_available_models(),
        "model_map": router.model_to_provider_map
    }
