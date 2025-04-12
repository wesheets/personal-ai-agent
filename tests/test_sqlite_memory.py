"""
Test SQLite Memory Persistence

This script tests the SQLite-backed memory persistence by:
1. Writing a new memory to the database
2. Reading it back using its memory_id
3. Verifying the content matches
4. Testing memory retrieval with various filters

This confirms that the SQLite persistence layer works correctly.
"""

import sys
import os
import json
import uuid
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the memory database
from app.db.memory_db import memory_db

def test_sqlite_memory_persistence():
    """Test the SQLite memory persistence functionality"""
    print("🧪 Starting SQLite memory persistence test...")
    
    # Generate a unique test memory
    test_memory = {
        "memory_id": str(uuid.uuid4()),
        "agent_id": "test-agent",
        "type": "test",
        "content": f"Testing SQLite memory persistence at {datetime.utcnow().isoformat()}",
        "tags": ["test", "sqlite", "persistence"],
        "timestamp": datetime.utcnow().isoformat(),
        "project_id": "test-project",
        "status": "testing",
        "task_type": "test",
        "task_id": "test-task",
        "memory_trace_id": "test-trace"
    }
    
    try:
        # Step 1: Write the test memory to the database
        print(f"📝 Writing test memory with ID: {test_memory['memory_id']}")
        memory_db.write_memory(test_memory)
        
        # Step 2: Read the memory back by its ID
        print(f"🔍 Reading memory with ID: {test_memory['memory_id']}")
        retrieved_memory = memory_db.read_memory_by_id(test_memory['memory_id'])
        
        if not retrieved_memory:
            print("❌ Failed to retrieve memory by ID")
            return False
        
        # Step 3: Verify the content matches
        if retrieved_memory['content'] != test_memory['content']:
            print("❌ Memory content does not match")
            print(f"Original: {test_memory['content']}")
            print(f"Retrieved: {retrieved_memory['content']}")
            return False
        
        print("✅ Memory content matches")
        
        # Step 4: Test memory retrieval with various filters
        print("🔍 Testing memory retrieval with agent_id filter")
        agent_memories = memory_db.read_memories(agent_id=test_memory['agent_id'])
        if not any(m['memory_id'] == test_memory['memory_id'] for m in agent_memories):
            print("❌ Failed to retrieve memory with agent_id filter")
            return False
        
        print("🔍 Testing memory retrieval with memory_type filter")
        type_memories = memory_db.read_memories(memory_type=test_memory['type'])
        if not any(m['memory_id'] == test_memory['memory_id'] for m in type_memories):
            print("❌ Failed to retrieve memory with memory_type filter")
            return False
        
        print("🔍 Testing memory retrieval with tag filter")
        tag_memories = memory_db.read_memories(tag=test_memory['tags'][0])
        if not any(m['memory_id'] == test_memory['memory_id'] for m in tag_memories):
            print("❌ Failed to retrieve memory with tag filter")
            return False
        
        print("🔍 Testing memory retrieval with project_id filter")
        project_memories = memory_db.read_memories(project_id=test_memory['project_id'])
        if not any(m['memory_id'] == test_memory['memory_id'] for m in project_memories):
            print("❌ Failed to retrieve memory with project_id filter")
            return False
        
        print("🔍 Testing memory retrieval with task_id filter")
        task_memories = memory_db.read_memories(task_id=test_memory['task_id'])
        if not any(m['memory_id'] == test_memory['memory_id'] for m in task_memories):
            print("❌ Failed to retrieve memory with task_id filter")
            return False
        
        print("✅ All memory retrieval tests passed")
        
        # Print database statistics
        cursor = memory_db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        print(f"📊 Total memories in database: {count}")
        
        print("✅ SQLite memory persistence test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Error during SQLite memory persistence test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_sqlite_memory_persistence()
    sys.exit(0 if success else 1)
