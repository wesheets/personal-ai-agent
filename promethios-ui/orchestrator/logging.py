"""
Orchestrator Logging System

This module implements the real-time narration and logging system for the Orchestrator,
providing transparent progress updates and maintaining a comprehensive action log.
"""

import os
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple

class OrchestratorLogger:
    """
    Manages logging and narration for the Orchestrator.
    
    This class provides methods for logging various types of events and actions,
    maintaining a comprehensive action log, and writing system update and decision
    memories.
    """
    
    def __init__(
        self,
        logs_directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs",
        memory_writer = None  # Will be initialized later to avoid circular imports
    ):
        """
        Initialize the orchestrator logger.
        
        Args:
            logs_directory: Directory to store log files
            memory_writer: Function to write memories (initialized later)
        """
        self.logs_directory = logs_directory
        self.action_log_path = os.path.join(logs_directory, "orchestrator_action_log.json")
        self.memory_writer = memory_writer
        
        # Ensure the logs directory exists
        os.makedirs(logs_directory, exist_ok=True)
        
        # Initialize the action log if it doesn't exist
        if not os.path.exists(self.action_log_path):
            with open(self.action_log_path, "w") as f:
                json.dump([], f)
                
    def set_memory_writer(self, memory_writer):
        """
        Set the memory writer function.
        
        Args:
            memory_writer: Function to write memories
        """
        self.memory_writer = memory_writer
        
    def log_action(
        self,
        action_type: str,
        description: str,
        goal_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        write_memory: bool = True
    ) -> str:
        """
        Log an orchestrator action.
        
        Args:
            action_type: Type of action (consultation, planning, delegation, checkpoint, approval, execution)
            description: Natural language description of the action
            goal_id: Optional ID of the related goal
            details: Optional additional details about the action
            write_memory: Whether to write a memory for this action
            
        Returns:
            ID of the logged action
        """
        # Generate a unique ID for this action
        action_id = str(uuid.uuid4())
        
        # Create the action log entry
        log_entry = {
            "log_id": action_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "action_type": action_type,
            "description": description,
            "goal_id": goal_id,
            "details": details or {}
        }
        
        # Append to the action log
        self._append_to_action_log(log_entry)
        
        # Write a memory if requested and memory_writer is available
        if write_memory and self.memory_writer and goal_id:
            memory_type = "decision" if action_type in ["planning", "approval"] else "system_update"
            self.memory_writer(
                goal_id=goal_id,
                agent_id="orchestrator",
                memory_type=memory_type,
                content=description,
                tags=["orchestrator", action_type]
            )
            
        return action_id
        
    def _append_to_action_log(self, log_entry: Dict[str, Any]) -> None:
        """
        Append an entry to the action log.
        
        Args:
            log_entry: Log entry to append
        """
        try:
            # Read the current log
            with open(self.action_log_path, "r") as f:
                log = json.load(f)
                
            # Append the new entry
            log.append(log_entry)
            
            # Write the updated log
            with open(self.action_log_path, "w") as f:
                json.dump(log, f, indent=2)
        except Exception as e:
            print(f"Error appending to action log: {e}")
            
    def log_consultation_start(self, goal: str, operator_id: str, session_id: str) -> str:
        """
        Log the start of a consultation session.
        
        Args:
            goal: Goal statement from the operator
            operator_id: ID of the operator
            session_id: ID of the consultation session
            
        Returns:
            ID of the logged action
        """
        description = f"✔️ Received goal: \"{goal}\"\n✔️ Starting consultation phase"
        details = {
            "operator_id": operator_id,
            "session_id": session_id
        }
        
        return self.log_action(
            action_type="consultation",
            description=description,
            details=details,
            write_memory=False  # No goal_id yet
        )
        
    def log_consultation_questions(self, session_id: str, question_count: int) -> str:
        """
        Log the asking of consultation questions.
        
        Args:
            session_id: ID of the consultation session
            question_count: Number of questions being asked
            
        Returns:
            ID of the logged action
        """
        description = f"✔️ Asking {question_count} strategic questions..."
        details = {
            "session_id": session_id,
            "question_count": question_count
        }
        
        return self.log_action(
            action_type="consultation",
            description=description,
            details=details,
            write_memory=False  # No goal_id yet
        )
        
    def log_plan_creation(self, session_id: str, plan_title: str, phase_count: int) -> str:
        """
        Log the creation of a plan.
        
        Args:
            session_id: ID of the consultation session
            plan_title: Title of the plan
            phase_count: Number of phases in the plan
            
        Returns:
            ID of the logged action
        """
        description = f"✔️ Drafting {phase_count}-phase roadmap: \"{plan_title}\"..."
        details = {
            "session_id": session_id,
            "plan_title": plan_title,
            "phase_count": phase_count
        }
        
        return self.log_action(
            action_type="planning",
            description=description,
            details=details,
            write_memory=False  # No goal_id yet
        )
        
    def log_awaiting_approval(self, session_id: str) -> str:
        """
        Log that the orchestrator is awaiting operator approval.
        
        Args:
            session_id: ID of the consultation session
            
        Returns:
            ID of the logged action
        """
        description = "✔️ Awaiting operator approval..."
        details = {
            "session_id": session_id
        }
        
        return self.log_action(
            action_type="approval",
            description=description,
            details=details,
            write_memory=False  # No goal_id yet
        )
        
    def log_plan_approved(self, session_id: str, goal_id: str) -> str:
        """
        Log that a plan has been approved.
        
        Args:
            session_id: ID of the consultation session
            goal_id: ID of the created goal
            
        Returns:
            ID of the logged action
        """
        description = "✔️ Plan approved! Switching to tactical execution mode."
        details = {
            "session_id": session_id,
            "goal_id": goal_id
        }
        
        return self.log_action(
            action_type="approval",
            description=description,
            goal_id=goal_id,
            details=details
        )
        
    def log_task_delegation(self, goal_id: str, agent_id: str, task_title: str, tools: List[str]) -> str:
        """
        Log the delegation of a task to an agent.
        
        Args:
            goal_id: ID of the goal
            agent_id: ID of the agent being assigned
            task_title: Title of the task
            tools: List of tools the agent will use
            
        Returns:
            ID of the logged action
        """
        tool_str = ", ".join(tools[:2])
        if len(tools) > 2:
            tool_str += f" and {len(tools) - 2} more"
            
        description = f"✔️ {agent_id.upper()} assigned: {task_title} using {tool_str}"
        details = {
            "agent_id": agent_id,
            "task_title": task_title,
            "tools": tools
        }
        
        return self.log_action(
            action_type="delegation",
            description=description,
            goal_id=goal_id,
            details=details
        )
        
    def log_checkpoint_created(self, goal_id: str, checkpoint_name: str, checkpoint_type: str, agent_id: str) -> str:
        """
        Log the creation of a checkpoint.
        
        Args:
            goal_id: ID of the goal
            checkpoint_name: Name of the checkpoint
            checkpoint_type: Type of checkpoint ("hard" or "soft")
            agent_id: ID of the agent that created the checkpoint
            
        Returns:
            ID of the logged action
        """
        description = f"✔️ Waiting for checkpoint: \"{checkpoint_name}\" ({checkpoint_type} checkpoint from {agent_id.upper()})"
        details = {
            "checkpoint_name": checkpoint_name,
            "checkpoint_type": checkpoint_type,
            "agent_id": agent_id
        }
        
        return self.log_action(
            action_type="checkpoint",
            description=description,
            goal_id=goal_id,
            details=details
        )
        
    def log_checkpoint_approved(self, goal_id: str, checkpoint_name: str, agent_id: str) -> str:
        """
        Log the approval of a checkpoint.
        
        Args:
            goal_id: ID of the goal
            checkpoint_name: Name of the checkpoint
            agent_id: ID of the agent that created the checkpoint
            
        Returns:
            ID of the logged action
        """
        description = f"✔️ Checkpoint approved: \"{checkpoint_name}\" from {agent_id.upper()}"
        details = {
            "checkpoint_name": checkpoint_name,
            "agent_id": agent_id
        }
        
        return self.log_action(
            action_type="approval",
            description=description,
            goal_id=goal_id,
            details=details
        )
        
    def log_checkpoint_rejected(self, goal_id: str, checkpoint_name: str, agent_id: str, feedback: str) -> str:
        """
        Log the rejection of a checkpoint.
        
        Args:
            goal_id: ID of the goal
            checkpoint_name: Name of the checkpoint
            agent_id: ID of the agent that created the checkpoint
            feedback: Feedback explaining the rejection
            
        Returns:
            ID of the logged action
        """
        description = f"✔️ Checkpoint rejected: \"{checkpoint_name}\" from {agent_id.upper()}\n✔️ Feedback: {feedback}"
        details = {
            "checkpoint_name": checkpoint_name,
            "agent_id": agent_id,
            "feedback": feedback
        }
        
        return self.log_action(
            action_type="approval",
            description=description,
            goal_id=goal_id,
            details=details
        )
        
    def log_credentials_stored(self, goal_id: str, credential_types: List[str]) -> str:
        """
        Log the storage of credentials.
        
        Args:
            goal_id: ID of the goal
            credential_types: Types of credentials stored
            
        Returns:
            ID of the logged action
        """
        credential_str = ", ".join(credential_types)
        description = f"✔️ Credentials stored: {credential_str}"
        details = {
            "credential_types": credential_types
        }
        
        return self.log_action(
            action_type="execution",
            description=description,
            goal_id=goal_id,
            details=details
        )
        
    def log_phase_started(self, goal_id: str, phase_title: str, phase_number: int, total_phases: int) -> str:
        """
        Log the start of a phase.
        
        Args:
            goal_id: ID of the goal
            phase_title: Title of the phase
            phase_number: Number of the phase (1-based)
            total_phases: Total number of phases
            
        Returns:
            ID of the logged action
        """
        description = f"✔️ Starting Phase {phase_number}/{total_phases}: {phase_title}"
        details = {
            "phase_title": phase_title,
            "phase_number": phase_number,
            "total_phases": total_phases
        }
        
        return self.log_action(
            action_type="execution",
            description=description,
            goal_id=goal_id,
            details=details
        )
        
    def log_phase_completed(self, goal_id: str, phase_title: str, phase_number: int, total_phases: int) -> str:
        """
        Log the completion of a phase.
        
        Args:
            goal_id: ID of the goal
            phase_title: Title of the phase
            phase_number: Number of the phase (1-based)
            total_phases: Total number of phases
            
        Returns:
            ID of the logged action
        """
        description = f"✔️ Completed Phase {phase_number}/{total_phases}: {phase_title}"
        details = {
            "phase_title": phase_title,
            "phase_number": phase_number,
            "total_phases": total_phases
        }
        
        return self.log_action(
            action_type="execution",
            description=description,
            goal_id=goal_id,
            details=details
        )
        
    def log_goal_completed(self, goal_id: str, goal_title: str) -> str:
        """
        Log the completion of a goal.
        
        Args:
            goal_id: ID of the goal
            goal_title: Title of the goal
            
        Returns:
            ID of the logged action
        """
        description = f"✔️ Goal completed: \"{goal_title}\""
        details = {
            "goal_title": goal_title
        }
        
        return self.log_action(
            action_type="execution",
            description=description,
            goal_id=goal_id,
            details=details
        )
        
    def log_error(self, error_message: str, goal_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log an error.
        
        Args:
            error_message: Error message
            goal_id: Optional ID of the related goal
            details: Optional additional details about the error
            
        Returns:
            ID of the logged action
        """
        description = f"❌ Error: {error_message}"
        
        return self.log_action(
            action_type="error",
            description=description,
            goal_id=goal_id,
            details=details or {}
        )
        
    def get_action_log(self, limit: Optional[int] = None, goal_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the action log, optionally filtered by goal and limited to a number of entries.
        
        Args:
            limit: Optional maximum number of entries to return
            goal_id: Optional goal ID to filter by
            
        Returns:
            List of action log entries
        """
        try:
            # Read the action log
            with open(self.action_log_path, "r") as f:
                log = json.load(f)
                
            # Filter by goal_id if provided
            if goal_id:
                log = [entry for entry in log if entry.get("goal_id") == goal_id]
                
            # Sort by timestamp (newest first)
            log.sort(key=lambda entry: entry["timestamp"], reverse=True)
            
            # Limit if specified
            if limit:
                log = log[:limit]
                
            return log
        except Exception as e:
            print(f"Error reading action log: {e}")
            return []
            
    def get_action_log_for_session(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the action log for a specific consultation session.
        
        Args:
            session_id: ID of the consultation session
            
        Returns:
            List of action log entries
        """
        try:
            # Read the action log
            with open(self.action_log_path, "r") as f:
                log = json.load(f)
                
            # Filter by session_id
            log = [
                entry for entry in log 
                if entry.get("details", {}).get("session_id") == session_id
            ]
            
            # Sort by timestamp
            log.sort(key=lambda entry: entry["timestamp"])
            
            return log
        except Exception as e:
            print(f"Error reading action log: {e}")
            return []
            
    def generate_progress_report(self, goal_id: str) -> Dict[str, Any]:
        """
        Generate a progress report for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Progress report dictionary
        """
        # Get the action log for this goal
        log = self.get_action_log(goal_id=goal_id)
        
        # Count actions by type
        action_counts = {}
        for entry in log:
            action_type = entry["action_type"]
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
            
        # Get the first and last timestamps
        timestamps = [entry["timestamp"] for entry in log]
        start_time = min(timestamps) if timestamps else None
        last_update = max(timestamps) if timestamps else None
        
        # Calculate duration
        duration = None
        if start_time and last_update:
            start_dt = datetime.datetime.fromisoformat(start_time)
            last_dt = datetime.datetime.fromisoformat(last_update)
            duration = (last_dt - start_dt).total_seconds()
            
        # Generate the report
        report = {
            "goal_id": goal_id,
            "action_count": len(log),
            "action_counts": action_counts,
            "start_time": start_time,
            "last_update": last_update,
            "duration_seconds": duration,
            "recent_actions": log[:5]  # Include the 5 most recent actions
        }
        
        return report
        
    def save_progress_report(self, goal_id: str) -> str:
        """
        Generate and save a progress report for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Path to the saved report file
        """
        # Generate the report
        report = self.generate_progress_report(goal_id)
        
        # Ensure the reports directory exists
        reports_dir = os.path.join(self.logs_directory, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate the filename
        filename = f"progress_report_{goal_id}.json"
        filepath = os.path.join(reports_dir, filename)
        
        # Write the report to file
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
            
        return filepath
