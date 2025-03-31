import os
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class PendingTask(BaseModel):
    """Model for a pending task"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_description: str
    origin_agent: str
    suggested_agent: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    priority: bool = False
    status: str = "pending"  # pending, executed, cancelled
    metadata: Dict[str, Any] = Field(default_factory=dict)
    original_input: Optional[str] = None
    original_output: Optional[str] = None

class TaskPersistenceManager:
    """
    Manager for suggested task persistence
    
    This class handles storing and retrieving pending tasks that were suggested
    by agents but not automatically executed.
    """
    
    def __init__(self):
        """Initialize the TaskPersistenceManager"""
        # Set up storage directory
        self.tasks_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pending_tasks")
        os.makedirs(self.tasks_dir, exist_ok=True)
        
        # For testing purposes, keep an in-memory cache of tasks
        self.tasks_cache = {}
    
    async def store_pending_task(
        self,
        task_description: str,
        origin_agent: str,
        suggested_agent: str,
        priority: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        original_input: Optional[str] = None,
        original_output: Optional[str] = None
    ) -> str:
        """
        Store a pending task
        
        Args:
            task_description: Description of the task
            origin_agent: Agent that suggested the task
            suggested_agent: Agent that should execute the task
            priority: Whether this is a high priority task
            metadata: Optional metadata about the task
            original_input: Original input that led to this task suggestion
            original_output: Original output that contained this task suggestion
            
        Returns:
            The ID of the stored task
        """
        # Create task object
        task = PendingTask(
            task_description=task_description,
            origin_agent=origin_agent,
            suggested_agent=suggested_agent,
            priority=priority,
            metadata=metadata or {},
            original_input=original_input,
            original_output=original_output
        )
        
        # Use custom task_id from metadata if provided
        if metadata and "task_id" in metadata:
            task.task_id = metadata["task_id"]
        
        # Store in memory cache
        self.tasks_cache[task.task_id] = task.model_dump()
        
        try:
            # Store to file
            task_path = os.path.join(self.tasks_dir, f"{task.task_id}.json")
            with open(task_path, "w") as f:
                f.write(task.model_dump_json(indent=2))
        except Exception as e:
            print(f"Warning: Could not persist task to file: {e}")
            # Continue with in-memory version only
        
        return task.task_id
    
    async def get_pending_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a pending task by ID
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            The task data or None if not found
        """
        # Check in-memory cache first
        if task_id in self.tasks_cache:
            return self.tasks_cache[task_id]
            
        # Try to load from file
        task_path = os.path.join(self.tasks_dir, f"{task_id}.json")
        if os.path.exists(task_path):
            try:
                with open(task_path, "r") as f:
                    task_data = json.load(f)
                    # Update cache
                    self.tasks_cache[task_id] = task_data
                    return task_data
            except Exception as e:
                print(f"Error loading task {task_id}: {e}")
        
        return None
    
    async def get_pending_tasks(
        self,
        agent: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get pending tasks, optionally filtered by agent and status
        
        Args:
            agent: Optional agent to filter by
            status: Optional status to filter by
            limit: Maximum number of tasks to return
            
        Returns:
            List of task data
        """
        # Try to load from files first
        tasks = []
        try:
            for filename in os.listdir(self.tasks_dir):
                if not filename.endswith(".json"):
                    continue
                
                task_path = os.path.join(self.tasks_dir, filename)
                try:
                    with open(task_path, "r") as f:
                        task_data = json.load(f)
                        
                        # Update cache
                        self.tasks_cache[task_data["task_id"]] = task_data
                        
                        # Apply filters
                        if agent and task_data.get("suggested_agent") != agent:
                            continue
                        if status and task_data.get("status") != status:
                            continue
                        
                        tasks.append(task_data)
                except Exception as e:
                    print(f"Error loading task {filename}: {e}")
        except Exception as e:
            print(f"Error listing tasks directory: {e}")
            # Fall back to in-memory cache
        
        # If no files were found or there was an error, use the in-memory cache
        if not tasks:
            for task_id, task_data in self.tasks_cache.items():
                # Apply filters
                if agent and task_data.get("suggested_agent") != agent:
                    continue
                if status and task_data.get("status") != status:
                    continue
                
                tasks.append(task_data)
        
        # Sort by created_at (newest first) and apply limit
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return tasks[:limit]
    
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update the status of a task
        
        Args:
            task_id: The ID of the task to update
            status: The new status
            
        Returns:
            True if updated, False if not found
        """
        # Get the task
        task_data = await self.get_pending_task(task_id)
        if not task_data:
            return False
        
        # Update status
        task_data["status"] = status
        
        # Update in-memory cache
        self.tasks_cache[task_id] = task_data
        
        try:
            # Update file
            task_path = os.path.join(self.tasks_dir, f"{task_id}.json")
            with open(task_path, "w") as f:
                json.dump(task_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not persist task status update to file: {e}")
            # Continue with in-memory version only
        
        return True

# Singleton instance
_task_persistence_manager = None

def get_task_persistence_manager() -> TaskPersistenceManager:
    """
    Get the singleton TaskPersistenceManager instance
    """
    global _task_persistence_manager
    if _task_persistence_manager is None:
        _task_persistence_manager = TaskPersistenceManager()
    return _task_persistence_manager
