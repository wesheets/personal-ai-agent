"""
Status Tracker Tool for agents to update task status.

This tool allows Builder, Memory, Research, Ops, and other agents to update
the status of their assigned tasks, report completion, request retries,
or indicate they are blocked.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.task_state_manager import get_task_state_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatusTracker:
    """
    Tool for agents to update task status and report progress.
    
    This class provides methods for agents to:
    - Update task status (complete, failed, blocked)
    - Report progress on ongoing tasks
    - Request retries for failed tasks
    - Indicate blocking issues
    """
    
    def __init__(self):
        """Initialize the status tracker."""
        self.task_state_manager = get_task_state_manager()
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname("/app/logs/task_state_log.json"), exist_ok=True)
    
    def update_status(self, 
                     subtask_id: str, 
                     status: str, 
                     output_summary: str = "", 
                     error_message: str = "") -> Dict[str, Any]:
        """
        Update the status of a task.
        
        Args:
            subtask_id: ID of the subtask
            status: New status (complete, failed, blocked, in_progress)
            output_summary: Optional summary of the output
            error_message: Optional error message if status is failed
            
        Returns:
            Updated task state
        """
        # Validate status
        valid_statuses = ["complete", "failed", "blocked", "in_progress"]
        if status not in valid_statuses:
            error_msg = f"Invalid status: {status}. Must be one of {valid_statuses}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Get the current task state
        task_state = self.task_state_manager.get_task_state(subtask_id)
        
        if not task_state:
            error_msg = f"Task state not found for subtask ID: {subtask_id}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Update the task status
        updated_state = self.task_state_manager.update_task_status(
            subtask_id=subtask_id,
            status=status,
            output_summary=output_summary,
            error_message=error_message
        )
        
        if not updated_state:
            error_msg = f"Failed to update task status for subtask ID: {subtask_id}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Log the status update
        self._log_status_update(
            subtask_id=subtask_id,
            status=status,
            output_summary=output_summary,
            error_message=error_message
        )
        
        return {
            "success": True,
            "subtask_id": subtask_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "task_state": updated_state
        }
    
    def complete_task(self, subtask_id: str, output_summary: str) -> Dict[str, Any]:
        """
        Mark a task as complete.
        
        Args:
            subtask_id: ID of the subtask
            output_summary: Summary of the output
            
        Returns:
            Updated task state
        """
        return self.update_status(
            subtask_id=subtask_id,
            status="complete",
            output_summary=output_summary
        )
    
    def fail_task(self, subtask_id: str, error_message: str) -> Dict[str, Any]:
        """
        Mark a task as failed.
        
        Args:
            subtask_id: ID of the subtask
            error_message: Error message
            
        Returns:
            Updated task state
        """
        return self.update_status(
            subtask_id=subtask_id,
            status="failed",
            error_message=error_message
        )
    
    def block_task(self, subtask_id: str, reason: str) -> Dict[str, Any]:
        """
        Mark a task as blocked.
        
        Args:
            subtask_id: ID of the subtask
            reason: Reason for blocking
            
        Returns:
            Updated task state
        """
        return self.update_status(
            subtask_id=subtask_id,
            status="blocked",
            error_message=reason
        )
    
    def start_task(self, subtask_id: str) -> Dict[str, Any]:
        """
        Mark a task as in progress.
        
        Args:
            subtask_id: ID of the subtask
            
        Returns:
            Updated task state
        """
        return self.update_status(
            subtask_id=subtask_id,
            status="in_progress"
        )
    
    def report_progress(self, 
                       subtask_id: str, 
                       progress_percentage: float, 
                       progress_message: str) -> Dict[str, Any]:
        """
        Report progress on a task.
        
        Args:
            subtask_id: ID of the subtask
            progress_percentage: Percentage of completion (0-100)
            progress_message: Progress message
            
        Returns:
            Updated task state
        """
        # Get the current task state
        task_state = self.task_state_manager.get_task_state(subtask_id)
        
        if not task_state:
            error_msg = f"Task state not found for subtask ID: {subtask_id}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Validate progress percentage
        if progress_percentage < 0 or progress_percentage > 100:
            error_msg = f"Invalid progress percentage: {progress_percentage}. Must be between 0 and 100"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Update the task state
        updates = {
            "progress_percentage": progress_percentage,
            "progress_message": progress_message,
            "status": "in_progress"  # Ensure the task is marked as in progress
        }
        
        updated_state = self.task_state_manager.update_task_state(
            subtask_id=subtask_id,
            updates=updates
        )
        
        if not updated_state:
            error_msg = f"Failed to update task progress for subtask ID: {subtask_id}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Log the progress update
        self._log_status_update(
            subtask_id=subtask_id,
            status="in_progress",
            output_summary=f"Progress: {progress_percentage}% - {progress_message}"
        )
        
        return {
            "success": True,
            "subtask_id": subtask_id,
            "progress_percentage": progress_percentage,
            "timestamp": datetime.now().isoformat(),
            "task_state": updated_state
        }
    
    def request_retry(self, subtask_id: str, reason: str) -> Dict[str, Any]:
        """
        Request a retry for a failed task.
        
        Args:
            subtask_id: ID of the subtask
            reason: Reason for retry
            
        Returns:
            Updated task state
        """
        # Get the current task state
        task_state = self.task_state_manager.get_task_state(subtask_id)
        
        if not task_state:
            error_msg = f"Task state not found for subtask ID: {subtask_id}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if the task is failed
        if task_state.get("status") != "failed":
            error_msg = f"Cannot request retry for task with status: {task_state.get('status')}. Task must be failed"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if the task has exceeded max retries
        retry_count = task_state.get("retry_count", 0)
        max_retries = 3  # TODO: Get from config
        
        if retry_count >= max_retries:
            error_msg = f"Task has exceeded maximum retry count ({max_retries})"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Update the task state to queued for retry
        updates = {
            "status": "queued",
            "retry_requested": True,
            "retry_reason": reason,
            "last_retry_request": datetime.now().isoformat()
        }
        
        updated_state = self.task_state_manager.update_task_state(
            subtask_id=subtask_id,
            updates=updates
        )
        
        if not updated_state:
            error_msg = f"Failed to request retry for subtask ID: {subtask_id}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # Log the retry request
        self._log_status_update(
            subtask_id=subtask_id,
            status="queued",
            output_summary=f"Retry requested: {reason}"
        )
        
        return {
            "success": True,
            "subtask_id": subtask_id,
            "status": "queued",
            "retry_count": retry_count,
            "timestamp": datetime.now().isoformat(),
            "task_state": updated_state
        }
    
    def get_task_info(self, subtask_id: str) -> Dict[str, Any]:
        """
        Get information about a task.
        
        Args:
            subtask_id: ID of the subtask
            
        Returns:
            Task information
        """
        # Get the task state
        task_state = self.task_state_manager.get_task_state(subtask_id)
        
        if not task_state:
            error_msg = f"Task state not found for subtask ID: {subtask_id}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "success": True,
            "subtask_id": subtask_id,
            "task_state": task_state,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_goal_progress(self, goal_id: str) -> Dict[str, Any]:
        """
        Get progress information for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Goal progress information
        """
        # Get goal progress from task state manager
        goal_progress = self.task_state_manager.get_goal_progress(goal_id)
        
        return {
            "success": True,
            "goal_id": goal_id,
            "progress": goal_progress,
            "timestamp": datetime.now().isoformat()
        }
    
    def _log_status_update(self, 
                          subtask_id: str, 
                          status: str, 
                          output_summary: str = "", 
                          error_message: str = "") -> None:
        """
        Log a status update to the task_state_log.json file.
        
        Args:
            subtask_id: ID of the subtask
            status: New status
            output_summary: Optional summary of the output
            error_message: Optional error message
        """
        # Get the task state
        task_state = self.task_state_manager.get_task_state(subtask_id)
        
        if not task_state:
            logger.error(f"Task state not found for subtask ID: {subtask_id}")
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "status_update",
            "subtask_id": subtask_id,
            "goal_id": task_state.get("goal_id", ""),
            "agent": task_state.get("assigned_agent", ""),
            "old_status": task_state.get("status", ""),
            "new_status": status,
            "output_summary": output_summary,
            "error_message": error_message
        }
        
        try:
            # Read existing logs
            logs = []
            log_file = "/app/logs/task_state_log.json"
            
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    try:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = []
                    except json.JSONDecodeError:
                        logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Write back to file
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error logging status update: {str(e)}")

# Create a singleton instance
_status_tracker = None

def get_status_tracker() -> StatusTracker:
    """
    Get the singleton instance of the status tracker.
    
    Returns:
        StatusTracker instance
    """
    global _status_tracker
    if _status_tracker is None:
        _status_tracker = StatusTracker()
    return _status_tracker

# For API integration
def update_status(subtask_id: str, 
                 status: str, 
                 output_summary: str = "", 
                 error_message: str = "") -> Dict[str, Any]:
    """
    Update the status of a task.
    
    Args:
        subtask_id: ID of the subtask
        status: New status (complete, failed, blocked, in_progress)
        output_summary: Optional summary of the output
        error_message: Optional error message if status is failed
        
    Returns:
        Updated task state
    """
    tracker = get_status_tracker()
    return tracker.update_status(subtask_id, status, output_summary, error_message)

def complete_task(subtask_id: str, output_summary: str) -> Dict[str, Any]:
    """
    Mark a task as complete.
    
    Args:
        subtask_id: ID of the subtask
        output_summary: Summary of the output
        
    Returns:
        Updated task state
    """
    tracker = get_status_tracker()
    return tracker.complete_task(subtask_id, output_summary)

def fail_task(subtask_id: str, error_message: str) -> Dict[str, Any]:
    """
    Mark a task as failed.
    
    Args:
        subtask_id: ID of the subtask
        error_message: Error message
        
    Returns:
        Updated task state
    """
    tracker = get_status_tracker()
    return tracker.fail_task(subtask_id, error_message)

def block_task(subtask_id: str, reason: str) -> Dict[str, Any]:
    """
    Mark a task as blocked.
    
    Args:
        subtask_id: ID of the subtask
        reason: Reason for blocking
        
    Returns:
        Updated task state
    """
    tracker = get_status_tracker()
    return tracker.block_task(subtask_id, reason)

def start_task(subtask_id: str) -> Dict[str, Any]:
    """
    Mark a task as in progress.
    
    Args:
        subtask_id: ID of the subtask
        
    Returns:
        Updated task state
    """
    tracker = get_status_tracker()
    return tracker.start_task(subtask_id)

def report_progress(subtask_id: str, 
                   progress_percentage: float, 
                   progress_message: str) -> Dict[str, Any]:
    """
    Report progress on a task.
    
    Args:
        subtask_id: ID of the subtask
        progress_percentage: Percentage of completion (0-100)
        progress_message: Progress message
        
    Returns:
        Updated task state
    """
    tracker = get_status_tracker()
    return tracker.report_progress(subtask_id, progress_percentage, progress_message)

def request_retry(subtask_id: str, reason: str) -> Dict[str, Any]:
    """
    Request a retry for a failed task.
    
    Args:
        subtask_id: ID of the subtask
        reason: Reason for retry
        
    Returns:
        Updated task state
    """
    tracker = get_status_tracker()
    return tracker.request_retry(subtask_id, reason)

def get_task_info(subtask_id: str) -> Dict[str, Any]:
    """
    Get information about a task.
    
    Args:
        subtask_id: ID of the subtask
        
    Returns:
        Task information
    """
    tracker = get_status_tracker()
    return tracker.get_task_info(subtask_id)

def get_goal_progress(goal_id: str) -> Dict[str, Any]:
    """
    Get progress information for a goal.
    
    Args:
        goal_id: ID of the goal
        
    Returns:
        Goal progress information
    """
    tracker = get_status_tracker()
    return tracker.get_goal_progress(goal_id)

# For testing purposes
if __name__ == "__main__":
    # Test the status tracker
    tracker = StatusTracker()
    
    # Create a test task state
    task_state_manager = get_task_state_manager()
    
    goal_id = "test_goal_1"
    subtask_id = f"{goal_id}_subtask_1"
    
    task_state = task_state_manager.create_task_state(
        goal_id=goal_id,
        subtask_id=subtask_id,
        subtask_description="Test subtask",
        assigned_agent="builder"
    )
    
    print(f"Created task state: {task_state}")
    
    # Start the task
    result = tracker.start_task(subtask_id)
    print(f"Started task: {result}")
    
    # Report progress
    result = tracker.report_progress(subtask_id, 50, "Halfway done")
    print(f"Reported progress: {result}")
    
    # Complete the task
    result = tracker.complete_task(subtask_id, "Task completed successfully")
    print(f"Completed task: {result}")
    
    # Get goal progress
    result = tracker.get_goal_progress(goal_id)
    print(f"Goal progress: {result}")
