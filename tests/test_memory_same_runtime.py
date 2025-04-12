"""
Test Memory Write and Read in Same Runtime

This script tests the memory write and read functionality in the same runtime by:
1. Writing a new memory using the /write endpoint
2. Capturing the returned memory_id
3. Immediately reading the memory using the /read endpoint with the captured memory_id
4. Verifying the content matches

This confirms that memory persistence works correctly within the same runtime.
"""

import sys
import os
import json
import uuid
import requests
from datetime import datetime

# Base URL for API endpoints (default to localhost for testing)
BASE_URL = "http://localhost:8000/api/modules"

def test_memory_write_read_same_runtime(base_url=BASE_URL):
    """Test memory write and read in the same runtime"""
    print("🧪 Starting memory write-read test in same runtime...")
    
    # Generate a unique test memory
    test_memory = {
        "agent_id": "test-agent",
        "memory_type": "test",
        "content": f"Testing memory persistence in same runtime at {datetime.utcnow().isoformat()}",
        "tags": ["test", "persistence", "same-runtime"],
        "project_id": "test-project",
        "status": "testing",
        "task_type": "test"
    }
    
    try:
        # Step 1: Write the test memory
        print("📝 Writing test memory...")
        write_url = f"{base_url}/write"
        write_response = requests.post(write_url, json=test_memory)
        
        if write_response.status_code != 200:
            print(f"❌ Failed to write memory: {write_response.status_code}")
            print(write_response.text)
            return False
        
        write_data = write_response.json()
        memory_id = write_data.get("memory_id")
        
        if not memory_id:
            print("❌ No memory_id returned from write endpoint")
            return False
        
        print(f"✅ Successfully wrote memory with ID: {memory_id}")
        
        # Step 2: Immediately read the memory back
        print(f"🔍 Reading memory with ID: {memory_id}")
        read_url = f"{base_url}/read?memory_id={memory_id}"
        read_response = requests.get(read_url)
        
        if read_response.status_code != 200:
            print(f"❌ Failed to read memory: {read_response.status_code}")
            print(read_response.text)
            return False
        
        read_data = read_response.json()
        
        if read_data.get("status") != "ok":
            print(f"❌ Read response status not ok: {read_data.get('status')}")
            return False
        
        memories = read_data.get("memories", [])
        
        if not memories:
            print("❌ No memories returned from read endpoint")
            return False
        
        memory = memories[0]
        
        # Step 3: Verify the content matches
        if memory.get("content") != test_memory["content"]:
            print("❌ Memory content does not match")
            print(f"Original: {test_memory['content']}")
            print(f"Retrieved: {memory.get('content')}")
            return False
        
        # Step 4: Verify memory_type, content, and tags are present
        if memory.get("type") != test_memory["memory_type"]:
            print("❌ Memory type does not match")
            print(f"Original: {test_memory['memory_type']}")
            print(f"Retrieved: {memory.get('type')}")
            return False
        
        if not memory.get("tags"):
            print("❌ Memory tags are missing")
            return False
        
        if set(memory.get("tags")) != set(test_memory["tags"]):
            print("❌ Memory tags do not match")
            print(f"Original: {test_memory['tags']}")
            print(f"Retrieved: {memory.get('tags')}")
            return False
        
        print("✅ Memory content, type, and tags match")
        print("✅ Memory write-read test in same runtime passed!")
        return True
    
    except Exception as e:
        print(f"❌ Error during memory write-read test: {str(e)}")
        return False

if __name__ == "__main__":
    # Check if a base URL was provided as a command-line argument
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    
    success = test_memory_write_read_same_runtime(BASE_URL)
    sys.exit(0 if success else 1)
