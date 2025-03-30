"""
Task State Manager for the Personal AI Agent System.

This module provides a comprehensive system for tracking task states across sessions,
enabling the Planner Agent to manage long-running goals, avoid repeating completed work,
and coordinate multi-agent workflows with parallel execution capabilities,
including dependency management and various task states.
"""

import os
import json
import uuid
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Set
from datetime import datetime
from dataclasses import dataclass, asdict, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskDependency:
    """Represents a dependency between tasks"""
    task_id: str
    dependent_task_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class TaskState:
    """Represents the state of a task"""
    task_id: str
    goal_id: str
    task_description: str
    status: str  # pending, in_progress, completed, failed, blocked
    priority: int
    assigned_agent: str
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

@dataclass
class GoalState:
    """Represents the state of a goal"""
    goal_id: str
    goal_description: str
    status: str  # pending, in_progress, completed, failed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

class TaskStateManager:
    """
    Manager for persistent task state tracking across sessions.
    
    This class provides CRUD operations for task states, memory integration,
    and logging support for multi-agent coordination with parallel execution
    and dependency management.
    """
    
    def __init__(self, vector_memory=None):
        """
        Initialize the task state manager.
        
        Args:
            vector_memory: Optional vector memory instance for persistent storage
        """
        self.vector_memory = vector_memory
        
        # Base directory for logs
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Create logs directory if it doesn't exist
        self.log_file = os.path.join(self.base_dir, "app", "core", "task_state_log.json")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Initialize in-memory state cache
        self.tasks: Dict[str, TaskState] = {}
        self.goals: Dict[str, GoalState] = {}
        self.dependencies: Dict[str, List[TaskDependency]] = {}
        
        # Load existing states from log file
        self._load_states_from_log()
    
    def _load_states_from_log(self):
        """Load existing task states from the log file into memory cache."""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    log_data = json.load(f)
                    
                    # Process goals
                    if "goal_id" in log_data:
                        # Single goal format
                        self._process_goal_from_log(log_data)
                    elif isinstance(log_data, dict) and "tasks" in log_data:
                        # New format with goal and tasks
                        self._process_goal_from_log(log_data)
                        for task_data in log_data.get("tasks", []):
                            self._process_task_from_log(task_data)
                    elif isinstance(log_data, list):
                        # List of entries format
                        for entry in log_data:
                            if "goal_id" in entry and "tasks" not in entry:
                                self._process_task_from_log(entry)
            
            logger.info(f"Loaded {len(self.tasks)} tasks and {len(self.goals)} goals from log file")
        
        except Exception as e:
            logger.error(f"Error loading task states from log file: {str(e)}")
    
    def _process_goal_from_log(self, data: Dict[str, Any]):
        """Process a goal entry from the log file."""
        if "goal_id" in data and "goal_description" in data:
            goal = GoalState(
                goal_id=data["goal_id"],
                goal_description=data["goal_description"],
                status=data.get("status", "pending"),
                created_at=data.get("created_at", datetime.now().isoformat()),
                updated_at=data.get("updated_at", datetime.now().isoformat()),
                completed_at=data.get("completed_at")
            )
            self.goals[goal.goal_id] = goal
    
    def _process_task_from_log(self, data: Dict[str, Any]):
        """Process a task entry from the log file."""
        if "task_id" in data and "goal_id" in data:
            task = TaskState(
                task_id=data["task_id"],
                goal_id=data["goal_id"],
                task_description=data["task_description"],
                status=data.get("status", "pending"),
                priority=data.get("priority", 3),
                assigned_agent=data.get("assigned_agent", ""),
                dependencies=data.get("dependencies", []),
                result=data.get("result"),
                error=data.get("error"),
                retry_count=data.get("retry_count", 0),
                max_retries=data.get("max_retries", 3),
                created_at=data.get("created_at", datetime.now().isoformat()),
                updated_at=data.get("updated_at", datetime.now().isoformat()),
                started_at=data.get("started_at"),
                completed_at=data.get("completed_at")
            )
            self.tasks[task.task_id] = task
            
            # Process dependencies
            for dep_id in task.dependencies:
                dep = TaskDependency(
                    task_id=dep_id,
                    dependent_task_id=task.task_id
                )
                if dep_id not in self.dependencies:
                    self.dependencies[dep_id] = []
                self.dependencies[dep_id].append(dep)
    
    async def create_goal(self, goal_id: str, goal_description: str) -> GoalState:
        """
        Create a new goal.
        
        Args:
            goal_id: Unique identifier for the goal
            goal_description: Description of the goal
            
        Returns:
            Newly created goal state
        """
        goal = GoalState(
            goal_id=goal_id,
            goal_description=goal_description,
            status="pending"
        )
        
        # Store in memory
        self.goals[goal_id] = goal
        
        # Log the creation
        await self._save_state_to_log()
        
        # Store in vector memory if available
        if self.vector_memory:
            self._store_in_memory(asdict(goal), "goal_state")
        
        return goal
    
    async def get_goal(self, goal_id: str) -> Optional[GoalState]:
        """
        Get a goal by ID.
        
        Args:
            goal_id: Unique identifier for the goal
            
        Returns:
            Goal state if found, None otherwise
        """
        return self.goals.get(goal_id)
    
    async def update_goal_status(self, goal_id: str, status: str) -> Optional[GoalState]:
        """
        Update a goal's status.
        
        Args:
            goal_id: Unique identifier for the goal
            status: New status for the goal
            
        Returns:
            Updated goal state if found, None otherwise
        """
        goal = await self.get_goal(goal_id)
        if not goal:
            logger.warning(f"Goal not found: {goal_id}")
            return None
        
        goal.status = status
        goal.updated_at = datetime.now().isoformat()
        
        if status == "completed":
            goal.completed_at = datetime.now().isoformat()
        
        # Save the updated state
        await self._save_state_to_log()
        
        # Store in vector memory if available
        if self.vector_memory:
            self._store_in_memory(asdict(goal), "goal_state")
        
        return goal
    
    async def create_task(self, task_id: str, goal_id: str, task_description: str, 
                         priority: int, assigned_agent: str, 
                         dependencies: List[str] = None) -> TaskState:
        """
        Create a new task.
        
        Args:
            task_id: Unique identifier for the task
            goal_id: ID of the parent goal
            task_description: Description of the task
            priority: Priority level (1-5, with 5 being highest)
            assigned_agent: Name of the assigned agent
            dependencies: List of task IDs that this task depends on
            
        Returns:
            Newly created task state
        """
        if dependencies is None:
            dependencies = []
        
        task = TaskState(
            task_id=task_id,
            goal_id=goal_id,
            task_description=task_description,
            status="pending" if not dependencies else "blocked",
            priority=priority,
            assigned_agent=assigned_agent,
            dependencies=dependencies
        )
        
        # Store in memory
        self.tasks[task_id] = task
        
        # Process dependencies
        for dep_id in dependencies:
            dep = TaskDependency(
                task_id=dep_id,
                dependent_task_id=task_id
            )
            if dep_id not in self.dependencies:
                self.dependencies[dep_id] = []
            self.dependencies[dep_id].append(dep)
        
        # Log the creation
        await self._save_state_to_log()
        
        # Store in vector memory if available
        if self.vector_memory:
            self._store_in_memory(asdict(task), "task_state")
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[TaskState]:
        """
        Get a task by ID.
        
        Args:
            task_id: Unique identifier for the task
            
        Returns:
            Task state if found, None otherwise
        """
        return self.tasks.get(task_id)
    
    async def get_goal_tasks(self, goal_id: str) -> List[TaskState]:
        """
        Get all tasks for a goal.
        
        Args:
            goal_id: Unique identifier for the goal
            
        Returns:
            List of task states for the goal
        """
        return [task for task in self.tasks.values() if task.goal_id == goal_id]
    
    async def get_available_tasks(self, goal_id: str) -> List[TaskState]:
        """
        Get all available tasks for a goal (those with all dependencies satisfied).
        
        Args:
            goal_id: Unique identifier for the goal
            
        Returns:
            List of available task states for the goal
        """
        available_tasks = []
        
        for task in self.tasks.values():
            if task.goal_id != goal_id:
                continue
                
            if task.status != "pending" and task.status != "blocked":
                continue
                
            # Check if all dependencies are completed
            all_dependencies_completed = True
            for dep_id in task.dependencies:
                dep_task = await self.get_task(dep_id)
                if not dep_task or dep_task.status != "completed":
                    all_dependencies_completed = False
                    break
            
            if all_dependencies_completed:
                if task.status == "blocked":
                    # Update status to pending since dependencies are now satisfied
                    task.status = "pending"
                    task.updated_at = datetime.now().isoformat()
                    await self._save_state_to_log()
                
                available_tasks.append(task)
        
        # Sort by priority (highest first)
        available_tasks.sort(key=lambda t: t.priority, reverse=True)
        
        return available_tasks
    
    async def update_task_status(self, task_id: str, status: str, 
                               result: Dict[str, Any] = None, 
                               error: str = None) -> Optional[TaskState]:
        """
        Update a task's status.
        
        Args:
            task_id: Unique identifier for the task
            status: New status for the task
            result: Optional result data for completed tasks
            error: Optional error message for failed tasks
            
        Returns:
            Updated task state if found, None otherwise
        """
        task = await self.get_task(task_id)
        if not task:
            logger.warning(f"Task not found: {task_id}")
            return None
        
        old_status = task.status
        task.status = status
        task.updated_at = datetime.now().isoformat()
        
        if status == "in_progress" and not task.started_at:
            task.started_at = datetime.now().isoformat()
        
        if status == "completed":
            task.completed_at = datetime.now().isoformat()
            if result:
                task.result = result
            
            # Unblock dependent tasks
            await self._unblock_dependent_tasks(task_id)
        
        if status == "failed":
            if error:
                task.error = error
            
            # Increment retry count
            task.retry_count += 1
            
            # If retries not exhausted, set back to pending
            if task.retry_count < task.max_retries:
                task.status = "pending"
        
        # Save the updated state
        await self._save_state_to_log()
        
        # Store in vector memory if available
        if self.vector_memory:
            self._store_in_memory(asdict(task), "task_state")
        
        # Log status change
        logger.info(f"Task {task_id} status changed from {old_status} to {status}")
        
        return task
    
    async def _unblock_dependent_tasks(self, task_id: str):
        """
        Unblock tasks that depend on the specified task.
        
        Args:
            task_id: ID of the task that was completed
        """
        if task_id not in self.dependencies:
            return
        
        for dep in self.dependencies[task_id]:
            dependent_task = await self.get_task(dep.dependent_task_id)
            if dependent_task and dependent_task.status == "blocked":
                # Check if all dependencies are now completed
                all_completed = True
                for dep_id in dependent_task.dependencies:
                    dep_task = await self.get_task(dep_id)
                    if not dep_task or dep_task.status != "completed":
                        all_completed = False
                        break
                
                if all_completed:
                    dependent_task.status = "pending"
                    dependent_task.updated_at = datetime.now().isoformat()
                    logger.info(f"Unblocked task {dependent_task.task_id} after dependency {task_id} was completed")
    
    async def _save_state_to_log(self):
        """Save the current state to the log file."""
        try:
            # Prepare data structure
            log_data = {}
            
            # Add goal information if available
            if self.goals:
                # Use the first goal for now (assuming single goal context)
                goal = next(iter(self.goals.values()))
                log_data.update(asdict(goal))
            
            # Add tasks
            log_data["tasks"] = [asdict(task) for task in self.tasks.values()]
            
            # Write to file
            with open(self.log_file, "w") as f:
                json.dump(log_data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error saving state to log file: {str(e)}")
    
    def _store_in_memory(self, data: Dict[str, Any], data_type: str):
        """
        Store data in vector memory.
        
        Args:
            data: Data to store
            data_type: Type of data (e.g., "task_state", "goal_state")
        """
        if not self.vector_memory:
            return
        
        try:
            # Convert data to string
            data_str = json.dumps(data)
            
            # Store in vector memory
            self.vector_memory.add(
                text=data_str,
                metadata={
                    "type": data_type,
                    "id": data.get("task_id") or data.get("goal_id"),
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            logger.error(f"Error storing data in vector memory: {str(e)}")

# Singleton instance
_task_state_manager = None

def get_task_state_manager() -> TaskStateManager:
    """
    Get the singleton instance of the TaskStateManager.
    
    Returns:
        TaskStateManager instance
    """
    global _task_state_manager
    if _task_state_manager is None:
        _task_state_manager = TaskStateManager()
    return _task_state_manager
