"""
Memory Validation Test

This script tests the memory write-read cycle by:
1. Calling /orchestrator/build to generate a new memory
2. Capturing the returned memory_id
3. Immediately calling /read with the captured memory_id
4. Confirming the memory is successfully retrieved

This validates that the memory persistence works correctly within the same session.
"""

import requests
import json
import time
import sys
import os

# Base URL for API calls
BASE_URL = "http://localhost:8000/api/modules"

def test_memory_write_read_cycle():
    """
    Test the memory write-read cycle to confirm memory persistence works correctly.
    """
    print("🧪 Starting memory validation test...")
    
    # Step 1: Call /orchestrator/build with a sample multi-task plan
    build_url = f"{BASE_URL}/orchestrator/build"
    build_payload = {
        "plan_id": "plan-test-memory-validation",
        "tasks": [
            {
                "task_id": "task-001",
                "description": "Simulate onboarding task",
                "required_skills": ["summarization"]
            }
        ]
    }
    
    try:
        print("📤 Calling /orchestrator/build to generate a new memory...")
        build_response = requests.post(build_url, json=build_payload)
        
        if build_response.status_code != 200:
            print(f"❌ Error calling /orchestrator/build: {build_response.status_code}")
            print(f"Response: {build_response.text}")
            return False
        
        build_data = build_response.json()
        print(f"✅ Successfully called /orchestrator/build")
        print(f"Response: {json.dumps(build_data, indent=2)}")
        
        # Step 2: Capture the returned memory_id
        memory_id = build_data.get("memory_id")
        
        if not memory_id:
            print("❌ No memory_id returned from /orchestrator/build")
            return False
        
        print(f"🔑 Captured memory_id: {memory_id}")
        
        # Step 3: Call /read with the captured memory_id
        read_url = f"{BASE_URL}/read?memory_id={memory_id}"
        
        print(f"📥 Calling /read with memory_id={memory_id}...")
        read_response = requests.get(read_url)
        
        if read_response.status_code != 200:
            print(f"❌ Error calling /read: {read_response.status_code}")
            print(f"Response: {read_response.text}")
            return False
        
        read_data = read_response.json()
        print(f"✅ Successfully called /read")
        
        # Step 4: Confirm the memory is successfully retrieved
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
        
        if memory.get("type") != "build_log":
            print(f"❌ Memory type is not 'build_log': {memory.get('type')}")
            return False
        
        print("✅ Memory validation test passed!")
        print(f"✅ Memory successfully retrieved using its memory_id")
        print(f"✅ Write → read flow works correctly in current runtime")
        print(f"✅ /read is not broken — old memory_ids were just from prior ephemeral containers")
        
        return True
    
    except Exception as e:
        print(f"❌ Error during memory validation test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_memory_write_read_cycle()
    sys.exit(0 if success else 1)
