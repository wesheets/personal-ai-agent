"""
Test script for the refactored /api/project/start endpoint.

This script tests that the circular import issue has been resolved
by using the chain_runner helper instead of directly importing app.
"""

import sys
import os
import json
import asyncio
from fastapi.testclient import TestClient

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app - this should not cause circular imports now
from app.main import app

def test_project_start_endpoint():
    """Test the refactored /api/project/start endpoint."""
    
    print("🧪 Testing refactored /api/project/start endpoint...")
    
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
            print("✅ SUCCESS: Project start endpoint is working correctly!")
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
    print("🧪 Testing refactored /api/project/start endpoint...")
    print("🔍 This test verifies that the circular import issue has been resolved")
    success = test_project_start_endpoint()
    if success:
        print("✅ Test passed: Circular import issue has been resolved!")
        sys.exit(0)
    else:
        print("❌ Test failed: There may still be issues with the implementation")
        sys.exit(1)
