
import asyncio
import sys
import os
from app.core.vector_memory import VectorMemorySystem

# Mock the embedding function for testing
class MockVectorMemorySystem(VectorMemorySystem):
    def __init__(self):
        # Skip the actual initialization that requires Supabase
        self.embedding_model = "text-embedding-ada-002"
        self.table_name = "agent_memories"
    
    def _get_embedding(self, text: str):
        # Return a mock embedding of the correct dimension
        return [0.0] * 1536
    
    async def store_memory(self, content, metadata=None, priority=False):
        print(f"MOCK: Storing memory: {content[:50]}...")
        print(f"MOCK: Metadata: {metadata}")
        print(f"MOCK: Priority: {priority}")
        return "mock-memory-id-12345"
    
    async def search_memories(self, query, limit=5, priority_only=False):
        print(f"MOCK: Searching for: {query}")
        print(f"MOCK: Limit: {limit}, Priority only: {priority_only}")
        return [
            {
                "id": "mock-memory-id-1",
                "content": "This is a mock memory related to " + query,
                "metadata": {"source": "test"},
                "similarity": 0.92,
                "priority": True,
                "created_at": "2025-03-29T18:00:00Z"
            },
            {
                "id": "mock-memory-id-2",
                "content": "Another mock memory about " + query,
                "metadata": {"source": "test"},
                "similarity": 0.85,
                "priority": False,
                "created_at": "2025-03-29T17:30:00Z"
            }
        ]
    
    async def format_memories_as_context(self, memories):
        if not memories:
            return ""
        
        context_parts = ["## Relevant Past Interactions\n"]
        for memory in memories:
            context_parts.append(f"- {memory['created_at']}: {memory['content']}")
        
        return "\n".join(context_parts)

async def test_memory_integration():
    print("Testing Vector Memory System...")
    
    # Create an instance of the mock memory system
    memory = MockVectorMemorySystem()
    
    # Test storing a memory
    print("\n1. Testing memory storage:")
    memory_id = await memory.store_memory(
        content="The user is working on a personal AI agent system with FastAPI, Docker, and OpenAI integration.",
        metadata={"topic": "project", "agent": "builder"},
        priority=True
    )
    print(f"Memory stored with ID: {memory_id}")
    
    # Test searching memories
    print("\n2. Testing memory search:")
    results = await memory.search_memories(
        query="AI agent system",
        limit=5,
        priority_only=False
    )
    print(f"Found {len(results)} memories")
    
    # Test formatting memories as context
    print("\n3. Testing memory formatting:")
    context = await memory.format_memories_as_context(results)
    print("Formatted context:")
    print(context)
    
    print("\nMemory integration tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_memory_integration())
