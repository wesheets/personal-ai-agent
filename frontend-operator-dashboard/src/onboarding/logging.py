"""
Logging and Tagging System for Agent Onboarding

This module implements the logging and tagging functionality for the agent onboarding process.
It provides functions for creating structured logs with appropriate tags and
generating reports on the onboarding process.
"""

import os
import json
import datetime
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('onboarding')

class OnboardingLogger:
    """
    Logger for the agent onboarding process.
    
    This class manages the creation of structured logs with appropriate tags
    and generates reports on the onboarding process.
    """
    
    def __init__(self, agent_id: str, log_dir: str = "/home/ubuntu/workspace/personal-ai-agent/logs"):
        """
        Initialize the onboarding logger for a specific agent.
        
        Args:
            agent_id: ID of the agent being onboarded
            log_dir: Directory to store log files
        """
        self.agent_id = agent_id
        self.log_dir = log_dir
        self.logs = []
        
        # Ensure the log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up file handler for agent-specific logs
        self.log_file = os.path.join(log_dir, f"onboarding_{agent_id.lower()}_log.json")
        
        # Initialize log file if it doesn't exist
        if not os.path.exists(self.log_file):
            self._initialize_log_file()
        else:
            # Load existing logs
            self._load_logs()
            
    def _initialize_log_file(self) -> None:
        """Initialize the log file with basic structure."""
        initial_log = {
            "agent_id": self.agent_id,
            "onboarding_started": datetime.datetime.now().isoformat(),
            "logs": [],
            "status": "initialized"
        }
        
        with open(self.log_file, "w") as f:
            json.dump(initial_log, f, indent=2)
            
    def _load_logs(self) -> None:
        """Load existing logs from the log file."""
        try:
            with open(self.log_file, "r") as f:
                log_data = json.load(f)
                self.logs = log_data.get("logs", [])
        except Exception as e:
            logger.error(f"Error loading logs from {self.log_file}: {e}")
            self.logs = []
            
    def _save_logs(self) -> None:
        """Save logs to the log file."""
        try:
            # Load current file content to preserve metadata
            with open(self.log_file, "r") as f:
                log_data = json.load(f)
                
            # Update logs and last updated timestamp
            log_data["logs"] = self.logs
            log_data["last_updated"] = datetime.datetime.now().isoformat()
            
            # Write back to file
            with open(self.log_file, "w") as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving logs to {self.log_file}: {e}")
            
    def log_event(
        self,
        event_type: str,
        message: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an onboarding event.
        
        Args:
            event_type: Type of event (step, tool, reflection, checkpoint, etc.)
            message: Description of the event
            tags: Optional list of tags
            metadata: Optional additional metadata
            
        Returns:
            The created log entry
        """
        if tags is None:
            tags = []
            
        if metadata is None:
            metadata = {}
            
        # Add standard tags
        tags.extend(["onboarding", f"agent:{self.agent_id}"])
        
        # Add event type tag
        tags.append(f"event:{event_type}")
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "event_type": event_type,
            "message": message,
            "tags": tags,
            "metadata": metadata
        }
        
        # Add to logs
        self.logs.append(log_entry)
        
        # Save to file
        self._save_logs()
        
        # Also log to console
        logger.info(f"[{self.agent_id}] {event_type}: {message}")
        
        return log_entry
        
    def log_step(
        self,
        step_id: str,
        status: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a step in the onboarding process.
        
        Args:
            step_id: ID of the step
            status: Status of the step (started, completed, error, etc.)
            message: Description of the step
            metadata: Optional additional metadata
            
        Returns:
            The created log entry
        """
        if metadata is None:
            metadata = {}
            
        metadata.update({
            "step_id": step_id,
            "status": status
        })
        
        return self.log_event(
            event_type="step",
            message=message,
            tags=["step", f"step:{step_id}", f"status:{status}"],
            metadata=metadata
        )
        
    def log_tool_usage(
        self,
        tool_name: str,
        status: str,
        message: str,
        result: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log tool usage during onboarding.
        
        Args:
            tool_name: Name of the tool used
            status: Status of the tool usage (success, error, etc.)
            message: Description of the tool usage
            result: Optional result of the tool execution
            metadata: Optional additional metadata
            
        Returns:
            The created log entry
        """
        if metadata is None:
            metadata = {}
            
        metadata.update({
            "tool_name": tool_name,
            "status": status
        })
        
        if result is not None:
            if isinstance(result, (str, int, float, bool, type(None))):
                metadata["result"] = result
            else:
                metadata["result"] = str(result)
                
        return self.log_event(
            event_type="tool",
            message=message,
            tags=["tool", f"tool:{tool_name}", f"status:{status}"],
            metadata=metadata
        )
        
    def log_reflection(
        self,
        content: str,
        tool_name: Optional[str] = None,
        step_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a reflection during onboarding.
        
        Args:
            content: Content of the reflection
            tool_name: Optional name of the tool that triggered this reflection
            step_id: Optional ID of the step that triggered this reflection
            metadata: Optional additional metadata
            
        Returns:
            The created log entry
        """
        if metadata is None:
            metadata = {}
            
        tags = ["reflection"]
        
        if tool_name:
            tags.append(f"tool:{tool_name}")
            metadata["tool_name"] = tool_name
            
        if step_id:
            tags.append(f"step:{step_id}")
            metadata["step_id"] = step_id
            
        return self.log_event(
            event_type="reflection",
            message=content,
            tags=tags,
            metadata=metadata
        )
        
    def log_checkpoint(
        self,
        checkpoint_id: str,
        status: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a checkpoint in the onboarding process.
        
        Args:
            checkpoint_id: ID of the checkpoint
            status: Status of the checkpoint (complete, error, etc.)
            message: Description of the checkpoint
            metadata: Optional additional metadata
            
        Returns:
            The created log entry
        """
        if metadata is None:
            metadata = {}
            
        metadata.update({
            "checkpoint_id": checkpoint_id,
            "status": status
        })
        
        return self.log_event(
            event_type="checkpoint",
            message=message,
            tags=["checkpoint", f"checkpoint:{checkpoint_id}", f"status:{status}"],
            metadata=metadata
        )
        
    def log_error(
        self,
        error_message: str,
        step_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        exception: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an error during onboarding.
        
        Args:
            error_message: Description of the error
            step_id: Optional ID of the step where the error occurred
            tool_name: Optional name of the tool that caused the error
            exception: Optional exception object
            metadata: Optional additional metadata
            
        Returns:
            The created log entry
        """
        if metadata is None:
            metadata = {}
            
        tags = ["error"]
        
        if step_id:
            tags.append(f"step:{step_id}")
            metadata["step_id"] = step_id
            
        if tool_name:
            tags.append(f"tool:{tool_name}")
            metadata["tool_name"] = tool_name
            
        if exception:
            metadata["exception"] = str(exception)
            metadata["exception_type"] = type(exception).__name__
            
        # Log to console with error level
        logger.error(f"[{self.agent_id}] Error: {error_message}")
        
        return self.log_event(
            event_type="error",
            message=error_message,
            tags=tags,
            metadata=metadata
        )
        
    def log_completion(
        self,
        status: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log completion of the onboarding process.
        
        Args:
            status: Status of the completion (success, partial, error, etc.)
            message: Description of the completion
            metadata: Optional additional metadata
            
        Returns:
            The created log entry
        """
        if metadata is None:
            metadata = {}
            
        metadata.update({
            "status": status,
            "completion_time": datetime.datetime.now().isoformat()
        })
        
        # Update the overall status in the log file
        try:
            with open(self.log_file, "r") as f:
                log_data = json.load(f)
                
            log_data["status"] = status
            log_data["onboarding_completed"] = datetime.datetime.now().isoformat()
            
            with open(self.log_file, "w") as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating log file status: {e}")
            
        return self.log_event(
            event_type="completion",
            message=message,
            tags=["completion", f"status:{status}"],
            metadata=metadata
        )
        
    def get_logs_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Get logs filtered by event type.
        
        Args:
            event_type: Type of events to retrieve
            
        Returns:
            List of matching log entries
        """
        return [log for log in self.logs if log["event_type"] == event_type]
        
    def get_logs_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """
        Get logs filtered by tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of matching log entries
        """
        return [log for log in self.logs if tag in log["tags"]]
        
    def get_log_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all logs.
        
        Returns:
            Dictionary containing log summary
        """
        # Count logs by event type
        type_counts = {}
        for log in self.logs:
            event_type = log["event_type"]
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
            
        # Count logs by status (if present in metadata)
        status_counts = {}
        for log in self.logs:
            status = log.get("metadata", {}).get("status")
            if status:
                status_counts[status] = status_counts.get(status, 0) + 1
                
        # Get all unique tags
        all_tags = []
        for log in self.logs:
            all_tags.extend(log["tags"])
        unique_tags = sorted(list(set(all_tags)))
        
        # Check for completion
        completion_logs = self.get_logs_by_type("completion")
        is_complete = any(log.get("metadata", {}).get("status") == "success" for log in completion_logs)
        
        return {
            "agent_id": self.agent_id,
            "total_logs": len(self.logs),
            "by_type": type_counts,
            "by_status": status_counts,
            "unique_tags": unique_tags,
            "is_complete": is_complete,
            "has_errors": len(self.get_logs_by_type("error")) > 0
        }
        
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report of the onboarding process.
        
        Returns:
            Dictionary containing the onboarding report
        """
        summary = self.get_log_summary()
        
        # Get step completion status
        steps = {}
        for log in self.get_logs_by_type("step"):
            step_id = log.get("metadata", {}).get("step_id")
            status = log.get("metadata", {}).get("status")
            if step_id and status:
                if step_id not in steps or status == "completed":
                    steps[step_id] = status
                    
        # Get checkpoint status
        checkpoints = {}
        for log in self.get_logs_by_type("checkpoint"):
            checkpoint_id = log.get("metadata", {}).get("checkpoint_id")
            status = log.get("metadata", {}).get("status")
            if checkpoint_id and status:
                checkpoints[checkpoint_id] = status
                
        # Get all reflections
        reflections = self.get_logs_by_type("reflection")
        
        # Get all errors
        errors = self.get_logs_by_type("error")
        
        return {
            "agent_id": self.agent_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": summary,
            "steps": steps,
            "checkpoints": checkpoints,
            "reflections_count": len(reflections),
            "errors_count": len(errors),
            "errors": [{"message": e["message"], "metadata": e["metadata"]} for e in errors] if errors else None,
            "is_complete": "agent_onboarding_complete" in checkpoints and checkpoints["agent_onboarding_complete"] == "complete"
        }
