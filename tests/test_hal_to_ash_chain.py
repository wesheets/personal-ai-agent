"""
Test script for verifying the HAL to ASH chain works correctly.

This script tests that ASH properly consumes HAL's output, summarizes it,
and returns the required summary.task.output and reflection fields.
"""

import sys
import os
import json
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from app.modules.instruction_validator import extract_outputs_from_memory, validate_instruction_outputs

def test_hal_to_ash_chain():
    """
    Test that ASH properly consumes HAL's output and returns the required fields.
    """
    print("🧪 Testing HAL to ASH chain...")
    print("🔍 This test verifies that ASH correctly summarizes HAL's output and returns the required fields")
    
    # Step 1: Verify HAL's output
    print("📋 Checking HAL's output...")
    hal_outputs = extract_outputs_from_memory("hal")
    
    # Find task.output in HAL's outputs
    hal_task_output = None
    for output in hal_outputs:
        if "task.output" in output.get("tags", []):
            hal_task_output = output.get("content")
            break
    
    if not hal_task_output:
        print("❌ ERROR: HAL's task.output not found")
        return False
    
    print(f"✅ SUCCESS: HAL's task.output found: {hal_task_output[:50]}...")
    
    # Step 2: Verify ASH's output
    print("📋 Checking ASH's output...")
    ash_outputs = extract_outputs_from_memory("ash")
    
    # Find summary.task.output in ASH's outputs
    ash_summary_output = None
    ash_reflection = None
    
    for output in ash_outputs:
        if "summary.task.output" in output.get("tags", []):
            ash_summary_output = output.get("content")
        elif "reflection" in output.get("tags", []):
            ash_reflection = output.get("content")
    
    if not ash_summary_output:
        print("❌ ERROR: ASH's summary.task.output not found")
        return False
    
    if not ash_reflection:
        print("❌ ERROR: ASH's reflection not found")
        return False
    
    print(f"✅ SUCCESS: ASH's summary.task.output found: {ash_summary_output}")
    print(f"✅ SUCCESS: ASH's reflection found: {ash_reflection}")
    
    # Step 3: Validate ASH's outputs against expected outputs
    print("📋 Validating ASH's outputs against expected outputs...")
    validation_result = validate_instruction_outputs(
        agent_id="ash",
        expected_outputs=["summary.task.output"],
        checkpoints=["reflection"]
    )
    
    if validation_result["status"] != "complete":
        print(f"❌ ERROR: Validation failed: {validation_result['details']}")
        return False
    
    print(f"✅ SUCCESS: Validation passed: {validation_result['details']}")
    
    # Step 4: Verify the content matches the expected format
    print("📋 Verifying content format...")
    expected_summary = "This function capitalizes each word by splitting the string and applying capitalize() to each word."
    expected_reflection = "HAL's implementation is correct."
    
    if ash_summary_output != expected_summary:
        print(f"❌ ERROR: ASH's summary.task.output doesn't match expected format")
        print(f"Expected: {expected_summary}")
        print(f"Actual: {ash_summary_output}")
        return False
    
    if ash_reflection != expected_reflection:
        print(f"❌ ERROR: ASH's reflection doesn't match expected format")
        print(f"Expected: {expected_reflection}")
        print(f"Actual: {ash_reflection}")
        return False
    
    print("✅ SUCCESS: Content format matches expected format")
    
    # All tests passed
    print("✅ Test passed: HAL to ASH chain works correctly!")
    return True

if __name__ == "__main__":
    test_result = test_hal_to_ash_chain()
    sys.exit(0 if test_result else 1)
