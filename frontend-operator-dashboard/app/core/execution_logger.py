import os
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

class ExecutionLogger:
    """
    System-wide execution logger for agent interactions
    """
    def __init__(self, log_dir: Optional[str] = None):
        # Set up logging directory
        self.log_dir = log_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "execution_logs")
        os.makedirs(self.log_dir, exist_ok=True)
    
    async def log_execution(
        self,
        agent_name: str,
        model: str,
        input_text: str,
        output_text: str,
        metadata: Optional[Dict[str, Any]] = None,
        tools_used: Optional[List[str]] = None
    ) -> str:
        """
        Log an agent execution
        
        Args:
            agent_name: Name of the agent
            model: Model used for the execution
            input_text: User input text
            output_text: Agent output text
            metadata: Additional metadata
            tools_used: List of tools used during execution
            
        Returns:
            ID of the log entry
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
            "model": model,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "tools_used": tools_used or [],
            "metadata": metadata or {}
        }
        
        # Save log entry to file
        log_file = os.path.join(self.log_dir, f"{log_id}.json")
        with open(log_file, "w") as f:
            json.dump(log_entry, f, indent=2)
        
        return log_id
    
    async def get_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific log entry
        
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
    
    async def get_logs(
        self,
        agent_name: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get log entries with optional filtering
        
        Args:
            agent_name: Filter by agent name
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
                
                logs.append(log_entry)
        
        return logs

# Singleton instance
_execution_logger = None

def get_execution_logger() -> ExecutionLogger:
    """
    Get the singleton ExecutionLogger instance
    """
    global _execution_logger
    if _execution_logger is None:
        _execution_logger = ExecutionLogger()
    return _execution_logger
