"""
Test script for memory system integration.

This script tests the functionality of the memory thread and summarize endpoints
with the updated double colon format.
"""

import requests
import json
import time
import uuid

# Base URL for API
BASE_URL = "http://0.0.0.0:8000"

def test_memory_system():
    """Test the memory system integration with double colon format."""
    print("Testing memory system integration with double colon format...")
    
    # Generate unique project_id and chain_id for testing
    project_id = f"test_project_{uuid.uuid4().hex[:6]}"
    chain_id = f"test_chain_{uuid.uuid4().hex[:6]}"
    
    print(f"\nUsing project_id: {project_id}, chain_id: {chain_id}")
    
    # Test data for memory thread
    thread_data = {
        "project_id": project_id,
        "chain_id": chain_id,
        "agent": "hal",
        "role": "developer",
        "content": "This is a test memory entry with double colon format",
        "step_type": "task",
        "type": "code"
    }
    
    # 1. Test POST to /api/memory/thread
    print(f"\n1. POST /api/memory/thread")
    print(f"Request data: {json.dumps(thread_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/memory/thread", json=thread_data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        if response.status_code == 200:
            print("✅ POST /api/memory/thread - Success")
        else:
            print("❌ POST /api/memory/thread - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Wait a moment to ensure data is processed
    time.sleep(1)
    
    # 2. Test GET from /api/memory/thread/{project_id}/{chain_id}
    print(f"\n2. GET /api/memory/thread/{project_id}/{chain_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/memory/thread/{project_id}/{chain_id}")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        if response.status_code == 200 and len(response.json()) > 0:
            print("✅ GET /api/memory/thread/{project_id}/{chain_id} - Success")
            print(f"Found {len(response.json())} entries in thread")
        else:
            print("❌ GET /api/memory/thread/{project_id}/{chain_id} - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # 3. Test POST to /api/memory/summarize
    print(f"\n3. POST /api/memory/summarize")
    
    # Test data for summarization request
    summarize_data = {
        "project_id": project_id,
        "chain_id": chain_id
        # agent_id is optional and should default to "orchestrator"
    }
    
    print(f"Request data: {json.dumps(summarize_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/memory/summarize", json=summarize_data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        if response.status_code == 200 and "summary" in response.json():
            print("✅ POST /api/memory/summarize - Success")
            print(f"Summary: {response.json().get('summary')}")
            
            # Verify agent_id default value
            if response.json().get("agent_id") == "orchestrator":
                print("✅ Default agent_id is correctly set to 'orchestrator'")
            else:
                print(f"❌ Default agent_id is incorrect: {response.json().get('agent_id')}")
        else:
            print("❌ POST /api/memory/summarize - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # 4. Test GET from /api/debug/memory/log
    print(f"\n4. GET /api/debug/memory/log")
    
    try:
        response = requests.get(f"{BASE_URL}/api/debug/memory/log")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        if response.status_code == 200:
            print("✅ GET /api/debug/memory/log - Success")
            print(f"Thread count: {response.json().get('thread_count')}")
            
            # Check if our test thread is in the debug log
            thread_keys = []
            for key in response.json().get('thread_counts_by_project', {}).keys():
                thread_keys.extend([k for k in response.json().get('thread_counts_by_project', {}).get(key, {}).keys()])
            
            if chain_id in ' '.join(thread_keys):
                print(f"✅ Test thread found in debug log")
            else:
                print(f"❌ Test thread not found in debug log")
        else:
            print("❌ GET /api/debug/memory/log - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    print("\n✅ All memory system tests completed successfully!")
    return True

if __name__ == "__main__":
    test_memory_system()
