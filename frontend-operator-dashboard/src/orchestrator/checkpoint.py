"""
Orchestrator Checkpoint Layer

This module implements the execution checkpoint layer for the Orchestrator, allowing
agents to report task completion and await operator approval before proceeding.
"""

import os
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple

class Checkpoint:
    """
    Represents a checkpoint in the execution flow.
    
    This class manages the creation, storage, and approval of checkpoints
    that agents create during task execution.
    """
    
    def __init__(
        self,
        checkpoint_name: str,
        checkpoint_type: str,
        goal_id: str,
        subgoal_id: str,
        agent_id: str,
        output_memory_id: str,
        auto_approve_if_silent: bool = False,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new checkpoint.
        
        Args:
            checkpoint_name: Name of the checkpoint
            checkpoint_type: Type of checkpoint ("hard" or "soft")
            goal_id: ID of the goal this checkpoint belongs to
            subgoal_id: ID of the subgoal this checkpoint belongs to
            agent_id: ID of the agent that created this checkpoint
            output_memory_id: ID of the memory containing the output
            auto_approve_if_silent: Whether to auto-approve if no response
            details: Additional details about the checkpoint
        """
        self.checkpoint_id = str(uuid.uuid4())
        self.checkpoint_name = checkpoint_name
        self.checkpoint_type = checkpoint_type
        self.goal_id = goal_id
        self.subgoal_id = subgoal_id
        self.agent_id = agent_id
        self.status = "pending"  # pending, approved, rejected
        self.auto_approve_if_silent = auto_approve_if_silent
        self.output_memory_id = output_memory_id
        self.details = details or {}
        self.created_at = datetime.datetime.now().isoformat()
        self.approved_at = None
        self.feedback = None
        self.modifications = None
        
    def approve(self, feedback: Optional[str] = None, modifications: Optional[Dict[str, Any]] = None) -> None:
        """
        Approve this checkpoint.
        
        Args:
            feedback: Optional feedback from the operator
            modifications: Optional modifications to the output
        """
        self.status = "approved"
        self.approved_at = datetime.datetime.now().isoformat()
        self.feedback = feedback
        self.modifications = modifications
        
    def reject(self, feedback: str) -> None:
        """
        Reject this checkpoint.
        
        Args:
            feedback: Feedback from the operator explaining the rejection
        """
        self.status = "rejected"
        self.approved_at = datetime.datetime.now().isoformat()
        self.feedback = feedback
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the checkpoint to a dictionary.
        
        Returns:
            Dictionary representation of the checkpoint
        """
        return {
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_name": self.checkpoint_name,
            "checkpoint_type": self.checkpoint_type,
            "goal_id": self.goal_id,
            "subgoal_id": self.subgoal_id,
            "agent_id": self.agent_id,
            "status": self.status,
            "auto_approve_if_silent": self.auto_approve_if_silent,
            "output_memory_id": self.output_memory_id,
            "details": self.details,
            "created_at": self.created_at,
            "approved_at": self.approved_at,
            "feedback": self.feedback,
            "modifications": self.modifications
        }
        
    def save(self, directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/checkpoints") -> str:
        """
        Save the checkpoint to a file.
        
        Args:
            directory: Directory to save the checkpoint file
            
        Returns:
            Path to the saved checkpoint file
        """
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Generate the filename
        filename = f"checkpoint_{self.checkpoint_id}.json"
        filepath = os.path.join(directory, filename)
        
        # Write the checkpoint to file
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            
        return filepath
        
    @classmethod
    def load(cls, checkpoint_id: str, directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/checkpoints") -> "Checkpoint":
        """
        Load a checkpoint from a file.
        
        Args:
            checkpoint_id: ID of the checkpoint to load
            directory: Directory where checkpoint files are stored
            
        Returns:
            Loaded Checkpoint object
        """
        # Generate the filepath
        filename = f"checkpoint_{checkpoint_id}.json"
        filepath = os.path.join(directory, filename)
        
        # Read the checkpoint from file
        with open(filepath, "r") as f:
            checkpoint_data = json.load(f)
            
        # Create a new checkpoint object
        checkpoint = cls(
            checkpoint_name=checkpoint_data["checkpoint_name"],
            checkpoint_type=checkpoint_data["checkpoint_type"],
            goal_id=checkpoint_data["goal_id"],
            subgoal_id=checkpoint_data["subgoal_id"],
            agent_id=checkpoint_data["agent_id"],
            output_memory_id=checkpoint_data["output_memory_id"],
            auto_approve_if_silent=checkpoint_data["auto_approve_if_silent"],
            details=checkpoint_data["details"]
        )
        
        # Update the checkpoint with the loaded data
        checkpoint.checkpoint_id = checkpoint_data["checkpoint_id"]
        checkpoint.status = checkpoint_data["status"]
        checkpoint.created_at = checkpoint_data["created_at"]
        checkpoint.approved_at = checkpoint_data["approved_at"]
        checkpoint.feedback = checkpoint_data["feedback"]
        checkpoint.modifications = checkpoint_data["modifications"]
        
        return checkpoint


class CheckpointManager:
    """
    Manages checkpoints in the execution flow.
    
    This class provides methods for creating, retrieving, and approving
    checkpoints during task execution.
    """
    
    def __init__(self, checkpoints_directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/checkpoints"):
        """
        Initialize the checkpoint manager.
        
        Args:
            checkpoints_directory: Directory to store checkpoint files
        """
        self.checkpoints_directory = checkpoints_directory
        os.makedirs(checkpoints_directory, exist_ok=True)
        self.active_checkpoints = {}
        
    def create_checkpoint(
        self,
        checkpoint_name: str,
        checkpoint_type: str,
        goal_id: str,
        subgoal_id: str,
        agent_id: str,
        output_memory_id: str,
        auto_approve_if_silent: bool = False,
        details: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """
        Create a new checkpoint.
        
        Args:
            checkpoint_name: Name of the checkpoint
            checkpoint_type: Type of checkpoint ("hard" or "soft")
            goal_id: ID of the goal this checkpoint belongs to
            subgoal_id: ID of the subgoal this checkpoint belongs to
            agent_id: ID of the agent that created this checkpoint
            output_memory_id: ID of the memory containing the output
            auto_approve_if_silent: Whether to auto-approve if no response
            details: Additional details about the checkpoint
            
        Returns:
            Created Checkpoint object
        """
        # Validate checkpoint type
        if checkpoint_type not in ["hard", "soft"]:
            raise ValueError("checkpoint_type must be either 'hard' or 'soft'")
            
        # Create the checkpoint
        checkpoint = Checkpoint(
            checkpoint_name=checkpoint_name,
            checkpoint_type=checkpoint_type,
            goal_id=goal_id,
            subgoal_id=subgoal_id,
            agent_id=agent_id,
            output_memory_id=output_memory_id,
            auto_approve_if_silent=auto_approve_if_silent,
            details=details
        )
        
        # Save the checkpoint
        checkpoint.save(self.checkpoints_directory)
        
        # Add to active checkpoints
        self.active_checkpoints[checkpoint.checkpoint_id] = checkpoint
        
        return checkpoint
        
    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint:
        """
        Get a checkpoint by ID.
        
        Args:
            checkpoint_id: ID of the checkpoint to retrieve
            
        Returns:
            Checkpoint object
        """
        # Check if the checkpoint is already in memory
        if checkpoint_id in self.active_checkpoints:
            return self.active_checkpoints[checkpoint_id]
            
        # Try to load the checkpoint from file
        try:
            checkpoint = Checkpoint.load(checkpoint_id, self.checkpoints_directory)
            self.active_checkpoints[checkpoint_id] = checkpoint
            return checkpoint
        except FileNotFoundError:
            raise ValueError(f"Checkpoint with ID {checkpoint_id} not found")
            
    def approve_checkpoint(
        self,
        checkpoint_id: str,
        feedback: Optional[str] = None,
        modifications: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """
        Approve a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to approve
            feedback: Optional feedback from the operator
            modifications: Optional modifications to the output
            
        Returns:
            Updated Checkpoint object
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        checkpoint.approve(feedback, modifications)
        checkpoint.save(self.checkpoints_directory)
        return checkpoint
        
    def reject_checkpoint(self, checkpoint_id: str, feedback: str) -> Checkpoint:
        """
        Reject a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to reject
            feedback: Feedback from the operator explaining the rejection
            
        Returns:
            Updated Checkpoint object
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        checkpoint.reject(feedback)
        checkpoint.save(self.checkpoints_directory)
        return checkpoint
        
    def list_checkpoints(
        self,
        goal_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List checkpoints, optionally filtered by goal, agent, or status.
        
        Args:
            goal_id: Optional goal ID to filter by
            agent_id: Optional agent ID to filter by
            status: Optional status to filter by
            
        Returns:
            List of checkpoint summary dictionaries
        """
        checkpoints = []
        
        # List all checkpoint files in the directory
        for filename in os.listdir(self.checkpoints_directory):
            if filename.startswith("checkpoint_") and filename.endswith(".json"):
                filepath = os.path.join(self.checkpoints_directory, filename)
                
                try:
                    with open(filepath, "r") as f:
                        checkpoint_data = json.load(f)
                        
                    # Apply filters
                    if goal_id is not None and checkpoint_data["goal_id"] != goal_id:
                        continue
                        
                    if agent_id is not None and checkpoint_data["agent_id"] != agent_id:
                        continue
                        
                    if status is not None and checkpoint_data["status"] != status:
                        continue
                        
                    # Create a summary of the checkpoint
                    summary = {
                        "checkpoint_id": checkpoint_data["checkpoint_id"],
                        "checkpoint_name": checkpoint_data["checkpoint_name"],
                        "checkpoint_type": checkpoint_data["checkpoint_type"],
                        "goal_id": checkpoint_data["goal_id"],
                        "subgoal_id": checkpoint_data["subgoal_id"],
                        "agent_id": checkpoint_data["agent_id"],
                        "status": checkpoint_data["status"],
                        "created_at": checkpoint_data["created_at"],
                        "approved_at": checkpoint_data["approved_at"],
                        "output_memory_id": checkpoint_data["output_memory_id"]
                    }
                    
                    checkpoints.append(summary)
                except Exception as e:
                    print(f"Error loading checkpoint from {filepath}: {e}")
                    
        # Sort checkpoints by created_at (newest first)
        checkpoints.sort(key=lambda c: c["created_at"], reverse=True)
        
        return checkpoints
        
    def get_pending_checkpoints(self, goal_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all pending checkpoints, optionally filtered by goal.
        
        Args:
            goal_id: Optional goal ID to filter by
            
        Returns:
            List of pending checkpoint summaries
        """
        return self.list_checkpoints(goal_id=goal_id, status="pending")
        
    def get_hard_checkpoints(self, goal_id: str) -> List[Dict[str, Any]]:
        """
        Get all hard checkpoints for a goal.
        
        Args:
            goal_id: Goal ID to filter by
            
        Returns:
            List of hard checkpoint summaries
        """
        checkpoints = self.list_checkpoints(goal_id=goal_id)
        return [c for c in checkpoints if c["checkpoint_type"] == "hard"]
        
    def get_soft_checkpoints(self, goal_id: str) -> List[Dict[str, Any]]:
        """
        Get all soft checkpoints for a goal.
        
        Args:
            goal_id: Goal ID to filter by
            
        Returns:
            List of soft checkpoint summaries
        """
        checkpoints = self.list_checkpoints(goal_id=goal_id)
        return [c for c in checkpoints if c["checkpoint_type"] == "soft"]
        
    def auto_approve_eligible_checkpoints(self) -> List[str]:
        """
        Auto-approve eligible soft checkpoints that have auto_approve_if_silent set.
        
        Returns:
            List of IDs of auto-approved checkpoints
        """
        auto_approved = []
        
        # Get all pending checkpoints
        pending = self.list_checkpoints(status="pending")
        
        for checkpoint_summary in pending:
            try:
                checkpoint = self.get_checkpoint(checkpoint_summary["checkpoint_id"])
                
                # Check if this checkpoint is eligible for auto-approval
                if checkpoint.checkpoint_type == "soft" and checkpoint.auto_approve_if_silent:
                    # Auto-approve the checkpoint
                    checkpoint.approve(feedback="Auto-approved due to auto_approve_if_silent setting")
                    checkpoint.save(self.checkpoints_directory)
                    auto_approved.append(checkpoint.checkpoint_id)
            except Exception as e:
                print(f"Error auto-approving checkpoint {checkpoint_summary['checkpoint_id']}: {e}")
                
        return auto_approved
        
    def can_proceed(self, goal_id: str, subgoal_id: str) -> bool:
        """
        Check if execution can proceed for a subgoal.
        
        Args:
            goal_id: ID of the goal
            subgoal_id: ID of the subgoal
            
        Returns:
            True if execution can proceed, False if blocked by pending hard checkpoints
        """
        # Get all pending checkpoints for this goal and subgoal
        pending = self.list_checkpoints(goal_id=goal_id, status="pending")
        pending_for_subgoal = [c for c in pending if c["subgoal_id"] == subgoal_id]
        
        # Check if there are any pending hard checkpoints
        for checkpoint in pending_for_subgoal:
            if checkpoint["checkpoint_type"] == "hard":
                return False
                
        return True
