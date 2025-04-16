"""
Test script for the respond endpoint.

This script tests:
1. Registering a test user with the user_context module
2. Sending a message to the respond endpoint
3. Verifying the response format and content
4. Testing with log_interaction flag to verify memory writing
5. Testing with different user preferences
"""

import sys
import os
import json
import requests
import uuid
from datetime import datetime

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Base URLs for API requests
USER_CONTEXT_URL = "http://localhost:8000/api/modules/user_context"
RESPOND_URL = "http://localhost:8000/api/modules/respond"

def test_respond_endpoint():
    """Test the respond endpoint functionality"""
    print("\n🧪 Testing respond endpoint...")
    
    # Generate unique test IDs
    test_id = f"test_{uuid.uuid4().hex[:8]}"
    user_id = f"user_{uuid.uuid4().hex[:6]}"
    
    # Test 1: Register a test user
    print(f"\n📝 Test 1: Registering test user with ID {user_id}...")
    
    # Create test data for user registration
    register_data = {
        "user_id": user_id,
        "name": f"Test User {test_id}",
        "agent_id": "hal",
        "preferences": {
            "mode": "reflective",
            "persona": "helpful_assistant"
        }
    }
    
    # Register the user
    try:
        response = requests.post(f"{USER_CONTEXT_URL}/register", json=register_data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ User registered successfully")
        print(f"  User Context ID: {result['user_context_id']}")
        print(f"  Memory Scope: {result['memory_scope']}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to register user: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False
    
    # Test 2: Send a message to the respond endpoint
    print(f"\n💬 Test 2: Sending message to respond endpoint...")
    
    # Create test data for respond request
    respond_data = {
        "user_id": user_id,
        "message": "Hello, what can you help me with today?",
        "log_interaction": False
    }
    
    # Send the message
    try:
        response = requests.post(RESPOND_URL, json=respond_data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Response received successfully")
        print(f"  Status: {result['status']}")
        print(f"  Agent ID: {result['agent_id']}")
        print(f"  Response: {result['response']}")
        
        # Verify response format
        assert result["status"] == "ok", "Status should be 'ok'"
        assert result["agent_id"] == "hal", "Agent ID should be 'hal'"
        assert result["response"], "Response should not be empty"
        assert result["memory_id"] is None, "Memory ID should be None when log_interaction is False"
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get response: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {str(e)}")
        return False
    
    # Test 3: Send a message with log_interaction=True
    print(f"\n💾 Test 3: Sending message with log_interaction=True...")
    
    # Create test data for respond request with log_interaction
    respond_data_with_log = {
        "user_id": user_id,
        "message": "Please remember this message for future reference.",
        "log_interaction": True
    }
    
    # Send the message
    try:
        response = requests.post(RESPOND_URL, json=respond_data_with_log)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Response received successfully")
        print(f"  Status: {result['status']}")
        print(f"  Agent ID: {result['agent_id']}")
        print(f"  Response: {result['response']}")
        print(f"  Memory ID: {result['memory_id']}")
        
        # Verify response format
        assert result["status"] == "ok", "Status should be 'ok'"
        assert result["agent_id"] == "hal", "Agent ID should be 'hal'"
        assert result["response"], "Response should not be empty"
        assert result["memory_id"], "Memory ID should not be None when log_interaction is True"
        
        # Store memory_id for later verification
        memory_id = result["memory_id"]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get response: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {str(e)}")
        return False
    
    # Test 4: Verify memory was written
    print(f"\n🔍 Test 4: Verifying memory was written...")
    
    # Check memory endpoint
    try:
        response = requests.get(f"http://localhost:8000/api/modules/read?memory_id={memory_id}")
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Memory retrieved successfully")
        print(f"  Memory ID: {result['memories'][0]['memory_id']}")
        print(f"  Type: {result['memories'][0]['type']}")
        print(f"  Content: {result['memories'][0]['content']}")
        
        # Verify memory content
        assert result["status"] == "ok", "Status should be 'ok'"
        assert result["memories"][0]["memory_id"] == memory_id, f"Memory ID should be {memory_id}"
        assert result["memories"][0]["type"] == "agent_reply", "Memory type should be 'agent_reply'"
        assert result["memories"][0]["content"], "Memory content should not be empty"
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to retrieve memory: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {str(e)}")
        return False
    
    # Test 5: Test with different user preferences
    print(f"\n🎭 Test 5: Testing with different user preferences...")
    
    # Create a new user with analytical preferences
    analytical_user_id = f"analytical_{uuid.uuid4().hex[:6]}"
    
    # Register the analytical user
    analytical_register_data = {
        "user_id": analytical_user_id,
        "name": f"Analytical User {test_id}",
        "agent_id": "hal",
        "preferences": {
            "mode": "analytical",
            "persona": "technical_expert"
        }
    }
    
    try:
        response = requests.post(f"{USER_CONTEXT_URL}/register", json=analytical_register_data)
        response.raise_for_status()
        
        # Send a message from the analytical user
        analytical_respond_data = {
            "user_id": analytical_user_id,
            "message": "Explain how this system works.",
            "log_interaction": False
        }
        
        response = requests.post(RESPOND_URL, json=analytical_respond_data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Analytical user response received successfully")
        print(f"  Status: {result['status']}")
        print(f"  Agent ID: {result['agent_id']}")
        print(f"  Response: {result['response']}")
        
        # Verify response format
        assert result["status"] == "ok", "Status should be 'ok'"
        assert result["agent_id"] == "hal", "Agent ID should be 'hal'"
        assert result["response"], "Response should not be empty"
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to test analytical user: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {str(e)}")
        return False
    
    # Test 6: Test with session_id for continuity
    print(f"\n🔄 Test 6: Testing with session_id for continuity...")
    
    # Generate a session ID
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    # Send first message in session
    session_respond_data_1 = {
        "user_id": user_id,
        "message": "Let's start a conversation about AI.",
        "log_interaction": True,
        "session_id": session_id
    }
    
    try:
        response = requests.post(RESPOND_URL, json=session_respond_data_1)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ First session message response received")
        print(f"  Session ID: {result['session_id']}")
        
        # Verify session ID is returned
        assert result["session_id"] == session_id, f"Session ID should be {session_id}"
        
        # Send second message in same session
        session_respond_data_2 = {
            "user_id": user_id,
            "message": "Continue our discussion about AI.",
            "log_interaction": True,
            "session_id": session_id
        }
        
        response = requests.post(RESPOND_URL, json=session_respond_data_2)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Second session message response received")
        print(f"  Session ID: {result['session_id']}")
        
        # Verify session ID is returned
        assert result["session_id"] == session_id, f"Session ID should be {session_id}"
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to test session continuity: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {str(e)}")
        return False
    
    print("\n✅ All respond endpoint tests passed successfully!")
    return True

if __name__ == "__main__":
    success = test_respond_endpoint()
    if success:
        print("\n🎉 Respond endpoint is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Respond endpoint test failed")
        sys.exit(1)
