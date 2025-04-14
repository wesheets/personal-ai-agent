#!/usr/bin/env python3
"""
Test script to verify memory persistence between write and thread endpoints.

This script tests the memory persistence by:
1. Writing a test memory with a unique goal_id
2. Immediately verifying the memory was written using the new verification in the write endpoint
3. Reading the memory using the thread endpoint to confirm cross-endpoint persistence
"""

import os
import sys
import json
import uuid
import requests
from datetime import datetime

# Base URL for API endpoints
BASE_URL = "http://localhost:8000/api"

def test_memory_write_with_verification():
    """Test memory write with the new verification functionality"""
    print("\n" + "="*80)
    print("TEST: Memory Write with Verification")
    print("="*80)
    
    # Generate a unique goal_id for this test
    goal_id = f"test_goal_{uuid.uuid4().hex[:8]}"
    print(f"Using test goal_id: {goal_id}")
    
    # Create a test memory request
    memory_request = {
        "agent_id": "test_agent",
        "memory_type": "test_memory",
        "content": f"This is a test memory for goal {goal_id} with verification",
        "tags": ["test", "verification"],
        "metadata": {
            "goal_id": goal_id,
            "test_run": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # Write the memory using the API
    print("\nWriting test memory via API...")
    try:
        response = requests.post(f"{BASE_URL}/memory/write", json=memory_request)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Memory written with ID: {result['memory_id']}")
        print(f"✅ Response status: {result['status']}")
        
        # Check verification results
        if 'db_contents_after_write' in result:
            print(f"📦 DB contents after write: {result['db_contents_after_write']}")
            
            if not result['db_contents_after_write']:
                print(f"❌ PERSISTENCE ISSUE: No memories found in database after write")
                return False
                
            if result['memory_id'] in result['db_contents_after_write']:
                print(f"✅ PERSISTENCE VERIFIED: Memory found in database immediately after write")
            else:
                print(f"❌ PERSISTENCE ISSUE: Memory not found in database immediately after write")
                return False
        else:
            print(f"⚠️ Verification data not included in response")
            
        if 'persistence_verified' in result:
            if result['persistence_verified']:
                print(f"✅ PERSISTENCE EXPLICITLY VERIFIED: {result['persistence_verified']}")
            else:
                print(f"❌ PERSISTENCE EXPLICITLY FAILED: {result['persistence_verified']}")
                return False
        
        # Store memory_id for later verification
        memory_id = result['memory_id']
        
    except Exception as e:
        print(f"❌ Error writing memory: {str(e)}")
        return False
    
    print("\n✅ Memory write with verification test PASSED")
    return True, memory_id, goal_id

def test_memory_thread_endpoint(goal_id):
    """Test memory thread endpoint to verify cross-endpoint persistence"""
    print("\n" + "="*80)
    print("TEST: Memory Thread Endpoint")
    print("="*80)
    
    print(f"Retrieving memories for goal_id: {goal_id}")
    
    # Read memories using the thread endpoint
    try:
        response = requests.get(f"{BASE_URL}/memory/thread?goal_id={goal_id}")
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Response status: {result['status']}")
        
        # Check if memories were found
        if 'thread' in result:
            memories = result['thread']
            print(f"📦 Found {len(memories)} memories in thread")
            
            if not memories:
                print(f"❌ CROSS-ENDPOINT PERSISTENCE ISSUE: No memories found for goal_id={goal_id}")
                return False
                
            # Check if memories have the correct goal_id
            for memory in memories:
                print(f"📝 Memory ID: {memory['memory_id']}, Content: {memory['content'][:50]}...")
                
                # Check top-level goal_id
                if memory.get('goal_id') == goal_id:
                    print(f"✅ GOAL ID MATCH: Memory has correct goal_id at top level")
                else:
                    print(f"⚠️ Goal ID not found at top level or doesn't match")
                    
                    # Check metadata goal_id
                    metadata = memory.get('metadata')
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except:
                            metadata = {}
                            
                    if isinstance(metadata, dict) and metadata.get('goal_id') == goal_id:
                        print(f"✅ GOAL ID MATCH: Memory has correct goal_id in metadata")
                    else:
                        print(f"❌ GOAL ID MISMATCH: Memory doesn't have correct goal_id in metadata")
                        return False
        else:
            print(f"❌ No 'thread' field in response")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving memory thread: {str(e)}")
        return False
    
    print("\n✅ Memory thread endpoint test PASSED")
    return True

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("MEMORY PERSISTENCE VERIFICATION TEST")
    print("="*80)
    
    # Test memory write with verification
    write_result, memory_id, goal_id = test_memory_write_with_verification()
    
    if not write_result:
        print("\n❌ Memory write test FAILED. Stopping tests.")
        return False
    
    # Test memory thread endpoint
    thread_result = test_memory_thread_endpoint(goal_id)
    
    if not thread_result:
        print("\n❌ Memory thread test FAILED.")
        return False
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED: Memory persistence verified between write and thread endpoints")
    print("="*80)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
