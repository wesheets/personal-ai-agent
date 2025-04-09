import uuid
from datetime import datetime
import os
import json
from pathlib import Path

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

def write_memory(agent_id: str, type: str, content: str, tags: list):
    memory = {
        "memory_id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "type": type,
        "content": content,
        "tags": tags,
        "timestamp": datetime.utcnow().isoformat()
    }
    memory_store.append(memory)
    _save_memories()  # Save to file after writing
    print(f"🧠 Memory written for {agent_id}: {memory['memory_id']}")
    return memory
