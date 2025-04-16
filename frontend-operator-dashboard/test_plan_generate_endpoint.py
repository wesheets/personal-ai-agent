import requests
import json
import uuid
from typing import Dict, Any, List, Optional

# Test configuration
BASE_URL = "http://localhost:3000"  # Update with actual server URL when testing
TEST_AGENT_ID = "hal"  # Using HAL as the test agent

def test_plan_generate_endpoint():
    """
    Comprehensive test for the /plan/generate endpoint
    
    This test verifies:
    1. Request with creative coach persona
    2. Response structure matches expected format
    3. Memory is written with correct metadata
    4. Plan appears in /observer/report and /thread
    """
    print("\n=== Testing /plan/generate endpoint ===")
    
    # Generate unique IDs for testing
    project_id = "musemind"
    memory_trace_id = f"trace-{uuid.uuid4()}"
    task_id = f"plan-test-{uuid.uuid4()}"
    
    # Test 1: Basic request with creative coach persona
    print("\n--- Test 1: Basic request with creative coach persona ---")
    try:
        # Create test request
        plan_request = {
            "agent_id": TEST_AGENT_ID,
            "project_id": project_id,
            "memory_trace_id": memory_trace_id,
            "persona": "creative coach",
            "objective": "Develop a weekly creative journaling plan",
            "input_data": {
                "theme": "creative self-reflection",
                "duration": "3 days"  # Requesting only 3 tasks for brevity
            },
            "task_id": task_id
        }
        
        print(f"Request: {json.dumps(plan_request, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/modules/plan/generate",
            json=plan_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Verify response structure
            assert "status" in result, "Response should include 'status' field"
            assert result["status"] == "success", "Status should be 'success'"
            assert "tasks" in result, "Response should include 'tasks' field"
            assert len(result["tasks"]) == 3, f"Should have 3 tasks, found {len(result['tasks'])}"
            assert "task_id" in result, "Response should include 'task_id' field"
            assert result["task_id"] == task_id, "task_id should match request"
            assert "project_id" in result, "Response should include 'project_id' field"
            assert result["project_id"] == project_id, "project_id should match request"
            assert "memory_trace_id" in result, "Response should include 'memory_trace_id' field"
            assert result["memory_trace_id"] == memory_trace_id, "memory_trace_id should match request"
            
            # Verify task structure
            for task in result["tasks"]:
                assert "day" in task, "Task should include 'day' field"
                assert "title" in task, "Task should include 'title' field"
                assert "type" in task, "Task should include 'type' field"
            
            print("✅ Basic request test passed: Response structure is correct")
        else:
            print(f"❌ Basic request test failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Basic request test error: {str(e)}")
        return
    
    # Test 2: Check memory thread for the plan
    print("\n--- Test 2: Check memory thread for the plan ---")
    try:
        thread_request = {
            "agent_id": TEST_AGENT_ID,
            "project_id": project_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/memory/thread",
            json=thread_request
        )
        
        if response.status_code == 200:
            result = response.json()
            memory_thread = result.get("memory_thread", [])
            
            # Find our plan in the memory thread
            plan_memories = [m for m in memory_thread if 
                           "content" in m and 
                           "Plan generated for objective" in m["content"] and
                           "Develop a weekly creative journaling plan" in m["content"]]
            
            if plan_memories:
                memory = plan_memories[0]
                print(f"Found plan in memory thread: {json.dumps(memory, indent=2)}")
                print("✅ Memory thread test passed: Plan appears in memory thread")
            else:
                print("❌ Memory thread test failed: Plan not found in memory thread")
        else:
            print(f"❌ Memory thread test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Memory thread test error: {str(e)}")
    
    # Test 3: Check observer report for the plan
    print("\n--- Test 3: Check observer report for the plan ---")
    try:
        observer_request = {
            "project_id": project_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/observer/report",
            json=observer_request
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if our plan is in the report
            plans_found = False
            for section in result.values():
                if isinstance(section, list):
                    for item in section:
                        if isinstance(item, dict) and "task_id" in item and item["task_id"] == task_id:
                            plans_found = True
                            print(f"Found plan in observer report: {json.dumps(item, indent=2)}")
                            break
            
            if plans_found:
                print("✅ Observer report test passed: Plan appears in observer report")
            else:
                print("❌ Observer report test failed: Plan not found in observer report")
        else:
            print(f"❌ Observer report test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Observer report test error: {str(e)}")
    
    # Test 4: Test with different persona
    print("\n--- Test 4: Test with productivity mentor persona ---")
    try:
        # Create test request with different persona
        plan_request = {
            "agent_id": TEST_AGENT_ID,
            "project_id": project_id,
            "memory_trace_id": memory_trace_id,
            "persona": "productivity mentor",
            "objective": "Optimize weekly workflow",
            "input_data": {
                "theme": "time management",
                "duration": "3 days"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/modules/plan/generate",
            json=plan_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Verify tasks are appropriate for productivity mentor
            productivity_keywords = ["workflow", "task", "time", "productivity", "organize", "plan", "efficiency"]
            tasks_match_persona = any(
                any(keyword in task["title"].lower() for keyword in productivity_keywords)
                for task in result["tasks"]
            )
            
            if tasks_match_persona:
                print("✅ Different persona test passed: Tasks match productivity mentor persona")
            else:
                print("❌ Different persona test failed: Tasks don't match productivity mentor persona")
        else:
            print(f"❌ Different persona test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Different persona test error: {str(e)}")
    
    print("\n=== Test suite completed ===")

if __name__ == "__main__":
    test_plan_generate_endpoint()
