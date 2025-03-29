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
            suggested_agent: Agent suggested to handle the task
            priority: Whether the task is high priority
            metadata: Additional metadata for the task
            original_input: Original input that led to this task suggestion
            original_output: Original output that contained the task suggestion
            
        Returns:
            ID of the stored task
        """
        # Create the task
        task = PendingTask(
            task_description=task_description,
            origin_agent=origin_agent,
            suggested_agent=suggested_agent,
            priority=priority,
            metadata=metadata or {},
            original_input=original_input,
            original_output=original_output
        )
        
        # Store the task
        task_file = os.path.join(self.tasks_dir, f"{task.task_id}.json")
        with open(task_file, "w") as f:
            json.dump(task.dict(), f, indent=2)
        
        return task.task_id
    
    async def get_pending_tasks(
        self,
        limit: int = 10,
        offset: int = 0,
        origin_agent: Optional[str] = None,
        suggested_agent: Optional[str] = None,
        status: str = "pending"
    ) -> List[PendingTask]:
        """
        Get pending tasks
        
        Args:
            limit: Maximum number of tasks to return
            offset: Offset for pagination
            origin_agent: Filter by origin agent
            suggested_agent: Filter by suggested agent
            status: Filter by status (pending, executed, cancelled)
            
        Returns:
            List of pending tasks
        """
        # Get all task files
        task_files = [f for f in os.listdir(self.tasks_dir) if f.endswith(".json")]
        
        # Load all tasks
        tasks = []
        for task_file in task_files:
            with open(os.path.join(self.tasks_dir, task_file), "r") as f:
                task_data = json.load(f)
                task = PendingTask(**task_data)
                
                # Apply filters
                if status and task.status != status:
                    continue
                
                if origin_agent and task.origin_agent != origin_agent:
                    continue
                
                if suggested_agent and task.suggested_agent != suggested_agent:
                    continue
                
                tasks.append(task)
        
        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Apply pagination
        tasks = tasks[offset:offset + limit]
        
        return tasks
    
    async def get_task(self, task_id: str) -> Optional[PendingTask]:
        """
        Get a specific task by ID
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task if found, None otherwise
        """
        task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
        
        if not os.path.exists(task_file):
            return None
        
        with open(task_file, "r") as f:
            task_data = json.load(f)
            return PendingTask(**task_data)
    
    async def update_task_status(
        self,
        task_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[PendingTask]:
        """
        Update the status of a task
        
        Args:
            task_id: ID of the task
            status: New status (pending, executed, cancelled)
            metadata: Additional metadata to update
            
        Returns:
            Updated task if found, None otherwise
        """
        task = await self.get_task(task_id)
        
        if not task:
            return None
        
        # Update the task
        task.status = status
        
        if metadata:
            task.metadata.update(metadata)
        
        # Store the updated task
        task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
        with open(task_file, "w") as f:
            json.dump(task.dict(), f, indent=2)
        
        return task
    
    async def execute_task(
        self,
        task_id: str,
        background_tasks=None,
        db=None,
        supabase_client=None
    ) -> Dict[str, Any]:
        """
        Execute a pending task
        
        Args:
            task_id: ID of the task to execute
            background_tasks: FastAPI background tasks
            db: Database connection
            supabase_client: Supabase client
            
        Returns:
            Result of the task execution
        """
        # Get the task
        task = await self.get_task(task_id)
        
        if not task:
            return {"error": f"Task not found: {task_id}"}
        
        if task.status != "pending":
            return {"error": f"Task is not pending: {task_id}", "status": task.status}
        
        try:
            # Import here to avoid circular imports
            from app.api.agent import AgentRequest, process_agent_request
            
            # Create a request for the suggested agent
            request = AgentRequest(
                input=task.task_description,
                context={
                    "origin_agent": task.origin_agent,
                    "original_input": task.original_input,
                    "original_output": task.original_output,
                    "is_pending_task": True,
                    "task_id": task.task_id,
                    **task.metadata
                },
                save_to_memory=True
            )
            
            # Process the request
            response = await process_agent_request(
                agent_type=task.suggested_agent,
                request=request,
                background_tasks=background_tasks,
                db=db,
                supabase_client=supabase_client
            )
            
            # Update the task status
            await self.update_task_status(
                task_id=task_id,
                status="executed",
                metadata={
                    "execution_timestamp": datetime.now().isoformat(),
                    "execution_result": {
                        "output": response.output,
                        "metadata": response.metadata,
                        "reflection": response.reflection
                    }
                }
            )
            
            # Return the response
            return {
                "task_id": task_id,
                "status": "executed",
                "result": {
                    "output": response.output,
                    "metadata": response.metadata,
                    "reflection": response.reflection
                }
            }
            
        except Exception as e:
            # Update the task status to reflect the error
            await self.update_task_status(
                task_id=task_id,
                status="error",
                metadata={
                    "execution_timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }
            )
            
            # Return the error
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }

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
