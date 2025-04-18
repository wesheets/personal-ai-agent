"""
Test script for HAL agent memory updates.

This script tests the HAL agent's ability to update project state in memory
after execution, which is critical for the full agent autonomy loop.
"""

import os
import sys
import json
import uuid
from typing import Dict, Any

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from app.agents.hal import run_hal_agent
from app.modules.project_state import read_project_state, write_project_state

def create_test_project() -> str:
    """
    Create a test project with initial state.
    
    Returns:
        The project_id of the created test project
    """
    # Generate a unique project_id
    project_id = f"test_hal_memory_{uuid.uuid4().hex[:8]}"
    
    # Create initial project state
    initial_state = {
        "project_id": project_id,
        "status": "in_progress",
        "domain": "test",
        "goal": "Test HAL memory updates",
        "next_recommended_step": "Create initial files for the project",
        "loop_count": 0,
        "max_loops": 10,
        "agents_involved": [],
        "completed_steps": [],
        "files_created": []
    }
    
    # Write the initial state
    write_project_state(project_id, initial_state)
    
    print(f"✅ Created test project: {project_id}")
    return project_id

def test_hal_memory_updates():
    """
    Test HAL agent memory updates.
    """
    print("\n=== Testing HAL Agent Memory Updates ===\n")
    
    # Create a test project
    project_id = create_test_project()
    
    # Read the initial state
    initial_state = read_project_state(project_id)
    print("\nInitial project state:")
    print(f"  loop_count: {initial_state.get('loop_count', 0)}")
    print(f"  last_completed_agent: {initial_state.get('last_completed_agent', 'None')}")
    print(f"  files_created: {initial_state.get('files_created', [])}")
    print(f"  next_recommended_step: {initial_state.get('next_recommended_step', 'None')}")
    
    # Run the HAL agent
    print("\nRunning HAL agent...")
    task = "Create initial files for the project"
    result = run_hal_agent(task, project_id)
    
    # Check if HAL execution was successful
    if result.get("status") != "success":
        print(f"❌ HAL agent execution failed: {result.get('message', 'Unknown error')}")
        return
    
    print(f"✅ HAL agent execution successful")
    
    # Read the updated state
    updated_state = read_project_state(project_id)
    print("\nUpdated project state:")
    print(f"  loop_count: {updated_state.get('loop_count', 0)}")
    print(f"  last_completed_agent: {updated_state.get('last_completed_agent', 'None')}")
    print(f"  files_created: {updated_state.get('files_created', [])}")
    print(f"  next_recommended_step: {updated_state.get('next_recommended_step', 'None')}")
    
    # Verify the changes
    print("\nVerifying changes...")
    
    # Check loop_count increment
    if updated_state.get("loop_count", 0) > initial_state.get("loop_count", 0):
        print(f"✅ loop_count incremented: {initial_state.get('loop_count', 0)} -> {updated_state.get('loop_count', 0)}")
    else:
        print(f"❌ loop_count not incremented: {updated_state.get('loop_count', 0)}")
    
    # Check last_completed_agent
    if updated_state.get("last_completed_agent") == "hal":
        print(f"✅ last_completed_agent set to 'hal'")
    else:
        print(f"❌ last_completed_agent not set correctly: {updated_state.get('last_completed_agent', 'None')}")
    
    # Check files_created
    if updated_state.get("files_created") and len(updated_state.get("files_created", [])) > 0:
        print(f"✅ files_created updated: {updated_state.get('files_created', [])}")
    else:
        print(f"❌ files_created not updated: {updated_state.get('files_created', [])}")
    
    # Check next_recommended_step
    if updated_state.get("next_recommended_step") != initial_state.get("next_recommended_step"):
        print(f"✅ next_recommended_step updated: {updated_state.get('next_recommended_step', 'None')}")
    else:
        print(f"❌ next_recommended_step not updated: {updated_state.get('next_recommended_step', 'None')}")
    
    print("\n=== Test Completed ===\n")

def test_full_autonomy_loop():
    """
    Test the full agent autonomy loop.
    """
    print("\n=== Testing Full Agent Autonomy Loop ===\n")
    
    # Create a test project
    project_id = create_test_project()
    
    # Read the initial state
    initial_state = read_project_state(project_id)
    print("\nInitial project state:")
    print(f"  loop_count: {initial_state.get('loop_count', 0)}")
    print(f"  next_recommended_step: {initial_state.get('next_recommended_step', 'None')}")
    
    # Run the HAL agent
    print("\nRunning HAL agent (first step in the loop)...")
    task = "Create initial files for the project"
    result = run_hal_agent(task, project_id)
    
    # Check if HAL execution was successful
    if result.get("status") != "success":
        print(f"❌ HAL agent execution failed: {result.get('message', 'Unknown error')}")
        return
    
    print(f"✅ HAL agent execution successful")
    
    # Read the updated state
    updated_state = read_project_state(project_id)
    print("\nUpdated project state:")
    print(f"  loop_count: {updated_state.get('loop_count', 0)}")
    print(f"  last_completed_agent: {updated_state.get('last_completed_agent', 'None')}")
    print(f"  next_recommended_step: {updated_state.get('next_recommended_step', 'None')}")
    
    # Verify the loop can continue
    print("\nVerifying loop can continue...")
    
    # Check if next_recommended_step is set for the next agent
    next_step = updated_state.get("next_recommended_step", "")
    if "nova" in next_step.lower() or "ash" in next_step.lower() or "critic" in next_step.lower():
        print(f"✅ next_recommended_step set for next agent: {next_step}")
        print(f"✅ Full autonomy loop can continue to the next agent")
    else:
        print(f"❌ next_recommended_step not set for next agent: {next_step}")
        print(f"❌ Full autonomy loop may not continue properly")
    
    print("\n=== Test Completed ===\n")

def main():
    """
    Main function to run all tests.
    """
    print("=== HAL Agent Memory Updates Test ===")
    
    # Test HAL memory updates
    test_hal_memory_updates()
    
    # Test full autonomy loop
    test_full_autonomy_loop()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main()
