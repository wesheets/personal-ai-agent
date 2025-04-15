"""
Test script for HAL agent task.output fix.

This script tests that HAL correctly includes task.output in its returned results
when fulfilling a task, specifically for the string reversal test case.
"""

import sys
import os
import json
from typing import Dict, Any

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the agent_tool_runner and instruction_validator modules
from app.modules.agent_tool_runner import run_agent_tool
from app.modules.instruction_validator import validate_instruction_outputs

def test_hal_task_output():
    """Test that HAL correctly includes task.output in its returned results."""
    
    print("🧪 Testing HAL task.output fix...")
    
    # Test data
    agent_id = "hal"
    goal = "Write a Python function that reverses a string"
    expected_outputs = ["task.output"]
    
    # Run the agent tool
    try:
        print(f"📋 Running HAL agent with goal: {goal}")
        result = run_agent_tool(agent_id, goal)
        
        # Check if the result contains outputs
        if "outputs" not in result:
            print("❌ ERROR: Agent tool result does not contain outputs")
            return False
        
        # Check if task.output is in the outputs
        task_output_found = False
        for output in result["outputs"]:
            if output.get("name") == "task.output":
                task_output_found = True
                print("✅ SUCCESS: task.output found in agent tool result")
                print(f"📝 task.output content: {output.get('content')[:100]}...")
                break
        
        if not task_output_found:
            print("❌ ERROR: task.output not found in agent tool result")
            return False
        
        # Validate the outputs against expected outputs
        print(f"📋 Validating outputs against expected outputs: {expected_outputs}")
        validation_result = validate_instruction_outputs(agent_id, expected_outputs)
        
        # Check if validation passed
        if validation_result["status"] == "complete":
            print("✅ SUCCESS: Validation passed")
            print(f"📝 Validation details: {validation_result['details']}")
            return True
        else:
            print("❌ ERROR: Validation failed")
            print(f"📝 Validation details: {validation_result['details']}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing HAL task.output fix...")
    print("🔍 This test verifies that HAL correctly includes task.output in its returned results")
    success = test_hal_task_output()
    if success:
        print("✅ Test passed: HAL now correctly includes task.output in its returned results!")
        sys.exit(0)
    else:
        print("❌ Test failed: There may still be issues with the implementation")
        sys.exit(1)
