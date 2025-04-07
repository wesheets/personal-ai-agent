import os
import time
import uuid
from typing import Dict, Any, Optional, List
import json

# This is a simple in-memory implementation
# In a production environment, this would use Supabase or a vector database
class MemoryManager:
    """
    Manages the storage and retrieval of agent interactions
    """
    def __init__(self):
        self.memories = []
        self.memory_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "db", 
            "memory.json"
        )
        self._load_memories()
    
    def _load_memories(self):
        """Load memories from file if it exists"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    self.memories = json.load(f)
        except Exception as e:
            print(f"Error loading memories: {str(e)}")
            # Initialize with empty list if there's an error
            self.memories = []
    
    def _save_memories(self):
        """Save memories to file"""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            
            with open(self.memory_file, 'w') as f:
                json.dump(self.memories, f, indent=2)
        except Exception as e:
            print(f"Error saving memories: {str(e)}")
    
    async def store(
        self, 
        input_text: str, 
        output_text: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store an interaction in the memory system
        
        Args:
            input_text: The user's input text
            output_text: The agent's output text
            metadata: Optional metadata about the interaction
            
        Returns:
            The ID of the stored memory
        """
        memory_id = str(uuid.uuid4())
        timestamp = time.time()
        
        memory_item = {
            "id": memory_id,
            "input": input_text,
            "output": output_text,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "timestamp_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        }
        
        self.memories.append(memory_item)
        self._save_memories()
        
        return memory_id
    
    async def query(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query the memory system for relevant past interactions
        
        Args:
            query: The query text
            limit: Maximum number of results to return
            
        Returns:
            List of memory items sorted by relevance
        """
        # This is a simple implementation that just does keyword matching
        # In a production environment, this would use vector similarity search
        
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # Score each memory based on simple keyword matching
        scored_memories = []
        for memory in self.memories:
            score = 0
            
            # Check if query terms appear in input or output
            if query_lower in memory["input"].lower():
                score += 2
            if query_lower in memory["output"].lower():
                score += 1
                
            # Add to scored memories if there's any match
            if score > 0:
                scored_memories.append((score, memory))
        
        # Sort by score (descending) and timestamp (descending)
        scored_memories.sort(key=lambda x: (x[0], x[1]["timestamp"]), reverse=True)
        
        # Return the top results
        return [memory for _, memory in scored_memories[:limit]]
    
    async def get_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            The memory item or None if not found
        """
        for memory in self.memories:
            if memory["id"] == memory_id:
                return memory
        
        return None
    
    async def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, memory in enumerate(self.memories):
            if memory["id"] == memory_id:
                del self.memories[i]
                self._save_memories()
                return True
        
        return False
