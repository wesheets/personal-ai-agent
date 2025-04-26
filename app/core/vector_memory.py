"""
Vector Memory Module

This module provides a vector-based memory system for storing and retrieving
agent interactions and other information.
"""
import logging
import time
import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger("app.core.vector_memory")

class MockMemorySystem:
    """
    A mock implementation of a vector memory system for development and testing.
    """
    
    def __init__(self):
        """Initialize the mock memory system."""
        self.memories = []
        logger.info("Initialized mock memory system")
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Generate a mock embedding for text.
        
        Args:
            text: The text to generate an embedding for
            
        Returns:
            A list of floats representing the embedding
        """
        # Generate a deterministic but unique embedding based on the text
        # This is just for testing - real embeddings would use a proper model
        import hashlib
        
        # Get hash of text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to a list of floats
        embedding = []
        for i in range(0, len(text_hash), 2):
            if i + 2 <= len(text_hash):
                hex_pair = text_hash[i:i+2]
                float_val = int(hex_pair, 16) / 255.0  # Normalize to 0-1
                embedding.append(float_val)
        
        # Pad to standard embedding length
        while len(embedding) < 32:
            embedding.append(0.0)
        
        return embedding[:32]  # Truncate to standard embedding length
    
    async def store_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None, priority: bool = False) -> Tuple[str, Optional[str]]:
        """
        Store a memory in the mock memory system
        
        Args:
            content: The text content to store
            metadata: Optional metadata about the memory
            priority: Whether this is a priority memory
            
        Returns:
            Tuple of (memory ID, warning message or None)
        """
        # Generate a unique ID
        memory_id = str(uuid.uuid4())
        
        # Create memory object
        memory = {
            "id": memory_id,
            "content": content,
            "metadata": metadata or {},
            "embedding": self._get_embedding(content),
            "priority": priority,
            "created_at": time.time()
        }
        
        # Store in memory
        self.memories.append(memory)
        
        logger.info(f"Stored memory with ID: {memory_id}")
        return memory_id, None
    
    async def search_memories(self, query: str, limit: int = 5, priority_only: bool = False) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Mock memory search - returns most recent memories
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            priority_only: Whether to only return priority memories
            
        Returns:
            Tuple of (list of memory items sorted by recency, warning message or None)
        """
        # Filter memories if priority_only is True
        filtered_memories = [m for m in self.memories if not priority_only or m.get("priority", False)]
        
        # Sort by created_at (most recent first)
        sorted_memories = sorted(filtered_memories, key=lambda m: m.get("created_at", 0), reverse=True)
        
        # Limit results
        results = sorted_memories[:limit]
        
        logger.info(f"Returning {len(results)} mock memories")
        return results, None
    
    async def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            The memory item or None if not found
        """
        for memory in self.memories:
            if memory.get("id") == memory_id:
                return memory
        
        return None
    
    async def update_memory_priority(self, memory_id: str, priority: bool) -> bool:
        """
        Update the priority flag of a memory
        
        Args:
            memory_id: The ID of the memory to update
            priority: The new priority value
            
        Returns:
            True if updated, False if not found
        """
        for memory in self.memories:
            if memory.get("id") == memory_id:
                memory["priority"] = priority
                return True
        
        return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, memory in enumerate(self.memories):
            if memory.get("id") == memory_id:
                self.memories.pop(i)
                return True
        
        return False
    
    async def format_memories_as_context(self, memories: List[Dict[str, Any]]) -> str:
        """
        Format a list of memories as context for an agent
        
        Args:
            memories: List of memory items
            
        Returns:
            Formatted context string
        """
        if not memories:
            return ""
        
        context_parts = ["## Relevant Past Interactions\n"]
        
        for memory in memories:
            # Format timestamp if available
            timestamp = memory.get("created_at", "")
            if timestamp:
                try:
                    # Convert to more readable format
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                except:
                    # If conversion fails, use as is
                    pass
            
            # Format memory
            memory_text = f"- {timestamp}: {memory['content']}"
            
            # Add metadata if available and not empty
            metadata = memory.get("metadata", {})
            if metadata and isinstance(metadata, dict) and len(metadata) > 0:
                # Format metadata as key-value pairs
                metadata_str = ", ".join([f"{k}: {v}" for k, v in metadata.items()])
                memory_text += f" [{metadata_str}]"
            
            context_parts.append(memory_text)
        
        return "\n".join(context_parts)

    # Add adapter methods to match the expected API in memory_api_routes.py
    async def add_memory(self, project_id: str, content: str, metadata: Optional[Dict[str, Any]] = None, 
                         tags: Optional[List[str]] = None, agent_id: Optional[str] = None) -> str:
        """
        Adapter method for add_memory to match the API expected by memory_api_routes.py
        
        Args:
            project_id: The project ID
            content: The text content to store
            metadata: Optional metadata about the memory
            tags: Optional tags for the memory
            agent_id: Optional agent ID
            
        Returns:
            Memory ID
        """
        # Prepare metadata with additional fields
        combined_metadata = metadata or {}
        combined_metadata["project_id"] = project_id
        
        if tags:
            combined_metadata["tags"] = tags
        
        if agent_id:
            combined_metadata["agent_id"] = agent_id
        
        # Call the underlying store_memory method
        memory_id, _ = await self.store_memory(content, combined_metadata)
        return memory_id
    
    async def search_memory(self, project_id: str, query: str, limit: int = 5, 
                           tags: Optional[List[str]] = None, agent_id: Optional[str] = None,
                           threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Adapter method for search_memory to match the API expected by memory_api_routes.py
        
        Args:
            project_id: The project ID
            query: The search query
            limit: Maximum number of results to return
            tags: Optional tags to filter by
            agent_id: Optional agent ID to filter by
            threshold: Similarity threshold
            
        Returns:
            List of memory items
        """
        # Get all memories
        results, _ = await self.search_memories(query, limit)
        
        # Filter by project_id
        filtered_results = []
        for memory in results:
            metadata = memory.get("metadata", {})
            
            # Check project_id
            if metadata.get("project_id") != project_id:
                continue
            
            # Check tags if specified
            if tags and not any(tag in metadata.get("tags", []) for tag in tags):
                continue
            
            # Check agent_id if specified
            if agent_id and metadata.get("agent_id") != agent_id:
                continue
            
            filtered_results.append(memory)
        
        return filtered_results

# Singleton instance
_memory_system = None

def get_memory_engine():
    """
    Get the memory engine instance.
    
    Returns:
        The memory engine instance
    """
    global _memory_system
    
    if _memory_system is None:
        _memory_system = MockMemorySystem()
    
    return _memory_system
