import os
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

class RationaleLogger:
    """
    System for logging agent rationale, assumptions, and improvement suggestions
    """
    def __init__(self, log_dir: Optional[str] = None):
        # Set up logging directory
        self.log_dir = log_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "rationale_logs")
        os.makedirs(self.log_dir, exist_ok=True)
    
    async def log_rationale(
        self,
        agent_name: str,
        input_text: str,
        output_text: str,
        rationale: str,
        assumptions: str,
        improvement_suggestions: str,
        confidence_level: str,
        failure_points: str,
        task_category: Optional[str] = None,
        suggested_next_step: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        execution_log_id: Optional[str] = None
    ) -> str:
        """
        Log an agent's rationale and self-evaluation
        
        Args:
            agent_name: Name of the agent
            input_text: User input text
            output_text: Agent output text
            rationale: Agent's rationale for the response
            assumptions: Assumptions made by the agent
            improvement_suggestions: Suggestions for improvement
            confidence_level: Agent's confidence in the output
            failure_points: Possible failure points identified by the agent
            task_category: Category of the task (e.g., code, strategy, research)
            suggested_next_step: Agent's suggestion for the next step
            metadata: Additional metadata
            execution_log_id: ID of the related execution log
            
        Returns:
            ID of the rationale log entry
        """
        # Generate a unique ID for this log entry
        log_id = str(uuid.uuid4())
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Truncate input and output if too long
        max_length = 500
        input_summary = input_text[:max_length] + "..." if len(input_text) > max_length else input_text
        output_summary = output_text[:max_length] + "..." if len(output_text) > max_length else output_text
        
        # Create log entry
        log_entry = {
            "id": log_id,
            "timestamp": timestamp,
            "agent_name": agent_name,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "reflection": {
                "rationale": rationale,
                "assumptions": assumptions,
                "improvement_suggestions": improvement_suggestions,
                "confidence_level": confidence_level,
                "failure_points": failure_points
            },
            "task_metadata": {
                "task_category": task_category,
                "suggested_next_step": suggested_next_step
            },
            "metadata": metadata or {},
            "execution_log_id": execution_log_id
        }
        
        # Save log entry to file
        log_file = os.path.join(self.log_dir, f"{log_id}.json")
        with open(log_file, "w") as f:
            json.dump(log_entry, f, indent=2)
        
        return log_id
    
    async def get_rationale_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific rationale log entry
        
        Args:
            log_id: ID of the log entry
            
        Returns:
            Log entry or None if not found
        """
        log_file = os.path.join(self.log_dir, f"{log_id}.json")
        
        if not os.path.exists(log_file):
            return None
        
        with open(log_file, "r") as f:
            return json.load(f)
    
    async def get_rationale_logs(
        self,
        agent_name: Optional[str] = None,
        task_category: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get rationale log entries with optional filtering
        
        Args:
            agent_name: Filter by agent name
            task_category: Filter by task category
            limit: Maximum number of logs to return
            offset: Offset for pagination
            
        Returns:
            List of log entries
        """
        # Get all log files
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith(".json")]
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.log_dir, f)), reverse=True)
        
        # Apply pagination
        log_files = log_files[offset:offset + limit]
        
        # Load log entries
        logs = []
        for log_file in log_files:
            with open(os.path.join(self.log_dir, log_file), "r") as f:
                log_entry = json.load(f)
                
                # Filter by agent name if specified
                if agent_name and log_entry.get("agent_name") != agent_name:
                    continue
                
                # Filter by task category if specified
                if task_category and log_entry.get("task_metadata", {}).get("task_category") != task_category:
                    continue
                
                logs.append(log_entry)
        
        return logs

# Singleton instance
_rationale_logger = None

def get_rationale_logger() -> RationaleLogger:
    """
    Get the singleton RationaleLogger instance
    """
    global _rationale_logger
    if _rationale_logger is None:
        _rationale_logger = RationaleLogger()
    return _rationale_logger
