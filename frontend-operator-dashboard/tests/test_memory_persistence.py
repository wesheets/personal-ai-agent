"""
Memory Persistence Test Script

This script tests memory persistence across app restarts by:
1. Writing test memories to the database
2. Verifying they can be retrieved
3. Simulating an app restart by reinitializing the memory module
4. Verifying the memories are still accessible after restart
"""

import sys
import os
import uuid
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the memory module
from app.api.modules.memory import write_memory, read_memory, initialize_memory_store, memory_store
from app.db.memory_db import memory_db

def test_memory_persistence():
    """Test memory persistence across app restarts"""
    print("\n🧪 TESTING MEMORY PERSISTENCE ACROSS RESTARTS 🧪")
    print("=" * 70)
    
    # Step 1: Write test memories
    print("\n📝 Step 1: Writing test memories...")
    memory_ids = []
    
    for i in range(2):
        memory_id = str(uuid.uuid4())
        memory_ids.append(memory_id)
        
        memory = write_memory(
            agent_id="test_agent",
            type="test_memory",
            content=f"Test memory {i+1} created at {datetime.now().isoformat()}",
            project_id="persistence_test",
            tags=["test", "persistence"],
            status="success"
        )
        
        print(f"✅ Created test memory {i+1}: {memory_id}")
    
    # Step 2: Verify memories can be retrieved
    print("\n🔍 Step 2: Verifying memories can be retrieved...")
    for i, memory_id in enumerate(memory_ids):
        memory = read_memory(memory_id)
        if memory:
            print(f"✅ Retrieved test memory {i+1}: {memory_id}")
        else:
            print(f"❌ Failed to retrieve test memory {i+1}: {memory_id}")
    
    # Step 3: Simulate app restart by clearing and reinitializing memory store
    print("\n🔄 Step 3: Simulating app restart...")
    print(f"📊 Before restart: memory_store has {len(memory_store)} entries")
    
    # Clear the memory store to simulate restart
    memory_store.clear()
    print(f"📊 After clearing: memory_store has {len(memory_store)} entries")
    
    # Reinitialize from SQLite
    count = initialize_memory_store()
    print(f"📊 After reinitialization: memory_store has {len(memory_store)} entries")
    
    # Step 4: Verify memories are still accessible after restart
    print("\n🔍 Step 4: Verifying memories are still accessible after restart...")
    for i, memory_id in enumerate(memory_ids):
        memory = read_memory(memory_id)
        if memory:
            print(f"✅ Retrieved test memory {i+1} after restart: {memory_id}")
        else:
            print(f"❌ Failed to retrieve test memory {i+1} after restart: {memory_id}")
    
    # Step 5: Verify /memory/recent would return the test memories
    print("\n🔍 Step 5: Verifying /memory/recent endpoint functionality...")
    recent_memories = memory_db.read_memories(
        agent_id="test_agent",
        memory_type="test_memory",
        limit=5
    )
    
    if recent_memories:
        print(f"✅ /memory/recent would return {len(recent_memories)} test memories")
        for memory in recent_memories:
            print(f"  - {memory['memory_id']} ({memory['timestamp']})")
    else:
        print("❌ /memory/recent would return no test memories")
    
    print("\n" + "=" * 70)
    print("🏁 MEMORY PERSISTENCE TEST COMPLETE")
    
    # Return success if all memories were retrieved after restart
    return all(read_memory(memory_id) for memory_id in memory_ids)

if __name__ == "__main__":
    success = test_memory_persistence()
    print(f"\n🧪 Test result: {'SUCCESS ✅' if success else 'FAILURE ❌'}")
    sys.exit(0 if success else 1)
