"""
Test script to verify the /api/project/start route registration.

This script tests that the project start router is properly imported and registered.
"""

import sys
import os
import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_project_start_registration():
    """Test that the project start router is properly registered."""
    
    logger.info("Testing project start router registration...")
    
    # Import the app from main.py
    try:
        # Add project root to path
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Import the app
        from app.main import app
        
        # Create a test client
        client = TestClient(app)
        
        # Check if the debug endpoint is available
        logger.info("Checking debug endpoint for project start registration...")
        response = client.get("/api/debug/project-start-registered")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("registered", False):
                logger.info("✅ Project start router is registered!")
                logger.info(f"Routes: {data.get('project_start_routes')}")
                print("✅ SUCCESS: Project start router is registered!")
                print(f"Routes: {data.get('project_start_routes')}")
                return True
            else:
                logger.error("❌ Project start router is not registered!")
                logger.error(f"Debug data: {data}")
                print("❌ ERROR: Project start router is not registered!")
                print(f"Debug data: {data}")
                return False
        else:
            logger.error(f"❌ Debug endpoint returned status {response.status_code}")
            logger.error(f"Response: {response.text}")
            print(f"❌ ERROR: Debug endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to check routes directly
            routes = [route for route in app.routes if "/api/project/start" in getattr(route, "path", "")]
            if routes:
                logger.info(f"✅ Found {len(routes)} routes matching /api/project/start")
                for route in routes:
                    logger.info(f"Route: {route.path} {route.methods}")
                print(f"✅ Found {len(routes)} routes matching /api/project/start")
                return True
            else:
                logger.error("❌ No routes found matching /api/project/start")
                print("❌ ERROR: No routes found matching /api/project/start")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error testing project start registration: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing project start router registration...")
    success = test_project_start_registration()
    if success:
        print("✅ Test passed: Project start router is properly registered!")
        sys.exit(0)
    else:
        print("❌ Test failed: Project start router is not properly registered!")
        sys.exit(1)
