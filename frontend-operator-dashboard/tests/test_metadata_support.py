"""
Test script to verify metadata support in the memory system.

This script tests:
1. Writing a memory with metadata
2. Reading the memory back and verifying metadata is preserved
3. Querying memories with specific metadata
"""

import sys
import os
import uuid
import json
from datetime import datetime

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the memory modules
from app.api.modules.memory import write_memory, initialize_memory_store
from app.db.memory_db import memory_db

def test_metadata_support():
    """Test that metadata is properly stored and retrieved"""
    print("\n🧪 Testing metadata support in memory system...")
    
    # Generate unique test IDs
    test_id = f"test_{uuid.uuid4().hex[:8]}"
    agent_id = f"test_agent_{uuid.uuid4().hex[:6]}"
    
    # Create test metadata
    test_metadata = {
        "test_key": "test_value",
        "numeric_value": 42,
        "nested": {
            "inner_key": "inner_value",
            "array": [1, 2, 3]
        },
        "test_id": test_id
    }
    
    print(f"\n📝 Writing test memory with metadata for agent {agent_id}...")
    
    # Write a memory with metadata
    memory = write_memory(
        agent_id=agent_id,
        type="test_metadata",
        content=f"Test content for metadata support - {test_id}",
        tags=["test", "metadata", test_id],
        project_id="test-project",
        status="testing",
        task_id=f"task_{test_id}",
        metadata=test_metadata
    )
    
    memory_id = memory["memory_id"]
    print(f"✅ Memory written with ID: {memory_id}")
    
    # Read the memory back directly from the database
    print(f"\n🔍 Reading memory directly from database...")
    db_memory = memory_db.read_memory_by_id(memory_id)
    
    if not db_memory:
        print(f"❌ Failed to read memory from database: {memory_id}")
        return False
    
    print(f"✅ Memory retrieved from database: {memory_id}")
    
    # Verify metadata is present and correct
    if "metadata" not in db_memory:
        print(f"❌ Metadata field missing from retrieved memory")
        return False
    
    if db_memory["metadata"] != test_metadata:
        print(f"❌ Metadata mismatch:")
        print(f"  Expected: {json.dumps(test_metadata, indent=2)}")
        print(f"  Actual:   {json.dumps(db_memory['metadata'], indent=2)}")
        return False
    
    print(f"✅ Metadata correctly stored and retrieved")
    
    # Test reading through the memory API
    print(f"\n🔄 Simulating app restart by clearing and reinitializing memory store...")
    
    # Clear the in-memory store to simulate an app restart
    from app.api.modules.memory import memory_store
    memory_store.clear()
    
    # Reinitialize from database
    count = initialize_memory_store()
    print(f"✅ Reinitialized memory store with {count} memories")
    
    # Read the memory through the API
    print(f"\n🔍 Reading memory through API after reinitialization...")
    
    # Import the read function
    from app.api.modules.memory import read_memory
    
    # Check if memory exists in memory_store directly
    from app.api.modules.memory import memory_store
    matching_memories = [m for m in memory_store if m["memory_id"] == memory_id]
    
    if not matching_memories:
        print(f"❌ Memory not found in memory_store after reinitialization")
        return False
    
    api_memory = matching_memories[0]
    
    # Verify metadata is present and correct
    if "metadata" not in api_memory:
        print(f"❌ Metadata field missing from API-retrieved memory")
        return False
    
    if api_memory["metadata"] != test_metadata:
        print(f"❌ Metadata mismatch in API-retrieved memory:")
        print(f"  Expected: {json.dumps(test_metadata, indent=2)}")
        print(f"  Actual:   {json.dumps(api_memory['metadata'], indent=2)}")
        return False
    
    print(f"✅ Metadata correctly retrieved through API after reinitialization")
    
    # Test querying memories with specific metadata
    print(f"\n🔍 Testing querying memories with specific metadata...")
    
    # Query memories with the test_id in metadata
    memories = memory_db.read_memories(agent_id=agent_id, memory_type="test_metadata")
    
    if not memories:
        print(f"❌ Failed to query memories with agent_id={agent_id}, type=test_metadata")
        return False
    
    # Filter memories with matching test_id in metadata
    matching_memories = [m for m in memories if m.get("metadata", {}).get("test_id") == test_id]
    
    if not matching_memories:
        print(f"❌ Failed to find memory with test_id={test_id} in metadata")
        return False
    
    print(f"✅ Successfully queried and filtered memories by metadata")
    
    print("\n✅ All metadata tests passed successfully!")
    return True

if __name__ == "__main__":
    success = test_metadata_support()
    if success:
        print("\n🎉 Metadata support is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Metadata support test failed")
        sys.exit(1)
