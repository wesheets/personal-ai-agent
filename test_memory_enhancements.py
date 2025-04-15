"""
Test script for memory system enhancements.

This script tests the following enhancements:
1. Memory batching via List
2. Expanded StepType enum
3. Optional agent_id in summarization
4. Batch thread memory operations
"""

import requests
import json
import time
import uuid
from enum import Enum

# Base URL for API
BASE_URL = "http://0.0.0.0:8000"

def test_memory_enhancements():
    """Test all memory system enhancements."""
    print("Testing memory system enhancements...")
    
    # Generate unique project_id and chain_id for testing
    project_id = f"test_project_{uuid.uuid4().hex[:6]}"
    chain_id = f"test_chain_{uuid.uuid4().hex[:6]}"
    
    print(f"\nUsing project_id: {project_id}, chain_id: {chain_id}")
    
    # 1. Test batch memory operations
    print("\n1. Testing batch memory operations")
    
    # Create batch request with multiple memory items
    batch_request = {
        "project_id": project_id,
        "chain_id": chain_id,
        "agent_id": "hal",
        "memories": [
            {
                "agent": "hal",
                "role": "developer",
                "content": "Implemented memory batching feature",
                "step_type": "task"
            },
            {
                "agent": "ash",
                "role": "reviewer",
                "content": "Reviewed memory batching implementation",
                "step_type": "reflection"
            },
            {
                "agent": "nova",
                "role": "architect",
                "content": "Memory system architecture diagram",
                "step_type": "ui"
            },
            {
                "agent": "hal",
                "role": "planner",
                "content": "Memory system enhancement plan",
                "step_type": "plan"
            },
            {
                "agent": "ash",
                "role": "documenter",
                "content": "Memory system API documentation",
                "step_type": "docs"
            }
        ]
    }
    
    print(f"Batch request data: {json.dumps(batch_request, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/memory/thread", json=batch_request)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        if response.status_code == 200:
            print("✅ Batch memory operations - Success")
            
            # Verify thread length
            if response.json().get("thread_length") == 5:
                print("✅ Thread length verification - Success")
            else:
                print(f"❌ Thread length verification - Failed. Expected 5, got {response.json().get('thread_length')}")
                return False
        else:
            print("❌ Batch memory operations - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Wait a moment to ensure data is processed
    time.sleep(1)
    
    # 2. Test expanded StepType enum by retrieving the thread
    print("\n2. Testing expanded StepType enum")
    
    try:
        response = requests.get(f"{BASE_URL}/api/memory/thread/{project_id}/{chain_id}")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            thread = response.json()
            print(f"Retrieved thread with {len(thread)} entries")
            
            # Check if all step types are present
            step_types = set(entry["step_type"] for entry in thread)
            expected_step_types = {"task", "reflection", "ui", "plan", "docs"}
            
            if expected_step_types.issubset(step_types):
                print(f"✅ Expanded StepType enum - Success. Found step types: {', '.join(step_types)}")
            else:
                print(f"❌ Expanded StepType enum - Failed. Expected {expected_step_types}, found {step_types}")
                return False
        else:
            print("❌ Thread retrieval - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # 3. Test optional agent_id in summarization
    print("\n3. Testing optional agent_id in summarization")
    
    # Test data for summarization request - intentionally omitting agent_id
    summarize_data = {
        "project_id": project_id,
        "chain_id": chain_id
    }
    
    print(f"Summarization request data (without agent_id): {json.dumps(summarize_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/memory/summarize", json=summarize_data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
        
        if response.status_code == 200:
            print("✅ Optional agent_id in summarization - Success")
            
            # Verify agent_id default value
            if response.json().get("agent_id") == "orchestrator":
                print("✅ Default agent_id is correctly set to 'orchestrator'")
            else:
                print(f"❌ Default agent_id is incorrect: {response.json().get('agent_id')}")
                return False
        else:
            print("❌ Optional agent_id in summarization - Failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    print("\n✅ All memory system enhancements tested successfully!")
    return True

if __name__ == "__main__":
    test_memory_enhancements()
