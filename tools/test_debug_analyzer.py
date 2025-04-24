"""
Test endpoint for Debug Analyzer Agent

This script tests the Debug Analyzer agent endpoint by sending a request to analyze
a loop execution and verifying the response structure.
"""

import sys
import os
import json
import asyncio
import requests
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import schemas for validation
from app.schemas.debug_schema import LoopDebugRequest, LoopDebugResult

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_ENDPOINT = "/debug/analyze-loop"
TEST_PROJECT_ID = "demo_writer_001"
TEST_LOOP_ID = "loop_17"

async def test_debug_analyzer_endpoint():
    """Test the Debug Analyzer endpoint with a sample request."""
    print(f"🧪 Testing Debug Analyzer endpoint: {TEST_ENDPOINT}")
    
    # Create test request
    request_data = {
        "loop_id": TEST_LOOP_ID,
        "project_id": TEST_PROJECT_ID,
        "agent_filter": ["hal", "critic"],
        "version": "1"
    }
    
    # Validate request against schema
    try:
        request_obj = LoopDebugRequest(**request_data)
        print(f"✅ Request validation passed")
    except Exception as e:
        print(f"❌ Request validation failed: {str(e)}")
        return False
    
    # Send request to endpoint
    try:
        response = requests.post(
            f"{BASE_URL}{TEST_ENDPOINT}",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response status
        if response.status_code != 200:
            print(f"❌ Request failed with status code {response.status_code}: {response.text}")
            return False
        
        # Parse response
        response_data = response.json()
        print(f"✅ Received response: {json.dumps(response_data, indent=2)}")
        
        # Validate response against schema
        try:
            response_obj = LoopDebugResult(**response_data)
            print(f"✅ Response validation passed")
        except Exception as e:
            print(f"❌ Response validation failed: {str(e)}")
            return False
        
        # Check response content
        if response_data["loop_id"] != TEST_LOOP_ID:
            print(f"❌ Response loop_id mismatch: {response_data['loop_id']} != {TEST_LOOP_ID}")
            return False
        
        if response_data["project_id"] != TEST_PROJECT_ID:
            print(f"❌ Response project_id mismatch: {response_data['project_id']} != {TEST_PROJECT_ID}")
            return False
        
        if "issues" not in response_data or not isinstance(response_data["issues"], list):
            print(f"❌ Response missing issues array")
            return False
        
        if "recommendations" not in response_data or not isinstance(response_data["recommendations"], list):
            print(f"❌ Response missing recommendations array")
            return False
        
        if "confidence_score" not in response_data or not isinstance(response_data["confidence_score"], (int, float)):
            print(f"❌ Response missing confidence_score")
            return False
        
        print(f"✅ Response content validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Request failed with exception: {str(e)}")
        return False

async def test_debug_analyzer_with_partial_memory():
    """Test the Debug Analyzer endpoint with partial memory data."""
    print(f"🧪 Testing Debug Analyzer with partial memory")
    
    # Create test request with raw log text to simulate partial memory
    request_data = {
        "loop_id": "loop_missing_data",
        "project_id": TEST_PROJECT_ID,
        "raw_log_text": "ERROR: HAL agent failed with timeout\nWARNING: Missing memory tag critic_review_loop_missing_data\nINFO: Orchestrator attempting recovery",
        "version": "1"
    }
    
    # Send request to endpoint
    try:
        response = requests.post(
            f"{BASE_URL}{TEST_ENDPOINT}",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response status
        if response.status_code != 200:
            print(f"❌ Partial memory test failed with status code {response.status_code}: {response.text}")
            return False
        
        # Parse response
        response_data = response.json()
        print(f"✅ Received partial memory response: {json.dumps(response_data, indent=2)}")
        
        # Check that the agent handled partial data gracefully
        if "issues" not in response_data or not isinstance(response_data["issues"], list):
            print(f"❌ Partial memory response missing issues array")
            return False
        
        # There should be at least one issue related to the log errors
        log_error_issues = [i for i in response_data["issues"] if i.get("issue_type") == "log_error"]
        if not log_error_issues:
            print(f"❌ Partial memory response should contain log_error issues")
            return False
        
        print(f"✅ Partial memory test passed")
        return True
        
    except Exception as e:
        print(f"❌ Partial memory test failed with exception: {str(e)}")
        return False

async def main():
    """Run all tests."""
    print(f"🧪 Starting Debug Analyzer endpoint tests at {datetime.now().isoformat()}")
    
    # Run tests
    endpoint_test_result = await test_debug_analyzer_endpoint()
    partial_memory_test_result = await test_debug_analyzer_with_partial_memory()
    
    # Print summary
    print("\n🧪 Test Summary:")
    print(f"Endpoint Test: {'✅ PASSED' if endpoint_test_result else '❌ FAILED'}")
    print(f"Partial Memory Test: {'✅ PASSED' if partial_memory_test_result else '❌ FAILED'}")
    
    # Overall result
    if endpoint_test_result and partial_memory_test_result:
        print("\n✅ All tests PASSED")
        return 0
    else:
        print("\n❌ Some tests FAILED")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
