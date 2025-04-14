"""
Agent Coordinator for the Personal AI Agent System.

This module provides functionality to coordinate multiple agents working on subtasks
in parallel, handling assignment, monitoring, and escalation.
"""

import os
import json
import uuid
import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.task_state_manager import get_task_state_manager, TaskState, GoalState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentAssignment(BaseModel):
    """Model for an agent assignment"""
    agent_id: str
    agent_type: str
    task_id: str
    assigned_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str = "assigned"  # assigned, working, completed, failed

class AgentCoordinator:
    """
    Coordinator for multiple agents working on subtasks in parallel.
    
    This class handles:
    - Assigning subtasks to available agents based on type
    - Monitoring progress of all subtasks
    - Handling retries and escalation logic per task
    - Finalizing task when all subtasks are resolved
    """
    
    def __init__(self):
        """Initialize the AgentCoordinator"""
        self.task_state_manager = get_task_state_manager()
        
        # Set up logging directory
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                    "logs", "execution_logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # In-memory tracking of agent assignments
        self._agent_assignments: Dict[str, AgentAssignment] = {}
        
        # Agent type capabilities
        self._agent_capabilities = {
            "builder": ["code", "development", "implementation"],
            "researcher": ["research", "analysis", "data"],
            "planner": ["planning", "coordination", "strategy"],
            "ops": ["operations", "deployment", "infrastructure"],
            "memory": ["retrieval", "storage", "context"]
        }
    
    async def assign_task(self, task_id: str) -> Optional[AgentAssignment]:
        """
        Assign a task to an appropriate agent
        
        Args:
            task_id: ID of the task to assign
            
        Returns:
            The agent assignment if successful, None otherwise
        """
        # Get the task
        task = await self.task_state_manager.get_task(task_id)
        if not task:
            logger.error(f"Task not found: {task_id}")
            return None
        
        # If task already has an assigned agent, use that
        if task.assigned_agent:
            agent_id = f"{task.assigned_agent}_{uuid.uuid4().hex[:8]}"
            assignment = AgentAssignment(
                agent_id=agent_id,
                agent_type=task.assigned_agent,
                task_id=task_id
            )
            self._agent_assignments[agent_id] = assignment
            
            # Log the assignment
            logger.info(f"Task {task_id} assigned to pre-specified agent: {task.assigned_agent}")
            self._log_coordination_event("task_assigned", {
                "task_id": task_id,
                "agent_id": agent_id,
                "agent_type": task.assigned_agent
            })
            
            return assignment
        
        # Determine the best agent type for this task
        agent_type = await self._determine_agent_type(task)
        
        # Create a new agent assignment
        agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        assignment = AgentAssignment(
            agent_id=agent_id,
            agent_type=agent_type,
            task_id=task_id
        )
        self._agent_assignments[agent_id] = assignment
        
        # Update the task with the assigned agent
        await self.task_state_manager.update_task_status(
            task_id=task_id,
            status=task.status,  # Keep the current status
            metadata={"assigned_agent": agent_type}
        )
        
        # Log the assignment
        logger.info(f"Task {task_id} assigned to agent: {agent_type}")
        self._log_coordination_event("task_assigned", {
            "task_id": task_id,
            "agent_id": agent_id,
            "agent_type": agent_type
        })
        
        return assignment
    
    async def monitor_task_progress(self, task_id: str) -> Dict[str, Any]:
        """
        Monitor the progress of a task
        
        Args:
            task_id: ID of the task to monitor
            
        Returns:
            Task progress information
        """
        # Get the task
        task = await self.task_state_manager.get_task(task_id)
        if not task:
            return {"error": f"Task not found: {task_id}"}
        
        # Get the agent assignment
        agent_assignment = None
        for assignment in self._agent_assignments.values():
            if assignment.task_id == task_id:
                agent_assignment = assignment
                break
        
        # Return progress information
        return {
            "task_id": task_id,
            "status": task.status,
            "progress": {
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at
            },
            "agent": {
                "agent_id": agent_assignment.agent_id if agent_assignment else None,
                "agent_type": agent_assignment.agent_type if agent_assignment else task.assigned_agent,
                "status": agent_assignment.status if agent_assignment else None
            } if agent_assignment or task.assigned_agent else None,
            "result": task.result,
            "error": task.error,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries
        }
    
    async def handle_task_completion(self, task_id: str, result: Dict[str, Any]) -> bool:
        """
        Handle the completion of a task
        
        Args:
            task_id: ID of the completed task
            result: Result of the task
            
        Returns:
            True if successful, False otherwise
        """
        # Get the task
        task = await self.task_state_manager.get_task(task_id)
        if not task:
            logger.error(f"Task not found: {task_id}")
            return False
        
        # Update the task status
        updated_task = await self.task_state_manager.update_task_status(
            task_id=task_id,
            status="completed",
            result=result
        )
        
        if not updated_task:
            logger.error(f"Failed to update task status: {task_id}")
            return False
        
        # Update the agent assignment
        for agent_id, assignment in self._agent_assignments.items():
            if assignment.task_id == task_id:
                assignment.status = "completed"
                
                # Log the completion
                logger.info(f"Task {task_id} completed by agent: {assignment.agent_type}")
                self._log_coordination_event("task_completed", {
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "agent_type": assignment.agent_type,
                    "result": result
                })
                
                break
        
        return True
    
    async def handle_task_failure(self, task_id: str, error: str) -> bool:
        """
        Handle the failure of a task
        
        Args:
            task_id: ID of the failed task
            error: Error message
            
        Returns:
            True if successful, False otherwise
        """
        # Get the task
        task = await self.task_state_manager.get_task(task_id)
        if not task:
            logger.error(f"Task not found: {task_id}")
            return False
        
        # Check if we should retry
        if task.retry_count < task.max_retries:
            # Retry the task
            retried_task = await self.task_state_manager.retry_task(task_id)
            
            if not retried_task:
                logger.error(f"Failed to retry task: {task_id}")
                return False
            
            # Log the retry
            logger.info(f"Task {task_id} failed, retrying (attempt {retried_task.retry_count}/{retried_task.max_retries})")
            self._log_coordination_event("task_retry", {
                "task_id": task_id,
                "retry_count": retried_task.retry_count,
                "max_retries": retried_task.max_retries,
                "error": error
            })
            
            # Update the agent assignment
            for agent_id, assignment in self._agent_assignments.items():
                if assignment.task_id == task_id:
                    # Remove the old assignment
                    del self._agent_assignments[agent_id]
                    break
            
            # Create a new assignment
            await self.assign_task(task_id)
            
            return True
        else:
            # Mark the task as failed
            updated_task = await self.task_state_manager.update_task_status(
                task_id=task_id,
                status="failed",
                error=error
            )
            
            if not updated_task:
                logger.error(f"Failed to update task status: {task_id}")
                return False
            
            # Update the agent assignment
            for agent_id, assignment in self._agent_assignments.items():
                if assignment.task_id == task_id:
                    assignment.status = "failed"
                    
                    # Log the failure
                    logger.info(f"Task {task_id} failed permanently after {task.retry_count} retries")
                    self._log_coordination_event("task_failed", {
                        "task_id": task_id,
                        "agent_id": agent_id,
                        "agent_type": assignment.agent_type,
                        "error": error,
                        "retry_count": task.retry_count,
                        "max_retries": task.max_retries
                    })
                    
                    break
            
            # Check if this failure should trigger escalation
            await self._check_for_escalation(task)
            
            return True
    
    async def finalize_goal(self, goal_id: str) -> Dict[str, Any]:
        """
        Finalize a goal when all subtasks are resolved
        
        Args:
            goal_id: ID of the goal to finalize
            
        Returns:
            Goal finalization information
        """
        # Get the goal
        goal = await self.task_state_manager.get_goal(goal_id)
        if not goal:
            return {"error": f"Goal not found: {goal_id}"}
        
        # Get all tasks for this goal
        tasks = await self.task_state_manager.get_goal_tasks(goal_id)
        
        # Check if all tasks are resolved (completed or failed)
        all_resolved = all(task.status in ["completed", "failed"] for task in tasks)
        all_completed = all(task.status == "completed" for task in tasks)
        
        if not all_resolved:
            return {
                "goal_id": goal_id,
                "status": "in_progress",
                "message": "Not all tasks are resolved yet"
            }
        
        # Update the goal status if needed
        if goal.status != "completed" and all_completed:
            goal.status = "completed"
            goal.completed_at = datetime.now().isoformat()
            await self.task_state_manager._save_goal(goal)
            
            # Log the completion
            logger.info(f"Goal {goal_id} completed successfully")
            self._log_coordination_event("goal_completed", {
                "goal_id": goal_id,
                "goal_description": goal.goal_description,
                "task_count": len(tasks)
            })
        elif goal.status != "failed" and not all_completed:
            goal.status = "failed"
            await self.task_state_manager._save_goal(goal)
            
            # Log the failure
            logger.info(f"Goal {goal_id} failed due to task failures")
            self._log_coordination_event("goal_failed", {
                "goal_id": goal_id,
                "goal_description": goal.goal_description,
                "task_count": len(tasks),
                "failed_tasks": [task.task_id for task in tasks if task.status == "failed"]
            })
        
        # Compile results
        results = {
            "goal_id": goal_id,
            "status": goal.status,
            "created_at": goal.created_at,
            "completed_at": goal.completed_at,
            "tasks": {
                "total": len(tasks),
                "completed": sum(1 for task in tasks if task.status == "completed"),
                "failed": sum(1 for task in tasks if task.status == "failed")
            },
            "task_results": {
                task.task_id: {
                    "description": task.task_description,
                    "status": task.status,
                    "agent": task.assigned_agent,
                    "result": task.result,
                    "error": task.error
                } for task in tasks
            }
        }
        
        # Update the goal progress log
        await self.task_state_manager._update_goal_progress_log(goal_id)
        
        return results
    
    async def _determine_agent_type(self, task: TaskState) -> str:
        """
        Determine the best agent type for a task
        
        Args:
            task: The task to assign
            
        Returns:
            The best agent type
        """
        # Check task metadata for hints
        if "preferred_agent" in task.metadata:
            return task.metadata["preferred_agent"]
        
        if "task_category" in task.metadata:
            category = task.metadata["task_category"]
            
            # Match category to agent capabilities
            for agent_type, capabilities in self._agent_capabilities.items():
                if category in capabilities:
                    return agent_type
        
        # Check task description for keywords
        description = task.task_description.lower()
        
        # Check for keywords in the description
        for agent_type, keywords in self._agent_capabilities.items():
            for keyword in keywords:
                if keyword.lower() in description:
                    return agent_type
        
        # Default to builder agent if no match
        return "builder"
    
    async def _check_for_escalation(self, task: TaskState):
        """
        Check if a task failure should trigger escalation
        
        Args:
            task: The failed task
        """
        # Check if this is a high-priority task
        if task.priority >= 4:
            # Log the escalation
            logger.warning(f"High-priority task {task.task_id} failed, triggering escalation")
            self._log_coordination_event("task_escalation", {
                "task_id": task.task_id,
                "priority": task.priority,
                "error": task.error,
                "retry_count": task.retry_count,
                "max_retries": task.max_retries
            })
            
            # In a real implementation, this would trigger an escalation workflow
            # For now, we'll just log it
    
    def _log_coordination_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log a coordination event
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Create the log entry
        log_entry = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Generate a timestamp for the log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(self.logs_dir, f"coordination_{event_type}_{timestamp}.json")
        
        # Write the log entry
        with open(log_path, "w") as f:
            json.dump(log_entry, f, indent=2)

# Singleton instance
_agent_coordinator = None

def get_agent_coordinator() -> AgentCoordinator:
    """
    Get the singleton AgentCoordinator instance
    """
    global _agent_coordinator
    if _agent_coordinator is None:
        _agent_coordinator = AgentCoordinator()
    return _agent_coordinator
