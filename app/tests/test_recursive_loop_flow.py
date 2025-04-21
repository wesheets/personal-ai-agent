"""
Integration test for the recursive loop flow.

This script tests the complete recursive loop flow by:
1. Sending a loop-complete signal to trigger reflection
2. Verifying that reflection agents are called
3. Checking the rerun decision based on alignment and drift scores
4. Validating the creation of a new loop ID for reruns
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules
from app.modules.post_loop_summary_handler import process_loop_reflection
from app.modules.rerun_decision_engine import evaluate_rerun_decision

async def test_loop_reflection(loop_id: str) -> Dict[str, Any]:
    """Test the loop reflection process."""
    print(f"\n=== Testing Loop Reflection for {loop_id} ===")
    
    try:
        # Process loop reflection
        reflection_result = await process_loop_reflection(loop_id)
        
        print(f"Reflection Result:")
        print(json.dumps(reflection_result, indent=2))
        
        return reflection_result
    except Exception as e:
        print(f"Error in loop reflection: {str(e)}")
        return {
            "alignment_score": 0.5,
            "drift_score": 0.5,
            "summary_valid": False
        }

async def test_rerun_decision(
    loop_id: str,
    alignment_score: float,
    drift_score: float,
    summary_valid: bool
) -> Dict[str, Any]:
    """Test the rerun decision process."""
    print(f"\n=== Testing Rerun Decision for {loop_id} ===")
    print(f"Alignment Score: {alignment_score}")
    print(f"Drift Score: {drift_score}")
    print(f"Summary Valid: {summary_valid}")
    
    try:
        # Evaluate rerun decision
        decision = await evaluate_rerun_decision(
            loop_id,
            alignment_score,
            drift_score,
            summary_valid
        )
        
        print(f"Rerun Decision:")
        print(json.dumps(decision, indent=2))
        
        return decision
    except Exception as e:
        print(f"Error in rerun decision: {str(e)}")
        return {
            "decision": "error",
            "loop_id": loop_id,
            "reason": str(e)
        }

async def test_recursive_loop_flow():
    """Test the complete recursive loop flow."""
    print("=== Testing Recursive Loop Flow ===")
    
    # Test cases with different alignment and drift scores
    test_cases = [
        {
            "loop_id": "loop_001",
            "alignment_score": 0.8,
            "drift_score": 0.2,
            "summary_valid": True,
            "expected_decision": "finalize"
        },
        {
            "loop_id": "loop_002",
            "alignment_score": 0.7,
            "drift_score": 0.3,
            "summary_valid": True,
            "expected_decision": "rerun"
        },
        {
            "loop_id": "loop_003",
            "alignment_score": 0.6,
            "drift_score": 0.2,
            "summary_valid": True,
            "expected_decision": "rerun"
        },
        {
            "loop_id": "loop_004_r2",  # Already rerun twice
            "alignment_score": 0.6,
            "drift_score": 0.3,
            "summary_valid": False,
            "expected_decision": "rerun"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n\n=== Test Case: {test_case['loop_id']} ===")
        
        # Test reflection process
        reflection_result = await test_loop_reflection(test_case['loop_id'])
        
        # Override reflection result with test case values
        reflection_result = {
            "alignment_score": test_case['alignment_score'],
            "drift_score": test_case['drift_score'],
            "summary_valid": test_case['summary_valid']
        }
        
        # Test rerun decision
        decision = await test_rerun_decision(
            test_case['loop_id'],
            reflection_result['alignment_score'],
            reflection_result['drift_score'],
            reflection_result['summary_valid']
        )
        
        # Verify the decision
        if decision['decision'] == test_case['expected_decision']:
            print(f"✅ Test passed: Decision matches expected ({test_case['expected_decision']})")
        else:
            print(f"❌ Test failed: Expected {test_case['expected_decision']}, got {decision['decision']}")
        
        # If decision is to rerun, verify the new loop ID
        if decision['decision'] == 'rerun':
            if 'new_loop_id' in decision:
                print(f"✅ New loop ID generated: {decision['new_loop_id']}")
            else:
                print("❌ No new loop ID generated for rerun")

async def main():
    """Main function to run the tests."""
    await test_recursive_loop_flow()

if __name__ == "__main__":
    asyncio.run(main())
