"""
Planner Agent API integration module.

This module enhances the Planner Agent behavior by integrating the task state manager,
status tracker, and planner orchestrator to provide task prioritization, escalation,
and persistent state tracking capabilities.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.task_state_manager import get_task_state_manager
from app.core.planner_orchestrator import get_planner_orchestrator
from app.tools.status_tracker import get_status_tracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlannerAgentEnhancer:
    """
    Enhancer for the Planner Agent that integrates task state management,
    status tracking, and orchestration to provide advanced capabilities.
    """
    
    def __init__(self):
        """Initialize the planner agent enhancer."""
        self.task_state_manager = get_task_state_manager()
        self.planner_orchestrator = get_planner_orchestrator()
        self.status_tracker = get_status_tracker()
        
        # Load planner configuration
        try:
            with open("/app/prompts/planner.json", "r") as f:
                self.planner_config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading planner configuration: {str(e)}")
            self.planner_config = {}
    
    def prioritize_tasks(self, goal_id: str) -> List[Dict[str, Any]]:
        """
        Prioritize tasks for a goal based on memory and configuration.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            List of prioritized tasks
        """
        # Get all tasks for the goal
        tasks = self.task_state_manager.get_goal_tasks(goal_id)
        
        if not tasks:
            logger.warning(f"No tasks found for goal {goal_id}")
            return []
        
        # Get prioritization configuration
        prioritization_config = self.planner_config.get("task_prioritization", {})
        
        # Skip completed tasks if configured
        if prioritization_config.get("skip_completed", True):
            tasks = [task for task in tasks if task.get("status") != "complete"]
        
        # Include failed tasks for retry if configured
        if not prioritization_config.get("retry_failed", True):
            tasks = [task for task in tasks if task.get("status") != "failed"]
        else:
            # Check retry count for failed tasks
            max_retries = prioritization_config.get("max_retries", 3)
            tasks = [
                task for task in tasks 
                if task.get("status") != "failed" or task.get("retry_count", 0) < max_retries
            ]
        
        # If no tasks remain after filtering, return empty list
        if not tasks:
            logger.info(f"No tasks remain for goal {goal_id} after filtering")
            return []
        
        # Get prioritization factors
        factors = prioritization_config.get("factors", {
            "dependency_count": 0.3,
            "estimated_complexity": 0.2,
            "agent_availability": 0.2,
            "time_sensitivity": 0.3
        })
        
        # Calculate priority score for each task
        for task in tasks:
            # Initialize score components
            dependency_score = 0
            complexity_score = 0
            availability_score = 0
            time_score = 0
            
            # Calculate dependency score (fewer dependencies = higher score)
            subtask_id = task.get("subtask_id", "")
            goal_tasks = self.task_state_manager.get_goal_tasks(goal_id)
            
            # Count how many tasks depend on this one
            dependent_count = 0
            for other_task in goal_tasks:
                dependencies = other_task.get("dependencies", [])
                if subtask_id in dependencies:
                    dependent_count += 1
            
            # More dependents = higher priority
            dependency_score = min(dependent_count / max(1, len(goal_tasks)), 1.0)
            
            # Calculate complexity score (based on description length and type)
            description = task.get("subtask_description", "")
            task_type = task.get("type", "")
            
            # Simple heuristic: longer descriptions and certain types indicate complexity
            complexity_words = ["complex", "difficult", "challenging", "intricate"]
            complex_types = ["architecture", "integration", "research"]
            
            complexity_factor = 0.5  # Default medium complexity
            
            # Check for complexity indicators in description
            if any(word in description.lower() for word in complexity_words):
                complexity_factor += 0.25
            
            # Check for complex task types
            if task_type in complex_types:
                complexity_factor += 0.25
            
            # Normalize complexity score
            complexity_score = min(complexity_factor, 1.0)
            
            # Calculate agent availability score
            agent_name = task.get("assigned_agent", "")
            
            # Check how many tasks are assigned to this agent
            agent_tasks = self.task_state_manager.get_agent_tasks(agent_name, "in_progress")
            
            # Fewer in-progress tasks = higher availability
            availability_score = 1.0 - min(len(agent_tasks) / 5, 1.0)  # Assume max 5 concurrent tasks
            
            # Calculate time sensitivity score
            created_at = task.get("created_at", "")
            
            if created_at:
                try:
                    # Calculate age of task
                    created_time = datetime.fromisoformat(created_at)
                    now = datetime.now()
                    age_hours = (now - created_time).total_seconds() / 3600
                    
                    # Older tasks get higher priority (up to 48 hours)
                    time_score = min(age_hours / 48, 1.0)
                except Exception as e:
                    logger.error(f"Error calculating task age: {str(e)}")
                    time_score = 0.5  # Default medium time sensitivity
            else:
                time_score = 0.5  # Default medium time sensitivity
            
            # Calculate overall priority score
            priority_score = (
                factors.get("dependency_count", 0.3) * dependency_score +
                factors.get("estimated_complexity", 0.2) * complexity_score +
                factors.get("agent_availability", 0.2) * availability_score +
                factors.get("time_sensitivity", 0.3) * time_score
            )
            
            # Add priority score to task
            task["priority_score"] = priority_score
        
        # Sort tasks by priority score (descending)
        prioritized_tasks = sorted(tasks, key=lambda t: t.get("priority_score", 0), reverse=True)
        
        return prioritized_tasks
    
    def check_for_stalled_tasks(self) -> List[Dict[str, Any]]:
        """
        Check for stalled tasks that need escalation.
        
        Returns:
            List of stalled tasks
        """
        # Get escalation policy configuration
        escalation_policy = self.planner_config.get("escalation_policy", {})
        
        if not escalation_policy.get("enabled", True):
            logger.info("Escalation policy is disabled")
            return []
        
        # Get stalled hours threshold
        stalled_hours = escalation_policy.get("stalled_hours_threshold", 24)
        
        # Get stalled tasks
        stalled_tasks = self.task_state_manager.get_stalled_tasks(stalled_hours)
        
        if not stalled_tasks:
            logger.info(f"No stalled tasks found (threshold: {stalled_hours} hours)")
            return []
        
        logger.info(f"Found {len(stalled_tasks)} stalled tasks")
        
        # Process stalled tasks for escalation
        for task in stalled_tasks:
            subtask_id = task.get("subtask_id", "")
            goal_id = task.get("goal_id", "")
            
            if not subtask_id or not goal_id:
                continue
            
            # Log the stalled task
            logger.warning(f"Stalled task detected: {subtask_id} (Goal: {goal_id})")
            
            # Escalate the issue
            self._escalate_stalled_task(task)
        
        return stalled_tasks
    
    def _escalate_stalled_task(self, task: Dict[str, Any]) -> None:
        """
        Escalate a stalled task according to the escalation policy.
        
        Args:
            task: Stalled task
        """
        # Get escalation policy configuration
        escalation_policy = self.planner_config.get("escalation_policy", {})
        escalate_to = escalation_policy.get("escalate_to", ["guardian", "human"])
        
        subtask_id = task.get("subtask_id", "")
        goal_id = task.get("goal_id", "")
        
        # Update task status to indicate escalation
        self.task_state_manager.update_task_state(
            subtask_id=subtask_id,
            updates={
                "escalated": True,
                "escalation_time": datetime.now().isoformat(),
                "escalation_reason": "Task stalled"
            }
        )
        
        # Log the escalation
        logger.info(f"Escalating stalled task {subtask_id} to {', '.join(escalate_to)}")
        
        # Implement escalation logic based on configuration
        if "guardian" in escalate_to:
            # TODO: Implement guardian escalation
            logger.info(f"Guardian escalation for task {subtask_id} not yet implemented")
        
        if "human" in escalate_to:
            # TODO: Implement human escalation
            logger.info(f"Human escalation for task {subtask_id} not yet implemented")
    
    def make_goal_queryable(self, goal_id: str) -> Dict[str, Any]:
        """
        Make a goal's progress queryable.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Goal status and progress information
        """
        # Get goal tracking configuration
        goal_tracking = self.planner_config.get("goal_tracking", {})
        
        if not goal_tracking.get("queryable", True):
            logger.info("Goal querying is disabled")
            return {
                "queryable": False,
                "goal_id": goal_id,
                "message": "Goal querying is disabled",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get goal status from orchestrator
        goal_status = self.planner_orchestrator.get_goal_status(goal_id)
        
        # Get goal progress from task state manager
        goal_progress = self.task_state_manager.get_goal_progress(goal_id)
        
        # Combine information
        queryable_goal = {
            "queryable": True,
            "goal_id": goal_id,
            "status": goal_status,
            "progress": goal_progress,
            "timestamp": datetime.now().isoformat()
        }
        
        return queryable_goal
    
    def ensure_persistence(self, goal_id: str) -> Dict[str, Any]:
        """
        Ensure a goal's state is persistent across sessions.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Persistence status
        """
        # Get goal tracking configuration
        goal_tracking = self.planner_config.get("goal_tracking", {})
        
        if not goal_tracking.get("persistence_enabled", True):
            logger.info("Goal persistence is disabled")
            return {
                "persistence": False,
                "goal_id": goal_id,
                "message": "Goal persistence is disabled",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get goal tasks
        tasks = self.task_state_manager.get_goal_tasks(goal_id)
        
        if not tasks:
            logger.warning(f"No tasks found for goal {goal_id}")
            return {
                "persistence": False,
                "goal_id": goal_id,
                "message": "No tasks found for goal",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if auto-resume is enabled
        auto_resume = goal_tracking.get("auto_resume_incomplete", True)
        
        # Get goal progress
        progress = self.task_state_manager.get_goal_progress(goal_id)
        
        # If goal is not complete and auto-resume is enabled, ensure it can be resumed
        if progress["status"] != "complete" and auto_resume:
            # Ensure the goal is in a resumable state
            # This is already handled by the task state manager and planner orchestrator
            logger.info(f"Goal {goal_id} is in a resumable state")
        
        return {
            "persistence": True,
            "goal_id": goal_id,
            "auto_resume": auto_resume,
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        }
    
    def process_goal_with_memory(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a goal with memory-driven state management.
        
        This is the main entry point for the enhanced planner agent.
        
        Args:
            goal: Goal to process
            
        Returns:
            Goal processing result
        """
        goal_id = goal.get("id", "")
        
        if not goal_id:
            logger.error("Goal ID is required")
            return {
                "status": "error",
                "message": "Goal ID is required",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if this goal has been processed before
        existing_tasks = self.task_state_manager.get_goal_tasks(goal_id)
        
        if existing_tasks:
            logger.info(f"Found {len(existing_tasks)} existing tasks for goal {goal_id}")
            
            # Get goal progress
            progress = self.task_state_manager.get_goal_progress(goal_id)
            
            if progress["status"] == "complete":
                logger.info(f"Goal {goal_id} is already complete")
                
                # Return the completed goal status
                return self.make_goal_queryable(goal_id)
            
            # Goal is not complete, check if auto-resume is enabled
            goal_tracking = self.planner_config.get("goal_tracking", {})
            auto_resume = goal_tracking.get("auto_resume_incomplete", True)
            
            if auto_resume:
                logger.info(f"Auto-resuming goal {goal_id}")
                
                # Resume the goal
                resume_result = self.planner_orchestrator.resume_goal(goal_id)
                
                return resume_result
            else:
                logger.info(f"Auto-resume is disabled for goal {goal_id}")
                
                # Return the current goal status
                return self.make_goal_queryable(goal_id)
        
        # Process a new goal
        logger.info(f"Processing new goal {goal_id}")
        
        # Process the goal using the planner orchestrator
        result = self.planner_orchestrator.process_goal(goal)
        
        return result

# Create a singleton instance
_planner_agent_enhancer = None

def get_planner_agent_enhancer() -> PlannerAgentEnhancer:
    """
    Get the singleton instance of the planner agent enhancer.
    
    Returns:
        PlannerAgentEnhancer instance
    """
    global _planner_agent_enhancer
    if _planner_agent_enhancer is None:
        _planner_agent_enhancer = PlannerAgentEnhancer()
    return _planner_agent_enhancer

# For API integration
def process_goal_with_memory(goal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a goal with memory-driven state management.
    
    Args:
        goal: Goal to process
        
    Returns:
            Goal processing result
    """
    enhancer = get_planner_agent_enhancer()
    return enhancer.process_goal_with_memory(goal)

def prioritize_tasks(goal_id: str) -> List[Dict[str, Any]]:
    """
    Prioritize tasks for a goal based on memory and configuration.
    
    Args:
        goal_id: ID of the goal
        
    Returns:
        List of prioritized tasks
    """
    enhancer = get_planner_agent_enhancer()
    return enhancer.prioritize_tasks(goal_id)

def check_for_stalled_tasks() -> List[Dict[str, Any]]:
    """
    Check for stalled tasks that need escalation.
    
    Returns:
        List of stalled tasks
    """
    enhancer = get_planner_agent_enhancer()
    return enhancer.check_for_stalled_tasks()

def make_goal_queryable(goal_id: str) -> Dict[str, Any]:
    """
    Make a goal's progress queryable.
    
    Args:
        goal_id: ID of the goal
        
    Returns:
        Goal status and progress information
    """
    enhancer = get_planner_agent_enhancer()
    return enhancer.make_goal_queryable(goal_id)

def ensure_persistence(goal_id: str) -> Dict[str, Any]:
    """
    Ensure a goal's state is persistent across sessions.
    
    Args:
        goal_id: ID of the goal
        
    Returns:
        Persistence status
    """
    enhancer = get_planner_agent_enhancer()
    return enhancer.ensure_persistence(goal_id)
