"""
Test script for ASH agent memory updates.

This script tests the ASH agent's ability to update project state in memory
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
from app.modules.ash_agent import run_ash_agent
from app.modules.project_state import read_project_state, write_project_state

def create_test_project() -> str:
    """
    Create a test project with initial state.
    
    Returns:
        The project_id of the created test project
    """
    # Generate a unique project_id
    project_id = f"test_ash_memory_{uuid.uuid4().hex[:8]}"
    
    # Create initial project state
    initial_state = {
        "project_id": project_id,
        "status": "in_progress",
        "domain": "test",
        "goal": "Test ASH memory updates",
        "next_recommended_step": "Document the project",
        "loop_count": 3,  # Assuming HAL, NOVA, and CRITIC have already run
        "max_loops": 10,
        "agents_involved": ["hal", "nova", "critic"],  # ASH requires CRITIC to have run first
        "completed_steps": ["hal", "nova", "critic"],
        "last_completed_agent": "critic",
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

def test_ash_memory_updates():
    """
    Test ASH agent memory updates.
    """
    print("\n=== Testing ASH Agent Memory Updates ===\n")
    
    # Create a test project
    project_id = create_test_project()
    
    # Read the initial state
    initial_state = read_project_state(project_id)
    print("\nInitial project state:")
    print(f"  loop_count: {initial_state.get('loop_count', 0)}")
    print(f"  last_completed_agent: {initial_state.get('last_completed_agent', 'None')}")
    print(f"  completed_steps: {initial_state.get('completed_steps', [])}")
    print(f"  files_created: {initial_state.get('files_created', [])}")
    print(f"  next_recommended_step: {initial_state.get('next_recommended_step', 'None')}")
    
    # Run the ASH agent
    print("\nRunning ASH agent...")
    task = "Document the project"
    result = run_ash_agent(task, project_id, ["memory_writer"])
    
    # Check if ASH execution was successful
    if result.get("status") != "success":
        print(f"❌ ASH agent execution failed: {result.get('message', 'Unknown error')}")
        return
    
    print(f"✅ ASH agent execution successful")
    
    # Read the updated state
    updated_state = read_project_state(project_id)
    print("\nUpdated project state:")
    print(f"  loop_count: {updated_state.get('loop_count', 0)}")
    print(f"  last_completed_agent: {updated_state.get('last_completed_agent', 'None')}")
    print(f"  completed_steps: {updated_state.get('completed_steps', [])}")
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
    if updated_state.get("last_completed_agent") == "ash":
        print(f"✅ last_completed_agent set to 'ash'")
    else:
        print(f"❌ last_completed_agent not set correctly: {updated_state.get('last_completed_agent', 'None')}")
    
    # Check completed_steps
    if "ash" in updated_state.get("completed_steps", []):
        print(f"✅ 'ash' added to completed_steps")
    else:
        print(f"❌ 'ash' not added to completed_steps: {updated_state.get('completed_steps', [])}")
    
    # Check files_created
    documentation_files = ["README.md", "docs/setup.md"]
    all_files_created = True
    for file in documentation_files:
        if file not in updated_state.get("files_created", []):
            all_files_created = False
            print(f"❌ File not found in files_created: {file}")
    
    if all_files_created:
        print(f"✅ files_created updated with documentation files")
    else:
        print(f"❌ files_created not updated correctly")
    
    # Check next_recommended_step
    if "SAGE" in updated_state.get("next_recommended_step", "").upper():
        print(f"✅ next_recommended_step updated to trigger SAGE: {updated_state.get('next_recommended_step', 'None')}")
    else:
        print(f"❌ next_recommended_step not set to trigger SAGE: {updated_state.get('next_recommended_step', 'None')}")
    
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
    
    # Run the ASH agent
    print("\nRunning ASH agent (fourth step in the loop)...")
    task = "Document the project"
    result = run_ash_agent(task, project_id, ["memory_writer"])
    
    # Check if ASH execution was successful
    if result.get("status") != "success":
        print(f"❌ ASH agent execution failed: {result.get('message', 'Unknown error')}")
        return
    
    print(f"✅ ASH agent execution successful")
    
    # Read the updated state
    updated_state = read_project_state(project_id)
    print("\nUpdated project state:")
    print(f"  loop_count: {updated_state.get('loop_count', 0)}")
    print(f"  last_completed_agent: {updated_state.get('last_completed_agent', 'None')}")
    print(f"  next_recommended_step: {updated_state.get('next_recommended_step', 'None')}")
    
    # Verify the loop can continue
    print("\nVerifying loop can continue...")
    
    # Check if next_recommended_step is set for SAGE
    next_step = updated_state.get("next_recommended_step", "")
    if "SAGE" in next_step.upper():
        print(f"✅ next_recommended_step set for SAGE: {next_step}")
        print(f"✅ Full autonomy loop can continue to SAGE")
    else:
        print(f"❌ next_recommended_step not set for SAGE: {next_step}")
        print(f"❌ Full autonomy loop may not continue properly")
    
    print("\n=== Test Completed ===\n")

def main():
    """
    Main function to run all tests.
    """
    print("=== ASH Agent Memory Updates Test ===")
    
    # Test ASH memory updates
    test_ash_memory_updates()
    
    # Test full autonomy loop
    test_full_autonomy_loop()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main()
