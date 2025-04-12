import uuid
from datetime import datetime
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import asyncio

# Use a file-based storage to persist memories between processes
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory_store.json")

# Path to agent manifest file
AGENT_MANIFEST_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "agent_manifest.json")

# Initialize memory_store
memory_store = []

# Initialize agent_manifest cache
agent_manifest = {}

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

# Load agent manifest
def _load_agent_manifest():
    global agent_manifest
    try:
        if os.path.exists(AGENT_MANIFEST_FILE):
            with open(AGENT_MANIFEST_FILE, 'r') as f:
                agent_manifest = json.load(f)
    except Exception as e:
        print(f"Error loading agent manifest: {str(e)}")
        agent_manifest = {}

# Save memories to file
def _save_memories():
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory_store, f)
    except Exception as e:
        print(f"Error saving memories: {str(e)}")

# Get agent tone profile from manifest
def get_agent_tone_profile(agent_id: str) -> Optional[Dict]:
    # Ensure agent manifest is loaded
    if not agent_manifest:
        _load_agent_manifest()
    
    # Normalize agent_id for lookup (handle both formats: "hal-agent" and "hal_agent")
    normalized_id = agent_id.replace('_', '-')
    
    # Look up agent in manifest
    if normalized_id in agent_manifest and "tone_profile" in agent_manifest[normalized_id]:
        return agent_manifest[normalized_id]["tone_profile"]
    
    # Try alternative format
    alternative_id = agent_id.replace('-', '_')
    if alternative_id in agent_manifest and "tone_profile" in agent_manifest[alternative_id]:
        return agent_manifest[alternative_id]["tone_profile"]
    
    # If agent not found or no tone profile, return None
    return None

# Load memories and agent manifest on module import
_load_memories()
_load_agent_manifest()

def write_memory(agent_id: str, type: str, content: str, tags: list, project_id: Optional[str] = None, status: Optional[str] = None, task_type: Optional[str] = None, task_id: Optional[str] = None, memory_trace_id: Optional[str] = None, metadata: Optional[Dict] = None):
    # Get agent tone profile
    agent_tone = get_agent_tone_profile(agent_id)
    
    memory = {
        "memory_id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "type": type,
        "content": content,
        "tags": tags,
        "timestamp": datetime.utcnow().isoformat(),
        "project_id": project_id,
        "status": status,
        "task_type": task_type,
        "task_id": task_id,
        "memory_trace_id": memory_trace_id,
        "metadata": metadata
    }
    
    # Add agent tone if available
    if agent_tone:
        memory["agent_tone"] = agent_tone
        print(f"🎭 Added tone profile for {agent_id}")
    
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
            
            # Include agent_tone in metadata if available
            metadata = {
                "agent_name": agent_id,
                "type": type,
                "memory_id": memory["memory_id"]
            }
            
            if agent_tone:
                metadata["agent_tone"] = agent_tone
            
            await shared_memory.store_memory(
                content=content,
                metadata=metadata,
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
