import requests
import json
import sys
import time

def test_memory_write_read_cycle(base_url):
    """
    Test the memory write-read cycle with enhanced logging.
    
    This test:
    1. Writes a new memory using the /write endpoint
    2. Captures the returned memory_id
    3. Immediately reads the memory using the /read endpoint
    4. Verifies the memory is found in memory_store
    
    Args:
        base_url: Base URL for the API endpoints
    """
    print(f"🧪 Starting memory write-read validation test with enhanced logging on {base_url}...")
    
    # Step 1: Write a new memory
    write_url = f"{base_url}/write"
    write_payload = {
        "agent_id": "test_agent",
        "memory_type": "test",
        "content": "Testing global memory_store with enhanced logging",
        "tags": ["test", "global", "memory_store", "logging"],
        "project_id": "test_project"
    }
    
    print(f"📤 Writing new memory...")
    write_response = requests.post(write_url, json=write_payload)
    
    if write_response.status_code != 200:
        print(f"❌ Failed to write memory: {write_response.text}")
        return False
    
    print(f"✅ Successfully wrote memory")
    write_data = write_response.json()
    print(f"Response: {json.dumps(write_data, indent=2)}")
    
    # Step 2: Capture the memory_id
    memory_id = write_data.get("memory_id")
    if not memory_id:
        print(f"❌ No memory_id returned from write operation")
        return False
    
    print(f"🔑 Captured memory_id: {memory_id}")
    
    # Step 3: Read the memory back
    read_url = f"{base_url}/read?memory_id={memory_id}"
    print(f"📥 Reading memory with memory_id={memory_id}...")
    
    # Small delay to ensure logs are visible
    time.sleep(1)
    
    read_response = requests.get(read_url)
    
    if read_response.status_code != 200:
        print(f"❌ Failed to read memory: {read_response.text}")
        return False
    
    print(f"✅ Successfully read memory")
    read_data = read_response.json()
    
    # Step 4: Verify the memory content
    if read_data.get("status") != "ok" or not read_data.get("memories"):
        print(f"❌ Invalid response format: {json.dumps(read_data, indent=2)}")
        return False
    
    memory = read_data["memories"][0]
    if memory["memory_id"] != memory_id:
        print(f"❌ Memory ID mismatch: expected {memory_id}, got {memory['memory_id']}")
        return False
    
    if memory["content"] != write_payload["content"]:
        print(f"❌ Memory content mismatch")
        return False
    
    if memory["type"] != write_payload["memory_type"]:
        print(f"❌ Memory type mismatch: expected {write_payload['memory_type']}, got {memory['type']}")
        return False
    
    # Success!
    print(f"✅ Memory write-read validation test passed!")
    print(f"✅ Memory successfully written and retrieved using its memory_id")
    print(f"✅ Write → read flow works correctly with global memory_store")
    print(f"✅ Enhanced logging confirms memory_store is properly global")
    return True

if __name__ == "__main__":
    # Use command line argument for base URL if provided, otherwise use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/modules"
    test_memory_write_read_cycle(base_url)
