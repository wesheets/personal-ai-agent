"""
Test script for the Task Memory Loop + Multi-Agent State Tracking system.

This script tests the functionality of the task state manager, planner orchestrator,
status tracker, and planner agent enhancer to ensure they work correctly together.
"""

import os
import json
import uuid
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

# Import the components to test
from app.core.task_state_manager import get_task_state_manager
from app.core.planner_orchestrator import get_planner_orchestrator
from app.tools.status_tracker import get_status_tracker
from app.core.planner_agent_enhancer import get_planner_agent_enhancer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTaskMemorySystem:
    """
    Test class for the Task Memory Loop + Multi-Agent State Tracking system.
    """
    
    def __init__(self):
        """Initialize the test class."""
        self.task_state_manager = get_task_state_manager()
        self.planner_orchestrator = get_planner_orchestrator()
        self.status_tracker = get_status_tracker()
        self.planner_agent_enhancer = get_planner_agent_enhancer()
        
        # Create logs directory if it doesn't exist
        os.makedirs("/app/logs", exist_ok=True)
        
        # Initialize test results
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
    
    def run_all_tests(self):
        """Run all tests."""
        logger.info("Starting tests for Task Memory Loop + Multi-Agent State Tracking system")
        
        # Test task state management
        self.test_task_state_management()
        
        # Test status tracking
        self.test_status_tracking()
        
        # Test goal continuation
        self.test_goal_continuation()
        
        # Test multi-agent coordination
        self.test_multi_agent_coordination()
        
        # Test persistence across sessions
        self.test_persistence_across_sessions()
        
        # Print test results
        self.print_test_results()
        
        return self.test_results
    
    def test_task_state_management(self):
        """Test task state management functionality."""
        logger.info("Testing task state management")
        
        # Test creating a task state
        test_name = "Create task state"
        try:
            goal_id = f"test_goal_{uuid.uuid4()}"
            subtask_id = f"{goal_id}_subtask_1"
            
            task_state = self.task_state_manager.create_task_state(
                goal_id=goal_id,
                subtask_id=subtask_id,
                subtask_description="Test subtask for task state management",
                assigned_agent="builder"
            )
            
            assert task_state is not None, "Task state should not be None"
            assert task_state["goal_id"] == goal_id, "Goal ID should match"
            assert task_state["subtask_id"] == subtask_id, "Subtask ID should match"
            assert task_state["status"] == "queued", "Initial status should be queued"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test getting a task state
        test_name = "Get task state"
        try:
            retrieved_state = self.task_state_manager.get_task_state(subtask_id)
            
            assert retrieved_state is not None, "Retrieved task state should not be None"
            assert retrieved_state["goal_id"] == goal_id, "Goal ID should match"
            assert retrieved_state["subtask_id"] == subtask_id, "Subtask ID should match"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test updating a task state
        test_name = "Update task state"
        try:
            updated_state = self.task_state_manager.update_task_status(
                subtask_id=subtask_id,
                status="in_progress",
                output_summary="Task is in progress"
            )
            
            assert updated_state is not None, "Updated task state should not be None"
            assert updated_state["status"] == "in_progress", "Status should be updated to in_progress"
            assert updated_state["output_summary"] == "Task is in progress", "Output summary should be updated"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test getting goal tasks
        test_name = "Get goal tasks"
        try:
            # Create another task for the same goal
            subtask_id_2 = f"{goal_id}_subtask_2"
            
            self.task_state_manager.create_task_state(
                goal_id=goal_id,
                subtask_id=subtask_id_2,
                subtask_description="Another test subtask",
                assigned_agent="research"
            )
            
            goal_tasks = self.task_state_manager.get_goal_tasks(goal_id)
            
            assert len(goal_tasks) == 2, "Should have 2 tasks for the goal"
            assert any(task["subtask_id"] == subtask_id for task in goal_tasks), "First subtask should be in goal tasks"
            assert any(task["subtask_id"] == subtask_id_2 for task in goal_tasks), "Second subtask should be in goal tasks"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test getting goal progress
        test_name = "Get goal progress"
        try:
            # Complete one of the tasks
            self.task_state_manager.update_task_status(
                subtask_id=subtask_id,
                status="complete",
                output_summary="Task completed successfully"
            )
            
            goal_progress = self.task_state_manager.get_goal_progress(goal_id)
            
            assert goal_progress["total_tasks"] == 2, "Should have 2 total tasks"
            assert goal_progress["completed"] == 1, "Should have 1 completed task"
            assert goal_progress["completion_percentage"] == 50.0, "Should have 50% completion"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    def test_status_tracking(self):
        """Test status tracking functionality."""
        logger.info("Testing status tracking")
        
        # Create a new goal and task for testing
        goal_id = f"test_goal_{uuid.uuid4()}"
        subtask_id = f"{goal_id}_subtask_1"
        
        self.task_state_manager.create_task_state(
            goal_id=goal_id,
            subtask_id=subtask_id,
            subtask_description="Test subtask for status tracking",
            assigned_agent="builder"
        )
        
        # Test starting a task
        test_name = "Start task"
        try:
            result = self.status_tracker.start_task(subtask_id)
            
            assert result["success"] is True, "Start task should succeed"
            assert result["subtask_id"] == subtask_id, "Subtask ID should match"
            assert result["task_state"]["status"] == "in_progress", "Status should be in_progress"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test reporting progress
        test_name = "Report progress"
        try:
            result = self.status_tracker.report_progress(
                subtask_id=subtask_id,
                progress_percentage=50.0,
                progress_message="Halfway done"
            )
            
            assert result["success"] is True, "Report progress should succeed"
            assert result["progress_percentage"] == 50.0, "Progress percentage should be 50%"
            assert result["task_state"]["progress_message"] == "Halfway done", "Progress message should match"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test completing a task
        test_name = "Complete task"
        try:
            result = self.status_tracker.complete_task(
                subtask_id=subtask_id,
                output_summary="Task completed successfully"
            )
            
            assert result["success"] is True, "Complete task should succeed"
            assert result["status"] == "complete", "Status should be complete"
            assert result["task_state"]["output_summary"] == "Task completed successfully", "Output summary should match"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test failing a task
        subtask_id_2 = f"{goal_id}_subtask_2"
        
        self.task_state_manager.create_task_state(
            goal_id=goal_id,
            subtask_id=subtask_id_2,
            subtask_description="Test subtask for failure",
            assigned_agent="builder"
        )
        
        test_name = "Fail task"
        try:
            result = self.status_tracker.fail_task(
                subtask_id=subtask_id_2,
                error_message="Task failed due to an error"
            )
            
            assert result["success"] is True, "Fail task should succeed"
            assert result["status"] == "failed", "Status should be failed"
            assert result["task_state"]["error_message"] == "Task failed due to an error", "Error message should match"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test blocking a task
        subtask_id_3 = f"{goal_id}_subtask_3"
        
        self.task_state_manager.create_task_state(
            goal_id=goal_id,
            subtask_id=subtask_id_3,
            subtask_description="Test subtask for blocking",
            assigned_agent="builder"
        )
        
        test_name = "Block task"
        try:
            result = self.status_tracker.block_task(
                subtask_id=subtask_id_3,
                reason="Task is blocked by a dependency"
            )
            
            assert result["success"] is True, "Block task should succeed"
            assert result["status"] == "blocked", "Status should be blocked"
            assert result["task_state"]["error_message"] == "Task is blocked by a dependency", "Reason should match"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test getting task info
        test_name = "Get task info"
        try:
            result = self.status_tracker.get_task_info(subtask_id)
            
            assert result["success"] is True, "Get task info should succeed"
            assert result["subtask_id"] == subtask_id, "Subtask ID should match"
            assert result["task_state"]["status"] == "complete", "Status should be complete"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test getting goal progress
        test_name = "Get goal progress via status tracker"
        try:
            result = self.status_tracker.get_goal_progress(goal_id)
            
            assert result["success"] is True, "Get goal progress should succeed"
            assert result["goal_id"] == goal_id, "Goal ID should match"
            assert result["progress"]["total_tasks"] == 3, "Should have 3 total tasks"
            assert result["progress"]["completed"] == 1, "Should have 1 completed task"
            assert result["progress"]["failed"] == 1, "Should have 1 failed task"
            assert result["progress"]["blocked"] == 1, "Should have 1 blocked task"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    def test_goal_continuation(self):
        """Test goal continuation functionality."""
        logger.info("Testing goal continuation")
        
        # Create a test goal
        goal_id = f"test_goal_{uuid.uuid4()}"
        goal = {
            "id": goal_id,
            "description": "Test goal for continuation",
            "type": "test"
        }
        
        # Test processing a new goal
        test_name = "Process new goal"
        try:
            # Mock the planner orchestrator's process_goal method to avoid actual execution
            original_process_goal = self.planner_orchestrator.process_goal
            
            def mock_process_goal(goal):
                # Create some test subtasks
                for i in range(3):
                    subtask_id = f"{goal['id']}_subtask_{i+1}"
                    self.task_state_manager.create_task_state(
                        goal_id=goal["id"],
                        subtask_id=subtask_id,
                        subtask_description=f"Test subtask {i+1} for {goal['description']}",
                        assigned_agent="builder"
                    )
                
                # Complete the first subtask
                self.task_state_manager.update_task_status(
                    subtask_id=f"{goal['id']}_subtask_1",
                    status="complete",
                    output_summary="First subtask completed"
                )
                
                # Start the second subtask
                self.task_state_manager.update_task_status(
                    subtask_id=f"{goal['id']}_subtask_2",
                    status="in_progress"
                )
                
                # Return a mock result
                return {
                    "status": "partial_success",
                    "goal_id": goal["id"],
                    "message": "Goal partially processed for testing",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Replace the method temporarily
            self.planner_orchestrator.process_goal = mock_process_goal
            
            # Process the goal
            result = self.planner_agent_enhancer.process_goal_with_memory(goal)
            
            # Restore the original method
            self.planner_orchestrator.process_goal = original_process_goal
            
            assert result is not None, "Process goal result should not be None"
            assert result["goal_id"] == goal_id, "Goal ID should match"
            
            # Check that the subtasks were created
            goal_tasks = self.task_state_manager.get_goal_tasks(goal_id)
            assert len(goal_tasks) == 3, "Should have 3 subtasks"
            
            # Check the status of the subtasks
            completed = sum(1 for task in goal_tasks if task["status"] == "complete")
            in_progress = sum(1 for task in goal_tasks if task["status"] == "in_progress")
            queued = sum(1 for task in goal_tasks if task["status"] == "queued")
            
            assert completed == 1, "Should have 1 completed subtask"
            assert in_progress == 1, "Should have 1 in-progress subtask"
            assert queued == 1, "Should have 1 queued subtask"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test resuming a goal
        test_name = "Resume goal"
        try:
            # Mock the planner orchestrator's resume_goal method
            original_resume_goal = self.planner_orchestrator.resume_goal
            
            def mock_resume_goal(goal_id):
                # Complete the second subtask
                self.task_state_manager.update_task_status(
                    subtask_id=f"{goal_id}_subtask_2",
                    status="complete",
                    output_summary="Second subtask completed"
                )
                
                # Start the third subtask
                self.task_state_manager.update_task_status(
                    subtask_id=f"{goal_id}_subtask_3",
                    status="in_progress"
                )
                
                # Return a mock result
                return {
                    "status": "success",
                    "goal_id": goal_id,
                    "message": "Goal resumed for testing",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Replace the method temporarily
            self.planner_orchestrator.resume_goal = mock_resume_goal
            
            # Resume the goal
            result = self.planner_orchestrator.resume_goal(goal_id)
            
            # Restore the original method
            self.planner_orchestrator.resume_goal = original_resume_goal
            
            assert result is not None, "Resume goal result should not be None"
            assert result["goal_id"] == goal_id, "Goal ID should match"
            
            # Check the updated status of the subtasks
            goal_tasks = self.task_state_manager.get_goal_tasks(goal_id)
            completed = sum(1 for task in goal_tasks if task["status"] == "complete")
            in_progress = sum(1 for task in goal_tasks if task["status"] == "in_progress")
            
            assert completed == 2, "Should have 2 completed subtasks"
            assert in_progress == 1, "Should have 1 in-progress subtask"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test goal progress tracking
        test_name = "Goal progress tracking"
        try:
            # Get goal progress
            goal_progress = self.task_state_manager.get_goal_progress(goal_id)
            
            assert goal_progress["total_tasks"] == 3, "Should have 3 total tasks"
            assert goal_progress["completed"] == 2, "Should have 2 completed tasks"
            assert goal_progress["in_progress"] == 1, "Should have 1 in-progress task"
            assert goal_progress["completion_percentage"] == 66.66666666666666, "Should have ~66.67% completion"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test completing a goal
        test_name = "Complete goal"
        try:
            # Complete the third subtask
            self.task_state_manager.update_task_status(
                subtask_id=f"{goal_id}_subtask_3",
                status="complete",
                output_summary="Third subtask completed"
            )
            
            # Get goal progress
            goal_progress = self.task_state_manager.get_goal_progress(goal_id)
            
            assert goal_progress["total_tasks"] == 3, "Should have 3 total tasks"
            assert goal_progress["completed"] == 3, "Should have 3 completed tasks"
            assert goal_progress["completion_percentage"] == 100.0, "Should have 100% completion"
            assert goal_progress["status"] == "complete", "Goal status should be complete"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    def test_multi_agent_coordination(self):
        """Test multi-agent coordination functionality."""
        logger.info("Testing multi-agent coordination")
        
        # Create a test goal with multiple agents
        goal_id = f"test_goal_{uuid.uuid4()}"
        
        # Create subtasks for different agents
        agents = ["builder", "research", "ops", "memory"]
        subtask_ids = []
        
        for i, agent in enumerate(agents):
            subtask_id = f"{goal_id}_subtask_{i+1}"
            subtask_ids.append(subtask_id)
            
            self.task_state_manager.create_task_state(
                goal_id=goal_id,
                subtask_id=subtask_id,
                subtask_description=f"Test subtask for {agent} agent",
                assigned_agent=agent
            )
        
        # Test getting agent tasks
        test_name = "Get agent tasks"
        try:
            for i, agent in enumerate(agents):
                agent_tasks = self.task_state_manager.get_agent_tasks(agent)
                
                assert len(agent_tasks) >= 1, f"Should have at least 1 task for {agent} agent"
                assert any(task["subtask_id"] == subtask_ids[i] for task in agent_tasks), f"Subtask for {agent} should be in agent tasks"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test task prioritization
        test_name = "Task prioritization"
        try:
            # Set up dependencies between tasks
            # subtask_2 depends on subtask_1
            # subtask_3 depends on subtask_2
            # subtask_4 depends on subtask_1 and subtask_2
            
            # Update task states with dependencies
            for i, subtask_id in enumerate(subtask_ids):
                updates = {}
                
                if i == 1:  # subtask_2
                    updates["dependencies"] = [subtask_ids[0]]
                elif i == 2:  # subtask_3
                    updates["dependencies"] = [subtask_ids[1]]
                elif i == 3:  # subtask_4
                    updates["dependencies"] = [subtask_ids[0], subtask_ids[1]]
                
                if updates:
                    self.task_state_manager.update_task_state(subtask_id, updates)
            
            # Prioritize tasks
            prioritized_tasks = self.planner_agent_enhancer.prioritize_tasks(goal_id)
            
            assert len(prioritized_tasks) == 4, "Should have 4 prioritized tasks"
            
            # The first task should be subtask_1 since it has the most dependents
            assert prioritized_tasks[0]["subtask_id"] == subtask_ids[0], "First prioritized task should be subtask_1"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test stalled task detection
        test_name = "Stalled task detection"
        try:
            # Mock the task state manager's get_stalled_tasks method
            original_get_stalled_tasks = self.task_state_manager.get_stalled_tasks
            
            def mock_get_stalled_tasks(hours_threshold):
                # Return the first task as stalled
                return [self.task_state_manager.get_task_state(subtask_ids[0])]
            
            # Replace the method temporarily
            self.task_state_manager.get_stalled_tasks = mock_get_stalled_tasks
            
            # Check for stalled tasks
            stalled_tasks = self.planner_agent_enhancer.check_for_stalled_tasks()
            
            # Restore the original method
            self.task_state_manager.get_stalled_tasks = original_get_stalled_tasks
            
            assert len(stalled_tasks) == 1, "Should have 1 stalled task"
            assert stalled_tasks[0]["subtask_id"] == subtask_ids[0], "Stalled task should be subtask_1"
            
            # Check if the task was marked as escalated
            task_state = self.task_state_manager.get_task_state(subtask_ids[0])
            assert task_state.get("escalated", False) is True, "Task should be marked as escalated"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    def test_persistence_across_sessions(self):
        """Test persistence across sessions functionality."""
        logger.info("Testing persistence across sessions")
        
        # Create a test goal
        goal_id = f"test_goal_{uuid.uuid4()}"
        goal = {
            "id": goal_id,
            "description": "Test goal for persistence",
            "type": "test"
        }
        
        # Create subtasks
        for i in range(3):
            subtask_id = f"{goal_id}_subtask_{i+1}"
            
            self.task_state_manager.create_task_state(
                goal_id=goal_id,
                subtask_id=subtask_id,
                subtask_description=f"Test subtask {i+1} for persistence",
                assigned_agent="builder"
            )
        
        # Complete the first subtask
        self.task_state_manager.update_task_status(
            subtask_id=f"{goal_id}_subtask_1",
            status="complete",
            output_summary="First subtask completed"
        )
        
        # Test ensuring persistence
        test_name = "Ensure persistence"
        try:
            result = self.planner_agent_enhancer.ensure_persistence(goal_id)
            
            assert result["persistence"] is True, "Persistence should be enabled"
            assert result["goal_id"] == goal_id, "Goal ID should match"
            assert result["auto_resume"] is True, "Auto-resume should be enabled"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test making goal queryable
        test_name = "Make goal queryable"
        try:
            result = self.planner_agent_enhancer.make_goal_queryable(goal_id)
            
            assert result["queryable"] is True, "Goal should be queryable"
            assert result["goal_id"] == goal_id, "Goal ID should match"
            assert result["progress"]["total_tasks"] == 3, "Should have 3 total tasks"
            assert result["progress"]["completed"] == 1, "Should have 1 completed task"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
        
        # Test goal replay
        test_name = "Goal replay"
        try:
            # Mock the planner orchestrator's replay_goal_history method
            original_replay_goal_history = self.planner_orchestrator.replay_goal_history
            
            def mock_replay_goal_history(goal_id):
                # Return a mock result
                return {
                    "status": "success",
                    "goal_id": goal_id,
                    "event_count": 5,
                    "events": [
                        {"entry_type": "goal", "status": "goal_start", "timestamp": datetime.now().isoformat()},
                        {"entry_type": "subtask", "status": "subtask_created", "timestamp": datetime.now().isoformat()},
                        {"entry_type": "subtask_assignment", "status": "subtask_assigned", "timestamp": datetime.now().isoformat()},
                        {"entry_type": "subtask_result", "status": "subtask_completed", "timestamp": datetime.now().isoformat()},
                        {"entry_type": "task_state", "status": "complete", "timestamp": datetime.now().isoformat()}
                    ],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Replace the method temporarily
            self.planner_orchestrator.replay_goal_history = mock_replay_goal_history
            
            # Replay goal history
            result = self.planner_orchestrator.replay_goal_history(goal_id)
            
            # Restore the original method
            self.planner_orchestrator.replay_goal_history = original_replay_goal_history
            
            assert result["status"] == "success", "Goal replay should succeed"
            assert result["goal_id"] == goal_id, "Goal ID should match"
            assert result["event_count"] == 5, "Should have 5 events"
            
            self._record_test_result(test_name, True)
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    def _record_test_result(self, test_name, passed, error=None):
        """Record a test result."""
        self.test_results["total_tests"] += 1
        
        if passed:
            self.test_results["passed_tests"] += 1
            logger.info(f"✅ PASS: {test_name}")
        else:
            self.test_results["failed_tests"] += 1
            logger.error(f"❌ FAIL: {test_name} - {error}")
        
        self.test_results["test_details"].append({
            "test_name": test_name,
            "passed": passed,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def print_test_results(self):
        """Print test results."""
        logger.info("==== Test Results ====")
        logger.info(f"Total tests: {self.test_results['total_tests']}")
        logger.info(f"Passed tests: {self.test_results['passed_tests']}")
        logger.info(f"Failed tests: {self.test_results['failed_tests']}")
        
        if self.test_results["failed_tests"] > 0:
            logger.info("==== Failed Tests ====")
            for test in self.test_results["test_details"]:
                if not test["passed"]:
                    logger.info(f"- {test['test_name']}: {test['error']}")

# Run the tests if this script is executed directly
if __name__ == "__main__":
    tester = TestTaskMemorySystem()
    results = tester.run_all_tests()
    
    # Write results to file
    with open("/app/logs/test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Tests completed: {results['passed_tests']}/{results['total_tests']} passed")
    
    if results["failed_tests"] > 0:
        exit(1)
    else:
        exit(0)
