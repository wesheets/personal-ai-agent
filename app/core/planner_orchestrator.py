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

# Fix import path from app.tools.agent_router to app.core.agent_router
from app.core.agent_router import get_agent_router, find_agent
from app.core.task_state_manager import TaskStateManager, get_task_state_manager
from app.core.agent_coordinator import AgentCoordinator, get_agent_coordinator
from app.core.vector_memory import VectorMemorySystem
from app.core.memory_manager import MemoryManager

# Set up logging
logger = logging.getLogger(__name__)

class PlannerOrchestrator:
    """
    Orchestrator for planning and executing tasks
    """
    
    def __init__(self):
        self.task_state_manager = get_task_state_manager()
        self.agent_coordinator = get_agent_coordinator()
        self.agent_router = get_agent_router()
        self.vector_memory = VectorMemorySystem()
        self.memory_manager = MemoryManager()
        
        # Create logs directory if it doesn't exist
        self.execution_log_dir = os.path.join("app", "logs", "execution_logs")
        os.makedirs(self.execution_log_dir, exist_ok=True)
    
    async def decompose_goal(self, goal_description: str, goal_id: Optional[str] = None) -> str:
        """
        Decompose a goal into subtasks
        
        Args:
            goal_description: Description of the goal
            goal_id: Optional goal ID (generated if not provided)
            
        Returns:
            Goal ID
        """
        # Generate goal ID if not provided
        if not goal_id:
            goal_id = str(uuid.uuid4())
        
        # Log goal decomposition
        self._log_execution(
            goal_id=goal_id,
            action="decompose_goal",
            details={
                "goal_description": goal_description
            }
        )
        
        # Create a planner agent to decompose the goal
        planner_agent = find_agent("planner")
        if not planner_agent:
            logger.error("Planner agent not found")
            raise ValueError("Planner agent not found")
        
        # Execute the planner agent to decompose the goal
        result = await planner_agent.run(
            input_text=f"Decompose the following goal into subtasks: {goal_description}",
            goal_id=goal_id
        )
        
        # Parse the result to extract subtasks
        subtasks = self._parse_subtasks(result)
        
        # Create task states for each subtask
        for i, subtask in enumerate(subtasks):
            subtask_id = f"{goal_id}_subtask_{i+1}"
            
            # Determine dependencies
            dependencies = []
            if "dependencies" in subtask:
                for dep in subtask["dependencies"]:
                    dep_id = f"{goal_id}_subtask_{dep}"
                    dependencies.append(dep_id)
            
            # Determine assigned agent
            assigned_agent = subtask.get("assigned_agent")
            if not assigned_agent:
                # Route task to appropriate agent
                agent_type, confidence, reason = self.agent_router.route_task(subtask["description"])
                assigned_agent = agent_type
            
            # Create task state
            await self.task_state_manager.create_task(
                goal_id=goal_id,
                task_id=subtask_id,
                task_description=subtask["description"],
                assigned_agent=assigned_agent,
                dependencies=dependencies,
                priority=subtask.get("priority", 0)
            )
        
        # Log subtasks
        self._log_execution(
            goal_id=goal_id,
            action="create_subtasks",
            details={
                "subtasks": [
                    {
                        "task_id": f"{goal_id}_subtask_{i+1}",
                        "description": subtask["description"],
                        "assigned_agent": subtask.get("assigned_agent") or self.agent_router.route_task(subtask["description"])[0]
                    }
                    for i, subtask in enumerate(subtasks)
                ]
            }
        )
        
        return goal_id
    
    async def execute_goal(self, goal_id: str, max_parallel: int = 3) -> Dict[str, Any]:
        """
        Execute a goal by executing its subtasks
        
        Args:
            goal_id: ID of the goal to execute
            max_parallel: Maximum number of tasks to execute in parallel
            
        Returns:
            Dictionary containing execution results
        """
        # Get all tasks for the goal
        tasks = await self.task_state_manager.get_tasks_for_goal(goal_id)
        if not tasks:
            logger.error(f"No tasks found for goal: {goal_id}")
            return {
                "success": False,
                "error": f"No tasks found for goal: {goal_id}"
            }
        
        # Log goal execution
        self._log_execution(
            goal_id=goal_id,
            action="execute_goal",
            details={
                "task_count": len(tasks)
            }
        )
        
        # Track task status
        pending_tasks = set()
        running_tasks = set()
        completed_tasks = []
        failed_tasks = []
        
        # Initialize pending tasks with tasks that have no dependencies
        for task in tasks:
            task_id = task["task_id"]
            dependencies = task.get("dependencies", [])
            
            if not dependencies:
                pending_tasks.add(task_id)
        
        # Execute tasks until all are completed or failed
        while pending_tasks or running_tasks:
            # Start pending tasks if there are slots available
            while pending_tasks and len(running_tasks) < max_parallel:
                task_id = pending_tasks.pop()
                running_tasks.add(task_id)
                
                # Execute task in background
                asyncio.create_task(self._execute_task(
                    task_id=task_id,
                    running_tasks=running_tasks,
                    completed_tasks=completed_tasks,
                    failed_tasks=failed_tasks
                ))
            
            # Wait for a short time
            await asyncio.sleep(0.1)
            
            # Check for newly available tasks
            for task in tasks:
                task_id = task["task_id"]
                
                # Skip tasks that are already processed
                if (task_id in pending_tasks or 
                    task_id in running_tasks or 
                    task_id in completed_tasks or 
                    task_id in failed_tasks):
                    continue
                
                # Check if all dependencies are completed
                dependencies = task.get("dependencies", [])
                if all(dep in completed_tasks for dep in dependencies):
                    pending_tasks.add(task_id)
        
        # Log goal completion
        self._log_execution(
            goal_id=goal_id,
            action="complete_goal",
            details={
                "completed_tasks": len(completed_tasks),
                "failed_tasks": len(failed_tasks)
            }
        )
        
        return {
            "success": True,
            "goal_id": goal_id,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks
        }
    
    async def _execute_task(self, task_id: str, running_tasks: Set[str], 
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
    
    def _parse_subtasks(self, planner_result: str) -> List[Dict[str, Any]]:
        """
        Parse the result from the planner agent to extract subtasks
        
        Args:
            planner_result: Result from the planner agent
            
        Returns:
            List of subtasks
        """
        # This is a placeholder implementation
        # In a real implementation, this would parse the planner result
        # to extract subtasks, dependencies, and assigned agents
        
        # For now, just create some dummy subtasks
        subtasks = [
            {
                "description": "Subtask 1",
                "dependencies": []
            },
            {
                "description": "Subtask 2",
                "dependencies": [1]
            },
            {
                "description": "Subtask 3",
                "dependencies": [1, 2]
            }
        ]
        
        return subtasks
    
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
