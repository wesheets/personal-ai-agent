"""
Test script for CRITIC agent memory updates.

This script tests the CRITIC agent's ability to update project state in memory
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
from app.modules.critic_agent import run_critic_agent
from app.modules.project_state import read_project_state, write_project_state

def create_test_project() -> str:
    """
    Create a test project with initial state.
    
    Returns:
        The project_id of the created test project
    """
    # Generate a unique project_id
    project_id = f"test_critic_memory_{uuid.uuid4().hex[:8]}"
    
    # Create initial project state
    initial_state = {
        "project_id": project_id,
        "status": "in_progress",
        "domain": "test",
        "goal": "Test CRITIC memory updates",
        "next_recommended_step": "Review UI components for the project",
        "loop_count": 2,  # Assuming HAL and NOVA have already run
        "max_loops": 10,
        "agents_involved": ["hal", "nova"],  # CRITIC requires HAL and NOVA to have run first
        "completed_steps": ["hal", "nova"],
        "last_completed_agent": "nova",
        "files_created": [
            "api/crm.py", 
            "README.md",
            "src/components/Dashboard.jsx",
            "src/components/LoginForm.jsx"
        ]  # Files created by HAL and NOVA
    }
    
    # Write the initial state
    write_project_state(project_id, initial_state)
    
    print(f"✅ Created test project: {project_id}")
    return project_id

def test_critic_memory_updates():
    """
    Test CRITIC agent memory updates.
    """
    print("\n=== Testing CRITIC Agent Memory Updates ===\n")
    
    # Create a test project
    project_id = create_test_project()
    
    # Read the initial state
    initial_state = read_project_state(project_id)
    print("\nInitial project state:")
    print(f"  loop_count: {initial_state.get('loop_count', 0)}")
    print(f"  last_completed_agent: {initial_state.get('last_completed_agent', 'None')}")
    print(f"  completed_steps: {initial_state.get('completed_steps', [])}")
    print(f"  next_recommended_step: {initial_state.get('next_recommended_step', 'None')}")
    
    # Run the CRITIC agent
    print("\nRunning CRITIC agent...")
    task = "Review UI components for the project"
    result = run_critic_agent(task, project_id, ["memory_writer"])
    
    # Check if CRITIC execution was successful
    if result.get("status") != "success":
        print(f"❌ CRITIC agent execution failed: {result.get('message', 'Unknown error')}")
        return
    
    print(f"✅ CRITIC agent execution successful")
    
    # Read the updated state
    updated_state = read_project_state(project_id)
    print("\nUpdated project state:")
    print(f"  loop_count: {updated_state.get('loop_count', 0)}")
    print(f"  last_completed_agent: {updated_state.get('last_completed_agent', 'None')}")
    print(f"  completed_steps: {updated_state.get('completed_steps', [])}")
    print(f"  next_recommended_step: {updated_state.get('next_recommended_step', 'None')}")
    print(f"  feedback_log: {updated_state.get('feedback_log', [])}")
    
    # Verify the changes
    print("\nVerifying changes...")
    
    # Check loop_count increment
    if updated_state.get("loop_count", 0) > initial_state.get("loop_count", 0):
        print(f"✅ loop_count incremented: {initial_state.get('loop_count', 0)} -> {updated_state.get('loop_count', 0)}")
    else:
        print(f"❌ loop_count not incremented: {updated_state.get('loop_count', 0)}")
    
    # Check last_completed_agent
    if updated_state.get("last_completed_agent") == "critic":
        print(f"✅ last_completed_agent set to 'critic'")
    else:
        print(f"❌ last_completed_agent not set correctly: {updated_state.get('last_completed_agent', 'None')}")
    
    # Check completed_steps
    if "critic" in updated_state.get("completed_steps", []):
        print(f"✅ 'critic' added to completed_steps")
    else:
        print(f"❌ 'critic' not added to completed_steps: {updated_state.get('completed_steps', [])}")
    
    # Check feedback_log
    if updated_state.get("feedback_log") and isinstance(updated_state.get("feedback_log"), list):
        print(f"✅ feedback_log added with {len(updated_state.get('feedback_log', []))} entries")
    else:
        print(f"❌ feedback_log not added or not a list: {updated_state.get('feedback_log', 'None')}")
    
    # Check next_recommended_step
    next_step = updated_state.get("next_recommended_step", "")
    if "ASH" in next_step or "NOVA" in next_step:
        print(f"✅ next_recommended_step updated to trigger next agent: {next_step}")
    else:
        print(f"❌ next_recommended_step not set correctly: {next_step}")
    
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
    print(f"  last_completed_agent: {initial_state.get('last_completed_agent', 'None')}")
    print(f"  next_recommended_step: {initial_state.get('next_recommended_step', 'None')}")
    
    # Run the CRITIC agent
    print("\nRunning CRITIC agent (third step in the loop)...")
    task = "Review UI components for the project"
    result = run_critic_agent(task, project_id, ["memory_writer"])
    
    # Check if CRITIC execution was successful
    if result.get("status") != "success":
        print(f"❌ CRITIC agent execution failed: {result.get('message', 'Unknown error')}")
        return
    
    print(f"✅ CRITIC agent execution successful")
    
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
    if "ASH" in next_step or "NOVA" in next_step:
        print(f"✅ next_recommended_step set for next agent: {next_step}")
        print(f"✅ Full autonomy loop can continue to {'ASH' if 'ASH' in next_step else 'NOVA'}")
    else:
        print(f"❌ next_recommended_step not set for next agent: {next_step}")
        print(f"❌ Full autonomy loop may not continue properly")
    
    print("\n=== Test Completed ===\n")

def main():
    """
    Main function to run all tests.
    """
    print("=== CRITIC Agent Memory Updates Test ===")
    
    # Test CRITIC memory updates
    test_critic_memory_updates()
    
    # Test full autonomy loop
    test_full_autonomy_loop()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main()
