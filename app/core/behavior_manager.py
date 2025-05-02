import os
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class BehaviorFeedbackData(BaseModel):
    """Model for behavior feedback data"""
    feedback_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    task_description: str
    was_successful: bool
    user_notes: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    task_metadata: Dict[str, Any] = Field(default_factory=dict)

class BehaviorManager:
    """
    Manager for behavior feedback loop
    
    This class handles storing and retrieving behavior feedback data
    to help agents adapt their behavior over time.
    """
    
    def __init__(self):
        """Initialize the BehaviorManager"""
        # Set up logging directory
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "behavior_logs")
        os.makedirs(self.logs_dir, exist_ok=True)
    
    async def record_feedback(
        self,
        agent_name: str,
        task_description: str,
        was_successful: bool,
        user_notes: Optional[str] = None,
        task_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record behavior feedback
        
        Args:
            agent_name: Name of the agent
            task_description: Description of the task
            was_successful: Whether the task was successful
            user_notes: Optional notes from the user
            task_metadata: Additional metadata about the task
            
        Returns:
            ID of the recorded feedback
        """
        # Create feedback data
        feedback_data = BehaviorFeedbackData(
            agent_name=agent_name,
            task_description=task_description,
            was_successful=was_successful,
            user_notes=user_notes,
            task_metadata=task_metadata or {}
        )
        
        # Ensure agent directory exists
        agent_dir = os.path.join(self.logs_dir, agent_name)
        os.makedirs(agent_dir, exist_ok=True)
        
        # Save feedback data
        feedback_file = os.path.join(agent_dir, f"{feedback_data.feedback_id}.json")
        with open(feedback_file, "w") as f:
            json.dump(feedback_data.dict(), f, indent=2)
        
        return feedback_data.feedback_id
    
    async def get_agent_feedback(
        self,
        agent_name: str,
        limit: int = 10,
        offset: int = 0,
        successful_only: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get feedback for a specific agent
        
        Args:
            agent_name: Name of the agent
            limit: Maximum number of feedback entries to return
            offset: Offset for pagination
            successful_only: Filter by success status
            
        Returns:
            List of feedback data
        """
        # Ensure agent directory exists
        agent_dir = os.path.join(self.logs_dir, agent_name)
        if not os.path.exists(agent_dir):
            return []
        
        # Get all feedback files
        feedback_files = [f for f in os.listdir(agent_dir) if f.endswith(".json")]
        
        # Sort by modification time (newest first)
        feedback_files.sort(key=lambda f: os.path.getmtime(os.path.join(agent_dir, f)), reverse=True)
        
        # Load and filter feedback data
        feedback_entries = []
        for feedback_file in feedback_files:
            with open(os.path.join(agent_dir, feedback_file), "r") as f:
                data = json.load(f)
                
                # Apply success filter if specified
                if successful_only is not None and data.get("was_successful") != successful_only:
                    continue
                
                feedback_entries.append(data)
        
        # Apply pagination
        feedback_entries = feedback_entries[offset:offset + limit]
        
        return feedback_entries
    
    async def get_feedback_summary(
        self,
        agent_name: str,
        recent_count: int = 10
    ) -> Dict[str, Any]:
        """
        Get a summary of feedback for a specific agent
        
        Args:
            agent_name: Name of the agent
            recent_count: Number of recent entries to consider for recent success rate
            
        Returns:
            Summary of feedback data
        """
        # Get all feedback for the agent
        all_feedback = await self.get_agent_feedback(agent_name, limit=1000)
        
        # Calculate total tasks
        total_tasks = len(all_feedback)
        
        if total_tasks == 0:
            return {
                "agent_name": agent_name,
                "total_tasks": 0,
                "success_rate": 0.0,
                "recent_success_rate": 0.0,
                "has_feedback": False
            }
        
        # Calculate overall success rate
        successful_tasks = sum(1 for entry in all_feedback if entry.get("was_successful", False))
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0.0
        
        # Calculate recent success rate
        recent_feedback = all_feedback[:recent_count]
        recent_successful = sum(1 for entry in recent_feedback if entry.get("was_successful", False))
        recent_success_rate = recent_successful / len(recent_feedback) if recent_feedback else 0.0
        
        # Get common user notes themes (simplified implementation)
        user_notes = [entry.get("user_notes", "") for entry in all_feedback if entry.get("user_notes")]
        
        return {
            "agent_name": agent_name,
            "total_tasks": total_tasks,
            "success_rate": success_rate,
            "recent_success_rate": recent_success_rate,
            "recent_count": min(recent_count, total_tasks),
            "has_feedback": True,
            "user_notes_count": len(user_notes)
        }
    
    async def get_recent_feedback_context(
        self,
        agent_name: str,
        limit: int = 5
    ) -> str:
        """
        Get a formatted context string of recent feedback for prompting
        
        Args:
            agent_name: Name of the agent
            limit: Maximum number of feedback entries to include
            
        Returns:
            Formatted context string
        """
        # Get recent feedback
        recent_feedback = await self.get_agent_feedback(agent_name, limit=limit)
        
        if not recent_feedback:
            return ""
        
        # Format the feedback as a context string
        context_parts = ["## Recent Behavior Feedback"]
        
        for i, feedback in enumerate(recent_feedback):
            success_str = "✓ Successful" if feedback.get("was_successful", False) else "✗ Unsuccessful"
            context_parts.append(f"\n### Feedback {i+1}: {success_str}")
            context_parts.append(f"Task: {feedback.get('task_description', 'Unknown task')}")
            
            if feedback.get("user_notes"):
                context_parts.append(f"User notes: {feedback.get('user_notes')}")
            
            context_parts.append("")  # Empty line between entries
        
        # Add summary
        summary = await self.get_feedback_summary(agent_name)
        context_parts.append("### Overall Performance")
        context_parts.append(f"Success rate: {summary.get('success_rate', 0.0) * 100:.1f}%")
        context_parts.append(f"Recent success rate: {summary.get('recent_success_rate', 0.0) * 100:.1f}%")
        context_parts.append("")
        
        return "\n".join(context_parts)

# Singleton instance
_behavior_manager = None

def get_behavior_manager() -> BehaviorManager:
    """
    Get the singleton BehaviorManager instance
    """
    global _behavior_manager
    if _behavior_manager is None:
        _behavior_manager = BehaviorManager()
    return _behavior_manager
