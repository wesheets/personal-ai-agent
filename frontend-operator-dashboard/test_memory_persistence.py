#!/usr/bin/env python3
"""
Test script to verify memory persistence between write and read operations.
This script performs a controlled write followed by immediate read operations
to diagnose potential issues with memory persistence.
"""

import os
import sys
import uuid
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory_test")

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the memory database module
from app.db.memory_db import memory_db

def test_memory_persistence():
    """Test memory persistence between write and read operations"""
    
    # Generate a unique test ID
    test_id = str(uuid.uuid4())
    logger.info(f"Starting memory persistence test with ID: {test_id}")
    
    # Create a test memory with the exact structure from the prompt
    memory = {
        "memory_id": f"test-{test_id}",
        "agent_id": "hal",
        "type": "goal_definition",
        "content": "Final memory test",
        "tags": ["test", "user:ted_001"],
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "goal_id": "goal_123"
        }
    }
    
    logger.info(f"Created test memory: {json.dumps(memory, indent=2)}")
    
    # Step 1: Write the memory to the database
    logger.info("Step 1: Writing memory to database...")
    try:
        written_memory = memory_db.write_memory(memory)
        logger.info(f"✅ Memory successfully written with ID: {written_memory['memory_id']}")
    except Exception as e:
        logger.error(f"❌ Error writing memory: {str(e)}")
        return False
    
    # Step 2: Read the memory by ID
    logger.info("Step 2: Reading memory by ID...")
    try:
        read_memory = memory_db.read_memory_by_id(memory["memory_id"])
        if read_memory:
            logger.info(f"✅ Memory successfully read by ID: {read_memory['memory_id']}")
            logger.info(f"Memory content: {json.dumps(read_memory, indent=2)}")
        else:
            logger.error(f"❌ Memory not found by ID: {memory['memory_id']}")
            return False
    except Exception as e:
        logger.error(f"❌ Error reading memory by ID: {str(e)}")
        return False
    
    # Step 3: Read memories with limit=5
    logger.info("Step 3: Reading memories with limit=5...")
    try:
        memories = memory_db.read_memories(limit=5)
        logger.info(f"✅ Read {len(memories)} memories with limit=5")
        
        # Check if our test memory is in the results
        found = False
        for m in memories:
            if m.get("memory_id") == memory["memory_id"]:
                found = True
                logger.info(f"✅ Test memory found in read_memories results")
                break
        
        if not found:
            logger.error(f"❌ Test memory not found in read_memories results")
            logger.info(f"Memory IDs in results: {[m.get('memory_id') for m in memories]}")
            return False
    except Exception as e:
        logger.error(f"❌ Error reading memories: {str(e)}")
        return False
    
    # Step 4: Read memories with goal_id filter
    logger.info("Step 4: Reading memories with goal_id filter...")
    try:
        # First, check if we can read by agent_id
        agent_memories = memory_db.read_memories(agent_id="hal", limit=10)
        logger.info(f"✅ Read {len(agent_memories)} memories with agent_id='hal'")
        
        # Now try to read by goal_id via the API endpoint
        # This is a bit tricky since read_memories doesn't directly support goal_id filtering
        # We'll need to filter the results manually
        all_memories = memory_db.read_memories(limit=100)
        goal_memories = []
        
        for m in all_memories:
            metadata = m.get("metadata", {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    continue
            
            if metadata.get("goal_id") == "goal_123":
                goal_memories.append(m)
        
        logger.info(f"✅ Found {len(goal_memories)} memories with goal_id='goal_123'")
        
        if len(goal_memories) > 0:
            logger.info(f"✅ Successfully filtered memories by goal_id")
            logger.info(f"Memory IDs with goal_id='goal_123': {[m.get('memory_id') for m in goal_memories]}")
        else:
            logger.error(f"❌ No memories found with goal_id='goal_123'")
            return False
    except Exception as e:
        logger.error(f"❌ Error reading memories with filters: {str(e)}")
        return False
    
    # Step 5: Check memory_view table directly with SQL
    logger.info("Step 5: Checking memory_view table directly with SQL...")
    try:
        conn = memory_db._get_connection()
        cursor = conn.cursor()
        
        # Check if our memory exists in the memories table
        cursor.execute("SELECT * FROM memories WHERE memory_id = ?", (memory["memory_id"],))
        row = cursor.fetchone()
        
        if row:
            logger.info(f"✅ Memory found in memories table with SQL query")
        else:
            logger.error(f"❌ Memory not found in memories table with SQL query")
            return False
        
        # Check if our memory exists in the memory_view view
        cursor.execute("SELECT * FROM memory_view WHERE memory_id = ?", (memory["memory_id"],))
        view_row = cursor.fetchone()
        
        if view_row:
            logger.info(f"✅ Memory found in memory_view with SQL query")
        else:
            logger.error(f"❌ Memory not found in memory_view with SQL query")
            return False
        
        # Check if goal_id is queryable in the metadata column
        cursor.execute("SELECT * FROM memories WHERE metadata LIKE ?", (f"%goal_123%",))
        metadata_rows = cursor.fetchall()
        
        if metadata_rows:
            logger.info(f"✅ Found {len(metadata_rows)} memories with goal_id in metadata")
        else:
            logger.error(f"❌ No memories found with goal_id in metadata")
            return False
    except Exception as e:
        logger.error(f"❌ Error executing SQL queries: {str(e)}")
        return False
    
    logger.info("✅ All tests passed successfully!")
    return True

if __name__ == "__main__":
    success = test_memory_persistence()
    if success:
        print("\n✅ MEMORY PERSISTENCE TEST: SUCCESS")
        sys.exit(0)
    else:
        print("\n❌ MEMORY PERSISTENCE TEST: FAILED")
        sys.exit(1)
