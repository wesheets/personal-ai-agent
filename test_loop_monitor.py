"""
Test Loop Monitor Module

This script tests the Loop Timeout and Frozen Task Detection functionality
to ensure it correctly identifies agents that exceed their execution timeout.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the modules to test
from app.modules.loop_monitor import (
    log_agent_execution_start,
    log_agent_execution_complete,
    check_for_frozen_agents,
    get_agent_execution_status,
    reset_frozen_agents
)
from app.modules.project_state import read_project_state, update_project_state

# Test project ID
TEST_PROJECT_ID = "test_timeout_detection_001"

def setup_test_project():
    """Set up a test project for timeout detection testing."""
    print("Setting up test project...")
    
    # Create a basic project state
    project_state = {
        "project_id": TEST_PROJECT_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "active",
        "next_recommended_step": "Run HAL to create initial files",
        "loop_status": "running",
        "agents": {},
        "task_log": [],
        "logic_modules": {},
        "registry": {},
        "loop_count": 0,
        "completed_steps": []
    }
    
    # Write the project state
    result = update_project_state(TEST_PROJECT_ID, project_state)
    print(f"Project setup result: {result['status']}")
    
    return result['status'] == "success"

def test_agent_execution_logging():
    """Test logging agent execution start and completion."""
    print("\n=== Testing Agent Execution Logging ===")
    
    # Log HAL agent start
    print("Logging HAL agent execution start...")
    start_result = log_agent_execution_start(TEST_PROJECT_ID, "hal")
    print(f"Start result: {start_result['status']}")
    
    # Wait a moment
    time.sleep(1)
    
    # Log HAL agent completion
    print("Logging HAL agent execution completion...")
    complete_result = log_agent_execution_complete(TEST_PROJECT_ID, "hal")
    print(f"Completion result: {complete_result['status']}")
    
    # Get execution status
    status = get_agent_execution_status(TEST_PROJECT_ID)
    print(f"Execution status: {json.dumps(status, indent=2)}")
    
    # Verify HAL agent was logged correctly
    if "hal" in status.get("current_status", {}):
        print("✅ HAL agent execution logging test passed")
        return True
    else:
        print("❌ HAL agent execution logging test failed")
        return False

def test_timeout_detection():
    """Test detecting agents that exceed their timeout."""
    print("\n=== Testing Timeout Detection ===")
    
    # Log NOVA agent start with a timestamp in the past (exceeding timeout)
    print("Logging NOVA agent execution start...")
    start_result = log_agent_execution_start(TEST_PROJECT_ID, "nova")
    print(f"Start result: {start_result['status']}")
    
    # Manually update the start time to be in the past (exceeding the timeout)
    project_state = read_project_state(TEST_PROJECT_ID)
    execution_log = project_state.get("agent_execution_log", [])
    
    for entry in execution_log:
        if entry["agent"] == "nova" and entry["status"] == "running":
            # Set start time to 60 seconds ago (nova timeout is 45 seconds)
            past_time = datetime.utcnow() - timedelta(seconds=60)
            entry["start_time"] = past_time.isoformat()
    
    # Update the project state with the modified execution log
    update_result = update_project_state(TEST_PROJECT_ID, {
        "agent_execution_log": execution_log
    })
    print(f"Update result: {update_result['status']}")
    
    # Check for frozen agents
    print("Checking for frozen agents...")
    frozen_agents = check_for_frozen_agents(TEST_PROJECT_ID)
    print(f"Frozen agents: {json.dumps(frozen_agents, indent=2)}")
    
    # Verify NOVA agent was detected as frozen
    if frozen_agents and any(agent["agent"] == "nova" for agent in frozen_agents):
        print("✅ Timeout detection test passed")
        return True
    else:
        print("❌ Timeout detection test failed")
        return False

def test_reset_frozen_agents():
    """Test resetting frozen agents."""
    print("\n=== Testing Reset Frozen Agents ===")
    
    # Reset frozen agents
    print("Resetting frozen agents...")
    reset_result = reset_frozen_agents(TEST_PROJECT_ID)
    print(f"Reset result: {json.dumps(reset_result, indent=2)}")
    
    # Get execution status after reset
    status = get_agent_execution_status(TEST_PROJECT_ID)
    
    # Verify NOVA agent was reset
    nova_status = status.get("current_status", {}).get("nova")
    if nova_status == "reset_after_timeout":
        print("✅ Reset frozen agents test passed")
        return True
    else:
        print("❌ Reset frozen agents test failed")
        return False

def test_multiple_agents():
    """Test timeout detection with multiple agents."""
    print("\n=== Testing Multiple Agents ===")
    
    # Log CRITIC agent start
    print("Logging CRITIC agent execution start...")
    start_result = log_agent_execution_start(TEST_PROJECT_ID, "critic")
    print(f"Start result: {start_result['status']}")
    
    # Log ASH agent start
    print("Logging ASH agent execution start...")
    start_result = log_agent_execution_start(TEST_PROJECT_ID, "ash")
    print(f"Start result: {start_result['status']}")
    
    # Manually update the CRITIC start time to be in the past (exceeding the timeout)
    project_state = read_project_state(TEST_PROJECT_ID)
    execution_log = project_state.get("agent_execution_log", [])
    
    for entry in execution_log:
        if entry["agent"] == "critic" and entry["status"] == "running":
            # Set start time to 30 seconds ago (critic timeout is 20 seconds)
            past_time = datetime.utcnow() - timedelta(seconds=30)
            entry["start_time"] = past_time.isoformat()
    
    # Update the project state with the modified execution log
    update_result = update_project_state(TEST_PROJECT_ID, {
        "agent_execution_log": execution_log
    })
    print(f"Update result: {update_result['status']}")
    
    # Check for frozen agents
    print("Checking for frozen agents...")
    frozen_agents = check_for_frozen_agents(TEST_PROJECT_ID)
    print(f"Frozen agents: {json.dumps(frozen_agents, indent=2)}")
    
    # Verify CRITIC agent was detected as frozen but ASH was not
    critic_frozen = any(agent["agent"] == "critic" for agent in frozen_agents)
    ash_frozen = any(agent["agent"] == "ash" for agent in frozen_agents)
    
    if critic_frozen and not ash_frozen:
        print("✅ Multiple agents test passed")
        return True
    else:
        print("❌ Multiple agents test failed")
        return False

def cleanup_test_project():
    """Clean up the test project."""
    print("\n=== Cleaning Up Test Project ===")
    
    # Mark the project as complete
    update_result = update_project_state(TEST_PROJECT_ID, {
        "status": "complete",
        "loop_status": "complete"
    })
    print(f"Cleanup result: {update_result['status']}")
    
    return update_result['status'] == "success"

def run_all_tests():
    """Run all tests."""
    print("=== Starting Loop Monitor Tests ===")
    
    # Set up test project
    if not setup_test_project():
        print("❌ Failed to set up test project")
        return False
    
    # Run tests
    test_results = [
        test_agent_execution_logging(),
        test_timeout_detection(),
        test_reset_frozen_agents(),
        test_multiple_agents()
    ]
    
    # Clean up
    cleanup_test_project()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Total tests: {len(test_results)}")
    print(f"Passed: {test_results.count(True)}")
    print(f"Failed: {test_results.count(False)}")
    
    return all(test_results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
