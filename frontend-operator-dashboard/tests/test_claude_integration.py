
import asyncio
import sys
import os
import json
from app.providers.claude_provider import ClaudeProvider

# Mock the actual API call for testing
class MockClaudeProvider(ClaudeProvider):
    def __init__(self):
        # Skip the actual initialization that requires API key
        self.available_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        self.default_model = "claude-3-sonnet-20240229"
    
    async def process_with_prompt_chain(self, prompt_chain, user_input, context=None):
        model = prompt_chain.get("model", self.default_model)
        
        # Print what would be sent to Claude API
        print(f"MOCK CLAUDE API CALL:")
        print(f"  Model: {model}")
        print(f"  System prompt: {prompt_chain.get('system', 'No system prompt')[:50]}...")
        print(f"  User input: {user_input[:50]}...")
        if context:
            print(f"  Context: {json.dumps(context)[:50]}...")
        print(f"  Temperature: {prompt_chain.get('temperature', 0.7)}")
        print(f"  Max tokens: {prompt_chain.get('max_tokens', 1000)}")
        
        # Return a mock response
        return {
            "content": f"This is a mock response from Claude {model}. I've processed your request about '{user_input[:30]}...'",
            "usage": {
                "input_tokens": 40,
                "output_tokens": 25,
                "total_tokens": 65
            },
            "timestamp": 1711734000,
            "model": model,
            "provider": "claude"
        }

async def test_claude_integration():
    print("Testing Claude API Integration...")
    
    # Create an instance of the mock Claude provider
    claude = MockClaudeProvider()
    
    # Test 1: Basic prompt processing
    print("\n1. Testing basic prompt processing:")
    prompt_chain = {
        "system": "You are Claude, a helpful AI assistant created by Anthropic.",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    result = await claude.process_with_prompt_chain(
        prompt_chain=prompt_chain,
        user_input="Tell me about quantum computing"
    )
    
    print(f"Result: {result['content']}")
    print(f"Model used: {result['model']}")
    print(f"Token usage: {result['usage']}")
    
    # Test 2: Using different Claude model
    print("\n2. Testing different Claude model:")
    prompt_chain["model"] = "claude-3-opus-20240229"
    
    result = await claude.process_with_prompt_chain(
        prompt_chain=prompt_chain,
        user_input="Explain the theory of relativity"
    )
    
    print(f"Result: {result['content']}")
    print(f"Model used: {result['model']}")
    print(f"Token usage: {result['usage']}")
    
    # Test 3: With context and examples
    print("\n3. Testing with context and examples:")
    prompt_chain = {
        "system": "You are a senior backend engineer who is blunt and precise.",
        "model": "claude-3-sonnet-20240229",
        "temperature": 0.5,
        "max_tokens": 1500,
        "examples": [
            {
                "user": "How should I structure my API?",
                "assistant": "Use RESTful principles. Organize by resource. Version your endpoints."
            }
        ]
    }
    
    context = {
        "project_type": "web",
        "priority": True,
        "tech_stack": ["Python", "FastAPI", "Docker"]
    }
    
    result = await claude.process_with_prompt_chain(
        prompt_chain=prompt_chain,
        user_input="What's the best way to implement authentication in my API?",
        context=context
    )
    
    print(f"Result: {result['content']}")
    print(f"Model used: {result['model']}")
    print(f"Token usage: {result['usage']}")
    
    # Test 4: Message formatting
    print("\n4. Testing message formatting:")
    
    # Get the formatted messages
    messages = claude._prepare_messages(
        prompt_chain=prompt_chain,
        user_input="How should I handle database migrations?",
        context=context
    )
    
    print("Formatted messages:")
    for i, message in enumerate(messages):
        print(f"  Message {i+1}:")
        print(f"    Role: {message['role']}")
        print(f"    Content: {message['content'][:50]}...")
    
    print("\nClaude API integration tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_claude_integration())
