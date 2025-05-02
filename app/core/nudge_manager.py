import os
import json
import uuid
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class NudgeData(BaseModel):
    """Model for nudge data"""
    agent_name: str
    input_text: str
    output_text: str
    reflection_data: Dict[str, Any]
    nudge_message: str
    nudge_reason: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    nudge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class NudgeManager:
    """
    Manager for nudging logic
    
    This class handles detecting when agents need user input and generating
    appropriate nudge messages.
    """
    
    def __init__(self):
        """Initialize the NudgeManager"""
        # Set up logging directory
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "nudge_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Define patterns that indicate an agent needs user input
        self.nudge_patterns = [
            r"i am unsure",
            r"i('m| am) not sure",
            r"user input needed",
            r"need(s|ed)? (more|additional) (information|input|clarification)",
            r"blocked",
            r"cannot proceed",
            r"can't proceed",
            r"unable to (proceed|continue)",
            r"insufficient (information|data|details)",
            r"clarification (is )?needed",
            r"please (provide|specify|clarify)",
            r"would (need|require) (more|additional)",
            r"don't have enough (information|data|details)",
            r"missing (information|data|details)",
            r"unclear (what|how|which|where|when)"
        ]
    
    async def check_for_nudge(
        self,
        agent_name: str,
        input_text: str,
        output_text: str,
        reflection_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if a nudge is needed based on agent reflection
        
        Args:
            agent_name: Name of the agent
            input_text: Input text
            output_text: Output text
            reflection_data: Reflection data from the agent
            
        Returns:
            Dictionary with nudge information if nudge is needed, otherwise empty dict
        """
        # Get the relevant reflection fields
        rationale = reflection_data.get("rationale", "")
        assumptions = reflection_data.get("assumptions", "")
        improvement_suggestions = reflection_data.get("improvement_suggestions", "")
        confidence_level = reflection_data.get("confidence_level", "")
        failure_points = reflection_data.get("failure_points", "")
        
        # Combine all reflection text
        combined_reflection = f"{rationale} {assumptions} {improvement_suggestions} {confidence_level} {failure_points}".lower()
        
        # Check if any nudge patterns are present
        nudge_needed = False
        matched_pattern = None
        
        for pattern in self.nudge_patterns:
            if re.search(pattern, combined_reflection, re.IGNORECASE):
                nudge_needed = True
                matched_pattern = pattern
                break
        
        # Also check the output text for patterns
        if not nudge_needed:
            for pattern in self.nudge_patterns:
                if re.search(pattern, output_text, re.IGNORECASE):
                    nudge_needed = True
                    matched_pattern = pattern
                    break
        
        # If nudge is needed, generate a nudge message
        if nudge_needed:
            return await self._generate_nudge(
                agent_name=agent_name,
                input_text=input_text,
                output_text=output_text,
                reflection_data=reflection_data,
                matched_pattern=matched_pattern
            )
        
        # Otherwise, return empty dict
        return {}
    
    async def _generate_nudge(
        self,
        agent_name: str,
        input_text: str,
        output_text: str,
        reflection_data: Dict[str, Any],
        matched_pattern: str
    ) -> Dict[str, Any]:
        """
        Generate a nudge message
        
        Args:
            agent_name: Name of the agent
            input_text: Input text
            output_text: Output text
            reflection_data: Reflection data from the agent
            matched_pattern: Pattern that triggered the nudge
            
        Returns:
            Dictionary with nudge information
        """
        # Determine the nudge reason based on the matched pattern
        nudge_reason = self._determine_nudge_reason(matched_pattern)
        
        # Generate an appropriate nudge message
        nudge_message = self._create_nudge_message(nudge_reason, agent_name, reflection_data)
        
        # Create nudge data
        nudge_data = NudgeData(
            agent_name=agent_name,
            input_text=input_text,
            output_text=output_text,
            reflection_data=reflection_data,
            nudge_message=nudge_message,
            nudge_reason=nudge_reason
        )
        
        # Log the nudge
        await self._log_nudge(nudge_data)
        
        # Return nudge information
        return {
            "nudge_needed": True,
            "nudge_message": nudge_message,
            "nudge_reason": nudge_reason,
            "nudge_id": nudge_data.nudge_id
        }
    
    def _determine_nudge_reason(self, matched_pattern: str) -> str:
        """
        Determine the reason for the nudge based on the matched pattern
        
        Args:
            matched_pattern: Pattern that triggered the nudge
            
        Returns:
            Nudge reason
        """
        if re.search(r"unsure|not sure", matched_pattern):
            return "uncertainty"
        elif re.search(r"user input|information|clarification|details|data", matched_pattern):
            return "needs_information"
        elif re.search(r"blocked|cannot proceed|can't proceed|unable", matched_pattern):
            return "blocked"
        else:
            return "general_assistance"
    
    def _create_nudge_message(
        self,
        nudge_reason: str,
        agent_name: str,
        reflection_data: Dict[str, Any]
    ) -> str:
        """
        Create an appropriate nudge message based on the reason
        
        Args:
            nudge_reason: Reason for the nudge
            agent_name: Name of the agent
            reflection_data: Reflection data from the agent
            
        Returns:
            Nudge message
        """
        failure_points = reflection_data.get("failure_points", "")
        
        if nudge_reason == "uncertainty":
            return f"I've reached a point where I'm uncertain about how to proceed. Would you like me to make an educated guess, or would you prefer to provide more guidance on {self._extract_uncertain_topic(failure_points)}?"
        
        elif nudge_reason == "needs_information":
            return f"I need additional information before proceeding. Could you please provide more details about {self._extract_missing_information(failure_points, reflection_data.get('assumptions', ''))}?"
        
        elif nudge_reason == "blocked":
            return f"I'm currently blocked and unable to proceed further. The specific issue is related to {self._extract_blocker(failure_points, reflection_data.get('rationale', ''))}. How would you like me to proceed?"
        
        else:
            return "I've reached a point where I need your input before proceeding. Would you like to continue or adjust direction?"
    
    def _extract_uncertain_topic(self, failure_points: str) -> str:
        """
        Extract the topic the agent is uncertain about
        
        Args:
            failure_points: Failure points from reflection
            
        Returns:
            Topic the agent is uncertain about
        """
        # Try to extract a specific topic from failure points
        if failure_points:
            # Look for phrases like "uncertain about X" or "not sure about X"
            uncertain_match = re.search(r"(uncertain|not sure|unclear) about ([^.]+)", failure_points, re.IGNORECASE)
            if uncertain_match:
                return uncertain_match.group(2).strip()
            
            # If no specific phrase, just return the first sentence
            sentences = failure_points.split('.')
            if sentences:
                return sentences[0].strip()
        
        return "this aspect"
    
    def _extract_missing_information(self, failure_points: str, assumptions: str) -> str:
        """
        Extract what information is missing
        
        Args:
            failure_points: Failure points from reflection
            assumptions: Assumptions from reflection
            
        Returns:
            Description of missing information
        """
        # Try to extract missing information from failure points
        if failure_points:
            # Look for phrases like "missing X" or "need X"
            missing_match = re.search(r"missing ([^.]+)", failure_points, re.IGNORECASE)
            if missing_match:
                return missing_match.group(1).strip()
            
            need_match = re.search(r"need(s|ed)? ([^.]+)", failure_points, re.IGNORECASE)
            if need_match:
                return need_match.group(2).strip()
        
        # Try to extract from assumptions
        if assumptions:
            # Look for phrases like "assumed X" which might indicate missing information
            assumed_match = re.search(r"assumed ([^.]+)", assumptions, re.IGNORECASE)
            if assumed_match:
                return assumed_match.group(1).strip()
        
        return "the specific requirements or constraints"
    
    def _extract_blocker(self, failure_points: str, rationale: str) -> str:
        """
        Extract what is blocking the agent
        
        Args:
            failure_points: Failure points from reflection
            rationale: Rationale from reflection
            
        Returns:
            Description of the blocker
        """
        # Try to extract blocker from failure points
        if failure_points:
            # Look for phrases like "blocked by X" or "cannot proceed because X"
            blocked_match = re.search(r"blocked by ([^.]+)", failure_points, re.IGNORECASE)
            if blocked_match:
                return blocked_match.group(1).strip()
            
            cannot_match = re.search(r"cannot (proceed|continue) (because|due to) ([^.]+)", failure_points, re.IGNORECASE)
            if cannot_match:
                return cannot_match.group(3).strip()
        
        # Try to extract from rationale
        if rationale:
            # Look for phrases like "unable to X because Y"
            unable_match = re.search(r"unable to ([^ ]+) because ([^.]+)", rationale, re.IGNORECASE)
            if unable_match:
                return f"{unable_match.group(1)} because {unable_match.group(2)}".strip()
        
        return "constraints in the current approach"
    
    async def _log_nudge(self, nudge_data: NudgeData) -> None:
        """
        Log a nudge
        
        Args:
            nudge_data: Nudge data to log
        """
        # Create the log file
        log_file = os.path.join(self.log_dir, f"{nudge_data.nudge_id}.json")
        
        # Write the nudge data
        with open(log_file, "w") as f:
            json.dump(nudge_data.dict(), f, indent=2)
    
    async def get_nudge_logs(
        self,
        limit: int = 10,
        offset: int = 0,
        agent_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get nudge logs
        
        Args:
            limit: Maximum number of logs to return
            offset: Offset for pagination
            agent_name: Filter by agent name
            
        Returns:
            List of nudge logs
        """
        # Get all log files
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith(".json")]
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.log_dir, f)), reverse=True)
        
        # Filter by agent name if specified
        if agent_name:
            filtered_logs = []
            for log_file in log_files:
                with open(os.path.join(self.log_dir, log_file), "r") as f:
                    log_data = json.load(f)
                    if log_data.get("agent_name") == agent_name:
                        filtered_logs.append(log_file)
            log_files = filtered_logs
        
        # Apply pagination
        log_files = log_files[offset:offset + limit]
        
        # Load log data
        logs = []
        for log_file in log_files:
            with open(os.path.join(self.log_dir, log_file), "r") as f:
                logs.append(json.load(f))
        
        return logs

# Singleton instance
_nudge_manager = None

def get_nudge_manager() -> NudgeManager:
    """
    Get the singleton NudgeManager instance
    """
    global _nudge_manager
    if _nudge_manager is None:
        _nudge_manager = NudgeManager()
    return _nudge_manager
