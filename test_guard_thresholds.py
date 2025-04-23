"""
Test script for loop execution guard with different thresholds

This script tests the loop_execution_guard function with different threshold scenarios
to ensure it behaves as expected when various conditions are triggered.
"""

import sys
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append('/home/ubuntu/personal-ai-agent')

# Import the required modules
from app.modules.loop_execution_guard import loop_execution_guard
from app.modules.recursive_reflection_engine import should_reflect
from app.modules.freeze_controller import should_freeze_loop
from app.modules.trust_score_evaluator import evaluate_trust_delta

def test_with_different_thresholds():
    """Test the loop_execution_guard function with different threshold scenarios."""
    
    # Test cases with different thresholds
    test_cases = [
        {
            "name": "Normal plan (no triggers)",
            "plan": {
                "loop_id": "test-loop-1",
                "agents": ["hal", "nova", "ash"],
                "mode": "balanced",
                "trust_score": 0.8,
                "uncertainty_level": 0.2,
                "contradictions": []
            },
            "expected_status": "ok"
        },
        {
            "name": "Low trust score (should freeze)",
            "plan": {
                "loop_id": "test-loop-2",
                "agents": ["hal", "nova", "ash"],
                "mode": "balanced",
                "trust_score": 0.2,  # Below 0.3 threshold
                "uncertainty_level": 0.3,
                "contradictions": []
            },
            "expected_status": "frozen"
        },
        {
            "name": "Critical contradiction (should freeze)",
            "plan": {
                "loop_id": "test-loop-3",
                "agents": ["hal", "nova", "ash"],
                "mode": "balanced",
                "trust_score": 0.7,
                "uncertainty_level": 0.4,
                "contradictions": [
                    {"id": "c1", "severity": "critical", "description": "Critical contradiction"}
                ]
            },
            "expected_status": "frozen"
        },
        {
            "name": "High uncertainty (should trigger reflection)",
            "plan": {
                "loop_id": "test-loop-4",
                "agents": ["hal", "nova", "ash"],
                "mode": "balanced",
                "trust_score": 0.6,
                "uncertainty_level": 0.8,  # Above 0.7 threshold
                "contradictions": []
            },
            "expected_status": "reflection-triggered"
        },
        {
            "name": "Low confidence (should trigger reflection)",
            "plan": {
                "loop_id": "test-loop-5",
                "agents": ["hal", "nova", "ash"],
                "mode": "balanced",
                "trust_score": 0.7,
                "uncertainty_level": 0.5,
                "confidence": 0.3,  # Below 0.5 threshold
                "contradictions": []
            },
            "expected_status": "reflection-triggered"
        },
        {
            "name": "Explicit freeze request",
            "plan": {
                "loop_id": "test-loop-6",
                "agents": ["hal", "nova", "ash"],
                "mode": "balanced",
                "trust_score": 0.7,
                "uncertainty_level": 0.3,
                "freeze_requested": True
            },
            "expected_status": "frozen"
        },
        {
            "name": "Explicit reflection request",
            "plan": {
                "loop_id": "test-loop-7",
                "agents": ["hal", "nova", "ash"],
                "mode": "balanced",
                "trust_score": 0.7,
                "uncertainty_level": 0.3,
                "needs_reflection": True
            },
            "expected_status": "reflection-triggered"
        }
    ]
    
    # Run tests
    results = []
    for test_case in test_cases:
        logger.info(f"Testing scenario: {test_case['name']}")
        result = loop_execution_guard(test_case["plan"])
        
        # Check if result matches expected status
        success = result["status"] == test_case["expected_status"]
        
        # Log result
        if success:
            logger.info(f"✅ Test passed: {test_case['name']}")
            logger.info(f"  Expected: {test_case['expected_status']}")
            logger.info(f"  Actual: {result['status']}")
        else:
            logger.error(f"❌ Test failed: {test_case['name']}")
            logger.error(f"  Expected: {test_case['expected_status']}")
            logger.error(f"  Actual: {result['status']}")
        
        # Store result
        results.append({
            "name": test_case["name"],
            "success": success,
            "expected": test_case["expected_status"],
            "actual": result["status"],
            "full_result": result
        })
    
    # Print summary
    logger.info("\nTest Summary:")
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    logger.info(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    test_with_different_thresholds()
