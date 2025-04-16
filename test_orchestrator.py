"""
Orchestrator Integration Test

This script tests the functionality of the Orchestrator Multi-Modal Planning & Approval System
by simulating a complete workflow from consultation to goal completion.
"""

import os
import json
import time
import datetime
from typing import Dict, Any, List, Optional

# Mock memory writer function
def mock_memory_writer(goal_id: str, agent_id: str, memory_type: str, content: str, tags: List[str]) -> str:
    """
    Mock function to simulate writing memories.
    
    Args:
        goal_id: ID of the goal
        agent_id: ID of the agent
        memory_type: Type of memory
        content: Memory content
        tags: Memory tags
        
    Returns:
        Generated memory ID
    """
    memory_id = f"memory_{time.time()}"
    
    # Print the memory for debugging
    print(f"\n--- Memory Created ---")
    print(f"Memory ID: {memory_id}")
    print(f"Goal ID: {goal_id}")
    print(f"Agent ID: {agent_id}")
    print(f"Type: {memory_type}")
    print(f"Tags: {tags}")
    print(f"Content: {content}")
    print("---------------------\n")
    
    return memory_id

# Import the OrchestratorAPI
from src.orchestrator.endpoints import OrchestratorAPI

def test_orchestrator():
    """Test the Orchestrator Multi-Modal Planning & Approval System."""
    print("=== Testing Orchestrator Multi-Modal Planning & Approval System ===\n")
    
    # Initialize the OrchestratorAPI
    orchestrator = OrchestratorAPI(memory_writer=mock_memory_writer)
    
    # Step 1: Start a consultation session
    print("Step 1: Starting consultation session...")
    operator_id = "test_operator"
    goal = "Build a SaaS application for podcast creators to manage their episodes and analytics"
    
    result = orchestrator.consult(operator_id, goal)
    session_id = result["session_id"]
    
    print(f"Session created with ID: {session_id}")
    print(f"Goal type detected: {result['goal_type']}")
    print(f"First question: {result['next_question']['question']}")
    
    # Step 2: Answer consultation questions
    print("\nStep 2: Answering consultation questions...")
    
    # Answer the first question
    question_id = result["next_question"]["question_id"]
    answer = "The application should help podcast creators manage their episode publishing workflow, track listener analytics, and monetize their content."
    
    result = orchestrator.respond_to_question(session_id, question_id, answer)
    
    # Continue answering questions until we get a plan
    while result["has_more_questions"]:
        question = result["next_question"]
        question_id = question["question_id"]
        
        print(f"Question: {question['question']}")
        
        # Simulate different answers based on the question
        if "target audience" in question["question"].lower():
            answer = "Independent podcast creators and small podcast networks who want to grow their audience and monetize their content."
        elif "core features" in question["question"].lower():
            answer = "Episode management, publishing workflow, listener analytics, monetization tools, and audience engagement features."
        elif "technical requirements" in question["question"].lower():
            answer = "The application should be a web-based SaaS with mobile responsiveness. We prefer a modern tech stack with React frontend and Node.js backend."
        elif "timeline" in question["question"].lower():
            answer = "We're looking to launch an MVP within 2 months and then iterate based on user feedback."
        else:
            answer = "This is a test answer for the consultation question."
            
        print(f"Answer: {answer}")
        
        result = orchestrator.respond_to_question(session_id, question_id, answer)
    
    # Step 3: Review and confirm the plan
    print("\nStep 3: Reviewing and confirming the plan...")
    
    plan = result["plan"]
    print(f"Plan title: {plan['title']}")
    print(f"Plan description: {plan['description']}")
    print(f"Number of phases: {len(plan['phases'])}")
    
    for i, phase in enumerate(plan['phases']):
        print(f"\nPhase {i+1}: {phase['title']}")
        print(f"Description: {phase['description']}")
        print(f"Estimated duration: {phase['estimated_duration']}")
        print(f"Tools: {', '.join(phase['tools'])}")
        print(f"Agents: {', '.join(phase['agents'])}")
    
    # Confirm the plan
    result = orchestrator.confirm(session_id, approved=True)
    
    goal_id = result["goal_id"]
    print(f"\nPlan approved! Goal created with ID: {goal_id}")
    print(f"Goal title: {result['goal_title']}")
    
    # Step 4: Store credentials
    print("\nStep 4: Storing credentials...")
    
    credentials = {
        "github_repo": "podcast-saas",
        "github_token": "github_pat_test_token",
        "hosting_provider": "AWS",
        "stripe_keys": {
            "public_key": "pk_test_example",
            "secret_key": "sk_test_example"
        },
        "environment": "staging"
    }
    
    result = orchestrator.credentials(goal_id, credentials)
    print(f"Credentials stored: {result['status']}")
    
    # Step 5: Delegate tasks and create checkpoints
    print("\nStep 5: Delegating tasks and creating checkpoints...")
    
    # Get the next task
    next_task = result["next_task"]
    subgoal_id = next_task["subgoal_id"]
    
    # Delegate the task
    result = orchestrator.delegate(goal_id, subgoal_id)
    print(f"Task delegated to {result['delegation']['agent_id']}: {result['delegation']['title']}")
    
    # Simulate HAL creating a checkpoint
    checkpoint_result = orchestrator.checkpoint(
        agent_id="hal",
        goal_id=goal_id,
        subgoal_id=subgoal_id,
        checkpoint_name="database_schema_created",
        checkpoint_type="hard",
        output_memory_id="memory_123",
        auto_approve_if_silent=False,
        details={
            "schema_file": "database_schema.json",
            "tables_created": ["users", "podcasts", "episodes", "analytics"]
        }
    )
    
    checkpoint_id = checkpoint_result["checkpoint_id"]
    print(f"Checkpoint created: {checkpoint_result['checkpoint_id']}")
    print(f"Checkpoint status: {checkpoint_result['checkpoint_status']}")
    print(f"Requires approval: {checkpoint_result['requires_approval']}")
    
    # Step 6: Review checkpoint status
    print("\nStep 6: Reviewing checkpoint status...")
    
    result = orchestrator.review_status(goal_id)
    print(f"Pending checkpoints: {result['pending_count']}")
    
    for checkpoint in result["pending_checkpoints"]:
        print(f"Checkpoint: {checkpoint['checkpoint_name']} ({checkpoint['checkpoint_type']})")
        print(f"Created by: {checkpoint['agent_id']}")
        print(f"Status: {checkpoint['status']}")
    
    # Step 7: Approve checkpoint
    print("\nStep 7: Approving checkpoint...")
    
    result = orchestrator.approve(
        checkpoint_id=checkpoint_id,
        approved=True,
        feedback="Database schema looks good. Proceed with implementation."
    )
    
    print(f"Checkpoint approval status: {result['status']}")
    print(f"Can proceed: {result['can_proceed']}")
    
    if result['next_task']:
        print(f"Next task: {result['next_task']['title']}")
    
    # Step 8: Create a phase reflection
    print("\nStep 8: Creating a phase reflection...")
    
    start_time = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
    end_time = datetime.datetime.now().isoformat()
    
    result = orchestrator.create_reflection(
        goal_id=goal_id,
        phase_title="Requirements and Design",
        phase_number=1,
        total_phases=3,
        agent_contributions={
            "hal": ["database schema", "API design", "authentication system"],
            "ash": ["user interface mockups", "brand guidelines"]
        },
        outcomes=[
            "Complete database schema with 12 tables",
            "RESTful API design document",
            "User interface wireframes for 8 key screens",
            "Authentication system using JWT"
        ],
        start_time=start_time,
        end_time=end_time
    )
    
    print(f"Reflection created: {result['status']}")
    print(f"Memory ID: {result['memory_id']}")
    
    # Step 9: Create a goal reflection
    print("\nStep 9: Creating a goal reflection...")
    
    project_start_time = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()
    project_end_time = datetime.datetime.now().isoformat()
    
    result = orchestrator.create_goal_reflection(
        goal_id=goal_id,
        goal_title="Podcast SaaS Application",
        phase_count=3,
        agent_contributions={
            "hal": ["backend implementation", "database design", "API development", "deployment pipeline"],
            "ash": ["frontend implementation", "branding", "user experience", "marketing materials"]
        },
        outcomes=[
            "Fully functional podcast management SaaS",
            "User authentication and subscription system",
            "Analytics dashboard with listener metrics",
            "Monetization features including subscription and ad management",
            "Responsive design for mobile and desktop"
        ],
        start_time=project_start_time,
        end_time=project_end_time
    )
    
    print(f"Goal reflection created: {result['status']}")
    print(f"Memory ID: {result['memory_id']}")
    
    # Step 10: Get action log and progress report
    print("\nStep 10: Getting action log and progress report...")
    
    log_result = orchestrator.get_action_log(goal_id=goal_id)
    print(f"Action log entries: {log_result['count']}")
    
    report_result = orchestrator.get_progress_report(goal_id=goal_id)
    print(f"Progress report saved to: {report_result['report_path']}")
    
    print("\n=== Orchestrator Test Completed Successfully ===")

if __name__ == "__main__":
    test_orchestrator()
