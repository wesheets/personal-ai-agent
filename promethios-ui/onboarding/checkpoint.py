"""
Onboarding Checkpoints Implementation

This module implements the checkpoint system for the agent onboarding process.
It provides functions for creating, validating, and reporting checkpoints
during the onboarding flow.
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional

class CheckpointSystem:
    """
    Checkpoint system for the agent onboarding process.
    
    This class manages the creation, validation, and reporting of checkpoints
    during the onboarding flow.
    """
    
    def __init__(self, agent_id: str, goal_id: str, checkpoint_dir: str = "/home/ubuntu/workspace/personal-ai-agent/logs/checkpoints"):
        """
        Initialize the checkpoint system for a specific agent and goal.
        
        Args:
            agent_id: ID of the agent
            goal_id: ID of the goal (typically onboarding goal)
            checkpoint_dir: Directory to store checkpoint files
        """
        self.agent_id = agent_id
        self.goal_id = goal_id
        self.checkpoint_dir = checkpoint_dir
        self.checkpoints = []
        
        # Ensure the checkpoint directory exists
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Create agent-specific directory
        self.agent_checkpoint_dir = os.path.join(checkpoint_dir, agent_id.lower())
        os.makedirs(self.agent_checkpoint_dir, exist_ok=True)
        
    def create_checkpoint(
        self,
        checkpoint_id: str,
        status: str,
        details: Dict[str, Any],
        memory_ids: Optional[List[str]] = None,
        escalation_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            status: Status of the checkpoint (complete, error, etc.)
            details: Additional details about the checkpoint
            memory_ids: Optional list of related memory IDs
            escalation_path: Optional escalation path for errors
            
        Returns:
            The created checkpoint object
        """
        if memory_ids is None:
            memory_ids = []
            
        # Generate checkpoint ID
        full_checkpoint_id = f"checkpoint_{checkpoint_id}_{self.agent_id}_{int(datetime.datetime.now().timestamp())}"
        
        # Create checkpoint object
        checkpoint = {
            "id": full_checkpoint_id,
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "goal_id": self.goal_id,
            "status": status,
            "details": details,
            "memory_ids": memory_ids,
            "tags": ["checkpoint", f"agent:{self.agent_id}", f"checkpoint:{checkpoint_id}"]
        }
        
        # Add escalation path if provided
        if escalation_path:
            checkpoint["escalation_path"] = escalation_path
            
        # Store the checkpoint
        self.checkpoints.append(checkpoint)
        self._save_checkpoint(checkpoint)
        
        return checkpoint
        
    def create_final_checkpoint(
        self,
        memory_ids: List[str],
        status: str = "complete",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create the final onboarding checkpoint.
        
        Args:
            memory_ids: List of related memory IDs
            status: Status of the checkpoint (complete, error, etc.)
            details: Optional additional details
            
        Returns:
            The created checkpoint object
        """
        if details is None:
            details = {}
            
        # Add standard details
        details.update({
            "onboarding_complete": True,
            "memory_count": len(memory_ids),
            "completion_time": datetime.datetime.now().isoformat()
        })
        
        # Create the checkpoint
        return self.create_checkpoint(
            checkpoint_id="agent_onboarding_complete",
            status=status,
            details=details,
            memory_ids=memory_ids,
            escalation_path="If agent fails to complete onboarding or errors, escalate to operator."
        )
        
    def create_error_checkpoint(
        self,
        error_message: str,
        step_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an error checkpoint.
        
        Args:
            error_message: Description of the error
            step_id: ID of the step where the error occurred
            details: Optional additional details
            
        Returns:
            The created checkpoint object
        """
        if details is None:
            details = {}
            
        # Add standard details
        details.update({
            "error_message": error_message,
            "step_id": step_id,
            "error_time": datetime.datetime.now().isoformat()
        })
        
        # Create the checkpoint
        return self.create_checkpoint(
            checkpoint_id=f"error_{step_id}",
            status="error",
            details=details,
            escalation_path=f"Error in step {step_id}: {error_message}. Escalate to operator for resolution."
        )
        
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a checkpoint by ID.
        
        Args:
            checkpoint_id: ID of the checkpoint to retrieve
            
        Returns:
            The checkpoint object if found, None otherwise
        """
        for checkpoint in self.checkpoints:
            if checkpoint["checkpoint_id"] == checkpoint_id:
                return checkpoint
        return None
        
    def get_checkpoints_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get checkpoints by status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of matching checkpoints
        """
        return [c for c in self.checkpoints if c["status"] == status]
        
    def has_completed_onboarding(self) -> bool:
        """
        Check if the agent has completed onboarding.
        
        Returns:
            True if the final checkpoint exists and is complete, False otherwise
        """
        final_checkpoint = self.get_checkpoint("agent_onboarding_complete")
        return final_checkpoint is not None and final_checkpoint["status"] == "complete"
        
    def get_checkpoint_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all checkpoints.
        
        Returns:
            Dictionary containing checkpoint summary
        """
        # Count checkpoints by status
        status_counts = {}
        for checkpoint in self.checkpoints:
            status = checkpoint["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            
        # Check for final checkpoint
        final_checkpoint = self.get_checkpoint("agent_onboarding_complete")
        
        return {
            "total_checkpoints": len(self.checkpoints),
            "by_status": status_counts,
            "has_final_checkpoint": final_checkpoint is not None,
            "onboarding_complete": self.has_completed_onboarding(),
            "latest_checkpoint": self.checkpoints[-1]["checkpoint_id"] if self.checkpoints else None
        }
        
    def _save_checkpoint(self, checkpoint: Dict[str, Any]) -> str:
        """
        Save a checkpoint to a file.
        
        Args:
            checkpoint: The checkpoint to save
            
        Returns:
            Path to the saved checkpoint file
        """
        # Generate filename
        filename = f"{checkpoint['id']}.json"
        filepath = os.path.join(self.agent_checkpoint_dir, filename)
        
        # Write checkpoint to file
        with open(filepath, "w") as f:
            json.dump(checkpoint, f, indent=2)
            
        return filepath
        
    def load_checkpoints(self) -> None:
        """Load all checkpoints for the current agent from files."""
        self.checkpoints = []
        
        # Check if agent checkpoint directory exists
        if not os.path.exists(self.agent_checkpoint_dir):
            return
            
        # Load all checkpoint files
        for filename in os.listdir(self.agent_checkpoint_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.agent_checkpoint_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        checkpoint = json.load(f)
                        self.checkpoints.append(checkpoint)
                except Exception as e:
                    print(f"Error loading checkpoint from {filepath}: {e}")
                    
        # Sort checkpoints by timestamp
        self.checkpoints.sort(key=lambda c: c["timestamp"])
