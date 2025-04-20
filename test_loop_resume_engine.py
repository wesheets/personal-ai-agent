"""
Test script for the Loop Resume Engine functionality.

This script tests the snapshot save and restore functionality
to ensure that the system can recover from crashes, freezes,
or operator interventions mid-loop.
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append('/home/ubuntu/personal-ai-agent')

# Import the necessary modules
from app.modules.loop_resume_engine import save_loop_snapshot, restore_last_snapshot, get_snapshot_history
from app.modules.project_state import read_project_state, update_project_state

# Test project ID
TEST_PROJECT_ID = f"test_resume_engine_{int(time.time())}"

def setup_test_project():
    """Set up a test project with initial state."""
    print(f"Setting up test project: {TEST_PROJECT_ID}")
    
    # Create initial project state
    initial_state = {
        "project_id": TEST_PROJECT_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "active",
        "next_recommended_step": "Run HAL to analyze requirements",
        "loop_status": "running",
        "completed_steps": [],
        "loop_count": 0,
        "loop_complete": False,
        "agents": {},
        "task_log": [],
        "logic_modules": {},
        "registry": {}
    }
    
    # Update project state
    result = update_project_state(TEST_PROJECT_ID, initial_state)
    
    print(f"Test project setup result: {result}")
    return result

def test_save_snapshot():
    """Test saving a snapshot of the project state."""
    print("\n=== Testing save_snapshot ===")
    
    # Save snapshot
    snapshot = save_loop_snapshot(TEST_PROJECT_ID)
    
    # Verify snapshot was saved
    print(f"Snapshot saved: {snapshot}")
    assert "timestamp" in snapshot, "Snapshot should have a timestamp"
    assert "loop" in snapshot, "Snapshot should have a loop count"
    assert "snapshot" in snapshot, "Snapshot should contain the project state"
    
    # Verify snapshot is in project state
    state = read_project_state(TEST_PROJECT_ID)
    assert "last_snapshot" in state, "Project state should have a last_snapshot field"
    assert "loop_snapshots" in state, "Project state should have a loop_snapshots field"
    assert len(state["loop_snapshots"]) > 0, "Project state should have at least one snapshot"
    
    print("✅ save_snapshot test passed")
    return snapshot

def test_update_project_after_snapshot():
    """Test updating the project state after saving a snapshot."""
    print("\n=== Testing project update after snapshot ===")
    
    # Update project state
    update_data = {
        "completed_steps": ["hal"],
        "loop_count": 1,
        "next_recommended_step": "Run NOVA to implement solution"
    }
    
    result = update_project_state(TEST_PROJECT_ID, update_data)
    print(f"Project update result: {result}")
    
    # Verify update
    state = read_project_state(TEST_PROJECT_ID)
    assert "hal" in state["completed_steps"], "Project state should have HAL in completed_steps"
    assert state["loop_count"] == 1, "Project state should have loop_count = 1"
    
    # Save another snapshot
    snapshot = save_loop_snapshot(TEST_PROJECT_ID)
    print(f"New snapshot saved: {snapshot}")
    
    # Verify multiple snapshots
    state = read_project_state(TEST_PROJECT_ID)
    assert len(state["loop_snapshots"]) > 1, "Project state should have multiple snapshots"
    
    print("✅ project update after snapshot test passed")
    return snapshot

def test_restore_snapshot():
    """Test restoring the project state from a snapshot."""
    print("\n=== Testing restore_snapshot ===")
    
    # Update project state to simulate progress
    update_data = {
        "completed_steps": ["hal", "nova"],
        "loop_count": 2,
        "next_recommended_step": "Run CRITIC to review implementation"
    }
    
    result = update_project_state(TEST_PROJECT_ID, update_data)
    print(f"Project update result before restore: {result}")
    
    # Verify update
    state_before_restore = read_project_state(TEST_PROJECT_ID)
    assert "nova" in state_before_restore["completed_steps"], "Project state should have NOVA in completed_steps"
    assert state_before_restore["loop_count"] == 2, "Project state should have loop_count = 2"
    
    # Restore from last snapshot
    restore_result = restore_last_snapshot(TEST_PROJECT_ID)
    print(f"Restore result: {restore_result}")
    
    # Verify restore
    state_after_restore = read_project_state(TEST_PROJECT_ID)
    assert state_after_restore["loop_count"] == 1, "Project state should be restored to loop_count = 1"
    assert "hal" in state_after_restore["completed_steps"], "Project state should have HAL in completed_steps"
    assert "nova" not in state_after_restore["completed_steps"], "Project state should not have NOVA in completed_steps"
    
    print("✅ restore_snapshot test passed")
    return restore_result

def test_snapshot_history():
    """Test retrieving the snapshot history."""
    print("\n=== Testing get_snapshot_history ===")
    
    # Get snapshot history
    history = get_snapshot_history(TEST_PROJECT_ID)
    print(f"Snapshot history: {history}")
    
    # Verify history
    assert "snapshots" in history, "History should contain snapshots"
    assert len(history["snapshots"]) >= 2, "History should have at least 2 snapshots"
    assert history["has_last_snapshot"] is True, "History should indicate a last snapshot exists"
    
    print("✅ get_snapshot_history test passed")
    return history

def test_multiple_snapshots_and_restores():
    """Test creating multiple snapshots and restoring between them."""
    print("\n=== Testing multiple snapshots and restores ===")
    
    # Create a series of updates and snapshots
    for i in range(3):
        # Update project state
        update_data = {
            "completed_steps": ["hal", "nova"] if i > 0 else ["hal"],
            "loop_count": i + 2,
            "next_recommended_step": f"Step {i + 2}"
        }
        
        update_project_state(TEST_PROJECT_ID, update_data)
        print(f"Updated project to loop {i + 2}")
        
        # Save snapshot
        snapshot = save_loop_snapshot(TEST_PROJECT_ID)
        print(f"Saved snapshot for loop {i + 2}")
    
    # Get history to verify snapshots
    history = get_snapshot_history(TEST_PROJECT_ID)
    print(f"Snapshot count: {history['snapshot_count']}")
    assert history["snapshot_count"] >= 5, "Should have at least 5 snapshots"
    
    # Restore from last snapshot
    restore_result = restore_last_snapshot(TEST_PROJECT_ID)
    print(f"Restore result: {restore_result}")
    
    # Verify restore
    state = read_project_state(TEST_PROJECT_ID)
    assert state["loop_count"] == 4, "Project state should be restored to loop_count = 4"
    
    print("✅ multiple snapshots and restores test passed")
    return history

def test_cleanup():
    """Clean up test data."""
    print("\n=== Cleaning up test data ===")
    
    # This is a mock cleanup since we're using a unique test project ID
    # In a real environment, you might want to delete the test project
    print(f"Test project {TEST_PROJECT_ID} can be safely ignored or deleted")
    
    print("✅ cleanup completed")

def run_all_tests():
    """Run all tests."""
    print("\n=== Running all Loop Resume Engine tests ===")
    
    try:
        # Setup
        setup_test_project()
        
        # Run tests
        test_save_snapshot()
        test_update_project_after_snapshot()
        test_restore_snapshot()
        test_snapshot_history()
        test_multiple_snapshots_and_restores()
        
        # Cleanup
        test_cleanup()
        
        print("\n✅ All tests passed!")
        return True
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_all_tests()
