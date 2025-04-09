"""
Test script for the patched AgentRunner module.

This script tests the enhanced AgentRunner module with additional
error handling, logging, and diagnostics to fix 502 errors.
"""

import sys
import os
import json
import time

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the agent_runner module
from app.modules.agent_runner import run_agent, test_core_forge_isolation

def test_with_core_forge():
    """
    Test the AgentRunner with Core.Forge agent.
    """
    print("\n=== Testing AgentRunner with Core.Forge ===\n")
    
    # Create test messages
    messages = [
        {"role": "user", "content": "What is 7 + 5?"}
    ]
    
    # Run the agent
    print(f"Running Core.Forge agent with message: {messages[0]['content']}")
    start_time = time.time()
    result = run_agent("Core.Forge", messages)
    execution_time = time.time() - start_time
    
    # Print the result
    print(f"\nResult:")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Response: {result.get('response', 'No response')}")
    print(f"Registry available: {result.get('registry_available', False)}")
    print(f"Execution time: {execution_time:.2f}s")
    
    if 'usage' in result:
        print(f"Token usage: {json.dumps(result['usage'], indent=2)}")
    
    # Verify the result
    if result.get('status') == 'ok':
        print("\n✅ Test passed: Core.Forge agent returned a response")
    else:
        print("\n❌ Test failed: Core.Forge agent did not return expected response")
    
    return result

def test_with_invalid_agent():
    """
    Test the AgentRunner with an invalid agent ID.
    """
    print("\n=== Testing AgentRunner with Invalid Agent ===\n")
    
    # Create test messages
    messages = [
        {"role": "user", "content": "Hello, are you there?"}
    ]
    
    # Run the agent
    print(f"Running non-existent agent with message: {messages[0]['content']}")
    start_time = time.time()
    result = run_agent("NonExistentAgent", messages)
    execution_time = time.time() - start_time
    
    # Print the result
    print(f"\nResult:")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Response: {result.get('response', 'No response')}")
    print(f"Registry available: {result.get('registry_available', False)}")
    print(f"Execution time: {execution_time:.2f}s")
    
    # Verify the result
    if result.get('status') == 'error' and 'not found' in result.get('response', ''):
        print("\n✅ Test passed: Invalid agent returned appropriate error")
    else:
        print("\n❌ Test failed: Invalid agent did not return expected error")
    
    return result

def test_with_missing_api_key():
    """
    Test the AgentRunner with a missing OpenAI API key.
    """
    print("\n=== Testing AgentRunner with Missing API Key ===\n")
    
    # Save current API key
    original_api_key = os.environ.get("OPENAI_API_KEY")
    
    try:
        # Remove API key from environment
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        # Create test messages
        messages = [
            {"role": "user", "content": "What is 7 + 5?"}
        ]
        
        # Run the agent
        print(f"Running Core.Forge agent without API key")
        start_time = time.time()
        result = run_agent("Core.Forge", messages)
        execution_time = time.time() - start_time
        
        # Print the result
        print(f"\nResult:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Response: {result.get('response', 'No response')}")
        print(f"Execution time: {execution_time:.2f}s")
        
        # Verify the result
        if result.get('status') == 'error' and 'API key' in result.get('response', ''):
            print("\n✅ Test passed: Missing API key returned appropriate error")
        else:
            print("\n❌ Test failed: Missing API key did not return expected error")
        
        return result
    
    finally:
        # Restore original API key
        if original_api_key:
            os.environ["OPENAI_API_KEY"] = original_api_key

def main():
    """
    Run all tests.
    """
    print("=== AgentRunner Module Enhanced Tests ===")
    
    # Test CoreForgeAgent in isolation
    isolation_result = test_core_forge_isolation()
    
    # Test with Core.Forge
    core_forge_result = test_with_core_forge()
    
    # Test with invalid agent
    invalid_agent_result = test_with_invalid_agent()
    
    # Test with missing API key
    missing_api_key_result = test_with_missing_api_key()
    
    # Print summary
    print("\n=== Test Summary ===\n")
    print(f"CoreForgeAgent isolation test: {'PASSED' if isolation_result.get('status') == 'success' else 'FAILED'}")
    print(f"Core.Forge test: {'PASSED' if core_forge_result.get('status') == 'ok' else 'FAILED'}")
    print(f"Invalid agent test: {'PASSED' if invalid_agent_result.get('status') == 'error' else 'FAILED'}")
    print(f"Missing API key test: {'PASSED' if missing_api_key_result.get('status') == 'error' else 'FAILED'}")

if __name__ == "__main__":
    main()
