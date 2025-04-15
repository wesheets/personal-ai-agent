"""
Memory and Reflection System for Agent Onboarding

This module implements the memory and reflection system for the agent onboarding process.
It provides functions for creating, storing, and retrieving memories and reflections
during the onboarding flow.
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional

# Define memory types
MEMORY_TYPES = {
    "system": "System memory for agent instructions and information",
    "reflection": "Agent's reflections on experiences and learnings",
    "action": "Record of agent actions and tool usage",
    "checkpoint": "Progress markers in the onboarding process"
}

class MemorySystem:
    """
    Memory system for the agent onboarding process.
    
    This class manages the creation, storage, and retrieval of memories
    and reflections during the onboarding flow.
    """
    
    def __init__(self, agent_id: str, goal_id: str, memory_dir: str = "/home/ubuntu/workspace/personal-ai-agent/logs/memories"):
        """
        Initialize the memory system for a specific agent and goal.
        
        Args:
            agent_id: ID of the agent
            goal_id: ID of the goal (typically onboarding goal)
            memory_dir: Directory to store memory files
        """
        self.agent_id = agent_id
        self.goal_id = goal_id
        self.memory_dir = memory_dir
        self.memories = []
        
        # Ensure the memory directory exists
        os.makedirs(memory_dir, exist_ok=True)
        
        # Create agent-specific directory
        self.agent_memory_dir = os.path.join(memory_dir, agent_id.lower())
        os.makedirs(self.agent_memory_dir, exist_ok=True)
        
    def create_memory(
        self,
        memory_type: str,
        content: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new memory.
        
        Args:
            memory_type: Type of memory (system, reflection, action, checkpoint)
            content: Content of the memory
            tags: Optional list of tags
            metadata: Optional additional metadata
            
        Returns:
            The created memory object
        """
        if memory_type not in MEMORY_TYPES:
            raise ValueError(f"Invalid memory type: {memory_type}. Must be one of {list(MEMORY_TYPES.keys())}")
            
        if tags is None:
            tags = []
            
        if metadata is None:
            metadata = {}
            
        # Add standard tags
        tags.extend(["onboarding", f"agent:{self.agent_id}"])
        
        # Add memory type tag
        tags.append(f"type:{memory_type}")
        
        # Generate memory ID
        memory_id = f"{memory_type}_{self.agent_id}_{int(datetime.datetime.now().timestamp())}"
        
        # Create memory object
        memory = {
            "id": memory_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "goal_id": self.goal_id,
            "type": memory_type,
            "content": content,
            "tags": tags,
            "metadata": metadata
        }
        
        # Store the memory
        self.memories.append(memory)
        self._save_memory(memory)
        
        return memory
        
    def create_system_memory(
        self,
        content: str,
        prompt: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a system memory.
        
        Args:
            content: Content of the memory
            prompt: Optional prompt that triggered this memory
            tags: Optional list of tags
            
        Returns:
            The created memory object
        """
        if tags is None:
            tags = []
            
        metadata = {}
        if prompt:
            metadata["prompt"] = prompt
            
        return self.create_memory(
            memory_type="system",
            content=content,
            tags=tags,
            metadata=metadata
        )
        
    def create_reflection(
        self,
        content: str,
        tool_name: Optional[str] = None,
        step_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a reflection memory.
        
        Args:
            content: Content of the reflection
            tool_name: Optional name of the tool that triggered this reflection
            step_id: Optional ID of the onboarding step
            tags: Optional list of tags
            
        Returns:
            The created reflection memory object
        """
        if tags is None:
            tags = ["reflection"]
        else:
            tags.append("reflection")
            
        metadata = {}
        if tool_name:
            tags.append(f"tool:{tool_name}")
            metadata["tool_name"] = tool_name
            
        if step_id:
            tags.append(f"step:{step_id}")
            metadata["step_id"] = step_id
            
        return self.create_memory(
            memory_type="reflection",
            content=content,
            tags=tags,
            metadata=metadata
        )
        
    def create_action_memory(
        self,
        action: str,
        tool_name: str,
        result: Any,
        status: str = "success",
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create an action memory for tool usage.
        
        Args:
            action: Description of the action
            tool_name: Name of the tool used
            result: Result of the tool execution
            status: Status of the action (success, error, etc.)
            tags: Optional list of tags
            
        Returns:
            The created action memory object
        """
        if tags is None:
            tags = ["action"]
        else:
            tags.append("action")
            
        # Add tool-specific tag
        tags.append(f"tool:{tool_name}")
        
        metadata = {
            "tool_name": tool_name,
            "status": status,
            "result": result if isinstance(result, (str, int, float, bool, type(None))) else str(result)
        }
        
        return self.create_memory(
            memory_type="action",
            content=action,
            tags=tags,
            metadata=metadata
        )
        
    def create_checkpoint(
        self,
        checkpoint_id: str,
        status: str,
        details: Dict[str, Any],
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a checkpoint memory.
        
        Args:
            checkpoint_id: ID of the checkpoint
            status: Status of the checkpoint (complete, error, etc.)
            details: Additional details about the checkpoint
            tags: Optional list of tags
            
        Returns:
            The created checkpoint memory object
        """
        if tags is None:
            tags = ["checkpoint"]
        else:
            tags.append("checkpoint")
            
        # Add checkpoint-specific tag
        tags.append(f"checkpoint:{checkpoint_id}")
        
        metadata = {
            "checkpoint_id": checkpoint_id,
            "status": status,
            "details": details
        }
        
        return self.create_memory(
            memory_type="checkpoint",
            content=f"Checkpoint {checkpoint_id}: {status}",
            tags=tags,
            metadata=metadata
        )
        
    def get_memories(
        self,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get memories filtered by type and tags.
        
        Args:
            memory_type: Optional type of memories to retrieve
            tags: Optional list of tags to filter by
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of matching memories
        """
        filtered_memories = self.memories
        
        # Filter by memory type
        if memory_type:
            filtered_memories = [m for m in filtered_memories if m["type"] == memory_type]
            
        # Filter by tags (all tags must be present)
        if tags:
            filtered_memories = [
                m for m in filtered_memories 
                if all(tag in m["tags"] for tag in tags)
            ]
            
        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit
        return filtered_memories[:limit]
        
    def get_reflections(self, tool_name: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get reflection memories, optionally filtered by tool name.
        
        Args:
            tool_name: Optional tool name to filter by
            limit: Maximum number of reflections to retrieve
            
        Returns:
            List of matching reflection memories
        """
        tags = ["reflection"]
        if tool_name:
            tags.append(f"tool:{tool_name}")
            
        return self.get_memories(memory_type="reflection", tags=tags, limit=limit)
        
    def get_checkpoints(self, checkpoint_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get checkpoint memories, optionally filtered by checkpoint ID.
        
        Args:
            checkpoint_id: Optional checkpoint ID to filter by
            
        Returns:
            List of matching checkpoint memories
        """
        tags = ["checkpoint"]
        if checkpoint_id:
            tags.append(f"checkpoint:{checkpoint_id}")
            
        return self.get_memories(memory_type="checkpoint", tags=tags)
        
    def _save_memory(self, memory: Dict[str, Any]) -> str:
        """
        Save a memory to a file.
        
        Args:
            memory: The memory to save
            
        Returns:
            Path to the saved memory file
        """
        # Generate filename
        filename = f"{memory['id']}.json"
        filepath = os.path.join(self.agent_memory_dir, filename)
        
        # Write memory to file
        with open(filepath, "w") as f:
            json.dump(memory, f, indent=2)
            
        return filepath
        
    def load_memories(self) -> None:
        """Load all memories for the current agent from files."""
        self.memories = []
        
        # Check if agent memory directory exists
        if not os.path.exists(self.agent_memory_dir):
            return
            
        # Load all memory files
        for filename in os.listdir(self.agent_memory_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.agent_memory_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        memory = json.load(f)
                        self.memories.append(memory)
                except Exception as e:
                    print(f"Error loading memory from {filepath}: {e}")
                    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memories.
        
        Returns:
            Dictionary of memory statistics
        """
        # Count memories by type
        type_counts = {}
        for memory in self.memories:
            memory_type = memory["type"]
            type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
            
        # Count unique tags
        all_tags = []
        for memory in self.memories:
            all_tags.extend(memory["tags"])
        unique_tags = set(all_tags)
        
        return {
            "total_memories": len(self.memories),
            "by_type": type_counts,
            "unique_tags": len(unique_tags),
            "tags": sorted(list(unique_tags))
        }
