
import asyncio
import sys
import os
from app.providers.model_router import ModelRouter, ModelProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.claude_provider import ClaudeProvider

# Mock model providers for testing
class MockOpenAIProvider(ModelProvider):
    def __init__(self):
        self.available_models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        self.default_model = "gpt-4"
    
    async def process_with_prompt_chain(self, prompt_chain, user_input, context=None):
        model = prompt_chain.get("model", self.default_model)
        print(f"MOCK: Processing with OpenAI model: {model}")
        print(f"MOCK: User input: {user_input[:50]}...")
        if context:
            print(f"MOCK: Context: {context}")
        
        return {
            "content": f"This is a mock response from OpenAI {model}",
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 30,
                "total_tokens": 80
            },
            "timestamp": 1711734000,
            "model": model,
            "provider": "openai"
        }
    
    def get_available_models(self):
        return self.available_models
    
    def get_default_model(self):
        return self.default_model

class MockClaudeProvider(ModelProvider):
    def __init__(self):
        self.available_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        self.default_model = "claude-3-sonnet-20240229"
    
    async def process_with_prompt_chain(self, prompt_chain, user_input, context=None):
        model = prompt_chain.get("model", self.default_model)
        print(f"MOCK: Processing with Claude model: {model}")
        print(f"MOCK: User input: {user_input[:50]}...")
        if context:
            print(f"MOCK: Context: {context}")
        
        return {
            "content": f"This is a mock response from Claude {model}",
            "usage": {
                "input_tokens": 40,
                "output_tokens": 25,
                "total_tokens": 65
            },
            "timestamp": 1711734000,
            "model": model,
            "provider": "claude"
        }
    
    def get_available_models(self):
        return self.available_models
    
    def get_default_model(self):
        return self.default_model

async def test_multi_model_support():
    print("Testing Multi-Model Support...")
    
    # Create a model router
    router = ModelRouter()
    
    # Register mock providers
    openai_provider = MockOpenAIProvider()
    claude_provider = MockClaudeProvider()
    
    router.register_provider(
        provider_name="openai",
        provider=openai_provider,
        models=openai_provider.get_available_models(),
        is_fallback=True
    )
    
    router.register_provider(
        provider_name="claude",
        provider=claude_provider,
        models=claude_provider.get_available_models(),
        is_fallback=True
    )
    
    # Add model aliases
    model_aliases = {
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307"
    }
    
    for alias, model_id in model_aliases.items():
        provider_name = router.model_to_provider_map.get(model_id)
        if provider_name:
            router.model_to_provider_map[alias] = provider_name
    
    # Test 1: Process with OpenAI model
    print("\n1. Testing OpenAI model:")
    prompt_chain = {
        "system": "You are a helpful assistant.",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    result = await router.process_with_model(
        model="gpt-4",
        prompt_chain=prompt_chain,
        user_input="Tell me about artificial intelligence",
        context={"topic": "AI"}
    )
    
    print(f"Result from OpenAI: {result['content']}")
    print(f"Model used: {result['model']}")
    print(f"Provider: {result['provider']}")
    
    # Test 2: Process with Claude model
    print("\n2. Testing Claude model:")
    result = await router.process_with_model(
        model="claude-3-sonnet",
        prompt_chain=prompt_chain,
        user_input="Explain quantum computing",
        context={"topic": "Computing"}
    )
    
    print(f"Result from Claude: {result['content']}")
    print(f"Model used: {result['model']}")
    print(f"Provider: {result['provider']}")
    
    # Test 3: Process with model alias
    print("\n3. Testing model alias:")
    result = await router.process_with_model(
        model="claude-3-opus",
        prompt_chain=prompt_chain,
        user_input="Write a poem about technology",
        context={"style": "creative"}
    )
    
    print(f"Result from alias: {result['content']}")
    print(f"Model used: {result['model']}")
    print(f"Provider: {result['provider']}")
    
    # Test 4: Test fallback mechanism
    print("\n4. Testing fallback mechanism:")
    
    # Create a router with a failing provider
    fallback_router = ModelRouter()
    
    class FailingProvider(ModelProvider):
        def __init__(self):
            self.available_models = ["failing-model"]
            self.default_model = "failing-model"
        
        async def process_with_prompt_chain(self, prompt_chain, user_input, context=None):
            raise Exception("This provider always fails")
        
        def get_available_models(self):
            return self.available_models
        
        def get_default_model(self):
            return self.default_model
    
    # Register providers
    fallback_router.register_provider(
        provider_name="failing",
        provider=FailingProvider(),
        models=["failing-model"],
        is_fallback=False
    )
    
    fallback_router.register_provider(
        provider_name="openai",
        provider=openai_provider,
        models=openai_provider.get_available_models(),
        is_fallback=True
    )
    
    try:
        result = await fallback_router.process_with_model(
            model="failing-model",
            prompt_chain=prompt_chain,
            user_input="This should fail and fallback to OpenAI",
            context={},
            use_fallbacks=True
        )
        
        print(f"Fallback result: {result['content']}")
        print(f"Fallback model used: {result['model']}")
        print(f"Fallback provider: {result['provider']}")
        if "fallback" in result.get("metadata", {}):
            print(f"Fallback metadata: {result['metadata']}")
    except Exception as e:
        print(f"Fallback test failed: {str(e)}")
    
    print("\nMulti-model support tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_multi_model_support())
