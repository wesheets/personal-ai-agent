"""
Test script for the internal chain call in the /api/project/start route.

This script tests the internal FastAPI call to ensure it works correctly.
"""

import sys
import os
import json
import asyncio
import httpx
from fastapi.testclient import TestClient

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app
from app.main import app

def test_internal_chain_call():
    """Test the internal chain call using TestClient."""
    
    print("🧪 Testing internal chain call in /api/project/start route...")
    
    # Create a test client
    client = TestClient(app)
    
    # Test data
    test_goal = "Write a simple Python function to calculate factorial"
    
    # Make a request to the /api/project/start endpoint
    try:
        response = client.post(
            "/api/project/start",
            json={"goal": test_goal}
        )
        
        # Print response status code
        print(f"📊 Response status code: {response.status_code}")
        
        # Check if the request was successful
        if response.status_code == 200:
            print("✅ SUCCESS: Internal chain call is working correctly!")
            print("📋 Response preview:")
            response_data = response.json()
            print(f"  Project ID: {response_data.get('project_id')}")
            print(f"  Chain ID: {response_data.get('chain_id')}")
            print(f"  Agents: {len(response_data.get('agents', []))}")
            return True
        else:
            print(f"❌ ERROR: Request failed with status code {response.status_code}")
            print(f"📋 Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing /api/project/start with internal chain call...")
    success = test_internal_chain_call()
    if success:
        print("✅ Test passed: Internal chain call is working correctly!")
        sys.exit(0)
    else:
        print("❌ Test failed: Internal chain call is not working correctly!")
        sys.exit(1)
