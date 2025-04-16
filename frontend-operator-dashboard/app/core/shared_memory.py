import os
from typing import Dict, Any, List, Optional
from app.core.vector_memory import VectorMemorySystem
import json
import time

class SharedMemoryLayer:
    """
    Shared memory layer that allows agents to write to and retrieve from a global memory index
    """
    def __init__(self):
        self.vector_memory = VectorMemorySystem()
    
    async def store_memory(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        priority: bool = False,
        scope: str = "agent",
        topics: Optional[List[str]] = None,
        agent_name: Optional[str] = None
    ) -> str:
        """
        Store a memory in the shared memory layer
        
        Args:
            content: The text content to store
            metadata: Optional metadata about the memory
            priority: Whether this is a priority memory
            scope: Scope of the memory ("global" or "agent")
            topics: List of topics for semantic filtering
            agent_name: Name of the agent (required if scope is "agent")
            
        Returns:
            The ID of the stored memory
        """
        # Validate scope
        if scope not in ["global", "agent"]:
            raise ValueError("Scope must be either 'global' or 'agent'")
        
        # Validate agent_name if scope is "agent"
        if scope == "agent" and not agent_name:
            raise ValueError("agent_name is required when scope is 'agent'")
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Add scope, topics, and agent_name to metadata
        metadata["scope"] = scope
        metadata["topics"] = topics or []
        if agent_name:
            metadata["agent_name"] = agent_name
        
        # Store in vector memory
        return await self.vector_memory.store_memory(
            content=content,
            metadata=metadata,
            priority=priority
        )
    
    async def search_memories(
        self, 
        query: str, 
        limit: int = 5, 
        priority_only: bool = False,
        scope: Optional[str] = None,
        topics: Optional[List[str]] = None,
        agent_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for memories in the shared memory layer
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            priority_only: Whether to only return priority memories
            scope: Filter by scope ("global" or "agent")
            topics: Filter by topics
            agent_name: Filter by agent name
            
        Returns:
            List of memory items sorted by relevance
        """
        # Get memories from vector memory
        memories = await self.vector_memory.search_memories(
            query=query,
            limit=limit * 2,  # Get more results for filtering
            priority_only=priority_only
        )
        
        # Filter results
        filtered_memories = []
        for memory in memories:
            metadata = memory.get("metadata", {})
            
            # Filter by scope
            if scope and metadata.get("scope") != scope:
                continue
            
            # Filter by agent_name
            if agent_name and metadata.get("agent_name") != agent_name:
                continue
            
            # Filter by topics
            if topics:
                memory_topics = metadata.get("topics", [])
                if not any(topic in memory_topics for topic in topics):
                    continue
            
            filtered_memories.append(memory)
        
        # Return limited results
        return filtered_memories[:limit]
    
    async def format_memories_as_context(
        self, 
        memories: List[Dict[str, Any]],
        include_metadata: bool = False
    ) -> str:
        """
        Format a list of memories as context for an agent
        
        Args:
            memories: List of memory items
            include_metadata: Whether to include metadata in the context
            
        Returns:
            Formatted context string
        """
        return await self.vector_memory.format_memories_as_context(memories)

# Singleton instance
_shared_memory = None

def get_shared_memory() -> SharedMemoryLayer:
    """
    Get the singleton SharedMemoryLayer instance
    """
    global _shared_memory
    if _shared_memory is None:
        _shared_memory = SharedMemoryLayer()
    return _shared_memory
