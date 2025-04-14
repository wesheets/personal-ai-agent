"""
Test Memory ID Retrieval Across Sessions

This script tests memory ID retrieval across sessions by:
1. Writing a memory to the database
2. Closing the database connection
3. Reopening the database connection
4. Reading the memory back using its memory_id

This confirms that memory persistence works across different sessions.
"""

import sys
import os
import json
import uuid
from datetime import datetime
import sqlite3

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the memory database
from app.db.memory_db import MemoryDB, DB_FILE

def test_memory_id_across_sessions():
    """Test memory ID retrieval across different database sessions"""
    print("🧪 Starting memory ID retrieval across sessions test...")
    
    # Generate a unique test memory
    test_memory_id = str(uuid.uuid4())
    test_memory = {
        "memory_id": test_memory_id,
        "agent_id": "cross-session-agent",
        "type": "cross-session-test",
        "content": f"Testing memory retrieval across sessions at {datetime.utcnow().isoformat()}",
        "tags": ["test", "sqlite", "cross-session"],
        "timestamp": datetime.utcnow().isoformat(),
        "project_id": "cross-session-project",
        "status": "testing",
        "task_type": "cross-session",
        "task_id": "cross-session-task",
        "memory_trace_id": "cross-session-trace"
    }
    
    try:
        # Step 1: Create first database session
        print("🔌 Creating first database session")
        db_session1 = MemoryDB()
        
        # Step 2: Write the test memory to the database
        print(f"📝 Writing test memory with ID: {test_memory['memory_id']}")
        db_session1.write_memory(test_memory)
        
        # Step 3: Close the first database session
        print("🔌 Closing first database session")
        db_session1.close()
        
        # Step 4: Create a new database session
        print("🔌 Creating new database session")
        db_session2 = MemoryDB()
        
        # Step 5: Read the memory back by its ID
        print(f"🔍 Reading memory with ID: {test_memory['memory_id']}")
        retrieved_memory = db_session2.read_memory_by_id(test_memory['memory_id'])
        
        if not retrieved_memory:
            print("❌ Failed to retrieve memory by ID in new session")
            return False
        
        # Step 6: Verify the content matches
        if retrieved_memory['content'] != test_memory['content']:
            print("❌ Memory content does not match")
            print(f"Original: {test_memory['content']}")
            print(f"Retrieved: {retrieved_memory['content']}")
            return False
        
        print("✅ Memory content matches across sessions")
        
        # Step 7: Verify all fields are preserved
        for key in test_memory:
            if key == 'tags' or key == 'agent_tone':
                # These are stored as JSON strings and parsed back
                continue
            if retrieved_memory[key] != test_memory[key]:
                print(f"❌ Memory field '{key}' does not match")
                print(f"Original: {test_memory[key]}")
                print(f"Retrieved: {retrieved_memory[key]}")
                return False
        
        print("✅ All memory fields preserved across sessions")
        
        # Step 8: Close the second database session
        print("🔌 Closing second database session")
        db_session2.close()
        
        # Step 9: Verify the database file exists
        if not os.path.exists(DB_FILE):
            print(f"❌ Database file not found at {DB_FILE}")
            return False
        
        print(f"✅ Database file exists at {DB_FILE}")
        
        # Step 10: Get database file size
        db_size = os.path.getsize(DB_FILE)
        print(f"📊 Database file size: {db_size} bytes")
        
        # Step 11: Connect directly to the database to verify structure
        print("🔍 Verifying database structure")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Tables in database: {[t[0] for t in tables]}")
        
        # Check memory count
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        print(f"📊 Total memories in database: {count}")
        
        # Close direct connection
        conn.close()
        
        print("✅ Memory ID retrieval across sessions test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Error during memory ID retrieval across sessions test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_memory_id_across_sessions()
    sys.exit(0 if success else 1)
