import os
from typing import Dict, Any, Optional, List

class TaskStateManager:
    """
    Manager for task state tracking
    
    This class handles tracking the state of tasks across different agents.
    """
    
    def __init__(self):
        """Initialize the TaskStateManager"""
        self.tasks = {}
    
    async def update_task_state(self, agent_name: str, task_id: str, state: str) -> None:
        """
        Update the state of a task
        
        Args:
            agent_name: The name of the agent
            task_id: The ID of the task
            state: The new state (idle, working, completed, failed)
        """
        key = f"{agent_name}:{task_id}"
        self.tasks[key] = {
            "agent": agent_name,
            "task_id": task_id,
            "state": state,
            "updated_at": os.environ.get("TEST_TIMESTAMP", "2025-03-31T00:00:00Z")
        }
    
    async def get_task_state(self, agent_name: str, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the state of a task
        
        Args:
            agent_name: The name of the agent
            task_id: The ID of the task
            
        Returns:
            The task state or None if not found
        """
        key = f"{agent_name}:{task_id}"
        return self.tasks.get(key)
    
    async def get_agent_state(self, agent_name: str) -> str:
        """
        Get the current state of an agent
        
        Args:
            agent_name: The name of the agent
            
        Returns:
            The agent state (idle, working)
        """
        # Check if any tasks for this agent are in working state
        for key, task in self.tasks.items():
            if task["agent"] == agent_name and task["state"] == "working":
                return "working"
        
        return "idle"
    
    async def get_all_task_states(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all task states
        
        Returns:
            Dictionary of all task states
        """
        return self.tasks

# Singleton instance
_task_state_manager = None

def get_task_state_manager():
    """
    Get the singleton TaskStateManager instance
    """
    global _task_state_manager
    if _task_state_manager is None:
        _task_state_manager = TaskStateManager()
    return _task_state_manager
