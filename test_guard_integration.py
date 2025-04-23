"""
Test script for loop execution guard with the provided test case

This script tests the validate_loop_endpoint function with the specific test case
provided in the task to ensure it properly processes the data and returns
the expected status.
"""

import sys
import logging
import json
import asyncio
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append('/home/ubuntu/personal-ai-agent')

# Import the required modules
from app.routes.orchestrator_routes import validate_loop_endpoint
from app.routes.orchestrator_routes import LoopValidateRequest

async def test_with_provided_case():
    """Test the validate_loop_endpoint function with the provided test case."""
    
    # The test case provided in the task
    test_case = {
        "loop_id": "loop_005",
        "project_id": "life_tree",
        "prompt": "Reflect before acting. Freeze if trust is low or uncertain. If any agent disagrees with HAL, stop.",
        "initiator": "operator"
    }
    
    logger.info("Testing with provided test case:")
    logger.info(json.dumps(test_case, indent=2))
    
    # Create a request object
    request = LoopValidateRequest(
        loop_id=test_case["loop_id"],
        loop_data=test_case,
        mode="balanced"
    )
    
    # Call the endpoint
    result = await validate_loop_endpoint(request)
    
    # Log the result
    logger.info(f"Result from validate_loop_endpoint: {json.dumps(result, indent=2)}")
    
    # Check if the result matches expectations
    if isinstance(result, dict) and result.get("status") in ["frozen", "reflection-triggered"]:
        logger.info("✅ Test PASSED: Endpoint returned expected status")
        logger.info(f"Status: {result['status']}")
        logger.info(f"Reason: {result.get('reason', '')}")
    else:
        logger.error("❌ Test FAILED: Endpoint did not return expected status")
        logger.error(f"Expected: 'frozen' or 'reflection-triggered'")
        logger.error(f"Actual: {result.get('status', 'unknown')}")
    
    return result

if __name__ == "__main__":
    logger.info("Starting test of validate_loop_endpoint with provided test case")
    
    # Run the test
    asyncio.run(test_with_provided_case())
