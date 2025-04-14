"""
Test script for the AgentRunner module.

This script tests the AgentRunner module with Core.Forge agent,
both with and without registry availability.
"""

import sys
import os
import json
import time

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the agent_runner module
from app.modules.agent_runner import run_agent

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
    if result.get('status') == 'ok' and '12' in result.get('response', ''):
        print("\n✅ Test passed: Core.Forge agent returned correct response")
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

def main():
    """
    Run all tests.
    """
    print("=== AgentRunner Module Tests ===")
    
    # Test with Core.Forge
    core_forge_result = test_with_core_forge()
    
    # Test with invalid agent
    invalid_agent_result = test_with_invalid_agent()
    
    # Print summary
    print("\n=== Test Summary ===\n")
    print(f"Core.Forge test: {'PASSED' if core_forge_result.get('status') == 'ok' else 'FAILED'}")
    print(f"Invalid agent test: {'PASSED' if invalid_agent_result.get('status') == 'error' else 'FAILED'}")

if __name__ == "__main__":
    main()
