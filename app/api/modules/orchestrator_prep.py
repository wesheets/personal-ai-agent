"""
Orchestrator preparation components for the Agent Context module.

This module provides helper functions and utilities to prepare agent context data
for use by the Orchestrator, which will coordinate multi-agent workflows.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

def prepare_orchestrator_view(agent_contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prepare a consolidated view of multiple agent contexts for the Orchestrator.
    
    This function takes multiple agent contexts and creates a unified view that
    the Orchestrator can use to make decisions about task allocation and coordination.
    
    Args:
        agent_contexts: List of agent context responses from the /agent/context endpoint
        
    Returns:
        A consolidated view with project groupings and agent availability
    """
    # Initialize the orchestrator view
    orchestrator_view = {
        "projects": {},
        "agents": {},
        "last_updated": datetime.utcnow().isoformat()
    }
    
    # Process each agent context
    for context in agent_contexts:
        agent_id = context.get("agent_id")
        if not agent_id:
            continue
        
        # Add agent to the agents dictionary
        orchestrator_view["agents"][agent_id] = {
            "agent_state": context.get("agent_state", "unknown"),
            "last_active": context.get("last_active"),
            "active_project_count": len(context.get("active_projects", [])),
            "total_tasks": sum(len(project.get("tasks", [])) for project in context.get("active_projects", []))
        }
        
        # Process each project in the agent context
        for project in context.get("active_projects", []):
            project_id = project.get("project_id")
            if not project_id:
                continue
            
            # Create project entry if it doesn't exist
            if project_id not in orchestrator_view["projects"]:
                orchestrator_view["projects"][project_id] = {
                    "agents": [],
                    "tasks": [],
                    "last_active": None
                }
            
            # Add agent to project's agents list if not already there
            if agent_id not in orchestrator_view["projects"][project_id]["agents"]:
                orchestrator_view["projects"][project_id]["agents"].append(agent_id)
            
            # Update project's last_active timestamp if newer
            project_last_active = project.get("last_active")
            if project_last_active:
                if not orchestrator_view["projects"][project_id]["last_active"] or \
                   project_last_active > orchestrator_view["projects"][project_id]["last_active"]:
                    orchestrator_view["projects"][project_id]["last_active"] = project_last_active
            
            # Add tasks to project's tasks list
            for task in project.get("tasks", []):
                task_entry = {
                    "task": task.get("task"),
                    "status": task.get("status"),
                    "agent_id": agent_id
                }
                # Only add if not already in the list (avoid duplicates)
                if task_entry not in orchestrator_view["projects"][project_id]["tasks"]:
                    orchestrator_view["projects"][project_id]["tasks"].append(task_entry)
    
    return orchestrator_view

def identify_available_agents(orchestrator_view: Dict[str, Any]) -> List[str]:
    """
    Identify agents that are available for new tasks based on their current state.
    
    Args:
        orchestrator_view: The consolidated orchestrator view
        
    Returns:
        List of agent IDs that are available for new tasks
    """
    available_agents = []
    
    for agent_id, agent_data in orchestrator_view.get("agents", {}).items():
        # Consider an agent available if it's in "idle" state
        if agent_data.get("agent_state") == "idle":
            available_agents.append(agent_id)
    
    return available_agents

def identify_stalled_tasks(orchestrator_view: Dict[str, Any], stall_threshold_hours: int = 24) -> List[Dict[str, Any]]:
    """
    Identify tasks that appear to be stalled based on project last_active timestamp.
    
    Args:
        orchestrator_view: The consolidated orchestrator view
        stall_threshold_hours: Number of hours after which a task is considered stalled
        
    Returns:
        List of stalled tasks with project and agent information
    """
    stalled_tasks = []
    now = datetime.utcnow()
    stall_threshold = timedelta(hours=stall_threshold_hours)
    
    for project_id, project_data in orchestrator_view.get("projects", {}).items():
        # Skip if no last_active timestamp
        if not project_data.get("last_active"):
            continue
        
        # Parse the last_active timestamp
        try:
            last_active = datetime.fromisoformat(project_data["last_active"])
            time_since_active = now - last_active
            
            # Check if project is stalled
            if time_since_active > stall_threshold:
                # Find in-progress tasks in this project
                for task in project_data.get("tasks", []):
                    if task.get("status") == "in_progress":
                        stalled_tasks.append({
                            "project_id": project_id,
                            "task": task.get("task"),
                            "agent_id": task.get("agent_id"),
                            "last_active": project_data["last_active"],
                            "hours_stalled": time_since_active.total_seconds() / 3600
                        })
        except (ValueError, TypeError):
            # Skip if timestamp is invalid
            continue
    
    return stalled_tasks

def suggest_task_reassignments(orchestrator_view: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Suggest task reassignments based on agent availability and task status.
    
    Args:
        orchestrator_view: The consolidated orchestrator view
        
    Returns:
        List of suggested task reassignments
    """
    suggestions = []
    
    # Get available agents
    available_agents = identify_available_agents(orchestrator_view)
    if not available_agents:
        return suggestions  # No available agents for reassignment
    
    # Get stalled tasks
    stalled_tasks = identify_stalled_tasks(orchestrator_view)
    
    # For each stalled task, suggest reassignment to an available agent
    for i, task in enumerate(stalled_tasks):
        # Skip if the task's agent is already in the available list
        if task.get("agent_id") in available_agents:
            continue
        
        # Assign to the next available agent (round-robin)
        new_agent_id = available_agents[i % len(available_agents)]
        
        suggestions.append({
            "project_id": task.get("project_id"),
            "task": task.get("task"),
            "current_agent_id": task.get("agent_id"),
            "suggested_agent_id": new_agent_id,
            "reason": f"Task appears stalled for {task.get('hours_stalled', 0):.1f} hours"
        })
    
    return suggestions
