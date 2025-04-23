"""
Test script for loop execution guard with the provided test case

This script tests the loop_execution_guard function with the specific test case
provided in the task to ensure it properly processes the data and returns
the expected status.
"""

import sys
import logging
import json
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append('/home/ubuntu/personal-ai-agent')

# Import the required modules
from app.modules.loop_execution_guard import loop_execution_guard
from app.modules.recursive_reflection_engine import should_reflect
from app.modules.freeze_controller import should_freeze_loop
from app.modules.trust_score_evaluator import evaluate_trust_delta, get_trust_score

def test_with_provided_case():
    """Test the loop_execution_guard function with the provided test case."""
    
    # The test case provided in the task
    test_case = {
        "loop_id": "loop_004",
        "project_id": "life_tree",
        "prompt": "If your confidence is under 50% or trust is unknown, freeze. If HAL and CRITIC disagree, stop.",
        "initiator": "operator"
    }
    
    logger.info("Testing with provided test case:")
    logger.info(json.dumps(test_case, indent=2))
    
    # Call the loop execution guard
    result = loop_execution_guard(test_case)
    
    # Log the result
    logger.info(f"Result from loop_execution_guard: {json.dumps(result, indent=2)}")
    
    # Check if the result matches expectations
    if result["status"] in ["frozen", "reflection-triggered"]:
        logger.info("✅ Test PASSED: Guard returned expected status")
        logger.info(f"Status: {result['status']}")
        logger.info(f"Reason: {result.get('reason', '')}")
    else:
        logger.error("❌ Test FAILED: Guard did not return expected status")
        logger.error(f"Expected: 'frozen' or 'reflection-triggered'")
        logger.error(f"Actual: {result['status']}")
    
    return result

def test_individual_components():
    """Test individual components with the provided test case."""
    
    # The test case provided in the task
    test_case = {
        "loop_id": "loop_004",
        "project_id": "life_tree",
        "prompt": "If your confidence is under 50% or trust is unknown, freeze. If HAL and CRITIC disagree, stop.",
        "initiator": "operator"
    }
    
    logger.info("\nTesting individual components:")
    
    # Test freeze controller
    logger.info("Testing freeze_controller.should_freeze_loop:")
    should_freeze = should_freeze_loop(test_case)
    logger.info(f"should_freeze_loop result: {should_freeze}")
    
    # Test reflection engine
    logger.info("Testing recursive_reflection_engine.should_reflect:")
    should_reflect_result = should_reflect(test_case)
    logger.info(f"should_reflect result: {should_reflect_result}")
    
    # Test trust evaluator
    logger.info("Testing trust_score_evaluator.get_trust_score:")
    trust_score = get_trust_score(test_case)
    logger.info(f"get_trust_score result: {trust_score}")
    
    logger.info("Testing trust_score_evaluator.evaluate_trust_delta:")
    trust_delta = evaluate_trust_delta(test_case)
    logger.info(f"evaluate_trust_delta result: {trust_delta}")
    
    return {
        "should_freeze": should_freeze,
        "should_reflect": should_reflect_result,
        "trust_score": trust_score,
        "trust_delta": trust_delta
    }

if __name__ == "__main__":
    logger.info("Starting test of loop execution guard with provided test case")
    
    # Test with the provided case
    result = test_with_provided_case()
    
    # Test individual components
    component_results = test_individual_components()
    
    # Print summary
    logger.info("\nTest Summary:")
    logger.info(f"Guard result status: {result['status']}")
    logger.info(f"Should freeze: {component_results['should_freeze']}")
    logger.info(f"Should reflect: {component_results['should_reflect']}")
    logger.info(f"Trust score: {component_results['trust_score']}")
    logger.info(f"Trust delta: {component_results['trust_delta']}")
