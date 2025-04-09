import uuid
from datetime import datetime

memory_store = []

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
    print(f"🧠 Memory written for {agent_id}: {memory['memory_id']}")
    return memory
