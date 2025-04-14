import requests
import json
import uuid
from typing import Dict, Any, List, Optional

# Test configuration
BASE_URL = "http://localhost:3000"  # Update with actual server URL when testing
TEST_AGENT_ID = "hal"  # Using HAL as the test agent

def test_agent_context_endpoint():
    """
    Comprehensive test for the /agent/context endpoint
    
    This test verifies:
    1. Request with known agent ID
    2. Response structure matches expected format
    3. Active projects are grouped correctly
    4. Agent state and last_active fields match agent registry
    """
    print("\n=== Testing /agent/context endpoint ===")
    
    # Test 1: Basic request with known agent ID
    print("\n--- Test 1: Basic request with known agent ID ---")
    try:
        # Create test request
        context_request = {
            "agent_id": TEST_AGENT_ID
        }
        
        response = requests.post(
            f"{BASE_URL}/api/modules/agent/context",
            json=context_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Verify response structure
            assert "status" in result, "Response should include 'status' field"
            assert result["status"] == "ok", "Status should be 'ok'"
            assert "agent_id" in result, "Response should include 'agent_id' field"
            assert result["agent_id"] == TEST_AGENT_ID, "agent_id should match request"
            assert "active_projects" in result, "Response should include 'active_projects' field"
            assert "agent_state" in result, "Response should include 'agent_state' field"
            assert "last_active" in result, "Response should include 'last_active' field"
            
            print("✅ Basic request test passed: Response structure is correct")
        else:
            print(f"❌ Basic request test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Basic request test error: {str(e)}")
    
    # Test 2: Populate memory with test data and verify context
    print("\n--- Test 2: Populate memory with test data and verify context ---")
    try:
        # Generate unique project ID for testing
        project_id = f"test-project-{uuid.uuid4()}"
        
        # Create test memory entries
        memory_entries = [
            # Loop snapshot memory
            {
                "agent_id": TEST_AGENT_ID,
                "memory_type": "loop_snapshot",
                "content": "Agent completed loop iteration 1",
                "tags": ["loop", "reflection"],
                "project_id": project_id,
                "status": "completed",
                "task_type": "loop"
            },
            # Task memory 1 (in progress)
            {
                "agent_id": TEST_AGENT_ID,
                "memory_type": "task_log",
                "content": "Summarize journal entries",
                "tags": ["task", "summary"],
                "project_id": project_id,
                "status": "in_progress",
                "task_type": "task"
            },
            # Task memory 2 (completed)
            {
                "agent_id": TEST_AGENT_ID,
                "memory_type": "task_log",
                "content": "Generate creative insights",
                "tags": ["task", "creative"],
                "project_id": project_id,
                "status": "completed",
                "task_type": "task"
            },
            # Delegation memory
            {
                "agent_id": TEST_AGENT_ID,
                "memory_type": "delegation_log",
                "content": "Delegated research task to ASH",
                "tags": ["delegation"],
                "project_id": project_id,
                "status": "delegated",
                "task_type": "delegated_task"
            }
        ]
        
        # Write test memories
        for memory in memory_entries:
            response = requests.post(
                f"{BASE_URL}/api/modules/memory/write",
                json=memory
            )
            if response.status_code == 200:
                print(f"✅ Created test memory: {memory['memory_type']} for project {project_id}")
            else:
                print(f"❌ Failed to create test memory: {response.status_code} - {response.text}")
        
        # Request context after creating memories
        context_request = {
            "agent_id": TEST_AGENT_ID
        }
        
        response = requests.post(
            f"{BASE_URL}/api/modules/agent/context",
            json=context_request
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Find our test project in the response
            test_project = None
            for project in result.get("active_projects", []):
                if project.get("project_id") == project_id:
                    test_project = project
                    break
            
            if test_project:
                print(f"Test project found in response: {json.dumps(test_project, indent=2)}")
                
                # Verify project structure
                assert "last_action" in test_project, "Project should include 'last_action' field"
                assert "loop_count" in test_project, "Project should include 'loop_count' field"
                assert test_project["loop_count"] >= 1, "Loop count should be at least 1"
                assert "last_active" in test_project, "Project should include 'last_active' field"
                assert "tasks" in test_project, "Project should include 'tasks' field"
                
                # Verify tasks
                tasks = test_project.get("tasks", [])
                assert len(tasks) >= 2, f"Project should have at least 2 tasks, found {len(tasks)}"
                
                # Check for in-progress and completed tasks
                has_in_progress = any(task.get("status") == "in_progress" for task in tasks)
                has_completed = any(task.get("status") == "completed" for task in tasks)
                
                assert has_in_progress, "Project should have at least one in-progress task"
                assert has_completed, "Project should have at least one completed task"
                
                print("✅ Memory population test passed: Project context is correct")
            else:
                print(f"❌ Memory population test failed: Test project not found in response")
        else:
            print(f"❌ Memory population test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Memory population test error: {str(e)}")
    
    # Test 3: Test with non-existent agent ID
    print("\n--- Test 3: Test with non-existent agent ID ---")
    try:
        # Create test request with non-existent agent ID
        context_request = {
            "agent_id": "non_existent_agent"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/modules/agent/context",
            json=context_request
        )
        
        # Should return 404 for non-existent agent
        if response.status_code == 404:
            print("✅ Non-existent agent test passed: Returned 404 as expected")
        else:
            print(f"❌ Non-existent agent test failed: Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"❌ Non-existent agent test error: {str(e)}")
    
    # Test 4: Test orchestrator preparation components
    print("\n--- Test 4: Test orchestrator preparation components ---")
    try:
        # Import orchestrator preparation functions
        import sys
        sys.path.append('/home/ubuntu/personal-ai-agent')
        from app.api.modules.orchestrator_prep import (
            prepare_orchestrator_view,
            identify_available_agents,
            identify_stalled_tasks
        )
        
        # Get context for multiple agents
        agent_contexts = []
        for agent_id in ["hal", "ash"]:
            response = requests.post(
                f"{BASE_URL}/api/modules/agent/context",
                json={"agent_id": agent_id}
            )
            if response.status_code == 200:
                agent_contexts.append(response.json())
        
        if len(agent_contexts) >= 2:
            # Prepare orchestrator view
            orchestrator_view = prepare_orchestrator_view(agent_contexts)
            print(f"Orchestrator view: {json.dumps(orchestrator_view, indent=2)}")
            
            # Verify orchestrator view structure
            assert "projects" in orchestrator_view, "Orchestrator view should include 'projects' field"
            assert "agents" in orchestrator_view, "Orchestrator view should include 'agents' field"
            assert "last_updated" in orchestrator_view, "Orchestrator view should include 'last_updated' field"
            
            # Test available agents function
            available_agents = identify_available_agents(orchestrator_view)
            print(f"Available agents: {available_agents}")
            
            # Test stalled tasks function
            stalled_tasks = identify_stalled_tasks(orchestrator_view, stall_threshold_hours=1)
            print(f"Stalled tasks: {stalled_tasks}")
            
            print("✅ Orchestrator preparation test passed")
        else:
            print(f"❌ Orchestrator preparation test failed: Not enough agent contexts available")
    except Exception as e:
        print(f"❌ Orchestrator preparation test error: {str(e)}")
    
    print("\n=== Test suite completed ===")

if __name__ == "__main__":
    test_agent_context_endpoint()
