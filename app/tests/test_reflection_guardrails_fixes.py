"""
Test script to verify the reflection guardrails functionality with type safety fixes.

This script tests:
1. Reflection fatigue scoring
2. Bias echo detection
3. Rerun decision logic
4. Type safety for all components

It simulates a loop with multiple reruns to ensure all guardrails work correctly.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Import the modules to test
from app.modules.post_loop_summary_handler import process_loop_reflection
from app.modules.reflection_guardrails import process_loop_completion
from app.modules.reflection_fatigue_scoring import process_reflection_fatigue
from app.modules.rerun_decision_engine import make_rerun_decision

# Mock memory storage for testing
mock_memory_store = {}

# Override the read_from_memory and write_to_memory functions for testing
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    return mock_memory_store.get(key)

async def write_to_memory(key: str, value: Any) -> bool:
    """Write data to memory storage."""
    mock_memory_store[key] = value
    print(f"Writing to memory: {key} = {json.dumps(value, indent=2)}")
    return True

# Patch the modules to use our mock memory functions
import app.modules.post_loop_summary_handler
import app.modules.reflection_guardrails
import app.modules.reflection_fatigue_scoring
import app.modules.rerun_decision_engine

app.modules.post_loop_summary_handler.read_from_memory = read_from_memory
app.modules.post_loop_summary_handler.write_to_memory = write_to_memory
app.modules.reflection_guardrails.read_from_memory = read_from_memory
app.modules.reflection_guardrails.write_to_memory = write_to_memory
app.modules.reflection_fatigue_scoring.read_from_memory = read_from_memory
app.modules.reflection_fatigue_scoring.write_to_memory = write_to_memory
app.modules.rerun_decision_engine.read_from_memory = read_from_memory
app.modules.rerun_decision_engine.write_to_memory = write_to_memory

# Test data
test_loop_id = "loop_005"
test_rerun_id = "loop_005_r1"
test_persona = "SAGE"

# Initialize test data in memory
def initialize_test_data():
    """Initialize test data in memory."""
    # Create a loop trace
    mock_memory_store[f"loop_trace[{test_loop_id}]"] = {
        "loop_id": test_loop_id,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "orchestrator_persona": test_persona,
        "rerun_count": 0,
        "max_reruns": 3,
        "reflection_fatigue": 0.0
    }
    
    # Create a loop summary text
    mock_memory_store[f"loop_summary_text[{test_loop_id}]"] = "This is a test summary for loop 005."
    
    # Create a loop summary with alignment and drift scores
    mock_memory_store[f"loop_summary[{test_loop_id}]"] = {
        "alignment_score": 0.72,
        "drift_score": 0.28,
        "summary_valid": True,
        "reflection_persona": test_persona,
        "bias_echo": False,
        "reflection_fatigue": 0.0,
        "rerun_trigger": ["alignment", "drift"],
        "rerun_reason": "alignment_threshold_not_met"
    }

# Test case 1: Test reflection fatigue scoring
async def test_reflection_fatigue_scoring():
    """Test reflection fatigue scoring functionality."""
    print("\n=== Testing Reflection Fatigue Scoring ===")
    
    # Test with normal dictionary input
    fatigue_result = await process_reflection_fatigue(
        test_loop_id,
        alignment_score=0.72,
        drift_score=0.28
    )
    
    print(f"Fatigue result with normal input: {fatigue_result}")
    assert isinstance(fatigue_result, dict), "Fatigue result should be a dictionary"
    assert "reflection_fatigue" in fatigue_result, "Fatigue result should contain reflection_fatigue"
    
    # Test with float input (simulating the error condition)
    # This should not crash with our type safety fixes
    mock_memory_store[f"loop_trace[{test_loop_id}]"] = 0.5  # Simulate a float instead of a dictionary
    
    try:
        fatigue_result = await process_reflection_fatigue(
            test_loop_id,
            alignment_score=0.72,
            drift_score=0.28
        )
        print(f"Fatigue result with float input: {fatigue_result}")
        assert isinstance(fatigue_result, dict), "Fatigue result should be a dictionary even with float input"
    except Exception as e:
        print(f"Error: {e}")
        assert False, "Should not raise an exception with float input"
    
    # Reset the test data
    initialize_test_data()
    
    print("Reflection fatigue scoring test passed!")

# Test case 2: Test bias echo detection
async def test_bias_echo_detection():
    """Test bias echo detection functionality."""
    print("\n=== Testing Bias Echo Detection ===")
    
    # Process loop reflection with normal input
    reflection_result = await process_loop_reflection(
        test_loop_id,
        override_fatigue=False,
        override_max_reruns=False
    )
    
    print(f"Reflection result: {reflection_result}")
    assert isinstance(reflection_result, dict), "Reflection result should be a dictionary"    assert "bias_echo" in reflection_result, "Reflection result should contain bias_echo"

    # Test with float input (simulating the error condition)
    mock_memory_store[f"loop_summary[{test_loop_id}]"] = 0.5  # Simulate a float instead of a dictionary

    try:
        reflection_result = await process_loop_reflection(
            test_loop_id,
            override_fatigue=False,
            override_max_reruns=False
        )
        print(f"Reflection result with float input: {reflection_result}")
        assert isinstance(reflection_result, dict), "Reflection result should be a dictionary even with float input"
    except Exception as e:
        print(f"Error: {e}")
        assert False, "Should not raise an exception with float input"
    
    # Reset the test data
    initialize_test_data()
    
    print("Bias echo detection test passed!")

# Test case 3: Test rerun decision logic
async def test_rerun_decision_logic():
    """Test rerun decision logic functionality."""
    print("\n=== Testing Rerun Decision Logic ===")
    
    # Make a rerun decision with normal input
    decision_result = await make_rerun_decision(
        test_loop_id,
        override_fatigue=False,
        override_max_reruns=False
    )
    
    print(f"Decision result: {decision_result}")
    assert isinstance(decision_result, dict), "Decision result should be a dictionary"    assert "decision" in decision_result, "Decision result should contain decision"

    # Test with float input (simulating the error condition)
    mock_memory_store[f"loop_summary[{test_loop_id}]"] = 0.5  # Simulate a float instead of a dictionary

    try:
        decision_result = await make_rerun_decision(
            test_loop_id,
            override_fatigue=False,
            override_max_reruns=False
        )
        print(f"Decision result with float input: {decision_result}")
        assert isinstance(decision_result, dict), "Decision result should be a dictionary even with float input"
        assert decision_result["decision"] == "finalize", "Should finalize when reflection result is not a dictionary"
    except Exception as e:
        print(f"Error: {e}")
        assert False, "Should not raise an exception with float input"
    
    # Reset the test data
    initialize_test_data()
    
    print("Rerun decision logic test passed!")

# Test case 4: Test the complete reflection guardrails flow
async def test_complete_reflection_flow():
    """Test the complete reflection guardrails flow."""
    print("\n=== Testing Complete Reflection Flow ===")
    
    # Process loop completion with normal input
    completion_result = await process_loop_completion(
        test_loop_id,
        reflection_status="done",
        orchestrator_persona=test_persona
    )
    
    print(f"Completion result: {completion_result}")
    assert isinstance(completion_result, dict), "Completion result should be a dictionary"
    assert "status" in completion_result, "Completion result should contain status"
    assert completion_result["status"] == "success", "Completion status should be success"
    
    # Test with float input at various stages (simulating the error condition)
    # This tests all the type safety fixes together
    
    # 1. Float in loop trace
    mock_memory_store[f"loop_trace[{test_loop_id}]"] = 0.5
    
    try:
        completion_result = await process_loop_completion(
            test_loop_id,
            reflection_status="done",
            orchestrator_persona=test_persona
        )
        print(f"Completion result with float loop trace: {completion_result}")
        assert isinstance(completion_result, dict), "Completion result should be a dictionary even with float input"
    except Exception as e:
        print(f"Error: {e}")
        assert False, "Should not raise an exception with float input"
    
    # Reset the test data
    initialize_test_data()
    
    # 2. Float in loop summary
    mock_memory_store[f"loop_summary[{test_loop_id}]"] = 0.5
    
    try:
        completion_result = await process_loop_completion(
            test_loop_id,
            reflection_status="done",
            orchestrator_persona=test_persona
        )
        print(f"Completion result with float loop summary: {completion_result}")
        assert isinstance(completion_result, dict), "Completion result should be a dictionary even with float input"
    except Exception as e:
        print(f"Error: {e}")
        assert False, "Should not raise an exception with float input"
    
    # Reset the test data
    initialize_test_data()
    
    print("Complete reflection flow test passed!")

# Test case 5: Test Loop 005 reflection specifically
async def test_loop_005_reflection():
    """Test Loop 005 reflection specifically."""
    print("\n=== Testing Loop 005 Reflection ===")
    
    # Set up Loop 005 with the exact conditions that caused the error
    mock_memory_store[f"loop_trace[loop_005]"] = {
        "loop_id": "loop_005",
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "orchestrator_persona": "SAGE",
        "rerun_count": 0,
        "max_reruns": 3,
        "reflection_fatigue": 0.0
    }
    
    mock_memory_store[f"loop_summary_text[loop_005]"] = "This is the summary for Loop 005."
    
    # The key issue: loop_summary is a float instead of a dictionary
    mock_memory_store[f"loop_summary[loop_005]"] = 0.5
    
    try:
        # Process loop completion
        completion_result = await process_loop_completion(
            "loop_005",
            reflection_status="done",
            orchestrator_persona="SAGE"
        )
        
        print(f"Loop 005 completion result: {completion_result}")
        assert isinstance(completion_result, dict), "Completion result should be a dictionary"
        assert "status" in completion_result, "Completion result should contain status"
        
        # Make a rerun decision
        decision_result = await make_rerun_decision(
            "loop_005",
            override_fatigue=False,
            override_max_reruns=False
        )
        
        print(f"Loop 005 decision result: {decision_result}")
        assert isinstance(decision_result, dict), "Decision result should be a dictionary"
        assert "decision" in decision_result, "Decision result should contain decision"
        
        print("Loop 005 reflection test passed!")
    except Exception as e:
        print(f"Error: {e}")
        assert False, "Should not raise an exception with float input"

# Run all tests
async def run_tests():
    """Run all tests."""
    print("Starting reflection guardrails tests...")
    
    # Initialize test data
    initialize_test_data()
    
    # Run the tests
    await test_reflection_fatigue_scoring()
    await test_bias_echo_detection()
    await test_rerun_decision_logic()
    await test_complete_reflection_flow()
    await test_loop_005_reflection()
    
    print("\nAll tests passed! The type safety fixes are working correctly.")

# Run the tests
if __name__ == "__main__":
    asyncio.run(run_tests())
