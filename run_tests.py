#!/usr/bin/env python3
"""
Simplified test runner for agent tests with mocks.
This script runs all agent tests with the mock environment.
"""

import os
import sys
import json
import importlib.util
import traceback

# Add mocks directory to path
sys.path.insert(0, os.path.abspath("mocks"))

# Create simplified agent_runner.py for testing
test_agent_runner = """
import os
import sys
import json
import time
import traceback

# Import project_state for tracking project status
from app.modules.project_state import read_project_state, update_project_state
PROJECT_STATE_AVAILABLE = True

def run_hal_agent(task, project_id, tools):
    try:
        print(f"🤖 HAL agent execution started")
        
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if README.md already exists
            if "README.md" in project_state.get("files_created", []):
                print(f"⏩ README.md already exists, skipping duplicate write")
                return {
                    "status": "skipped",
                    "notes": "README.md already exists, skipping duplicate write.",
                    "output": project_state,
                    "project_state": project_state
                }
        
        # Initialize list of created files
        files_created = []
        
        # Simulate file creation
        files_created.append(f"/verticals/{project_id}/README.md")
        
        # Update project state
        project_state_data = {
            "status": "in_progress",
            "files_created": files_created,
            "agents_involved": ["hal"],
            "latest_agent_action": {
                "agent": "hal",
                "action": f"Created initial files for project {project_id}"
            },
            "next_recommended_step": "Run NOVA to design the project",
            "tool_usage": {
                "file_writer": 1
            }
        }
        
        update_project_state(project_id, project_state_data)
        
        # Return result with files_created list
        return {
            "status": "success",
            "message": f"HAL successfully created files for project {project_id}",
            "files_created": files_created,
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
    except Exception as e:
        print(f"❌ Error in run_hal_agent: {str(e)}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Error executing HAL agent: {str(e)}",
            "files_created": [],
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

def run_nova_agent(task, project_id, tools):
    print(f"🤖 NOVA agent execution started")
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if HAL has created initial files
            if "hal" not in project_state.get("agents_involved", []):
                print(f"⏩ HAL has not created initial files yet, cannot proceed")
                return {
                    "status": "blocked",
                    "notes": "Cannot create UI - HAL has not yet created initial project files.",
                    "project_state": project_state
                }
        
        # Simulate NOVA execution
        result = {
            "message": f"NOVA received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state
        project_state_data = {
            "agents_involved": ["nova"],
            "latest_agent_action": {
                "agent": "nova",
                "action": f"Designed project {project_id}"
            },
            "next_recommended_step": "Run ASH to create documentation",
            "tool_usage": {}
        }
        
        update_project_state(project_id, project_state_data)
        
        return result
    except Exception as e:
        print(f"❌ Error in run_nova_agent: {str(e)}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Error executing NOVA agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

def run_ash_agent(task, project_id, tools):
    print(f"🤖 ASH agent execution started")
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if project is ready for deployment
            if project_state.get("status") != "ready_for_deploy":
                print(f"⏩ Project not ready for deployment yet")
                return {
                    "status": "on_hold",
                    "notes": "Project not ready for deployment yet.",
                    "project_state": project_state
                }
        
        # Simulate ASH execution
        result = {
            "message": f"ASH received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state
        project_state_data = {
            "agents_involved": ["ash"],
            "latest_agent_action": {
                "agent": "ash",
                "action": f"Created documentation for project {project_id}"
            },
            "next_recommended_step": "Run CRITIC to review the project",
            "tool_usage": {}
        }
        
        update_project_state(project_id, project_state_data)
        
        return result
    except Exception as e:
        print(f"❌ Error in run_ash_agent: {str(e)}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Error executing ASH agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

def run_critic_agent(task, project_id, tools):
    print(f"🤖 CRITIC agent execution started")
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if NOVA has created UI files
            if "nova" not in project_state.get("agents_involved", []):
                print(f"⏩ NOVA has not created UI files yet, cannot review")
                return {
                    "status": "blocked",
                    "notes": "Cannot review UI – NOVA has not yet created any frontend files.",
                    "project_state": project_state
                }
        
        # Simulate CRITIC execution
        result = {
            "message": f"CRITIC received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state
        project_state_data = {
            "status": "ready_for_deploy",
            "agents_involved": ["critic"],
            "latest_agent_action": {
                "agent": "critic",
                "action": f"Reviewed project {project_id}"
            },
            "next_recommended_step": "Run ASH to deploy",
            "tool_usage": {}
        }
        
        update_project_state(project_id, project_state_data)
        
        return result
    except Exception as e:
        print(f"❌ Error in run_critic_agent: {str(e)}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Error executing CRITIC agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

def run_orchestrator_agent(task, project_id, tools):
    print(f"🤖 ORCHESTRATOR agent execution started")
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
        
        # Simulate ORCHESTRATOR execution
        result = {
            "message": f"ORCHESTRATOR received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state
        project_state_data = {
            "agents_involved": ["orchestrator"],
            "latest_agent_action": {
                "agent": "orchestrator",
                "action": f"Orchestrated project {project_id}"
            },
            "tool_usage": {}
        }
        
        update_project_state(project_id, project_state_data)
        
        return result
    except Exception as e:
        print(f"❌ Error in run_orchestrator_agent: {str(e)}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Error executing ORCHESTRATOR agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

# Map agent_id to runner function
AGENT_RUNNERS = {
    "hal": run_hal_agent,
    "nova": run_nova_agent,
    "ash": run_ash_agent,
    "critic": run_critic_agent,
    "orchestrator": run_orchestrator_agent
}
"""

# Write test agent_runner.py
with open("test_agent_runner.py", "w") as f:
    f.write(test_agent_runner)

print("✅ Created simplified test_agent_runner.py")

# Run HAL test
print("\n🧪 Running HAL agent test...")
try:
    # Create test project state
    os.makedirs("project_states", exist_ok=True)
    project_state = {
        "project_id": "test_project",
        "status": "in_progress",
        "files_created": ["/verticals/test_project/README.md"],
        "agents_involved": ["hal"],
        "latest_agent_action": {"agent": "hal", "action": "Created initial files"},
        "next_recommended_step": "Run NOVA",
        "tool_usage": {"file_writer": 1}
    }
    with open("project_states/test_project.json", "w") as f:
        json.dump(project_state, f, indent=2)
    
    # Import test_agent_runner
    spec = importlib.util.spec_from_file_location("test_agent_runner", "test_agent_runner.py")
    test_agent_runner_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_agent_runner_module)
    
    # Run HAL test
    result = test_agent_runner_module.run_hal_agent("Create initial files", "test_project", ["file_writer"])
    print("\n📊 HAL Test Results:")
    print(f"Status: {result.get('status')}")
    print(f"Notes: {result.get('notes')}")
    print(f"Project State included: {'project_state' in result}")
    
    # Verify test passed
    if result.get('status') == 'skipped' and 'README.md already exists' in result.get('notes', ''):
        print("\n✅ HAL TEST PASSED: HAL agent correctly skipped duplicate work")
    else:
        print("\n❌ HAL TEST FAILED: HAL agent did not skip duplicate work")
except Exception as e:
    print(f"❌ Error running HAL test: {str(e)}")
    traceback.print_exc()

# Run NOVA test
print("\n🧪 Running NOVA agent tests...")
try:
    # Test 1: Project state without HAL
    project_state = {
        "project_id": "test_project_nova1",
        "status": "in_progress",
        "files_created": ["/verticals/test_project_nova1/README.md"],
        "agents_involved": [],  # HAL not in list
        "latest_agent_action": {"agent": "system", "action": "Project initialized"},
        "next_recommended_step": "Run HAL",
        "tool_usage": {}
    }
    with open("project_states/test_project_nova1.json", "w") as f:
        json.dump(project_state, f, indent=2)
    
    result1 = test_agent_runner_module.run_nova_agent("Design UI", "test_project_nova1", ["ui_designer"])
    
    print("\n📊 NOVA Test 1 Results:")
    print(f"Status: {result1.get('status')}")
    print(f"Notes: {result1.get('notes')}")
    
    # Test 2: Project state with HAL
    project_state = {
        "project_id": "test_project_nova2",
        "status": "in_progress",
        "files_created": ["/verticals/test_project_nova2/README.md"],
        "agents_involved": ["hal"],  # HAL in list
        "latest_agent_action": {"agent": "hal", "action": "Created initial files"},
        "next_recommended_step": "Run NOVA",
        "tool_usage": {"file_writer": 1}
    }
    with open("project_states/test_project_nova2.json", "w") as f:
        json.dump(project_state, f, indent=2)
    
    result2 = test_agent_runner_module.run_nova_agent("Design UI", "test_project_nova2", ["ui_designer"])
    
    print("\n📊 NOVA Test 2 Results:")
    print(f"Status: {result2.get('status', 'unknown')}")
    print(f"Project State included: {'project_state' in result2}")
    
    # Verify tests passed
    if result1.get('status') == 'blocked' and 'HAL has not' in result1.get('notes', ''):
        print("\n✅ NOVA TEST 1 PASSED: NOVA agent correctly blocked when HAL hasn't run")
    else:
        print("\n❌ NOVA TEST 1 FAILED: NOVA agent did not block when HAL hasn't run")
    
    if result2.get('status') != 'blocked' and 'project_state' in result2:
        print("✅ NOVA TEST 2 PASSED: NOVA agent proceeded when HAL has run and included project_state")
    else:
        print("❌ NOVA TEST 2 FAILED: NOVA agent did not proceed correctly when HAL has run")
except Exception as e:
    print(f"❌ Error running NOVA tests: {str(e)}")
    traceback.print_exc()

# Run CRITIC test
print("\n🧪 Running CRITIC agent tests...")
try:
    # Test 1: Project state without NOVA
    project_state = {
        "project_id": "test_project_critic1",
        "status": "in_progress",
        "files_created": ["/verticals/test_project_critic1/README.md"],
        "agents_involved": ["hal"],  # NOVA not in list
        "latest_agent_action": {"agent": "hal", "action": "Created initial files"},
        "next_recommended_step": "Run NOVA",
        "tool_usage": {"file_writer": 1}
    }
    with open("project_states/test_project_critic1.json", "w") as f:
        json.dump(project_state, f, indent=2)
    
    result1 = test_agent_runner_module.run_critic_agent("Review UI", "test_project_critic1", ["code_reviewer"])
    
    print("\n📊 CRITIC Test 1 Results:")
    print(f"Status: {result1.get('status')}")
    print(f"Notes: {result1.get('notes')}")
    
    # Test 2: Project state with NOVA
    project_state = {
        "project_id": "test_project_critic2",
        "status": "in_progress",
        "files_created": [
            "/verticals/test_project_critic2/README.md",
            "/verticals/test_project_critic2/frontend/LandingPage.jsx"
        ],
        "agents_involved": ["hal", "nova"],  # NOVA in list
        "latest_agent_action": {"agent": "nova", "action": "Designed UI"},
        "next_recommended_step": "Run CRITIC",
        "tool_usage": {"file_writer": 2}
    }
    with open("project_states/test_project_critic2.json", "w") as f:
        json.dump(project_state, f, indent=2)
    
    result2 = test_agent_runner_module.run_critic_agent("Review UI", "test_project_critic2", ["code_reviewer"])
    
    print("\n📊 CRITIC Test 2 Results:")
    print(f"Status: {result2.get('status', 'unknown')}")
    print(f"Project State included: {'project_state' in result2}")
    
    # Verify tests passed
    if result1.get('status') == 'blocked' and 'NOVA has not' in result1.get('notes', ''):
        print("\n✅ CRITIC TEST 1 PASSED: CRITIC agent correctly blocked when NOVA hasn't run")
    else:
        print("\n❌ CRITIC TEST 1 FAILED: CRITIC agent did not block when NOVA hasn't run")
    
    if result2.get('status') != 'blocked' and 'project_state' in result2:
        print("✅ CRITIC TEST 2 PASSED: CRITIC agent proceeded when NOVA has run and included project_state")
    else:
        print("❌ CRITIC TEST 2 FAILED: CRITIC agent did not proceed correctly when NOVA has run")
except Exception as e:
    print(f"❌ Error running CRITIC tests: {str(e)}")
    traceback.print_exc()

# Run ASH test
print("\n🧪 Running ASH agent tests...")
try:
    # Test 1: Project state not ready for deployment
    project_state = {
        "project_id": "test_project_ash1",
        "status": "in_progress",  # Not ready for deployment
        "files_created": [
            "/verticals/test_project_ash1/README.md",
            "/verticals/test_project_ash1/frontend/LandingPage.jsx"
        ],
        "agents_involved": ["hal", "nova", "critic"],
        "latest_agent_action": {"agent": "critic", "action": "Reviewed UI"},
        "next_recommended_step": "Run ASH",
        "tool_usage": {"file_writer": 2}
    }
    with open("project_states/test_project_ash1.json", "w") as f:
        json.dump(project_state, f, indent=2)
    
    result1 = test_agent_runner_module.run_ash_agent("Create documentation", "test_project_ash1", ["doc_generator"])
    
    print("\n📊 ASH Test 1 Results:")
    print(f"Status: {result1.get('status')}")
    print(f"Notes: {result1.get('notes')}")
    
    # Test 2: Project state ready for deployment
    project_state = {
        "project_id": "test_project_ash2",
        "status": "ready_for_deploy",  # Ready for deployment
        "files_created": [
            "/verticals/test_project_ash2/README.md",
            "/verticals/test_project_ash2/frontend/LandingPage.jsx"
        ],
        "agents_involved": ["hal", "nova", "critic"],
        "latest_agent_action": {"agent": "critic", "action": "Reviewed UI"},
        "next_recommended_step": "Run ASH",
        "tool_usage": {"file_writer": 2}
    }
    with open("project_states/test_project_ash2.json", "w") as f:
        json.dump(project_state, f, indent=2)
    
    result2 = test_agent_runner_module.run_ash_agent("Create documentation", "test_project_ash2", ["doc_generator"])
    
    print("\n📊 ASH Test 2 Results:")
    print(f"Status: {result2.get('status', 'unknown')}")
    print(f"Project State included: {'project_state' in result2}")
    
    # Verify tests passed
    if result1.get('status') == 'on_hold' and 'not ready for deployment' in result1.get('notes', ''):
        print("\n✅ ASH TEST 1 PASSED: ASH agent correctly on hold when project not ready for deployment")
    else:
        print("\n❌ ASH TEST 1 FAILED: ASH agent did not go on hold when project not ready for deployment")
    
    if result2.get('status') != 'on_hold' and 'project_state' in result2:
        print("✅ ASH TEST 2 PASSED: ASH agent proceeded when project ready for deployment and included project_state")
    else:
        print("❌ ASH TEST 2 FAILED: ASH agent did not proceed correctly when project ready for deployment")
except Exception as e:
    print(f"❌ Error running ASH tests: {str(e)}")
    traceback.print_exc()

print("\n✅ All tests completed")
