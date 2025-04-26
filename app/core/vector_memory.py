"""
Vector Memory System

This module provides a simple vector memory system for storing and retrieving text.
"""
import os
import time
import json
import logging
import asyncio
from typing import Dict, List, Tuple, Any, Optional

# Configure logging
logger = logging.getLogger("app.core.vector_memory")

class MockMemorySystem:
    """
    A mock implementation of a vector memory system.
    This is used for development and testing.
    """
    
    def __init__(self):
        """Initialize the mock memory system."""
        self.memories = []
        self.next_id = 1
        
        # Load existing memories if available
        self._load_memories()
    
    def _load_memories(self):
        """Load memories from disk if available."""
        try:
            memory_file = os.path.join(os.path.dirname(__file__), "../data/memories.json")
            if os.path.exists(memory_file):
                with open(memory_file, "r") as f:
                    self.memories = json.load(f)
                
                # Find the highest ID to continue from
                if self.memories:
                    highest_id = max([int(m.get("id", "0").replace("mem_", "")) for m in self.memories])
                    self.next_id = highest_id + 1
                
                logger.info(f"Loaded {len(self.memories)} memories from disk")
        except Exception as e:
            logger.error(f"Failed to load memories from disk: {e}")
    
    def _save_memories(self):
        """Save memories to disk."""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.join(os.path.dirname(__file__), "../data"), exist_ok=True)
            
            memory_file = os.path.join(os.path.dirname(__file__), "../data/memories.json")
            with open(memory_file, "w") as f:
                json.dump(self.memories, f, indent=2)
            
            logger.info(f"Saved {len(self.memories)} memories to disk")
        except Exception as e:
            logger.error(f"Failed to save memories to disk: {e}")
    
    async def store_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Store a text in the memory system.
        
        Args:
            text: The text to store
            metadata: Optional metadata about the text
            
        Returns:
            Tuple of (memory_id, memory_object)
        """
        # Create memory ID
        memory_id = f"mem_{self.next_id}"
        self.next_id += 1
        
        # Create memory object
        memory = {
            "id": memory_id,
            "content": text,
            "metadata": metadata or {},
            "created_at": time.time()
        }
        
        # Add to memories
        self.memories.append(memory)
        
        # Save to disk
        self._save_memories()
        
        return memory_id, memory
    
    async def search_memories(self, query: str, limit: int = 5) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Search for memories similar to the query.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            Tuple of (list of memories, search metadata)
        """
        # In a real implementation, this would use vector similarity search
        # For this mock, we'll just do simple substring matching
        results = []
        
        for memory in self.memories:
            if query.lower() in memory["content"].lower():
                results.append(memory)
        
        # Sort by recency (newest first)
        results.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        
        # Limit results
        results = results[:limit]
        
        return results, {"method": "substring_match", "query": query}
    
    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by ID
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            The memory object or None if not found
        """
        for memory in self.memories:
            if memory.get("id") == memory_id:
                return memory
        
        return None
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a memory by ID
        
        Args:
            memory_id: The ID of the memory to update
            updates: Dictionary of fields to update
            
        Returns:
            True if updated, False if not found
        """
        for memory in self.memories:
            if memory.get("id") == memory_id:
                # Update fields
                for key, value in updates.items():
                    if key == "metadata" and isinstance(value, dict) and isinstance(memory.get("metadata"), dict):
                        # Merge metadata
                        memory["metadata"].update(value)
                    else:
                        memory[key] = value
                
                # Save changes
                self._save_memories()
                
                return True
        
        return False
    
    async def tag_memory(self, memory_id: str, tags: List[str]) -> bool:
        """
        Add tags to a memory
        
        Args:
            memory_id: The ID of the memory to tag
            tags: List of tags to add
            
        Returns:
            True if tagged, False if not found
        """
        for memory in self.memories:
            if memory.get("id") == memory_id:
                # Initialize metadata and tags if needed
                if "metadata" not in memory:
                    memory["metadata"] = {}
                
                if "tags" not in memory["metadata"]:
                    memory["metadata"]["tags"] = []
                
                # Add new tags
                for tag in tags:
                    if tag not in memory["metadata"]["tags"]:
                        memory["metadata"]["tags"].append(tag)
                
                # Save changes
                self._save_memories()
                
                return True
        
        return False
    
    async def set_priority(self, memory_id: str, priority: bool = True) -> bool:
        """
        Set a memory as priority
        
        Args:
            memory_id: The ID of the memory to update
            priority: Whether this is a priority memory
            
        Returns:
            True if updated, False if not found
        """
        for memory in self.memories:
            if memory.get("id") == memory_id:
                # Initialize metadata if needed
                if "metadata" not in memory:
                    memory["metadata"] = {}
                
                # Set priority flag
                memory["metadata"]["priority"] = priority
                
                # Save changes
                self._save_memories()
                
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
                
                # Save changes
                self._save_memories()
                
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

    # Adapter methods to match the expected API in memory_api_routes.py
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
        try:
            # Log the parameters for debugging
            logger.info(f"add_memory called with: project_id={project_id}, content={content[:50]}..., metadata={metadata}, tags={tags}, agent_id={agent_id}")
            
            # Prepare metadata with additional fields
            combined_metadata = metadata or {}
            combined_metadata["project_id"] = project_id
            
            if tags:
                combined_metadata["tags"] = tags
            
            if agent_id:
                combined_metadata["agent_id"] = agent_id
            
            # Call the underlying store_memory method
            memory_id, _ = await self.store_memory(content, combined_metadata)
            
            # Log success
            logger.info(f"Successfully added memory with ID: {memory_id}")
            
            return memory_id
        except Exception as e:
            # Log the error
            logger.error(f"Error in add_memory adapter: {str(e)}")
            # Re-raise to ensure the error is properly handled
            raise
    
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
        try:
            # Log the parameters for debugging
            logger.info(f"search_memory called with: project_id={project_id}, query={query}, limit={limit}, tags={tags}, agent_id={agent_id}, threshold={threshold}")
            
            # Get all memories
            results, _ = await self.search_memories(query, limit)
            
            # Log initial results
            logger.info(f"Initial search returned {len(results)} results")
            
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
            
            # Log filtered results
            logger.info(f"After filtering, returning {len(filtered_results)} results")
            
            return filtered_results
        except Exception as e:
            # Log the error
            logger.error(f"Error in search_memory adapter: {str(e)}")
            # Re-raise to ensure the error is properly handled
            raise

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
        logger.info("Initialized new MockMemorySystem instance")
    
    return _memory_system
