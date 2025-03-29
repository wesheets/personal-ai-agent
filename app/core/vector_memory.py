import os
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
from openai import OpenAI
import numpy as np
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VectorMemorySystem:
    """
    Vector-based memory system using Supabase with pgvector
    """
    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase = create_client(supabase_url, supabase_key)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = "text-embedding-ada-002"
        self.table_name = "agent_memories"
        
        # Ensure the table exists
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """
        Ensure the vector table exists in Supabase
        """
        try:
            # Check if table exists by querying it
            self.supabase.table(self.table_name).select("id").limit(1).execute()
        except Exception as e:
            # Table doesn't exist, create it
            # Note: This is a simplified approach. In production, you would use migrations
            # or a more robust method to create and manage database schema
            print(f"Creating table {self.table_name} for vector storage")
            
            # SQL to create the table with pgvector extension
            # This would typically be done through Supabase UI or migrations
            # For demonstration purposes only
            sql = f"""
            -- Enable pgvector extension if not already enabled
            CREATE EXTENSION IF NOT EXISTS vector;
            
            -- Create the table if it doesn't exist
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                content TEXT NOT NULL,
                metadata JSONB,
                embedding VECTOR(1536),
                priority BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Create an index for vector similarity search
            CREATE INDEX IF NOT EXISTS {self.table_name}_embedding_idx ON {self.table_name} USING ivfflat (embedding vector_cosine_ops);
            """
            
            # Execute the SQL (note: in practice, you would use migrations)
            # This is simplified for demonstration
            print("Note: In a production environment, you should use migrations to create database schema")
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text using OpenAI's embedding API
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    async def store_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None, priority: bool = False) -> str:
        """
        Store a memory in the vector database
        
        Args:
            content: The text content to store
            metadata: Optional metadata about the memory
            priority: Whether this is a priority memory
            
        Returns:
            The ID of the stored memory
        """
        # Get embedding for the content
        embedding = self._get_embedding(content)
        
        # Store in Supabase
        result = self.supabase.table(self.table_name).insert({
            "content": content,
            "metadata": metadata or {},
            "embedding": embedding,
            "priority": priority
        }).execute()
        
        # Return the ID of the inserted record
        return result.data[0]["id"]
    
    async def search_memories(self, query: str, limit: int = 5, priority_only: bool = False) -> List[Dict[str, Any]]:
        """
        Search for memories similar to the query
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            priority_only: Whether to only return priority memories
            
        Returns:
            List of memory items sorted by relevance
        """
        # Get embedding for the query
        query_embedding = self._get_embedding(query)
        
        # Build the query
        rpc_query = {
            "query_embedding": query_embedding,
            "match_threshold": 0.5,  # Adjust as needed
            "match_count": limit
        }
        
        # Execute the query
        if priority_only:
            # Only return priority memories
            result = self.supabase.rpc(
                "match_memories_priority", 
                rpc_query
            ).execute()
        else:
            # Return all memories
            result = self.supabase.rpc(
                "match_memories", 
                rpc_query
            ).execute()
        
        return result.data
    
    async def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            The memory item or None if not found
        """
        result = self.supabase.table(self.table_name).select("*").eq("id", memory_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
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
        result = self.supabase.table(self.table_name).update({"priority": priority}).eq("id", memory_id).execute()
        
        return len(result.data) > 0
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = self.supabase.table(self.table_name).delete().eq("id", memory_id).execute()
        
        return len(result.data) > 0
    
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
