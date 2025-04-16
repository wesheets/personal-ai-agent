"""
Test script for updated Pydantic schema in memory_summarize.py.

This script tests that the agent_id field is truly optional in the
SummarizationRequest model and defaults to "orchestrator" when not provided.
"""

import requests
import json
import time
import uuid

# Base URL for API
BASE_URL = "http://0.0.0.0:8000"

def test_updated_schema():
    """Test the updated Pydantic schema in memory_summarize.py."""
    print("Testing updated Pydantic schema in memory_summarize.py...")
    
    # Generate unique project_id and chain_id for testing
    project_id = f"test_project_{uuid.uuid4().hex[:6]}"
    chain_id = f"test_chain_{uuid.uuid4().hex[:6]}"
    
    print(f"\nUsing project_id: {project_id}, chain_id: {chain_id}")
    
    # 1. First create a memory thread entry
    thread_data = {
        "project_id": project_id,
        "chain_id": chain_id,
        "agent": "hal",
        "role": "developer",
        "content": "This is a test memory entry for schema validation",
        "step_type": "task",
        "type": "code"
    }
    
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
    
    # 2. Test POST to /api/memory/summarize WITHOUT agent_id
    print(f"\n2. POST /api/memory/summarize WITHOUT agent_id")
    
    # Test data for summarization request - intentionally omitting agent_id
    summarize_data = {
        "project_id": project_id,
        "chain_id": chain_id
    }
    
    print(f"Request data: {json.dumps(summarize_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/memory/summarize", json=summarize_data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        if response.status_code == 200:
            print("✅ POST /api/memory/summarize WITHOUT agent_id - Success")
            
            # Verify agent_id default value
            if response.json().get("agent_id") == "orchestrator":
                print("✅ Default agent_id is correctly set to 'orchestrator'")
            else:
                print(f"❌ Default agent_id is incorrect: {response.json().get('agent_id')}")
                return False
        else:
            print("❌ POST /api/memory/summarize WITHOUT agent_id - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # 3. Test POST to /api/memory/summarize WITH agent_id
    print(f"\n3. POST /api/memory/summarize WITH agent_id")
    
    # Test data for summarization request - including agent_id
    summarize_data_with_agent = {
        "project_id": project_id,
        "chain_id": chain_id,
        "agent_id": "custom_agent"
    }
    
    print(f"Request data: {json.dumps(summarize_data_with_agent, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/memory/summarize", json=summarize_data_with_agent)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        if response.status_code == 200:
            print("✅ POST /api/memory/summarize WITH agent_id - Success")
            
            # Verify custom agent_id is used
            if response.json().get("agent_id") == "custom_agent":
                print("✅ Custom agent_id is correctly used")
            else:
                print(f"❌ Custom agent_id is not used: {response.json().get('agent_id')}")
                return False
        else:
            print("❌ POST /api/memory/summarize WITH agent_id - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    print("\n✅ All schema validation tests completed successfully!")
    return True

if __name__ == "__main__":
    test_updated_schema()
