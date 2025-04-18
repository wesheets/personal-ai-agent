"""
Test script for the agent loop functionality.

This script simulates different project states with various next_recommended_step values
to test the agent autonomy chain.
"""

import json
import os
import sys
from typing import Dict, Any

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.loop import run_agent_from_loop, determine_agent_from_step
from app.modules.project_state import write_project_state, read_project_state

def create_test_project_state(project_id: str, next_step: str) -> Dict[str, Any]:
    """
    Create a test project state with the specified next_recommended_step.
    
    Args:
        project_id: The project identifier
        next_step: The next recommended step
        
    Returns:
        Dict containing the project state
    """
    project_state = {
        "project_id": project_id,
        "status": "in_progress",
        "domain": "test",
        "goal": "Test agent autonomy",
        "next_recommended_step": next_step,
        "loop_count": 0,
        "max_loops": 10,
        "agents_involved": [],
        "completed_steps": []
    }
    
    # Write the project state to disk
    write_project_state(project_id, project_state)
    
    return project_state

def test_agent_selection():
    """
    Test the agent selection logic with different step descriptions.
    """
    print("\n=== Testing Agent Selection Logic ===")
    
    test_steps = [
        "Run HAL to create initial files",
        "Design UI components with NOVA",
        "Document the API with ASH",
        "Review the code with CRITIC",
        "Generate a summary with SAGE",
        "Coordinate the project with ORCHESTRATOR",
        "Create a new feature",
        "Design the layout",
        "Document the changes",
        "Review the implementation",
        "Summarize the project",
        "Plan the next steps"
    ]
    
    for step in test_steps:
        agent = determine_agent_from_step(step)
        print(f"Step: \"{step}\" -> Agent: {agent}")
    
    print("Agent selection test completed.\n")

def test_with_different_project_states():
    """
    Test the run_agent_from_loop function with different project states.
    """
    print("\n=== Testing with Different Project States ===")
    
    test_cases = [
        {
            "project_id": "test_hal_001",
            "next_step": "Run HAL to create initial files for the project"
        },
        {
            "project_id": "test_nova_001",
            "next_step": "Design UI components with NOVA for better user experience"
        },
        {
            "project_id": "test_ash_001",
            "next_step": "Document the API with ASH for developer reference"
        },
        {
            "project_id": "test_critic_001",
            "next_step": "Review the code with CRITIC to identify issues"
        },
        {
            "project_id": "test_sage_001",
            "next_step": "Generate a summary with SAGE for project status"
        },
        {
            "project_id": "test_orchestrator_001",
            "next_step": "Coordinate the project with ORCHESTRATOR for next phase"
        },
        {
            "project_id": "test_implicit_hal_001",
            "next_step": "Create a new feature for user authentication"
        },
        {
            "project_id": "test_implicit_nova_001",
            "next_step": "Design the layout for the dashboard page"
        },
        {
            "project_id": "test_implicit_ash_001",
            "next_step": "Document the changes made to the API"
        },
        {
            "project_id": "test_implicit_critic_001",
            "next_step": "Review the implementation of the new feature"
        },
        {
            "project_id": "test_implicit_sage_001",
            "next_step": "Summarize the project progress for stakeholders"
        },
        {
            "project_id": "test_implicit_orchestrator_001",
            "next_step": "Plan the next steps for the project roadmap"
        }
    ]
    
    for test_case in test_cases:
        project_id = test_case["project_id"]
        next_step = test_case["next_step"]
        
        print(f"\nTesting with project_id={project_id}, next_step=\"{next_step}\"")
        
        # Create test project state
        create_test_project_state(project_id, next_step)
        
        # Verify project state was created
        project_state = read_project_state(project_id)
        if not project_state:
            print(f"❌ Failed to create project state for {project_id}")
            continue
            
        print(f"✅ Project state created for {project_id}")
        
        # Determine expected agent
        expected_agent = determine_agent_from_step(next_step)
        print(f"Expected agent: {expected_agent}")
        
        # Test run_agent_from_loop function
        try:
            print(f"Simulating run_agent_from_loop({project_id})...")
            # In a real test, we would call run_agent_from_loop(project_id)
            # But since we don't want to actually execute agents, we'll just print the expected result
            print(f"✅ Would trigger {expected_agent} agent with task: \"{next_step}\"")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\nProject state tests completed.")

def main():
    """
    Main function to run all tests.
    """
    print("=== Agent Loop Functionality Test ===")
    
    # Test agent selection logic
    test_agent_selection()
    
    # Test with different project states
    test_with_different_project_states()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main()
