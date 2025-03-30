"""
Planner Orchestrator Module for the Autonomous Goal Decomposer + Planner Agent

This module serves as the execution core that receives a main goal, breaks it into subtasks,
assigns subtasks to agents, sequences execution based on dependencies, stores progress in
vector memory, and escalates issues when necessary.

Updated to integrate with the Task State Manager for persistent memory-driven state management
and to provide functionality to execute subtasks in parallel for decomposed goals,
managing dependencies and coordinating multiple agents.
"""

import os
import json
import uuid
import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from datetime import datetime

# Import required modules
from app.tools.agent_router import get_agent_router, find_agent
from app.core.vector_memory import VectorMemory, get_vector_memory
from app.core.task_state_manager import get_task_state_manager
from app.core.agent_coordinator import get_agent_coordinator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlannerOrchestrator:
    """
    Orchestrates the planning and execution of complex goals by breaking them down
    into subtasks, managing dependencies, and coordinating parallel execution across agents.
    """
    
    def __init__(self):
        """Initialize the PlannerOrchestrator with required components."""
        self.task_state_manager = get_task_state_manager()
        self.agent_router = get_agent_router()
        self.agent_coordinator = get_agent_coordinator()
        self.vector_memory = get_vector_memory()
        self.execution_log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                             "logs", "execution_logs")
        os.makedirs(self.execution_log_dir, exist_ok=True)
    
    async def decompose_goal(self, goal_id: str, goal_description: str) -> Dict[str, Any]:
        """
        Decompose a complex goal into subtasks with dependencies.
        
        Args:
            goal_id: Unique identifier for the goal
            goal_description: Description of the goal to decompose
            
        Returns:
            Dictionary containing goal information and subtasks
        """
        logger.info(f"Decomposing goal: {goal_description} (ID: {goal_id})")
        
        # Create goal in task state manager
        goal = await self.task_state_manager.create_goal(
            goal_id=goal_id,
            goal_description=goal_description
        )
        
        # Use planner agent to decompose goal into subtasks
        planner_agent = find_agent("planner")
        decomposition_result = await planner_agent.run(
            input_text=f"Decompose this goal into subtasks with dependencies: {goal_description}",
            goal_id=goal_id
        )
        
        # Parse subtasks from decomposition result
        subtasks = decomposition_result.get("subtasks", [])
        
        # Create tasks in task state manager
        for subtask in subtasks:
            task_id = f"{goal_id}-task-{uuid.uuid4().hex[:8]}"
            
            # Determine agent assignment based on task type
            agent_assignment = self.agent_router.route_task(subtask["description"])
            
            await self.task_state_manager.create_task(
                task_id=task_id,
                goal_id=goal_id,
                task_description=subtask["description"],
                priority=subtask.get("priority", 3),
                assigned_agent=agent_assignment["assigned_agent"],
                dependencies=subtask.get("dependencies", [])
            )
        
        # Store decomposition in memory
        self.vector_memory.add(
            text=f"Goal: {goal_description}\nDecomposition: {json.dumps(subtasks)}",
            metadata={
                "type": "goal_decomposition",
                "goal_id": goal_id,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Log decomposition
        self._log_execution(
            goal_id=goal_id,
            action="decompose_goal",
            details={
                "goal_description": goal_description,
                "subtasks_count": len(subtasks)
            }
        )
        
        return {
            "goal_id": goal_id,
            "goal_description": goal_description,
            "subtasks": subtasks,
            "status": "decomposed"
        }
    
    async def execute_goal(self, goal_id: str) -> Dict[str, Any]:
        """
        Execute a decomposed goal by running all subtasks in parallel when dependencies allow.
        
        Args:
            goal_id: Unique identifier for the goal to execute
            
        Returns:
            Dictionary containing execution results
        """
        logger.info(f"Executing goal: {goal_id}")
        
        # Get goal information
        goal = await self.task_state_manager.get_goal(goal_id)
        if not goal:
            raise ValueError(f"Goal not found: {goal_id}")
        
        # Update goal status to in_progress
        await self.task_state_manager.update_goal_status(goal_id, "in_progress")
        
        # Log execution start
        self._log_execution(
            goal_id=goal_id,
            action="execute_goal_start",
            details={"goal_description": goal.goal_description}
        )
        
        # Execute tasks in parallel with dependency management
        execution_result = await self._execute_tasks_in_parallel(goal_id)
        
        # Update goal status based on execution result
        if execution_result["success"]:
            await self.task_state_manager.update_goal_status(goal_id, "completed")
        else:
            await self.task_state_manager.update_goal_status(goal_id, "failed")
        
        # Log execution completion
        self._log_execution(
            goal_id=goal_id,
            action="execute_goal_complete",
            details={
                "success": execution_result["success"],
                "completed_tasks": execution_result["completed_tasks"],
                "failed_tasks": execution_result["failed_tasks"]
            }
        )
        
        return {
            "goal_id": goal_id,
            "success": execution_result["success"],
            "completed_tasks": execution_result["completed_tasks"],
            "failed_tasks": execution_result["failed_tasks"],
            "execution_time": execution_result["execution_time"]
        }
    
    async def _execute_tasks_in_parallel(self, goal_id: str) -> Dict[str, Any]:
        """
        Execute tasks in parallel, respecting dependencies.
        
        Args:
            goal_id: Unique identifier for the goal
            
        Returns:
            Dictionary containing execution results
        """
        start_time = time.time()
        completed_tasks = []
        failed_tasks = []
        
        # Keep track of tasks that are currently running
        running_tasks: Set[str] = set()
        
        # Keep executing until all tasks are either completed or failed
        while True:
            # Get available tasks (those with all dependencies satisfied)
            available_tasks = await self.task_state_manager.get_available_tasks(goal_id)
            
            # If no available tasks and no running tasks, we're done
            if not available_tasks and not running_tasks:
                break
            
            # Start execution of available tasks
            for task in available_tasks:
                if task.task_id not in running_tasks:
                    running_tasks.add(task.task_id)
                    # Execute task asynchronously
                    asyncio.create_task(self._execute_single_task(task.task_id, running_tasks, completed_tasks, failed_tasks))
            
            # Wait a bit before checking again
            await asyncio.sleep(0.5)
        
        execution_time = time.time() - start_time
        
        # Determine overall success
        success = len(failed_tasks) == 0
        
        return {
            "success": success,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "execution_time": execution_time
        }
    
    async def _execute_single_task(self, task_id: str, running_tasks: Set[str], 
                                  completed_tasks: List[str], failed_tasks: List[str]) -> None:
        """
        Execute a single task and update its status.
        
        Args:
            task_id: Unique identifier for the task
            running_tasks: Set of task IDs that are currently running
            completed_tasks: List to append completed task IDs to
            failed_tasks: List to append failed task IDs to
        """
        try:
            # Get task information
            task = await self.task_state_manager.get_task(task_id)
            if not task:
                logger.error(f"Task not found: {task_id}")
                running_tasks.remove(task_id)
                failed_tasks.append(task_id)
                return
            
            logger.info(f"Executing task: {task.task_description} (ID: {task_id})")
            
            # Update task status to in_progress
            await self.task_state_manager.update_task_status(task_id, "in_progress")
            
            # Assign task to agent
            assignment = await self.agent_coordinator.assign_task(task_id)
            
            # Execute task with appropriate agent
            agent = find_agent(task.assigned_agent)
            if not agent:
                logger.error(f"Agent not found: {task.assigned_agent}")
                await self.task_state_manager.update_task_status(
                    task_id=task_id,
                    status="failed",
                    error=f"Agent not found: {task.assigned_agent}"
                )
                running_tasks.remove(task_id)
                failed_tasks.append(task_id)
                return
            
            # Execute the task
            result = await agent.run(
                input_text=task.task_description,
                goal_id=task.goal_id,
                task_id=task_id
            )
            
            # Handle task completion
            await self.agent_coordinator.handle_task_completion(task_id, result)
            
            # Update task status to completed
            await self.task_state_manager.update_task_status(
                task_id=task_id,
                status="completed",
                result=result
            )
            
            # Log task completion
            self._log_execution(
                goal_id=task.goal_id,
                action="complete_task",
                details={
                    "task_id": task_id,
                    "task_description": task.task_description,
                    "agent": task.assigned_agent
                }
            )
            
            # Update tracking lists
            running_tasks.remove(task_id)
            completed_tasks.append(task_id)
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            
            # Update task status to failed
            await self.task_state_manager.update_task_status(
                task_id=task_id,
                status="failed",
                error=str(e)
            )
            
            # Log task failure
            self._log_execution(
                goal_id=task.goal_id,
                action="fail_task",
                details={
                    "task_id": task_id,
                    "error": str(e)
                }
            )
            
            # Update tracking lists
            running_tasks.remove(task_id)
            failed_tasks.append(task_id)
    
    def _log_execution(self, goal_id: str, action: str, details: Dict[str, Any]) -> None:
        """
        Log execution details to a file.
        
        Args:
            goal_id: Unique identifier for the goal
            action: Action being performed
            details: Additional details to log
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "goal_id": goal_id,
            "action": action,
            "details": details
        }
        
        log_file = os.path.join(self.execution_log_dir, f"{goal_id}.json")
        
        # Append to existing log or create new log file
        try:
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    logs = json.load(f)
                logs.append(log_entry)
            else:
                logs = [log_entry]
                
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.error(f"Error logging execution: {str(e)}")

# Singleton instance
_planner_orchestrator = None

def get_planner_orchestrator() -> PlannerOrchestrator:
    """
    Get the singleton instance of the PlannerOrchestrator.
    
    Returns:
        PlannerOrchestrator instance
    """
    global _planner_orchestrator
    if _planner_orchestrator is None:
        _planner_orchestrator = PlannerOrchestrator()
    return _planner_orchestrator
