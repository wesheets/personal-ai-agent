"""
Status Tracker Tool
This module provides functionality to track the status of tasks and goals.
It integrates with the Task State Manager to provide persistent state tracking.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.task_state_manager import TaskStateManager, get_task_state_manager

# Set up logging
logger = logging.getLogger(__name__)

class StatusTracker:
    """
    Tool for tracking the status of tasks and goals
    """
    
    def __init__(self):
        self.name = "status_tracker"
        self.description = "Track the status of tasks and goals"
        self.task_state_manager = get_task_state_manager()
        
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join("app", "logs", "status_logs")
        os.makedirs(self.logs_dir, exist_ok=True)
    
    async def run(self, action: str, subtask_id: str, **kwargs) -> Dict[str, Any]:
        """
        Run the status tracker tool with the specified action
        
        Args:
            action: The action to perform (update_status, complete_task, fail_task, etc.)
            subtask_id: ID of the subtask
            **kwargs: Additional arguments specific to the action
            
        Returns:
            Dictionary containing the result of the action
        """
        if action == "update_status":
            status = kwargs.get("status", "")
            output_summary = kwargs.get("output_summary", "")
            error_message = kwargs.get("error_message", "")
            return self.update_status(subtask_id, status, output_summary, error_message)
        
        elif action == "complete_task":
            output_summary = kwargs.get("output_summary", "")
            return self.complete_task(subtask_id, output_summary)
        
        elif action == "fail_task":
            error_message = kwargs.get("error_message", "")
            return self.fail_task(subtask_id, error_message)
        
        elif action == "block_task":
            reason = kwargs.get("reason", "")
            return self.block_task(subtask_id, reason)
        
        elif action == "start_task":
            return self.start_task(subtask_id)
        
        elif action == "report_progress":
            progress_percentage = kwargs.get("progress_percentage", 0)
            progress_message = kwargs.get("progress_message", "")
            return self.report_progress(subtask_id, progress_percentage, progress_message)
        
        elif action == "request_retry":
            reason = kwargs.get("reason", "")
            return self.request_retry(subtask_id, reason)
        
        elif action == "get_task_info":
            return self.get_task_info(subtask_id)
        
        elif action == "get_goal_progress":
            goal_id = subtask_id  # In this case, subtask_id is actually the goal_id
            return self.get_goal_progress(goal_id)
        
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
    
    def update_status(self, subtask_id: str, 
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
        try:
            # Get the task state
            task_state = self.task_state_manager.get_task_state(subtask_id)
            if not task_state:
                return {
                    "success": False,
                    "error": f"Task not found: {subtask_id}"
                }
            
            # Update the task state
            task_state["status"] = status
            task_state["last_updated"] = datetime.now().isoformat()
            
            if output_summary:
                task_state["output_summary"] = output_summary
            
            if error_message:
                task_state["error_message"] = error_message
            
            # Save the updated task state
            self.task_state_manager.update_task_state(subtask_id, task_state)
            
            # Log the status update
            self._log_status_update(subtask_id, status, output_summary, error_message)
            
            return {
                "success": True,
                "task_id": subtask_id,
                "status": status,
                "task_state": task_state
            }
        
        except Exception as e:
            logger.error(f"Error updating status for task {subtask_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
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
        return self.update_status(subtask_id, "complete", output_summary)
    
    def fail_task(self, subtask_id: str, error_message: str) -> Dict[str, Any]:
        """
        Mark a task as failed.
        
        Args:
            subtask_id: ID of the subtask
            error_message: Error message
            
        Returns:
            Updated task state
        """
        return self.update_status(subtask_id, "failed", error_message=error_message)
    
    def block_task(self, subtask_id: str, reason: str) -> Dict[str, Any]:
        """
        Mark a task as blocked.
        
        Args:
            subtask_id: ID of the subtask
            reason: Reason for blocking
            
        Returns:
            Updated task state
        """
        return self.update_status(subtask_id, "blocked", error_message=reason)
    
    def start_task(self, subtask_id: str) -> Dict[str, Any]:
        """
        Mark a task as in progress.
        
        Args:
            subtask_id: ID of the subtask
            
        Returns:
            Updated task state
        """
        return self.update_status(subtask_id, "in_progress")
    
    def report_progress(self, subtask_id: str, 
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
        try:
            # Get the task state
            task_state = self.task_state_manager.get_task_state(subtask_id)
            if not task_state:
                return {
                    "success": False,
                    "error": f"Task not found: {subtask_id}"
                }
            
            # Update the task state
            task_state["status"] = "in_progress"
            task_state["last_updated"] = datetime.now().isoformat()
            task_state["progress_percentage"] = progress_percentage
            task_state["progress_message"] = progress_message
            
            # Save the updated task state
            self.task_state_manager.update_task_state(subtask_id, task_state)
            
            # Log the progress update
            self._log_status_update(
                subtask_id, 
                "progress", 
                f"Progress: {progress_percentage}% - {progress_message}"
            )
            
            return {
                "success": True,
                "task_id": subtask_id,
                "status": "in_progress",
                "progress_percentage": progress_percentage,
                "task_state": task_state
            }
        
        except Exception as e:
            logger.error(f"Error reporting progress for task {subtask_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
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
        try:
            # Get the task state
            task_state = self.task_state_manager.get_task_state(subtask_id)
            if not task_state:
                return {
                    "success": False,
                    "error": f"Task not found: {subtask_id}"
                }
            
            # Update the task state
            task_state["status"] = "retry_requested"
            task_state["last_updated"] = datetime.now().isoformat()
            task_state["retry_reason"] = reason
            
            # Increment retry count
            retry_count = task_state.get("retry_count", 0)
            task_state["retry_count"] = retry_count + 1
            
            # Save the updated task state
            self.task_state_manager.update_task_state(subtask_id, task_state)
            
            # Log the retry request
            self._log_status_update(
                subtask_id, 
                "retry_requested", 
                f"Retry requested: {reason}"
            )
            
            return {
                "success": True,
                "task_id": subtask_id,
                "status": "retry_requested",
                "retry_count": task_state["retry_count"],
                "task_state": task_state
            }
        
        except Exception as e:
            logger.error(f"Error requesting retry for task {subtask_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_task_info(self, subtask_id: str) -> Dict[str, Any]:
        """
        Get information about a task.
        
        Args:
            subtask_id: ID of the subtask
            
        Returns:
            Task information
        """
        try:
            # Get the task state
            task_state = self.task_state_manager.get_task_state(subtask_id)
            if not task_state:
                return {
                    "success": False,
                    "error": f"Task not found: {subtask_id}"
                }
            
            return {
                "success": True,
                "task_id": subtask_id,
                "task_state": task_state
            }
        
        except Exception as e:
            logger.error(f"Error getting task info for {subtask_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_goal_progress(self, goal_id: str) -> Dict[str, Any]:
        """
        Get progress information for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Goal progress information
        """
        try:
            # Get all tasks for the goal
            tasks = self.task_state_manager.get_tasks_for_goal(goal_id)
            
            # Calculate progress statistics
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task.get("status") == "complete")
            failed_tasks = sum(1 for task in tasks if task.get("status") == "failed")
            blocked_tasks = sum(1 for task in tasks if task.get("status") == "blocked")
            in_progress_tasks = sum(1 for task in tasks if task.get("status") == "in_progress")
            pending_tasks = total_tasks - completed_tasks - failed_tasks - blocked_tasks - in_progress_tasks
            
            # Calculate overall progress percentage
            if total_tasks > 0:
                progress_percentage = (completed_tasks / total_tasks) * 100
            else:
                progress_percentage = 0
            
            return {
                "success": True,
                "goal_id": goal_id,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "blocked_tasks": blocked_tasks,
                "in_progress_tasks": in_progress_tasks,
                "pending_tasks": pending_tasks,
                "progress_percentage": progress_percentage,
                "tasks": tasks
            }
        
        except Exception as e:
            logger.error(f"Error getting goal progress for {goal_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _log_status_update(self, subtask_id: str, status: str, 
                          output_summary: str = "", 
                          error_message: str = "") -> None:
        """
        Log a status update to a file.
        
        Args:
            subtask_id: ID of the subtask
            status: New status
            output_summary: Optional summary of the output
            error_message: Optional error message
        """
        try:
            # Get the goal ID from the subtask ID
            goal_id = subtask_id.split("_")[0] if "_" in subtask_id else "unknown_goal"
            
            # Create the log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "subtask_id": subtask_id,
                "goal_id": goal_id,
                "status": status
            }
            
            if output_summary:
                log_entry["output_summary"] = output_summary
            
            if error_message:
                log_entry["error_message"] = error_message
            
            # Create the log file path
            log_file = os.path.join(self.logs_dir, f"{goal_id}_status.json")
            
            # Append to existing log or create new log file
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    logs = json.load(f)
                logs.append(log_entry)
            else:
                logs = [log_entry]
                
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
