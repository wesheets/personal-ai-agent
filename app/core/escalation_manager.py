import os
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import re

class EscalationData(BaseModel):
    """Model for escalation data"""
    escalation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    task_description: str
    escalation_reason: str
    reflection_data: Dict[str, Any]
    memory_summary: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    forwarded_to_agent: Optional[str] = None
    status: str = "pending"  # pending, resolved, forwarded

class EscalationManager:
    """
    Manager for escalation protocol
    
    This class handles detecting when agents need escalation and logging
    escalation events.
    """
    
    def __init__(self):
        """Initialize the EscalationManager"""
        # Set up logging directory
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "escalation_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Define patterns that indicate an agent needs escalation
        self.escalation_patterns = [
            r"i('m| am) stuck",
            r"need help",
            r"escalating",
            r"cannot (proceed|continue|resolve)",
            r"unable to (proceed|continue|resolve)",
            r"blocked (by|on|with)",
            r"require(s)? (assistance|help|guidance)",
            r"beyond (my|the) (capabilities|scope)",
            r"need(s)? (expert|human|additional) (input|assistance|intervention)",
            r"critical (issue|problem|error)",
            r"failed (to|after) (multiple|several|repeated) (attempts|tries)",
            r"exhausted (all|available) (options|approaches|solutions)"
        ]
    
    async def check_for_escalation(
        self,
        agent_name: str,
        task_description: str,
        reflection_data: Dict[str, Any],
        retry_count: int = 0,
        memory_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if escalation is needed based on retry count and reflection data
        
        Args:
            agent_name: Name of the agent
            task_description: Description of the task
            reflection_data: Reflection data from the agent
            retry_count: Number of retries attempted
            memory_summary: Summary of relevant memories
            
        Returns:
            Dictionary with escalation information if needed, otherwise empty dict
        """
        # Check if retry count exceeds threshold
        if retry_count >= 2:
            return await self._create_escalation(
                agent_name=agent_name,
                task_description=task_description,
                escalation_reason="Exceeded retry limit",
                reflection_data=reflection_data,
                memory_summary=memory_summary
            )
        
        # Get the relevant reflection fields
        rationale = reflection_data.get("rationale", "")
        assumptions = reflection_data.get("assumptions", "")
        improvement_suggestions = reflection_data.get("improvement_suggestions", "")
        confidence_level = reflection_data.get("confidence_level", "")
        failure_points = reflection_data.get("failure_points", "")
        
        # Combine all reflection text
        combined_reflection = f"{rationale} {assumptions} {improvement_suggestions} {confidence_level} {failure_points}".lower()
        
        # Check if any escalation patterns are present
        escalation_needed = False
        matched_pattern = None
        
        for pattern in self.escalation_patterns:
            if re.search(pattern, combined_reflection, re.IGNORECASE):
                escalation_needed = True
                matched_pattern = pattern
                break
        
        # If escalation is needed, create an escalation event
        if escalation_needed:
            return await self._create_escalation(
                agent_name=agent_name,
                task_description=task_description,
                escalation_reason=f"Detected pattern: {matched_pattern}",
                reflection_data=reflection_data,
                memory_summary=memory_summary
            )
        
        # Otherwise, return empty dict
        return {}
    
    async def _create_escalation(
        self,
        agent_name: str,
        task_description: str,
        escalation_reason: str,
        reflection_data: Dict[str, Any],
        memory_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an escalation event
        
        Args:
            agent_name: Name of the agent
            task_description: Description of the task
            escalation_reason: Reason for the escalation
            reflection_data: Reflection data from the agent
            memory_summary: Summary of relevant memories
            
        Returns:
            Dictionary with escalation information
        """
        # Create escalation data
        escalation_data = EscalationData(
            agent_name=agent_name,
            task_description=task_description,
            escalation_reason=escalation_reason,
            reflection_data=reflection_data,
            memory_summary=memory_summary
        )
        
        # Log the escalation
        await self._log_escalation(escalation_data)
        
        # Return escalation information
        return {
            "escalation_needed": True,
            "escalation_id": escalation_data.escalation_id,
            "escalation_reason": escalation_reason,
            "timestamp": escalation_data.timestamp
        }
    
    async def _log_escalation(self, escalation_data: EscalationData) -> None:
        """
        Log an escalation
        
        Args:
            escalation_data: Escalation data to log
        """
        # Create the log file
        log_file = os.path.join(self.log_dir, f"{escalation_data.escalation_id}.json")
        
        # Write the escalation data
        with open(log_file, "w") as f:
            json.dump(escalation_data.dict(), f, indent=2)
    
    async def forward_escalation(
        self,
        escalation_id: str,
        target_agent: str
    ) -> Dict[str, Any]:
        """
        Forward an escalation to another agent
        
        Args:
            escalation_id: ID of the escalation to forward
            target_agent: Agent to forward the escalation to
            
        Returns:
            Dictionary with forwarding result
        """
        # Get the escalation data
        escalation_data = await self.get_escalation(escalation_id)
        
        if not escalation_data:
            return {"error": f"Escalation not found: {escalation_id}"}
        
        # Update the escalation data
        escalation_data.forwarded_to_agent = target_agent
        escalation_data.status = "forwarded"
        
        # Save the updated escalation data
        log_file = os.path.join(self.log_dir, f"{escalation_id}.json")
        with open(log_file, "w") as f:
            json.dump(escalation_data.dict(), f, indent=2)
        
        # Import here to avoid circular imports
        from app.api.agent import AgentRequest, process_agent_request
        
        # Create a request for the target agent
        request = AgentRequest(
            input=f"ESCALATION: {escalation_data.task_description}",
            context={
                "escalation_id": escalation_id,
                "original_agent": escalation_data.agent_name,
                "escalation_reason": escalation_data.escalation_reason,
                "reflection_data": escalation_data.reflection_data,
                "memory_summary": escalation_data.memory_summary,
                "is_escalation": True
            },
            save_to_memory=True
        )
        
        # Process the request (this will be called by the API endpoint)
        return {
            "escalation_id": escalation_id,
            "forwarded_to": target_agent,
            "status": "forwarded",
            "request": request.dict()
        }
    
    async def resolve_escalation(
        self,
        escalation_id: str,
        resolution_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark an escalation as resolved
        
        Args:
            escalation_id: ID of the escalation to resolve
            resolution_notes: Notes on how the escalation was resolved
            
        Returns:
            Dictionary with resolution result
        """
        # Get the escalation data
        escalation_data = await self.get_escalation(escalation_id)
        
        if not escalation_data:
            return {"error": f"Escalation not found: {escalation_id}"}
        
        # Update the escalation data
        escalation_data.status = "resolved"
        if resolution_notes:
            if "resolution_notes" not in escalation_data.dict():
                escalation_data.dict()["resolution_notes"] = resolution_notes
        
        # Save the updated escalation data
        log_file = os.path.join(self.log_dir, f"{escalation_id}.json")
        with open(log_file, "w") as f:
            json.dump(escalation_data.dict(), f, indent=2)
        
        return {
            "escalation_id": escalation_id,
            "status": "resolved"
        }
    
    async def get_escalation(self, escalation_id: str) -> Optional[EscalationData]:
        """
        Get an escalation by ID
        
        Args:
            escalation_id: ID of the escalation
            
        Returns:
            Escalation data if found, None otherwise
        """
        log_file = os.path.join(self.log_dir, f"{escalation_id}.json")
        
        if not os.path.exists(log_file):
            return None
        
        with open(log_file, "r") as f:
            data = json.load(f)
            return EscalationData(**data)
    
    async def get_escalations(
        self,
        limit: int = 10,
        offset: int = 0,
        agent_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get escalations with optional filtering
        
        Args:
            limit: Maximum number of escalations to return
            offset: Offset for pagination
            agent_name: Filter by agent name
            status: Filter by status (pending, resolved, forwarded)
            
        Returns:
            List of escalation data
        """
        # Get all log files
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith(".json")]
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.log_dir, f)), reverse=True)
        
        # Filter and load escalation data
        escalations = []
        for log_file in log_files:
            with open(os.path.join(self.log_dir, log_file), "r") as f:
                data = json.load(f)
                
                # Apply filters
                if agent_name and data.get("agent_name") != agent_name:
                    continue
                
                if status and data.get("status") != status:
                    continue
                
                escalations.append(data)
        
        # Apply pagination
        escalations = escalations[offset:offset + limit]
        
        return escalations
    
    async def get_escalation_count(
        self,
        agent_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """
        Get the count of escalations with optional filtering
        
        Args:
            agent_name: Filter by agent name
            status: Filter by status (pending, resolved, forwarded)
            
        Returns:
            Count of escalations
        """
        # Get all log files
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith(".json")]
        
        # Filter and count
        count = 0
        for log_file in log_files:
            with open(os.path.join(self.log_dir, log_file), "r") as f:
                data = json.load(f)
                
                # Apply filters
                if agent_name and data.get("agent_name") != agent_name:
                    continue
                
                if status and data.get("status") != status:
                    continue
                
                count += 1
        
        return count

# Singleton instance
_escalation_manager = None

def get_escalation_manager() -> EscalationManager:
    """
    Get the singleton EscalationManager instance
    """
    global _escalation_manager
    if _escalation_manager is None:
        _escalation_manager = EscalationManager()
    return _escalation_manager
