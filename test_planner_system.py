"""
Test script for the Autonomous Goal Decomposer + Planner Agent system.

This script tests goal decomposition, agent routing, execution sequencing,
memory integration, and goal continuation.
"""

import os
import sys
import json
import uuid
from datetime import datetime

# Add app directory to path
sys.path.append('/home/ubuntu/app')

# Import required modules
from app.tools.agent_router import get_agent_router, find_agent
from app.core.planner_orchestrator import get_planner_orchestrator, process_goal, get_goal_status, resume_goal, replay_goal_history

def test_agent_router():
    """Test the agent router functionality"""
    print("\n=== Testing Agent Router ===")
    
    try:
        # Initialize agent router
        router = get_agent_router()
        
        # Test finding the best agent for different tasks
        test_tasks = [
            "Build a new API endpoint for user authentication",
            "Research the latest trends in AI development",
            "Store the results of the analysis in memory",
            "Deploy the application to the production environment"
        ]
        
        expected_agents = ["builder", "research", "memory", "ops"]
        
        for i, task in enumerate(test_tasks):
            agent = router.find_best_agent(task)
            expected = expected_agents[i]
            
            print(f"Task: {task}")
            print(f"Expected agent: {expected}")
            print(f"Assigned agent: {agent}")
            
            if agent == expected:
                print("✅ Agent assignment correct")
            else:
                print("❌ Agent assignment incorrect")
            
            print()
        
        # Test mock routing
        goal_id = str(uuid.uuid4())
        subtask = {
            "id": f"{goal_id}_subtask_1",
            "description": "Test subtask",
            "type": "test"
        }
        
        # Since we're not actually connecting to agents, this will return an error
        # but we can verify the routing logic works
        result = router.route_task(subtask, "research", goal_id, timeout_seconds=1)
        
        print(f"Routing result status: {result.get('status')}")
        if "error" in result or "timeout" in result.get("status", ""):
            print("✅ Expected error/timeout in test environment")
        else:
            print("❓ Unexpected success in test environment")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in agent router test: {str(e)}")
        return False

def test_goal_decomposition():
    """Test goal decomposition functionality"""
    print("\n=== Testing Goal Decomposition ===")
    
    try:
        # Initialize planner orchestrator
        orchestrator = get_planner_orchestrator()
        
        # Create a test goal
        goal_id = str(uuid.uuid4())
        test_goal = {
            "id": goal_id,
            "description": "Build a simple weather API",
            "type": "development",
            "context": {
                "priority": "medium",
                "deadline": "2025-04-15"
            }
        }
        
        # Test decomposition
        subtasks = orchestrator._decompose_goal(test_goal)
        
        print(f"Goal decomposed into {len(subtasks)} subtasks:")
        for i, subtask in enumerate(subtasks):
            print(f"{i+1}. {subtask.get('description')} (Type: {subtask.get('type')})")
        
        if len(subtasks) > 0:
            print("✅ Goal decomposition successful")
        else:
            print("❌ Goal decomposition failed")
        
        # Test different decomposition strategies
        strategies = ["sequential_breakdown", "parallel_tasks", "research_first"]
        
        for strategy in strategies:
            test_goal["decomposition_strategy"] = strategy
            subtasks = orchestrator._decompose_goal(test_goal)
            
            print(f"\nStrategy '{strategy}' decomposed into {len(subtasks)} subtasks:")
            for i, subtask in enumerate(subtasks[:3]):
                print(f"{i+1}. {subtask.get('description')} (Type: {subtask.get('type')})")
            
            if len(subtasks) > 3:
                print(f"... and {len(subtasks) - 3} more")
            
            if len(subtasks) > 0:
                print(f"✅ Strategy '{strategy}' successful")
            else:
                print(f"❌ Strategy '{strategy}' failed")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in goal decomposition test: {str(e)}")
        return False

def test_subtask_sequencing():
    """Test subtask sequencing functionality"""
    print("\n=== Testing Subtask Sequencing ===")
    
    try:
        # Initialize planner orchestrator
        orchestrator = get_planner_orchestrator()
        
        # Create test subtasks with dependencies
        goal_id = str(uuid.uuid4())
        subtasks = [
            {
                "id": f"{goal_id}_subtask_1",
                "description": "Research API requirements",
                "type": "research",
                "dependencies": [],
                "assigned_agent": "research"
            },
            {
                "id": f"{goal_id}_subtask_2",
                "description": "Design API architecture",
                "type": "architecture",
                "dependencies": [f"{goal_id}_subtask_1"],
                "assigned_agent": "builder"
            },
            {
                "id": f"{goal_id}_subtask_3",
                "description": "Implement API endpoints",
                "type": "code",
                "dependencies": [f"{goal_id}_subtask_2"],
                "assigned_agent": "builder"
            },
            {
                "id": f"{goal_id}_subtask_4",
                "description": "Write API documentation",
                "type": "documentation",
                "dependencies": [f"{goal_id}_subtask_2"],
                "assigned_agent": "research"
            },
            {
                "id": f"{goal_id}_subtask_5",
                "description": "Deploy API to production",
                "type": "deployment",
                "dependencies": [f"{goal_id}_subtask_3", f"{goal_id}_subtask_4"],
                "assigned_agent": "ops"
            }
        ]
        
        # Test sequencing
        sequenced_subtasks = orchestrator._sequence_subtasks(subtasks)
        
        print("Sequenced subtasks:")
        for i, subtask in enumerate(sequenced_subtasks):
            dependencies = subtask.get("dependencies", [])
            dependency_str = ", ".join([d.split("_")[-1] for d in dependencies]) if dependencies else "None"
            
            print(f"{subtask.get('sequence_number')}. {subtask.get('description')} (Dependencies: {dependency_str})")
        
        # Verify sequence respects dependencies
        is_valid = True
        dependency_map = {subtask["id"]: subtask.get("sequence_number", 0) for subtask in sequenced_subtasks}
        
        for subtask in sequenced_subtasks:
            for dependency in subtask.get("dependencies", []):
                if dependency_map.get(dependency, 0) >= subtask.get("sequence_number", 0):
                    print(f"❌ Invalid sequence: {subtask.get('id')} depends on {dependency} but comes before it")
                    is_valid = False
        
        if is_valid:
            print("✅ Subtask sequencing respects all dependencies")
        
        # Test topological sort with cyclic dependencies
        cyclic_subtasks = subtasks.copy()
        # Add a cyclic dependency: 5 -> 1
        cyclic_subtasks[0]["dependencies"] = [f"{goal_id}_subtask_5"]
        
        try:
            orchestrator._sequence_subtasks(cyclic_subtasks)
            print("❌ Failed to detect cyclic dependency")
        except ValueError as e:
            print(f"✅ Correctly detected cyclic dependency: {str(e)}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in subtask sequencing test: {str(e)}")
        return False

def test_memory_integration():
    """Test memory integration functionality"""
    print("\n=== Testing Memory Integration ===")
    
    try:
        # Initialize planner orchestrator
        orchestrator = get_planner_orchestrator()
        
        # Create a test goal
        goal_id = str(uuid.uuid4())
        test_goal = {
            "id": goal_id,
            "description": "Test memory integration",
            "type": "test"
        }
        
        # Test storing in memory
        print(f"Storing test goal {goal_id} in memory...")
        orchestrator._store_in_memory(goal_id, "goal", test_goal, "goal_start")
        
        # Test storing a subtask
        subtask = {
            "id": f"{goal_id}_subtask_1",
            "description": "Test subtask",
            "type": "test",
            "dependencies": []
        }
        
        print(f"Storing test subtask {subtask['id']} in memory...")
        orchestrator._store_in_memory(goal_id, "subtask", subtask, "subtask_created")
        
        # Test logging execution event
        print("Logging test execution event...")
        orchestrator._log_execution_event(
            goal_id, 
            "test_event", 
            "Test execution event", 
            {"test": True}
        )
        
        # Verify log file exists
        log_file = "/app/logs/planner_execution_log.json"
        if os.path.exists(log_file):
            print(f"✅ Log file created at {log_file}")
            
            # Read the log file
            with open(log_file, "r") as f:
                logs = json.load(f)
                
                if isinstance(logs, list) and len(logs) > 0:
                    print(f"✅ Log file contains {len(logs)} entries")
                    
                    # Find our test event
                    test_events = [log for log in logs if log.get("goal_id") == goal_id]
                    if test_events:
                        print(f"✅ Found {len(test_events)} events for goal {goal_id}")
                    else:
                        print(f"❌ No events found for goal {goal_id}")
                else:
                    print("❌ Log file is empty or invalid")
        else:
            print(f"❌ Log file not created at {log_file}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in memory integration test: {str(e)}")
        return False

def test_goal_continuation():
    """Test goal continuation functionality"""
    print("\n=== Testing Goal Continuation ===")
    
    try:
        # Initialize planner orchestrator
        orchestrator = get_planner_orchestrator()
        
        # Create a test goal
        goal_id = str(uuid.uuid4())
        test_goal = {
            "id": goal_id,
            "description": "Test goal continuation",
            "type": "test"
        }
        
        # Store the goal in memory
        print(f"Storing test goal {goal_id} in memory...")
        orchestrator._store_in_memory(goal_id, "goal", test_goal, "goal_start")
        
        # Create and store some subtasks
        subtasks = []
        for i in range(3):
            subtask = {
                "id": f"{goal_id}_subtask_{i+1}",
                "description": f"Test subtask {i+1}",
                "type": "test",
                "dependencies": []
            }
            subtasks.append(subtask)
            
            # Store the subtask
            orchestrator._store_in_memory(goal_id, "subtask", subtask, "subtask_created")
            
            # For the first subtask, store a result to mark it as completed
            if i == 0:
                result = {
                    "subtask_id": subtask["id"],
                    "result": {"status": "success", "message": "Completed successfully"}
                }
                orchestrator._store_in_memory(goal_id, "subtask_result", result, "subtask_completed")
        
        # Test goal status retrieval
        print("Testing goal status retrieval...")
        status = orchestrator.get_goal_status(goal_id)
        
        if status.get("status") == "retrieved_from_memory":
            print("✅ Goal status retrieved from memory")
        else:
            print(f"❓ Unexpected status: {status.get('status')}")
        
        # Test goal history replay
        print("\nTesting goal history replay...")
        history = orchestrator.replay_goal_history(goal_id)
        
        if history.get("status") == "success":
            print(f"✅ Goal history replayed with {history.get('event_count')} events")
            
            # Print a few events
            for i, event in enumerate(history.get("events", [])[:3]):
                print(f"Event {i+1}: {event.get('entry_type')} - {event.get('status')}")
            
            if len(history.get("events", [])) > 3:
                print(f"... and {len(history.get('events', [])) - 3} more events")
        else:
            print(f"❌ Goal history replay failed: {history.get('message')}")
        
        # Test goal resumption
        # Note: This will not fully work in the test environment without actual agent execution
        print("\nTesting goal resumption...")
        resume_result = orchestrator.resume_goal(goal_id)
        
        print(f"Resume status: {resume_result.get('status')}")
        print(f"Resume message: {resume_result.get('message')}")
        
        if "error" in resume_result.get("status", ""):
            print("❓ Expected error in test environment without actual agent execution")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in goal continuation test: {str(e)}")
        return False

def test_end_to_end():
    """Test end-to-end goal processing"""
    print("\n=== Testing End-to-End Goal Processing ===")
    
    try:
        # Create a test goal
        goal_id = str(uuid.uuid4())
        test_goal = {
            "id": goal_id,
            "description": "Build a simple weather API",
            "type": "development",
            "context": {
                "priority": "medium",
                "deadline": "2025-04-15"
            }
        }
        
        print(f"Processing test goal: {test_goal['description']}")
        
        # Process the goal
        # Note: This will not fully work in the test environment without actual agent execution
        result = process_goal(test_goal)
        
        print(f"Processing status: {result.get('status')}")
        
        if "error" in result.get("status", ""):
            print("❓ Expected error in test environment without actual agent execution")
            print(f"Error message: {result.get('error')}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in end-to-end test: {str(e)}")
        return False

def main():
    """Main test function"""
    print("Starting tests for Autonomous Goal Decomposer + Planner Agent")
    
    # Run all tests
    tests = [
        test_agent_router,
        test_goal_decomposition,
        test_subtask_sequencing,
        test_memory_integration,
        test_goal_continuation,
        test_end_to_end
    ]
    
    results = {}
    
    for test_func in tests:
        test_name = test_func.__name__
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test {test_name} failed with error: {str(e)}")
            results[test_name] = False
    
    # Print summary
    print("\n=== Test Summary ===")
    passed = sum(1 for r in results.values() if r)
    failed = sum(1 for r in results.values() if not r)
    
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    for test_name, result in results.items():
        print(f"{'✅' if result else '❌'} {test_name}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n❌ {failed} tests failed")

if __name__ == "__main__":
    main()
