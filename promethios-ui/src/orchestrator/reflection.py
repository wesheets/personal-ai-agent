"""
Orchestrator Reflection Memory System

This module implements the reflection memory system for the Orchestrator, allowing
it to automatically generate and store reflections after completing build phases.
"""

import os
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple

class ReflectionManager:
    """
    Manages the creation and storage of reflection memories.
    
    This class provides methods for generating reflections after phase completion
    and storing them in the memory system.
    """
    
    def __init__(
        self,
        memory_writer = None,  # Will be initialized later to avoid circular imports
        reflections_directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/reflections"
    ):
        """
        Initialize the reflection manager.
        
        Args:
            memory_writer: Function to write memories (initialized later)
            reflections_directory: Directory to store reflection files
        """
        self.memory_writer = memory_writer
        self.reflections_directory = reflections_directory
        os.makedirs(reflections_directory, exist_ok=True)
        
    def set_memory_writer(self, memory_writer):
        """
        Set the memory writer function.
        
        Args:
            memory_writer: Function to write memories
        """
        self.memory_writer = memory_writer
        
    def create_phase_reflection(
        self,
        goal_id: str,
        phase_title: str,
        phase_number: int,
        total_phases: int,
        agent_contributions: Dict[str, List[str]],
        outcomes: List[str],
        start_time: str,
        end_time: str
    ) -> str:
        """
        Create a reflection memory for a completed phase.
        
        Args:
            goal_id: ID of the goal
            phase_title: Title of the completed phase
            phase_number: Number of the phase (1-based)
            total_phases: Total number of phases
            agent_contributions: Dictionary mapping agent IDs to lists of contributions
            outcomes: List of outcomes achieved in this phase
            start_time: ISO format timestamp when the phase started
            end_time: ISO format timestamp when the phase completed
            
        Returns:
            ID of the created reflection memory
        """
        # Calculate the duration
        start_dt = datetime.datetime.fromisoformat(start_time)
        end_dt = datetime.datetime.fromisoformat(end_time)
        duration_seconds = (end_dt - start_dt).total_seconds()
        
        # Format the duration as a human-readable string
        duration_str = self._format_duration(duration_seconds)
        
        # Generate the reflection content
        content = f"Build Phase {phase_number} complete: {phase_title}.\n\n"
        
        # Add agent contributions
        for agent_id, contributions in agent_contributions.items():
            agent_name = agent_id.upper()
            contribution_text = ", ".join(contributions)
            content += f"{agent_name} delivered {contribution_text}. "
        
        content += "\n\n"
        
        # Add outcomes
        content += "Key outcomes:\n"
        for outcome in outcomes:
            content += f"- {outcome}\n"
            
        content += f"\nPhase completed in {duration_str}."
        
        # Create the reflection memory
        reflection_id = self._generate_reflection_id()
        
        # Write the memory if memory_writer is available
        if self.memory_writer:
            memory_id = self.memory_writer(
                goal_id=goal_id,
                agent_id="orchestrator",
                memory_type="reflection",
                content=content,
                tags=["orchestrator", "phase_reflection", f"phase_{phase_number}"]
            )
            
            # Save the reflection details
            self._save_reflection(
                reflection_id=reflection_id,
                memory_id=memory_id,
                goal_id=goal_id,
                phase_title=phase_title,
                phase_number=phase_number,
                total_phases=total_phases,
                agent_contributions=agent_contributions,
                outcomes=outcomes,
                start_time=start_time,
                end_time=end_time,
                content=content
            )
            
            return memory_id
        else:
            # Just save the reflection details without creating a memory
            self._save_reflection(
                reflection_id=reflection_id,
                memory_id=None,
                goal_id=goal_id,
                phase_title=phase_title,
                phase_number=phase_number,
                total_phases=total_phases,
                agent_contributions=agent_contributions,
                outcomes=outcomes,
                start_time=start_time,
                end_time=end_time,
                content=content
            )
            
            return reflection_id
            
    def create_goal_reflection(
        self,
        goal_id: str,
        goal_title: str,
        phase_count: int,
        agent_contributions: Dict[str, List[str]],
        outcomes: List[str],
        start_time: str,
        end_time: str
    ) -> str:
        """
        Create a reflection memory for a completed goal.
        
        Args:
            goal_id: ID of the goal
            goal_title: Title of the completed goal
            phase_count: Number of phases in the goal
            agent_contributions: Dictionary mapping agent IDs to lists of contributions
            outcomes: List of outcomes achieved in this goal
            start_time: ISO format timestamp when the goal started
            end_time: ISO format timestamp when the goal completed
            
        Returns:
            ID of the created reflection memory
        """
        # Calculate the duration
        start_dt = datetime.datetime.fromisoformat(start_time)
        end_dt = datetime.datetime.fromisoformat(end_time)
        duration_seconds = (end_dt - start_dt).total_seconds()
        
        # Format the duration as a human-readable string
        duration_str = self._format_duration(duration_seconds)
        
        # Generate the reflection content
        content = f"Goal complete: {goal_title}.\n\n"
        
        # Add agent contributions
        for agent_id, contributions in agent_contributions.items():
            agent_name = agent_id.upper()
            contribution_text = ", ".join(contributions)
            content += f"{agent_name} delivered {contribution_text}. "
        
        content += "\n\n"
        
        # Add outcomes
        content += "Key outcomes:\n"
        for outcome in outcomes:
            content += f"- {outcome}\n"
            
        content += f"\nGoal completed in {duration_str} across {phase_count} phases."
        
        # Create the reflection memory
        reflection_id = self._generate_reflection_id()
        
        # Write the memory if memory_writer is available
        if self.memory_writer:
            memory_id = self.memory_writer(
                goal_id=goal_id,
                agent_id="orchestrator",
                memory_type="reflection",
                content=content,
                tags=["orchestrator", "goal_reflection"]
            )
            
            # Save the reflection details
            self._save_reflection(
                reflection_id=reflection_id,
                memory_id=memory_id,
                goal_id=goal_id,
                goal_title=goal_title,
                phase_count=phase_count,
                agent_contributions=agent_contributions,
                outcomes=outcomes,
                start_time=start_time,
                end_time=end_time,
                content=content,
                is_goal_reflection=True
            )
            
            return memory_id
        else:
            # Just save the reflection details without creating a memory
            self._save_reflection(
                reflection_id=reflection_id,
                memory_id=None,
                goal_id=goal_id,
                goal_title=goal_title,
                phase_count=phase_count,
                agent_contributions=agent_contributions,
                outcomes=outcomes,
                start_time=start_time,
                end_time=end_time,
                content=content,
                is_goal_reflection=True
            )
            
            return reflection_id
            
    def _generate_reflection_id(self) -> str:
        """
        Generate a unique reflection ID.
        
        Returns:
            Unique reflection ID
        """
        return f"reflection_{str(uuid.uuid4())}"
        
    def _format_duration(self, duration_seconds: float) -> str:
        """
        Format a duration in seconds as a human-readable string.
        
        Args:
            duration_seconds: Duration in seconds
            
        Returns:
            Human-readable duration string
        """
        # Handle edge cases
        if duration_seconds < 0:
            return "invalid duration"
        if duration_seconds < 1:
            return "less than a second"
            
        # Convert to days, hours, minutes, seconds
        days, remainder = divmod(int(duration_seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Build the duration string
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 and len(parts) < 2:  # Only include seconds if we have less than 2 parts already
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
            
        # Join the parts
        if len(parts) == 0:
            return "less than a second"
        elif len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} and {parts[1]}"
        else:
            return f"{', '.join(parts[:-1])}, and {parts[-1]}"
            
    def _save_reflection(
        self,
        reflection_id: str,
        memory_id: Optional[str],
        goal_id: str,
        content: str,
        start_time: str,
        end_time: str,
        is_goal_reflection: bool = False,
        **kwargs
    ) -> str:
        """
        Save reflection details to a file.
        
        Args:
            reflection_id: ID of the reflection
            memory_id: ID of the memory (if created)
            goal_id: ID of the goal
            content: Reflection content
            start_time: Start time of the phase or goal
            end_time: End time of the phase or goal
            is_goal_reflection: Whether this is a goal reflection
            **kwargs: Additional reflection details
            
        Returns:
            Path to the saved reflection file
        """
        # Create the reflection object
        reflection = {
            "reflection_id": reflection_id,
            "memory_id": memory_id,
            "goal_id": goal_id,
            "is_goal_reflection": is_goal_reflection,
            "content": content,
            "start_time": start_time,
            "end_time": end_time,
            "created_at": datetime.datetime.now().isoformat(),
            **kwargs
        }
        
        # Generate the filename
        filename = f"{reflection_id}.json"
        filepath = os.path.join(self.reflections_directory, filename)
        
        # Write the reflection to file
        with open(filepath, "w") as f:
            json.dump(reflection, f, indent=2)
            
        return filepath
        
    def get_reflections_for_goal(self, goal_id: str) -> List[Dict[str, Any]]:
        """
        Get all reflections for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            List of reflection dictionaries
        """
        reflections = []
        
        # List all reflection files in the directory
        for filename in os.listdir(self.reflections_directory):
            if filename.endswith(".json"):
                filepath = os.path.join(self.reflections_directory, filename)
                
                try:
                    with open(filepath, "r") as f:
                        reflection = json.load(f)
                        
                    # Check if this reflection is for the specified goal
                    if reflection.get("goal_id") == goal_id:
                        reflections.append(reflection)
                except Exception as e:
                    print(f"Error loading reflection from {filepath}: {e}")
                    
        # Sort reflections by created_at
        reflections.sort(key=lambda r: r["created_at"])
        
        return reflections
        
    def get_phase_reflections(self, goal_id: str) -> List[Dict[str, Any]]:
        """
        Get all phase reflections for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            List of phase reflection dictionaries
        """
        reflections = self.get_reflections_for_goal(goal_id)
        return [r for r in reflections if not r.get("is_goal_reflection", False)]
        
    def get_goal_reflection(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the goal reflection for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Goal reflection dictionary or None if not found
        """
        reflections = self.get_reflections_for_goal(goal_id)
        goal_reflections = [r for r in reflections if r.get("is_goal_reflection", False)]
        
        if goal_reflections:
            return goal_reflections[0]
        
        return None
