"""
Test script for the user_context module.

This script tests:
1. Registering a new user with the user_context module
2. Retrieving a user's context
3. Updating an existing user's context
4. Default preferences when none are provided
"""

import sys
import os
import json
import requests
import uuid
from datetime import datetime

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Base URL for API requests
BASE_URL = "http://localhost:8000/api/modules/user_context"

def test_user_context_module():
    """Test the user_context module endpoints"""
    print("\n🧪 Testing user_context module...")
    
    # Generate unique test IDs
    test_id = f"test_{uuid.uuid4().hex[:8]}"
    user_id = f"user_{uuid.uuid4().hex[:6]}"
    
    # Test 1: Register a new user
    print(f"\n📝 Test 1: Registering new user with ID {user_id}...")
    
    # Create test data
    register_data = {
        "user_id": user_id,
        "name": f"Test User {test_id}",
        "agent_id": "hal",
        "preferences": {
            "mode": "reflective",
            "persona": "creative_counselor"
        }
    }
    
    # Make the request
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ User registered successfully")
        print(f"  User Context ID: {result['user_context_id']}")
        print(f"  Memory Scope: {result['memory_scope']}")
        
        # Verify response format
        assert result["status"] == "ok", "Status should be 'ok'"
        assert result["user_context_id"] == f"ctx_{user_id}", "User context ID should be 'ctx_{user_id}'"
        assert result["memory_scope"] == f"user:{user_id}", "Memory scope should be 'user:{user_id}'"
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to register user: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {str(e)}")
        return False
    
    # Test 2: Get user context
    print(f"\n🔍 Test 2: Retrieving user context for {user_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/get?user_id={user_id}")
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ User context retrieved successfully")
        print(f"  User ID: {result['user_id']}")
        print(f"  Agent ID: {result['agent_id']}")
        print(f"  Memory Scope: {result['memory_scope']}")
        print(f"  Preferences: {json.dumps(result['preferences'], indent=2)}")
        print(f"  Created At: {result['created_at']}")
        
        # Verify response format
        assert result["user_id"] == user_id, f"User ID should be '{user_id}'"
        assert result["agent_id"] == "hal", "Agent ID should be 'hal'"
        assert result["memory_scope"] == f"user:{user_id}", f"Memory scope should be 'user:{user_id}'"
        assert result["preferences"]["mode"] == "reflective", "Mode should be 'reflective'"
        assert result["preferences"]["persona"] == "creative_counselor", "Persona should be 'creative_counselor'"
        assert "created_at" in result, "Created at timestamp should be present"
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to retrieve user context: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {str(e)}")
        return False
    
    # Test 3: Update existing user
    print(f"\n🔄 Test 3: Updating existing user {user_id}...")
    
    # Create updated test data
    updated_register_data = {
        "user_id": user_id,
        "name": f"Updated User {test_id}",
        "agent_id": "ash",
        "preferences": {
            "mode": "analytical",
            "persona": "technical_expert",
            "tone": "professional"
        }
    }
    
    # Make the request
    try:
        response = requests.post(f"{BASE_URL}/register", json=updated_register_data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ User updated successfully")
        print(f"  User Context ID: {result['user_context_id']}")
        print(f"  Memory Scope: {result['memory_scope']}")
        
        # Verify response format
        assert result["status"] == "ok", "Status should be 'ok'"
        assert result["user_context_id"] == f"ctx_{user_id}", "User context ID should be 'ctx_{user_id}'"
        assert result["memory_scope"] == f"user:{user_id}", "Memory scope should be 'user:{user_id}'"
        
        # Get updated user context
        response = requests.get(f"{BASE_URL}/get?user_id={user_id}")
        response.raise_for_status()
        result = response.json()
        
        # Verify updated data
        assert result["name"] == f"Updated User {test_id}", "Name should be updated"
        assert result["agent_id"] == "ash", "Agent ID should be updated to 'ash'"
        assert result["preferences"]["mode"] == "analytical", "Mode should be updated to 'analytical'"
        assert result["preferences"]["persona"] == "technical_expert", "Persona should be updated to 'technical_expert'"
        assert result["preferences"]["tone"] == "professional", "Tone should be added as 'professional'"
        
        print(f"✅ User context updated and verified")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to update user: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {str(e)}")
        return False
    
    # Test 4: Register user with default preferences
    print(f"\n🔄 Test 4: Registering user with default preferences...")
    
    # Generate a new user ID
    default_user_id = f"default_{uuid.uuid4().hex[:6]}"
    
    # Create test data with no preferences
    default_register_data = {
        "user_id": default_user_id,
        "name": f"Default User {test_id}",
        "agent_id": "hal",
        "preferences": {}
    }
    
    # Make the request
    try:
        response = requests.post(f"{BASE_URL}/register", json=default_register_data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ User registered successfully")
        print(f"  User Context ID: {result['user_context_id']}")
        print(f"  Memory Scope: {result['memory_scope']}")
        
        # Get user context to check default preferences
        response = requests.get(f"{BASE_URL}/get?user_id={default_user_id}")
        response.raise_for_status()
        result = response.json()
        
        # Verify default preferences
        assert "mode" in result["preferences"], "Default mode should be set"
        assert "persona" in result["preferences"], "Default persona should be set"
        assert result["preferences"]["mode"] == "standard", "Default mode should be 'standard'"
        assert result["preferences"]["persona"] == "default", "Default persona should be 'default'"
        
        print(f"✅ Default preferences verified:")
        print(f"  Mode: {result['preferences']['mode']}")
        print(f"  Persona: {result['preferences']['persona']}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to register user with default preferences: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"  Response: {e.response.text}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {str(e)}")
        return False
    
    # Test 5: Get non-existent user
    print(f"\n🔍 Test 5: Retrieving non-existent user...")
    
    try:
        response = requests.get(f"{BASE_URL}/get?user_id=non_existent_user")
        
        # This should return a 404 status code
        assert response.status_code == 404, "Should return 404 for non-existent user"
        result = response.json()
        assert result["status"] == "error", "Status should be 'error'"
        assert "not found" in result["message"].lower(), "Message should indicate user not found"
        
        print(f"✅ Non-existent user test passed")
        print(f"  Status Code: {response.status_code}")
        print(f"  Message: {result['message']}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {str(e)}")
        return False
    
    print("\n✅ All user_context module tests passed successfully!")
    return True

if __name__ == "__main__":
    success = test_user_context_module()
    if success:
        print("\n🎉 User context module is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ User context module test failed")
        sys.exit(1)
