"""
Test script for Phase 6.1 Agent Timing & Synchronization features

This script tests the implementation of:
1. Agent retry and recovery flow
2. Project state watch hooks
3. Post-block memory updates
4. Passive reflection engine
5. Intelligent reset flags
"""
import os
import sys
import json
import time
import requests
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
try:
    from app.modules.agent_retry import register_blocked_agent, check_for_unblocked_agents, get_retry_status
    AGENT_RETRY_AVAILABLE = True
except ImportError:
    AGENT_RETRY_AVAILABLE = False
    print("❌ agent_retry import failed")

try:
    from app.modules.project_state import read_project_state, update_project_state
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    print("❌ project_state import failed")

try:
    from app.modules.project_state_watch import subscribe_to_state_changes, get_state_changes
    PROJECT_STATE_WATCH_AVAILABLE = True
except ImportError:
    PROJECT_STATE_WATCH_AVAILABLE = False
    print("❌ project_state_watch import failed")

try:
    from app.modules.memory_block_writer import write_block_memory, write_unblock_memory
    MEMORY_BLOCK_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_BLOCK_WRITER_AVAILABLE = False
    print("❌ memory_block_writer import failed")

try:
    from app.modules.passive_reflection import start_reflection, re_evaluate_task
    PASSIVE_REFLECTION_AVAILABLE = True
except ImportError:
    PASSIVE_REFLECTION_AVAILABLE = False
    print("❌ passive_reflection import failed")

try:
    from app.modules.reset_flags import reset_agent_state, reset_project_state, get_reset_status
    RESET_FLAGS_AVAILABLE = True
except ImportError:
    RESET_FLAGS_AVAILABLE = False
    print("❌ reset_flags import failed")

# Test project ID
TEST_PROJECT_ID = "test_phase_6_1_project"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def print_result(test_name, result):
    """Print a test result"""
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} - {test_name}")

def test_agent_retry_flow():
    """Test agent retry and recovery flow"""
    print_header("Testing Agent Retry Flow")
    
    if not AGENT_RETRY_AVAILABLE or not PROJECT_STATE_AVAILABLE:
        print("❌ Required modules not available, skipping test")
        return False
    
    try:
        # Initialize project state
        update_project_state(TEST_PROJECT_ID, {
            "agents_involved": ["hal"],
            "status": "in_progress"
        })
        print("📊 Initialized project state")
        
        # Register a blocked agent
        register_blocked_agent(
            project_id=TEST_PROJECT_ID,
            agent_id="nova",
            blocked_due_to="hal",
            unblock_condition="initial_files_created"
        )
        print("🔒 Registered blocked NOVA agent")
        
        # Verify agent is blocked
        retry_status = get_retry_status(TEST_PROJECT_ID, "nova")
        print(f"📋 Retry status: {retry_status}")
        
        is_blocked = retry_status and retry_status.get("status") == "blocked"
        print_result("Agent is blocked", is_blocked)
        
        # Update project state to unblock agent
        update_project_state(TEST_PROJECT_ID, {
            "agents_involved": ["hal", "nova"],
            "files_created": ["README.md", "requirements.txt"],
            "initial_files_created": True
        })
        print("📊 Updated project state to unblock agent")
        
        # Check for unblocked agents
        unblocked_agents = check_for_unblocked_agents(TEST_PROJECT_ID)
        print(f"🔓 Unblocked agents: {unblocked_agents}")
        
        has_unblocked = len(unblocked_agents) > 0 and unblocked_agents[0].get("agent_id") == "nova"
        print_result("Agent was unblocked", has_unblocked)
        
        # Verify agent status is now unblocked
        retry_status = get_retry_status(TEST_PROJECT_ID, "nova")
        print(f"📋 Updated retry status: {retry_status}")
        
        is_unblocked = retry_status and retry_status.get("status") == "unblocked"
        print_result("Agent status is unblocked", is_unblocked)
        
        return is_blocked and has_unblocked and is_unblocked
        
    except Exception as e:
        print(f"❌ Error in test_agent_retry_flow: {str(e)}")
        return False

def test_project_state_watch():
    """Test project state watch hooks"""
    print_header("Testing Project State Watch")
    
    if not PROJECT_STATE_WATCH_AVAILABLE or not PROJECT_STATE_AVAILABLE:
        print("❌ Required modules not available, skipping test")
        return False
    
    try:
        # Initialize project state
        update_project_state(TEST_PROJECT_ID, {
            "agents_involved": ["hal"],
            "status": "in_progress",
            "test_value": 1
        })
        print("📊 Initialized project state")
        
        # Subscribe to state changes
        subscription_id = subscribe_to_state_changes(TEST_PROJECT_ID)
        print(f"👂 Subscribed to state changes with ID: {subscription_id}")
        
        # Update project state
        update_project_state(TEST_PROJECT_ID, {
            "test_value": 2,
            "new_field": "test"
        })
        print("📊 Updated project state")
        
        # Get state changes
        changes = get_state_changes(subscription_id)
        print(f"📋 State changes: {changes}")
        
        has_changes = len(changes) > 0
        print_result("Detected state changes", has_changes)
        
        correct_changes = any(
            change.get("field") == "test_value" and change.get("new_value") == 2
            for change in changes
        )
        print_result("Correct state changes detected", correct_changes)
        
        return has_changes and correct_changes
        
    except Exception as e:
        print(f"❌ Error in test_project_state_watch: {str(e)}")
        return False

def test_memory_block_writer():
    """Test post-block memory updates"""
    print_header("Testing Memory Block Writer")
    
    if not MEMORY_BLOCK_WRITER_AVAILABLE or not PROJECT_STATE_AVAILABLE:
        print("❌ Required modules not available, skipping test")
        return False
    
    try:
        # Initialize project state
        update_project_state(TEST_PROJECT_ID, {
            "agents_involved": ["hal"],
            "status": "in_progress"
        })
        print("📊 Initialized project state")
        
        # Write block memory
        block_result = write_block_memory({
            "project_id": TEST_PROJECT_ID,
            "agent": "nova",
            "action": "blocked",
            "content": "NOVA agent blocked - HAL has not created initial files yet",
            "blocked_due_to": "hal",
            "unblock_condition": "initial_files_created"
        })
        print(f"📝 Block memory result: {block_result}")
        
        block_success = block_result.get("status") == "success"
        print_result("Block memory written", block_success)
        
        # Write unblock memory
        unblock_result = write_unblock_memory({
            "project_id": TEST_PROJECT_ID,
            "agent": "nova",
            "action": "unblocked",
            "content": "NOVA agent unblocked - HAL has created initial files",
            "previously_blocked_due_to": "hal",
            "unblock_reason": "initial_files_created condition met"
        })
        print(f"📝 Unblock memory result: {unblock_result}")
        
        unblock_success = unblock_result.get("status") == "success"
        print_result("Unblock memory written", unblock_success)
        
        # Check project state for memory updates
        project_state = read_project_state(TEST_PROJECT_ID)
        
        has_block_memory = "block_memory" in project_state
        print_result("Project state has block memory", has_block_memory)
        
        return block_success and unblock_success and has_block_memory
        
    except Exception as e:
        print(f"❌ Error in test_memory_block_writer: {str(e)}")
        return False

def test_passive_reflection():
    """Test passive reflection engine"""
    print_header("Testing Passive Reflection Engine")
    
    if not PASSIVE_REFLECTION_AVAILABLE or not PROJECT_STATE_AVAILABLE or not AGENT_RETRY_AVAILABLE:
        print("❌ Required modules not available, skipping test")
        return False
    
    try:
        # Initialize project state
        update_project_state(TEST_PROJECT_ID, {
            "agents_involved": ["hal"],
            "status": "in_progress"
        })
        print("📊 Initialized project state")
        
        # Register a blocked agent
        register_blocked_agent(
            project_id=TEST_PROJECT_ID,
            agent_id="nova",
            blocked_due_to="hal",
            unblock_condition="initial_files_created"
        )
        print("🔒 Registered blocked NOVA agent")
        
        # Start reflection
        reflection_result = start_reflection(TEST_PROJECT_ID, interval=1)
        print(f"🧠 Reflection start result: {reflection_result}")
        
        reflection_started = reflection_result.get("status") == "success"
        print_result("Reflection started", reflection_started)
        
        # Update project state to unblock agent
        update_project_state(TEST_PROJECT_ID, {
            "agents_involved": ["hal", "nova"],
            "files_created": ["README.md", "requirements.txt"],
            "initial_files_created": True
        })
        print("📊 Updated project state to unblock agent")
        
        # Wait for reflection to detect changes
        print("⏳ Waiting for reflection to detect changes...")
        time.sleep(2)
        
        # Check for unblocked agents
        unblocked_agents = check_for_unblocked_agents(TEST_PROJECT_ID)
        print(f"🔓 Unblocked agents: {unblocked_agents}")
        
        has_unblocked = len(unblocked_agents) > 0
        print_result("Agent was unblocked by reflection", has_unblocked)
        
        # Re-evaluate task
        task = {"original_task": "Create UI", "project_id": TEST_PROJECT_ID}
        re_eval_result = re_evaluate_task(TEST_PROJECT_ID, "nova", task)
        print(f"🔄 Re-evaluation result: {re_eval_result}")
        
        task_updated = re_eval_result.get("status") == "success" and "task" in re_eval_result
        print_result("Task was re-evaluated", task_updated)
        
        return reflection_started and has_unblocked and task_updated
        
    except Exception as e:
        print(f"❌ Error in test_passive_reflection: {str(e)}")
        return False

def test_reset_flags():
    """Test intelligent reset flags"""
    print_header("Testing Intelligent Reset Flags")
    
    if not RESET_FLAGS_AVAILABLE or not PROJECT_STATE_AVAILABLE:
        print("❌ Required modules not available, skipping test")
        return False
    
    try:
        # Initialize project state
        update_project_state(TEST_PROJECT_ID, {
            "agents_involved": ["hal", "nova", "critic", "ash"],
            "files_created": ["README.md", "requirements.txt"],
            "status": "in_progress"
        })
        print("📊 Initialized project state")
        
        # Reset agent state
        agent_reset_result = reset_agent_state(TEST_PROJECT_ID, "hal")
        print(f"🔄 Agent reset result: {agent_reset_result}")
        
        agent_reset_success = agent_reset_result.get("status") == "success"
        print_result("Agent state reset", agent_reset_success)
        
        # Check project state after agent reset
        project_state = read_project_state(TEST_PROJECT_ID)
        
        agent_reset_reflected = project_state.get("latest_agent_action", {}).get("agent") == "hal"
        print_result("Agent reset reflected in project state", agent_reset_reflected)
        
        # Reset project state (partial)
        project_reset_result = reset_project_state(TEST_PROJECT_ID, full_reset=False)
        print(f"🔄 Project reset result: {project_reset_result}")
        
        project_reset_success = project_reset_result.get("status") == "success"
        print_result("Project state reset (partial)", project_reset_success)
        
        # Check reset status
        reset_status_result = get_reset_status(TEST_PROJECT_ID)
        print(f"📋 Reset status: {reset_status_result}")
        
        has_reset_status = reset_status_result.get("status") == "success" and reset_status_result.get("reset_status") == "reset"
        print_result("Reset status available", has_reset_status)
        
        # Reset project state (full)
        full_reset_result = reset_project_state(TEST_PROJECT_ID, full_reset=True)
        print(f"🔄 Full project reset result: {full_reset_result}")
        
        full_reset_success = full_reset_result.get("status") == "success"
        print_result("Project state reset (full)", full_reset_success)
        
        # Check project state after full reset
        project_state = read_project_state(TEST_PROJECT_ID)
        
        full_reset_reflected = len(project_state.get("agents_involved", [])) == 0
        print_result("Full reset reflected in project state", full_reset_reflected)
        
        return (agent_reset_success and agent_reset_reflected and 
                project_reset_success and has_reset_status and 
                full_reset_success and full_reset_reflected)
        
    except Exception as e:
        print(f"❌ Error in test_reset_flags: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and return overall result"""
    print_header("PHASE 6.1 AGENT TIMING & SYNCHRONIZATION TESTS")
    
    results = {
        "Agent Retry Flow": test_agent_retry_flow(),
        "Project State Watch": test_project_state_watch(),
        "Memory Block Writer": test_memory_block_writer(),
        "Passive Reflection Engine": test_passive_reflection(),
        "Intelligent Reset Flags": test_reset_flags()
    }
    
    print_header("TEST SUMMARY")
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        all_passed = all_passed and result
        print(f"{status} - {test_name}")
    
    print("\nOVERALL RESULT:", "✅ PASSED" if all_passed else "❌ FAILED")
    return all_passed

if __name__ == "__main__":
    run_all_tests()
