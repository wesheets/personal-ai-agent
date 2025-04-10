import uuid
from datetime import datetime
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import asyncio

# Use a file-based storage to persist memories between processes
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory_store.json")

# Initialize memory_store
memory_store = []

# Load existing memories if file exists
def _load_memories():
    global memory_store
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                memory_store = json.load(f)
    except Exception as e:
        print(f"Error loading memories: {str(e)}")
        memory_store = []

# Save memories to file
def _save_memories():
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory_store, f)
    except Exception as e:
        print(f"Error saving memories: {str(e)}")

# Load memories on module import
_load_memories()

def write_memory(agent_id: str, type: str, content: str, tags: list, project_id: Optional[str] = None, status: Optional[str] = None, task_type: Optional[str] = None):
    memory = {
        "memory_id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "type": type,
        "content": content,
        "tags": tags,
        "timestamp": datetime.utcnow().isoformat(),
        "project_id": project_id,
        "status": status,
        "task_type": task_type
    }
    
    # Add to local memory store
    memory_store.append(memory)
    _save_memories()  # Save to file after writing
    
    # Also store in shared memory layer
    try:
        # Import here to avoid circular imports
        from app.core.shared_memory import get_shared_memory
        
        # Create async function to store in shared memory
        async def store_in_shared_memory():
            shared_memory = get_shared_memory()
            await shared_memory.store_memory(
                content=content,
                metadata={
                    "agent_name": agent_id,
                    "type": type,
                    "memory_id": memory["memory_id"]
                },
                scope="agent",
                agent_name=agent_id,
                topics=tags
            )
        
        # Run the async function in a new event loop if we're not in an async context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, create a task
                asyncio.create_task(store_in_shared_memory())
            else:
                # We're not in an async context, run in a new loop
                asyncio.run(store_in_shared_memory())
        except RuntimeError:
            # No event loop, run in a new one
            asyncio.run(store_in_shared_memory())
            
        print(f"🧠 Memory also stored in shared memory layer for {agent_id}")
    except Exception as e:
        print(f"⚠️ Error storing in shared memory: {str(e)}")
    
    print(f"🧠 Memory written for {agent_id}: {memory['memory_id']}")
    return memory

def generate_reflection(memories: List[Dict]) -> str:
    """
    Generate a reflection based on a list of memories.
    This is a placeholder implementation that will be AI-powered later.
    
    Args:
        memories: List of memory dictionaries to reflect on
        
    Returns:
        A reflection string based on the memories
    """
    if not memories:
        return "No relevant memories to reflect on."
    
    return f"I have processed {len(memories)} memories. A pattern is forming..."
