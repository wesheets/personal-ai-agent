import os
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
import logging

# Configure logging
logger = logging.getLogger("vector_memory")

# Singleton instance
_vector_memory_instance = None

def get_vector_memory() -> 'VectorMemorySystem':
    """
    Get the singleton instance of VectorMemorySystem
    
    Returns:
        The VectorMemorySystem instance
    """
    global _vector_memory_instance
    if _vector_memory_instance is None:
        _vector_memory_instance = VectorMemorySystem()
    return _vector_memory_instance

class VectorMemorySystem:
    """Mock Vector memory system for development/testing"""
    
    def __init__(self):
        """Initialize the mock vector memory system"""
        logger.info("Initializing mock VectorMemorySystem for development/testing")
        
        # In-memory storage for memories
        self.memories = []
        
        # Table name for vector storage (kept for compatibility)
        self.table_name = "agent_memories"
        
        logger.info("Mock VectorMemorySystem initialized successfully")
        print("✅ Mock VectorMemorySystem initialized for development/testing")
    
    def _ensure_table_exists(self):
        """Mock method for table creation"""
        pass
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Mock embedding generation - returns a fixed-length vector of zeros
        
        Args:
            text: The text to get embedding for
            
        Returns:
            A mock embedding vector
        """
        # Return a mock embedding (vector of zeros)
        return [0.0] * 384  # Standard embedding length
    
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
