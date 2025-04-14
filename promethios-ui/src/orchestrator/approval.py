"""
Orchestrator Approval Loop

This module implements the operator approval loop for the Orchestrator, allowing
operators to approve or modify proposed plans and manage the execution flow.
"""

import os
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple

# Import consultation module to access session data
from src.orchestrator.consultation import ConsultationManager

class Goal:
    """
    Represents a goal with subgoals and execution status.
    
    This class manages the breakdown of a plan into executable subgoals,
    tracks their status, and handles delegation to agents.
    """
    
    def __init__(self, session_id: str, title: str, description: str):
        """
        Initialize a new goal.
        
        Args:
            session_id: ID of the consultation session
            title: Title of the goal
            description: Description of the goal
        """
        self.goal_id = str(uuid.uuid4())
        self.session_id = session_id
        self.title = title
        self.description = description
        self.status = "pending"  # pending, in_progress, completed, failed
        self.subgoals = []
        self.created_at = datetime.datetime.now().isoformat()
        self.completed_at = None
        
    def add_subgoal(self, title: str, description: str, assigned_agent: str, tools: List[str]) -> str:
        """
        Add a subgoal to this goal.
        
        Args:
            title: Title of the subgoal
            description: Description of the subgoal
            assigned_agent: ID of the agent assigned to this subgoal
            tools: List of tools to be used for this subgoal
            
        Returns:
            ID of the created subgoal
        """
        subgoal_id = str(uuid.uuid4())
        
        subgoal = {
            "subgoal_id": subgoal_id,
            "title": title,
            "description": description,
            "assigned_agent": assigned_agent,
            "status": "pending",
            "tools": tools,
            "created_at": datetime.datetime.now().isoformat(),
            "completed_at": None
        }
        
        self.subgoals.append(subgoal)
        return subgoal_id
        
    def update_subgoal_status(self, subgoal_id: str, status: str) -> None:
        """
        Update the status of a subgoal.
        
        Args:
            subgoal_id: ID of the subgoal to update
            status: New status (pending, in_progress, completed, failed)
        """
        for subgoal in self.subgoals:
            if subgoal["subgoal_id"] == subgoal_id:
                subgoal["status"] = status
                
                # If completed or failed, set completed_at timestamp
                if status in ["completed", "failed"]:
                    subgoal["completed_at"] = datetime.datetime.now().isoformat()
                
                # Update overall goal status based on subgoals
                self._update_goal_status()
                return
                
        raise ValueError(f"Subgoal with ID {subgoal_id} not found")
        
    def _update_goal_status(self) -> None:
        """Update the overall goal status based on subgoal statuses."""
        # If all subgoals are completed, mark goal as completed
        if all(subgoal["status"] == "completed" for subgoal in self.subgoals):
            self.status = "completed"
            self.completed_at = datetime.datetime.now().isoformat()
            return
            
        # If any subgoal has failed, mark goal as failed
        if any(subgoal["status"] == "failed" for subgoal in self.subgoals):
            self.status = "failed"
            self.completed_at = datetime.datetime.now().isoformat()
            return
            
        # If any subgoal is in progress, mark goal as in progress
        if any(subgoal["status"] == "in_progress" for subgoal in self.subgoals):
            self.status = "in_progress"
            return
            
        # Otherwise, goal is still pending
        self.status = "pending"
        
    def get_subgoal(self, subgoal_id: str) -> Dict[str, Any]:
        """
        Get a subgoal by ID.
        
        Args:
            subgoal_id: ID of the subgoal to retrieve
            
        Returns:
            Subgoal dictionary
        """
        for subgoal in self.subgoals:
            if subgoal["subgoal_id"] == subgoal_id:
                return subgoal
                
        raise ValueError(f"Subgoal with ID {subgoal_id} not found")
        
    def get_next_pending_subgoal(self) -> Optional[Dict[str, Any]]:
        """
        Get the next pending subgoal.
        
        Returns:
            Next pending subgoal or None if no pending subgoals
        """
        for subgoal in self.subgoals:
            if subgoal["status"] == "pending":
                return subgoal
                
        return None
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the goal to a dictionary.
        
        Returns:
            Dictionary representation of the goal
        """
        return {
            "goal_id": self.goal_id,
            "session_id": self.session_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "subgoals": self.subgoals,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }
        
    def save(self, directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/goals") -> str:
        """
        Save the goal to a file.
        
        Args:
            directory: Directory to save the goal file
            
        Returns:
            Path to the saved goal file
        """
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Generate the filename
        filename = f"goal_{self.goal_id}.json"
        filepath = os.path.join(directory, filename)
        
        # Write the goal to file
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            
        return filepath
        
    @classmethod
    def load(cls, goal_id: str, directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/goals") -> "Goal":
        """
        Load a goal from a file.
        
        Args:
            goal_id: ID of the goal to load
            directory: Directory where goal files are stored
            
        Returns:
            Loaded Goal object
        """
        # Generate the filepath
        filename = f"goal_{goal_id}.json"
        filepath = os.path.join(directory, filename)
        
        # Read the goal from file
        with open(filepath, "r") as f:
            goal_data = json.load(f)
            
        # Create a new goal object
        goal = cls(goal_data["session_id"], goal_data["title"], goal_data["description"])
        
        # Update the goal with the loaded data
        goal.goal_id = goal_data["goal_id"]
        goal.status = goal_data["status"]
        goal.subgoals = goal_data["subgoals"]
        goal.created_at = goal_data["created_at"]
        goal.completed_at = goal_data["completed_at"]
        
        return goal


class ApprovalManager:
    """
    Manages the operator approval loop for plans and execution.
    
    This class handles the confirmation of plans, creation of goals and subgoals,
    and delegation of tasks to agents.
    """
    
    def __init__(
        self,
        consultation_manager: ConsultationManager,
        goals_directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/goals"
    ):
        """
        Initialize the approval manager.
        
        Args:
            consultation_manager: ConsultationManager instance
            goals_directory: Directory to store goal files
        """
        self.consultation_manager = consultation_manager
        self.goals_directory = goals_directory
        os.makedirs(goals_directory, exist_ok=True)
        self.active_goals = {}
        
    def confirm_plan(self, session_id: str, approved: bool, modifications: Optional[Dict[str, Any]] = None) -> Optional[Goal]:
        """
        Confirm or reject a plan proposed during consultation.
        
        Args:
            session_id: ID of the consultation session
            approved: Whether the plan is approved
            modifications: Optional modifications to the plan
            
        Returns:
            Created Goal object if approved, None if rejected
        """
        # Get the consultation session
        session = self.consultation_manager.get_session(session_id)
        
        # If not approved, return None
        if not approved:
            return None
            
        # Get the plan from the session
        plan = session.plan
        
        # Apply modifications if provided
        if modifications:
            self._apply_plan_modifications(plan, modifications)
            
        # Create a new goal
        goal = Goal(session_id, plan["title"], plan["description"])
        
        # Add subgoals based on phases
        for phase in plan["phases"]:
            goal.add_subgoal(
                title=phase["title"],
                description=phase["description"],
                assigned_agent=phase["agents"][0],  # Assign to first agent in list
                tools=phase["tools"]
            )
            
        # Save the goal
        goal.save(self.goals_directory)
        
        # Add to active goals
        self.active_goals[goal.goal_id] = goal
        
        return goal
        
    def _apply_plan_modifications(self, plan: Dict[str, Any], modifications: Dict[str, Any]) -> None:
        """
        Apply modifications to a plan.
        
        Args:
            plan: Plan to modify
            modifications: Modifications to apply
        """
        # Update plan title and description if provided
        if "title" in modifications:
            plan["title"] = modifications["title"]
            
        if "description" in modifications:
            plan["description"] = modifications["description"]
            
        # Update phases if provided
        if "phases" in modifications:
            for i, phase_mods in enumerate(modifications["phases"]):
                if i < len(plan["phases"]):
                    phase = plan["phases"][i]
                    
                    # Update phase fields
                    for key, value in phase_mods.items():
                        if key in phase:
                            phase[key] = value
                            
        # Add new phases if provided
        if "new_phases" in modifications:
            for new_phase in modifications["new_phases"]:
                plan["phases"].append(new_phase)
                
        # Remove phases if specified
        if "remove_phases" in modifications:
            for phase_id in modifications["remove_phases"]:
                plan["phases"] = [p for p in plan["phases"] if p["phase_id"] != phase_id]
                
    def get_goal(self, goal_id: str) -> Goal:
        """
        Get a goal by ID.
        
        Args:
            goal_id: ID of the goal to retrieve
            
        Returns:
            Goal object
        """
        # Check if the goal is already in memory
        if goal_id in self.active_goals:
            return self.active_goals[goal_id]
            
        # Try to load the goal from file
        try:
            goal = Goal.load(goal_id, self.goals_directory)
            self.active_goals[goal_id] = goal
            return goal
        except FileNotFoundError:
            raise ValueError(f"Goal with ID {goal_id} not found")
            
    def update_subgoal_status(self, goal_id: str, subgoal_id: str, status: str) -> Goal:
        """
        Update the status of a subgoal.
        
        Args:
            goal_id: ID of the goal
            subgoal_id: ID of the subgoal to update
            status: New status (pending, in_progress, completed, failed)
            
        Returns:
            Updated Goal object
        """
        goal = self.get_goal(goal_id)
        goal.update_subgoal_status(subgoal_id, status)
        goal.save(self.goals_directory)
        return goal
        
    def delegate_task(self, goal_id: str, subgoal_id: str) -> Dict[str, Any]:
        """
        Delegate a task to an agent.
        
        Args:
            goal_id: ID of the goal
            subgoal_id: ID of the subgoal to delegate
            
        Returns:
            Delegation details
        """
        goal = self.get_goal(goal_id)
        subgoal = goal.get_subgoal(subgoal_id)
        
        # Mark the subgoal as in progress
        goal.update_subgoal_status(subgoal_id, "in_progress")
        goal.save(self.goals_directory)
        
        # Create delegation details
        delegation = {
            "goal_id": goal_id,
            "subgoal_id": subgoal_id,
            "agent_id": subgoal["assigned_agent"],
            "title": subgoal["title"],
            "description": subgoal["description"],
            "tools": subgoal["tools"],
            "delegated_at": datetime.datetime.now().isoformat()
        }
        
        return delegation
        
    def get_next_task(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the next task to delegate for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Next task details or None if no pending tasks
        """
        goal = self.get_goal(goal_id)
        next_subgoal = goal.get_next_pending_subgoal()
        
        if next_subgoal:
            return {
                "goal_id": goal_id,
                "subgoal_id": next_subgoal["subgoal_id"],
                "title": next_subgoal["title"],
                "description": next_subgoal["description"],
                "assigned_agent": next_subgoal["assigned_agent"],
                "tools": next_subgoal["tools"]
            }
            
        return None
        
    def list_goals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all goals, optionally filtered by status.
        
        Args:
            status: Optional status to filter by
            
        Returns:
            List of goal summary dictionaries
        """
        goals = []
        
        # List all goal files in the directory
        for filename in os.listdir(self.goals_directory):
            if filename.startswith("goal_") and filename.endswith(".json"):
                filepath = os.path.join(self.goals_directory, filename)
                
                try:
                    with open(filepath, "r") as f:
                        goal_data = json.load(f)
                        
                    # Filter by status if provided
                    if status is None or goal_data["status"] == status:
                        # Create a summary of the goal
                        summary = {
                            "goal_id": goal_data["goal_id"],
                            "session_id": goal_data["session_id"],
                            "title": goal_data["title"],
                            "description": goal_data["description"],
                            "status": goal_data["status"],
                            "created_at": goal_data["created_at"],
                            "completed_at": goal_data["completed_at"],
                            "subgoals_count": len(goal_data["subgoals"]),
                            "completed_subgoals": sum(1 for sg in goal_data["subgoals"] if sg["status"] == "completed")
                        }
                        
                        goals.append(summary)
                except Exception as e:
                    print(f"Error loading goal from {filepath}: {e}")
                    
        # Sort goals by created_at (newest first)
        goals.sort(key=lambda g: g["created_at"], reverse=True)
        
        return goals
