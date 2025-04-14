"""
Memory Write-Read Validation Script

This script validates memory persistence by:
1. Writing a new memory using the /write endpoint
2. Capturing the returned memory_id
3. Reading the memory back using the /read endpoint
4. Verifying the memory content matches what was written

This confirms that memory persistence works correctly in production.
"""

import requests
import json
import time
import sys
import argparse

def test_memory_write_read(base_url):
    """
    Test the memory write-read cycle to confirm memory persistence works correctly.
    
    Args:
        base_url: The base URL of the API (e.g., https://web-production-2639.up.railway.app)
    
    Returns:
        bool: True if the test passes, False otherwise
    """
    print(f"🧪 Starting memory write-read validation test on {base_url}...")
    
    # Step 1: Write a new memory using the /write endpoint
    write_url = f"{base_url}/api/modules/write"
    write_payload = {
        "agent_id": "hal",
        "memory_type": "reflection",
        "content": f"Testing memory persistence and /read endpoint at {time.strftime('%Y-%m-%d %H:%M:%S')}.",
        "project_id": "promethios-core",
        "tags": ["test", "memory_id", "read_check"]
    }
    
    try:
        print("📤 Writing new memory...")
        write_response = requests.post(write_url, json=write_payload)
        
        if write_response.status_code != 200:
            print(f"❌ Error writing memory: {write_response.status_code}")
            print(f"Response: {write_response.text}")
            return False
        
        write_data = write_response.json()
        print(f"✅ Successfully wrote memory")
        print(f"Response: {json.dumps(write_data, indent=2)}")
        
        # Step 2: Capture the returned memory_id
        memory_id = write_data.get("memory_id")
        
        if not memory_id:
            print("❌ No memory_id returned from /write")
            return False
        
        print(f"🔑 Captured memory_id: {memory_id}")
        
        # Step 3: Read the memory back using the /read endpoint
        read_url = f"{base_url}/api/modules/read?memory_id={memory_id}"
        
        print(f"📥 Reading memory with memory_id={memory_id}...")
        read_response = requests.get(read_url)
        
        if read_response.status_code != 200:
            print(f"❌ Error reading memory: {read_response.status_code}")
            print(f"Response: {read_response.text}")
            return False
        
        read_data = read_response.json()
        print(f"✅ Successfully read memory")
        
        # Step 4: Verify the memory content matches what was written
        if read_data.get("status") != "ok":
            print(f"❌ Read response status is not 'ok': {read_data.get('status')}")
            return False
        
        memories = read_data.get("memories", [])
        if not memories:
            print("❌ No memories returned from /read")
            return False
        
        memory = memories[0]
        if memory.get("memory_id") != memory_id:
            print(f"❌ Returned memory_id {memory.get('memory_id')} does not match requested memory_id {memory_id}")
            return False
        
        if memory.get("content") != write_payload["content"]:
            print(f"❌ Memory content does not match what was written")
            print(f"Written: {write_payload['content']}")
            print(f"Read: {memory.get('content')}")
            return False
        
        print("✅ Memory write-read validation test passed!")
        print(f"✅ Memory successfully written and retrieved using its memory_id")
        print(f"✅ Write → read flow works correctly in production")
        print(f"✅ Memory persistence is functioning properly")
        
        # Print verification steps for manual testing
        print("\n📋 Manual Verification Steps:")
        print(f"1. POST {write_url}")
        print(f"   Payload: {json.dumps(write_payload, indent=2)}")
        print(f"2. Capture memory_id from response")
        print(f"3. GET {base_url}/api/modules/read?memory_id=<captured-memory-id>")
        
        return True
    
    except Exception as e:
        print(f"❌ Error during memory write-read validation: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test memory write-read cycle')
    parser.add_argument('--url', type=str, default="http://localhost:8000", 
                        help='Base URL of the API (default: http://localhost:8000)')
    
    args = parser.parse_args()
    success = test_memory_write_read(args.url)
    sys.exit(0 if success else 1)
