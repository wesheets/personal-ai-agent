"""
Task State Manager for persistent memory-driven state management.

This module provides a comprehensive system for tracking task states across sessions,
enabling the Planner Agent to manage long-running goals, avoid repeating completed work,
and coordinate multi-agent workflows.
"""

import os
import json
import uuid
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStateManager:
    """
    Manager for persistent task state tracking across sessions.
    
    This class provides CRUD operations for task states, memory integration,
    and logging support for multi-agent coordination.
    """
    
    def __init__(self, vector_memory=None):
        """
        Initialize the task state manager.
        
        Args:
            vector_memory: Optional vector memory instance for persistent storage
        """
        self.vector_memory = vector_memory
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname("/app/logs/task_state_log.json"), exist_ok=True)
        
        # Initialize in-memory state cache
        self.state_cache = {}
        
        # Load existing states from log file
        self._load_states_from_log()
    
    def _load_states_from_log(self):
        """Load existing task states from the log file into memory cache."""
        try:
            log_file = "/app/logs/task_state_log.json"
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    logs = json.load(f)
                    
                    # Process logs to build state cache
                    for log_entry in logs:
                        if "task_state" in log_entry:
                            task_state = log_entry["task_state"]
                            subtask_id = task_state.get("subtask_id")
                            if subtask_id:
                                self.state_cache[subtask_id] = task_state
            
            logger.info(f"Loaded {len(self.state_cache)} task states from log file")
        
        except Exception as e:
            logger.error(f"Error loading task states from log file: {str(e)}")
    
    def create_task_state(self, 
                         goal_id: str, 
                         subtask_id: str, 
                         subtask_description: str, 
                         assigned_agent: str) -> Dict[str, Any]:
        """
        Create a new task state.
        
        Args:
            goal_id: ID of the parent goal
            subtask_id: ID of the subtask
            subtask_description: Description of the subtask
            assigned_agent: Name of the assigned agent
            
        Returns:
            Newly created task state
        """
        # Create the task state
        task_state = {
            "goal_id": goal_id,
            "subtask_id": subtask_id,
            "subtask_description": subtask_description,
            "assigned_agent": assigned_agent,
            "status": "queued",
            "last_update": datetime.now().isoformat(),
            "output_summary": "",
            "error_message": "",
            "retry_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        # Store in cache
        self.state_cache[subtask_id] = task_state
        
        # Log the creation
        self._log_state_change(task_state, "task_created", "Task state created")
        
        # Store in vector memory if available
        if self.vector_memory:
            self._store_in_memory(task_state)
        
        return task_state
    
    def get_task_state(self, subtask_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task state by subtask ID.
        
        Args:
            subtask_id: ID of the subtask
            
        Returns:
            Task state if found, None otherwise
        """
        # Check cache first
        if subtask_id in self.state_cache:
            return self.state_cache[subtask_id]
        
        # If not in cache, try to retrieve from vector memory
        if self.vector_memory:
            try:
                # Search for the task state in vector memory
                query = f"subtask_id:{subtask_id}"
                results = self.vector_memory.search(
                    query=query,
                    metadata_filter={"type": "task_state"},
                    limit=1
                )
                
                if results and len(results) > 0:
                    # Parse the task state from the result
                    task_state = json.loads(results[0]["text"])
                    
                    # Update cache
                    self.state_cache[subtask_id] = task_state
                    
                    return task_state
            
            except Exception as e:
                logger.error(f"Error retrieving task state from vector memory: {str(e)}")
        
        return None
    
    def update_task_state(self, 
                         subtask_id: str, 
                         updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a task state.
        
        Args:
            subtask_id: ID of the subtask
            updates: Dictionary of fields to update
            
        Returns:
            Updated task state if found, None otherwise
        """
        # Get the current state
        task_state = self.get_task_state(subtask_id)
        
        if not task_state:
            logger.warning(f"Task state not found for subtask ID: {subtask_id}")
            return None
        
        # Update the state
        for key, value in updates.items():
            if key in task_state:
                task_state[key] = value
        
        # Always update the last_update timestamp
        task_state["last_update"] = datetime.now().isoformat()
        
        # Store in cache
        self.state_cache[subtask_id] = task_state
        
        # Log the update
        self._log_state_change(task_state, "task_updated", f"Task state updated: {', '.join(updates.keys())}")
        
        # Store in vector memory if available
        if self.vector_memory:
            self._store_in_memory(task_state)
        
        return task_state
    
    def update_task_status(self, 
                          subtask_id: str, 
                          status: str, 
                          output_summary: str = "", 
                          error_message: str = "") -> Optional[Dict[str, Any]]:
        """
        Update a task status.
        
        Args:
            subtask_id: ID of the subtask
            status: New status (queued, in_progress, complete, failed)
            output_summary: Optional summary of the output
            error_message: Optional error message if status is failed
            
        Returns:
            Updated task state if found, None otherwise
        """
        # Validate status
        valid_statuses = ["queued", "in_progress", "complete", "failed", "blocked"]
        if status not in valid_statuses:
            logger.error(f"Invalid status: {status}. Must be one of {valid_statuses}")
            return None
        
        # Prepare updates
        updates = {"status": status}
        
        if output_summary:
            updates["output_summary"] = output_summary
        
        if error_message:
            updates["error_message"] = error_message
        
        # If status is failed, increment retry count
        if status == "failed":
            task_state = self.get_task_state(subtask_id)
            if task_state:
                retry_count = task_state.get("retry_count", 0) + 1
                updates["retry_count"] = retry_count
        
        # Update the state
        return self.update_task_state(subtask_id, updates)
    
    def get_goal_tasks(self, goal_id: str) -> List[Dict[str, Any]]:
        """
        Get all task states for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            List of task states for the goal
        """
        # First check cache
        goal_tasks = [
            task for task in self.state_cache.values() 
            if task.get("goal_id") == goal_id
        ]
        
        # If no tasks found in cache and vector memory is available, search there
        if not goal_tasks and self.vector_memory:
            try:
                # Search for task states in vector memory
                query = f"goal_id:{goal_id}"
                results = self.vector_memory.search(
                    query=query,
                    metadata_filter={"type": "task_state"},
                    limit=100
                )
                
                if results:
                    # Parse task states from results
                    for result in results:
                        task_state = json.loads(result["text"])
                        subtask_id = task_state.get("subtask_id")
                        
                        if subtask_id and subtask_id not in self.state_cache:
                            self.state_cache[subtask_id] = task_state
                            goal_tasks.append(task_state)
            
            except Exception as e:
                logger.error(f"Error retrieving goal tasks from vector memory: {str(e)}")
        
        return goal_tasks
    
    def get_agent_tasks(self, agent_name: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all task states assigned to an agent.
        
        Args:
            agent_name: Name of the agent
            status: Optional status filter
            
        Returns:
            List of task states assigned to the agent
        """
        # Filter tasks from cache
        agent_tasks = [
            task for task in self.state_cache.values() 
            if task.get("assigned_agent") == agent_name and
            (status is None or task.get("status") == status)
        ]
        
        # If vector memory is available, search there as well
        if self.vector_memory:
            try:
                # Search for task states in vector memory
                query = f"assigned_agent:{agent_name}"
                if status:
                    query += f" status:{status}"
                
                results = self.vector_memory.search(
                    query=query,
                    metadata_filter={"type": "task_state"},
                    limit=100
                )
                
                if results:
                    # Parse task states from results
                    for result in results:
                        task_state = json.loads(result["text"])
                        subtask_id = task_state.get("subtask_id")
                        
                        if subtask_id and subtask_id not in self.state_cache:
                            self.state_cache[subtask_id] = task_state
                            agent_tasks.append(task_state)
            
            except Exception as e:
                logger.error(f"Error retrieving agent tasks from vector memory: {str(e)}")
        
        return agent_tasks
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get all task states with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of task states with the specified status
        """
        # Filter tasks from cache
        status_tasks = [
            task for task in self.state_cache.values() 
            if task.get("status") == status
        ]
        
        # If vector memory is available, search there as well
        if self.vector_memory:
            try:
                # Search for task states in vector memory
                query = f"status:{status}"
                results = self.vector_memory.search(
                    query=query,
                    metadata_filter={"type": "task_state"},
                    limit=100
                )
                
                if results:
                    # Parse task states from results
                    for result in results:
                        task_state = json.loads(result["text"])
                        subtask_id = task_state.get("subtask_id")
                        
                        if subtask_id and subtask_id not in self.state_cache:
                            self.state_cache[subtask_id] = task_state
                            status_tasks.append(task_state)
            
            except Exception as e:
                logger.error(f"Error retrieving tasks by status from vector memory: {str(e)}")
        
        return status_tasks
    
    def get_stalled_tasks(self, hours_threshold: int = 24) -> List[Dict[str, Any]]:
        """
        Get all task states that have been stalled for a certain period.
        
        Args:
            hours_threshold: Number of hours to consider a task stalled
            
        Returns:
            List of stalled task states
        """
        now = datetime.now()
        stalled_tasks = []
        
        for task in self.state_cache.values():
            # Skip completed tasks
            if task.get("status") == "complete":
                continue
            
            # Check if the task is stalled
            last_update_str = task.get("last_update", "")
            if last_update_str:
                try:
                    last_update = datetime.fromisoformat(last_update_str)
                    hours_diff = (now - last_update).total_seconds() / 3600
                    
                    if hours_diff >= hours_threshold:
                        stalled_tasks.append(task)
                
                except Exception as e:
                    logger.error(f"Error parsing last_update timestamp: {str(e)}")
        
        return stalled_tasks
    
    def get_failed_tasks_for_retry(self, max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        Get all failed task states that are eligible for retry.
        
        Args:
            max_retries: Maximum number of retries allowed
            
        Returns:
            List of failed task states eligible for retry
        """
        # Filter tasks from cache
        retry_tasks = [
            task for task in self.state_cache.values() 
            if task.get("status") == "failed" and
            task.get("retry_count", 0) < max_retries
        ]
        
        return retry_tasks
    
    def clear_completed_tasks(self, goal_id: str) -> int:
        """
        Clear completed tasks for a goal from the cache.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Number of tasks cleared
        """
        # Find completed tasks for the goal
        completed_tasks = [
            task for task in self.state_cache.values() 
            if task.get("goal_id") == goal_id and
            task.get("status") == "complete"
        ]
        
        # Remove from cache
        for task in completed_tasks:
            subtask_id = task.get("subtask_id")
            if subtask_id in self.state_cache:
                del self.state_cache[subtask_id]
        
        return len(completed_tasks)
    
    def _log_state_change(self, task_state: Dict[str, Any], event_type: str, message: str) -> None:
        """
        Log a task state change to the task_state_log.json file.
        
        Args:
            task_state: Task state
            event_type: Type of event
            message: Event message
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "task_state": task_state
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
            logger.error(f"Error logging task state change: {str(e)}")
    
    def _store_in_memory(self, task_state: Dict[str, Any]) -> None:
        """
        Store a task state in vector memory.
        
        Args:
            task_state: Task state to store
        """
        if not self.vector_memory:
            return
        
        try:
            # Prepare metadata
            metadata = {
                "type": "task_state",
                "goal_id": task_state.get("goal_id", ""),
                "subtask_id": task_state.get("subtask_id", ""),
                "assigned_agent": task_state.get("assigned_agent", ""),
                "status": task_state.get("status", ""),
                "last_update": task_state.get("last_update", "")
            }
            
            # Store in vector memory
            self.vector_memory.add_memory(
                text=json.dumps(task_state),
                metadata=metadata
            )
        
        except Exception as e:
            logger.error(f"Error storing task state in vector memory: {str(e)}")
    
    def get_goal_progress(self, goal_id: str) -> Dict[str, Any]:
        """
        Get progress statistics for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Progress statistics
        """
        # Get all tasks for the goal
        goal_tasks = self.get_goal_tasks(goal_id)
        
        if not goal_tasks:
            return {
                "goal_id": goal_id,
                "total_tasks": 0,
                "completed": 0,
                "in_progress": 0,
                "queued": 0,
                "failed": 0,
                "blocked": 0,
                "completion_percentage": 0,
                "status": "unknown"
            }
        
        # Count tasks by status
        total = len(goal_tasks)
        completed = sum(1 for task in goal_tasks if task.get("status") == "complete")
        in_progress = sum(1 for task in goal_tasks if task.get("status") == "in_progress")
        queued = sum(1 for task in goal_tasks if task.get("status") == "queued")
        failed = sum(1 for task in goal_tasks if task.get("status") == "failed")
        blocked = sum(1 for task in goal_tasks if task.get("status") == "blocked")
        
        # Calculate completion percentage
        completion_percentage = (completed / total) * 100 if total > 0 else 0
        
        # Determine overall status
        if completed == total:
            status = "complete"
        elif failed > 0:
            status = "has_failures"
        elif blocked > 0:
            status = "blocked"
        elif in_progress > 0:
            status = "in_progress"
        elif queued > 0:
            status = "queued"
        else:
            status = "unknown"
        
        return {
            "goal_id": goal_id,
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "queued": queued,
            "failed": failed,
            "blocked": blocked,
            "completion_percentage": completion_percentage,
            "status": status
        }

# Create a singleton instance
_task_state_manager = None

def get_task_state_manager(vector_memory=None) -> TaskStateManager:
    """
    Get the singleton instance of the task state manager.
    
    Args:
        vector_memory: Optional vector memory instance for persistent storage
        
    Returns:
        TaskStateManager instance
    """
    global _task_state_manager
    if _task_state_manager is None:
        _task_state_manager = TaskStateManager(vector_memory)
    return _task_state_manager

# For testing purposes
if __name__ == "__main__":
    # Test the task state manager
    manager = TaskStateManager()
    
    # Create a test task state
    goal_id = str(uuid.uuid4())
    subtask_id = f"{goal_id}_subtask_1"
    
    task_state = manager.create_task_state(
        goal_id=goal_id,
        subtask_id=subtask_id,
        subtask_description="Test subtask",
        assigned_agent="builder"
    )
    
    print(f"Created task state: {task_state}")
    
    # Update the task status
    updated_state = manager.update_task_status(
        subtask_id=subtask_id,
        status="in_progress"
    )
    
    print(f"Updated task state: {updated_state}")
    
    # Get the task state
    retrieved_state = manager.get_task_state(subtask_id)
    
    print(f"Retrieved task state: {retrieved_state}")
    
    # Get goal progress
    progress = manager.get_goal_progress(goal_id)
    
    print(f"Goal progress: {progress}")
