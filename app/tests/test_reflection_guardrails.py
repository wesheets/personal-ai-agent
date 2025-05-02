"""
Test Reflection Guardrails Module

This module contains tests for the reflection guardrails system to ensure
all components work together correctly and handle various scenarios properly.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

# Import the modules to test
from app.modules.reflection_guardrails import process_loop_completion, get_guardrails_status, override_guardrails
from app.modules.post_loop_summary_handler import process_loop_reflection
from app.modules.rerun_decision_engine import make_rerun_decision
from app.modules.pessimist_bias_tracking import track_bias
from app.modules.reflection_fatigue_scoring import process_reflection_fatigue

# Mock data for testing
MOCK_LOOP_ID = "test_loop_001"
MOCK_REFLECTION_STATUS = "done"
MOCK_ORCHESTRATOR_PERSONA = "SAGE"

async def test_process_loop_completion():
    """Test the main process_loop_completion function."""
    print("\n=== Testing process_loop_completion ===")
    
    # Test with default parameters
    result = await process_loop_completion(
        MOCK_LOOP_ID,
        MOCK_REFLECTION_STATUS,
        MOCK_ORCHESTRATOR_PERSONA
    )
    
    print(f"Result status: {result['status']}")
    print(f"Decision: {result['decision_result']['decision']}")
    
    # Validate the result
    assert result["status"] == "success", "Expected status to be 'success'"
    assert "reflection_result" in result, "Expected reflection_result in result"
    assert "decision_result" in result, "Expected decision_result in result"
    assert "orchestrator_persona" in result, "Expected orchestrator_persona in result"
    
    print("✅ process_loop_completion test passed")
    return result

async def test_process_loop_completion_with_overrides():
    """Test process_loop_completion with overrides."""
    print("\n=== Testing process_loop_completion with overrides ===")
    
    # Test with overrides
    result = await process_loop_completion(
        MOCK_LOOP_ID,
        MOCK_REFLECTION_STATUS,
        MOCK_ORCHESTRATOR_PERSONA,
        override_fatigue=True,
        override_max_reruns=True,
        override_by="test_operator"
    )
    
    print(f"Result status: {result['status']}")
    print(f"Decision: {result['decision_result']['decision']}")
    print(f"Overridden by: {result['decision_result'].get('overridden_by')}")
    
    # Validate the result
    assert result["status"] == "success", "Expected status to be 'success'"
    assert "reflection_result" in result, "Expected reflection_result in result"
    assert "decision_result" in result, "Expected decision_result in result"
    
    # Check if overrides were applied
    if "overridden_by" in result["decision_result"]:
        assert result["decision_result"]["overridden_by"] == "test_operator", "Expected overridden_by to be 'test_operator'"
    
    print("✅ process_loop_completion with overrides test passed")
    return result

async def test_get_guardrails_status():
    """Test the get_guardrails_status function."""
    print("\n=== Testing get_guardrails_status ===")
    
    # First process a loop to have data to check
    await process_loop_completion(
        MOCK_LOOP_ID,
        MOCK_REFLECTION_STATUS,
        MOCK_ORCHESTRATOR_PERSONA
    )
    
    # Now get the guardrails status
    result = await get_guardrails_status(MOCK_LOOP_ID)
    
    print(f"Result status: {result['status']}")
    if "guardrails_status" in result:
        status = result["guardrails_status"]
        print(f"Rerun count: {status.get('rerun_count', 'N/A')}")
        print(f"Max reruns: {status.get('max_reruns', 'N/A')}")
        print(f"Bias echo: {status.get('bias_echo', 'N/A')}")
        print(f"Reflection fatigue: {status.get('reflection_fatigue', 'N/A')}")
    
    # Validate the result
    assert result["status"] == "success", "Expected status to be 'success'"
    assert "guardrails_status" in result, "Expected guardrails_status in result"
    
    print("✅ get_guardrails_status test passed")
    return result

async def test_override_guardrails():
    """Test the override_guardrails function."""
    print("\n=== Testing override_guardrails ===")
    
    # First process a loop to have data to override
    await process_loop_completion(
        MOCK_LOOP_ID,
        MOCK_REFLECTION_STATUS,
        MOCK_ORCHESTRATOR_PERSONA
    )
    
    # Now override the guardrails
    result = await override_guardrails(
        MOCK_LOOP_ID,
        override_fatigue=True,
        override_max_reruns=True,
        override_by="test_operator",
        override_reason="Testing override functionality"
    )
    
    print(f"Result status: {result['status']}")
    print(f"Override fatigue: {result.get('override_fatigue', 'N/A')}")
    print(f"Override max reruns: {result.get('override_max_reruns', 'N/A')}")
    print(f"Overridden by: {result.get('overridden_by', 'N/A')}")
    print(f"Override reason: {result.get('override_reason', 'N/A')}")
    
    # Validate the result
    assert result["status"] == "success", "Expected status to be 'success'"
    assert result["override_fatigue"] == True, "Expected override_fatigue to be True"
    assert result["override_max_reruns"] == True, "Expected override_max_reruns to be True"
    assert result["overridden_by"] == "test_operator", "Expected overridden_by to be 'test_operator'"
    
    print("✅ override_guardrails test passed")
    return result

async def test_bias_echo_detection():
    """Test the bias echo detection functionality."""
    print("\n=== Testing bias echo detection ===")
    
    # Create mock bias tags with repetition
    bias_tags = [
        {"tag": "tone_exaggeration", "severity": 0.8, "impact": "high"},
        {"tag": "overconfidence", "severity": 0.6, "impact": "medium"}
    ]
    
    # Track bias for multiple loops to trigger echo detection
    for i in range(4):  # Track for 4 loops to exceed threshold of 3
        loop_id = f"{MOCK_LOOP_ID}_bias_{i}"
        result = await track_bias(loop_id, bias_tags)
        
        print(f"Loop {i+1} bias tracking result:")
        print(f"  Bias echo: {result.get('bias_echo', 'N/A')}")
        print(f"  Repeated tags: {result.get('repeated_tags', 'N/A')}")
        
        # On the last iteration, we expect bias echo to be detected
        if i == 3:
            assert result["bias_echo"] == True, "Expected bias_echo to be True after 4 iterations"
            assert "tone_exaggeration" in result["repeated_tags"], "Expected 'tone_exaggeration' in repeated_tags"
    
    print("✅ bias echo detection test passed")
    return result

async def test_reflection_fatigue_scoring():
    """Test the reflection fatigue scoring functionality."""
    print("\n=== Testing reflection fatigue scoring ===")
    
    # Process fatigue for a loop with no improvement
    result = await process_reflection_fatigue(
        MOCK_LOOP_ID,
        alignment_score=0.72,  # Below threshold of 0.75
        drift_score=0.28       # Above threshold of 0.25
    )
    
    print(f"Reflection fatigue: {result.get('reflection_fatigue', 'N/A')}")
    print(f"Previous fatigue: {result.get('previous_fatigue', 'N/A')}")
    print(f"Fatigue increased: {result.get('fatigue_increased', 'N/A')}")
    print(f"Threshold exceeded: {result.get('threshold_exceeded', 'N/A')}")
    
    # Validate the result
    assert "reflection_fatigue" in result, "Expected reflection_fatigue in result"
    assert "fatigue_increased" in result, "Expected fatigue_increased in result"
    
    # Process fatigue multiple times to exceed threshold
    fatigue = 0.0
    for i in range(4):  # Process 4 times to exceed threshold of 0.5
        result = await process_reflection_fatigue(
            f"{MOCK_LOOP_ID}_fatigue_{i}",
            alignment_score=0.72,  # No improvement
            drift_score=0.28,      # No improvement
            previous_fatigue=fatigue
        )
        fatigue = result["reflection_fatigue"]
        
        print(f"Iteration {i+1} fatigue: {fatigue}")
        print(f"Threshold exceeded: {result.get('threshold_exceeded', 'N/A')}")
        
        # On the last iteration, we expect the threshold to be exceeded
        if i == 3:
            assert result["threshold_exceeded"] == True, "Expected threshold_exceeded to be True after 4 iterations"
    
    print("✅ reflection fatigue scoring test passed")
    return result

async def run_all_tests():
    """Run all tests for the reflection guardrails system."""
    print("\n=== Running all reflection guardrails tests ===\n")
    
    # Run the tests
    await test_process_loop_completion()
    await test_process_loop_completion_with_overrides()
    await test_get_guardrails_status()
    await test_override_guardrails()
    await test_bias_echo_detection()
    await test_reflection_fatigue_scoring()
    
    print("\n=== All tests completed successfully ===")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_all_tests())
