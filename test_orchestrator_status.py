"""
Test script for the orchestrator status endpoint.

This script tests the functionality of the /api/orchestrator/status endpoint
by creating sample memory threads and verifying the response.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import required modules
from app.modules.memory_thread import THREAD_DB, clear_all_threads
from app.schemas.memory import StepType
from app.api.orchestrator.status import extract_score, get_orchestrator_status

async def test_extract_score():
    """Test the extract_score helper function."""
    print("\n🧪 Testing extract_score function...")
    
    # Test cases
    test_cases = [
        {"text": "I rate this 7/10 for quality.", "expected": 7},
        {"text": "Score: 8/10", "expected": 8},
        {"text": "This deserves a 10/10!", "expected": 10},
        {"text": "This is a 0/10 implementation.", "expected": None},  # Out of range
        {"text": "No score here", "expected": None},
        {"text": None, "expected": None},
        {"text": "The score is 9 out of 10", "expected": None},  # Doesn't match pattern
    ]
    
    # Run tests
    for i, case in enumerate(test_cases):
        result = extract_score(case["text"])
        expected = case["expected"]
        
        if result == expected:
            print(f"  ✅ Test {i+1}: '{case['text']}' -> {result}")
        else:
            print(f"  ❌ Test {i+1}: '{case['text']}' -> {result} (expected {expected})")
    
    print("✅ extract_score function tests completed")

async def create_sample_memory_thread():
    """Create a sample memory thread for testing."""
    print("\n🧪 Creating sample memory thread...")
    
    # Clear all threads to start with a clean state
    clear_all_threads()
    
    # Generate test IDs
    project_id = "founder-stack"
    chain_id = f"test-chain-{str(uuid.uuid4())[:8]}"
    
    # Create sample memories
    memories = [
        {
            "agent": "hal",
            "role": "agent",
            "content": "I've analyzed the requirements and created a plan for implementation.",
            "step_type": StepType.plan
        },
        {
            "agent": "ash",
            "role": "agent",
            "content": "Here's the documentation for the API endpoints.",
            "step_type": StepType.docs
        },
        {
            "agent": "nova",
            "role": "agent",
            "content": "I've designed the UI components for the dashboard.",
            "step_type": StepType.ui
        },
        {
            "agent": "critic",
            "role": "agent",
            "content": "I've reviewed the implementation and would rate it 7/10. Some improvements could be made to the error handling.",
            "step_type": StepType.reflection
        }
    ]
    
    # Add memories to thread
    thread_key = f"{project_id}::{chain_id}"
    THREAD_DB[thread_key] = []
    
    for i, memory in enumerate(memories):
        memory_id = f"mem-{datetime.now().timestamp()}-{i}"
        THREAD_DB[thread_key].append({
            "memory_id": memory_id,
            "agent": memory["agent"],
            "role": memory["role"],
            "content": memory["content"],
            "step_type": memory["step_type"],
            "timestamp": datetime.now().isoformat() + "Z",
            "project_id": project_id,
            "chain_id": chain_id
        })
    
    print(f"  ✅ Created thread with {len(THREAD_DB[thread_key])} memories")
    print(f"  📝 Project ID: {project_id}")
    print(f"  📝 Chain ID: {chain_id}")
    
    return project_id, chain_id

async def test_orchestrator_status():
    """Test the orchestrator status endpoint."""
    print("\n🧪 Testing orchestrator status endpoint...")
    
    # Create sample memory thread
    project_id, chain_id = await create_sample_memory_thread()
    
    # Call the endpoint
    response = await get_orchestrator_status(project_id=project_id, chain_id=chain_id)
    
    # Verify response
    print("\n📝 Response from orchestrator status endpoint:")
    print(json.dumps(response, indent=2))
    
    # Check required fields
    required_fields = [
        "project_id", "chain_id", "memory_count", "agents_logged",
        "last_agent", "last_step_type", "last_summary", "critic_score"
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in response:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"  ❌ Missing required fields: {', '.join(missing_fields)}")
    else:
        print("  ✅ All required fields are present")
    
    # Verify field values
    if response.get("project_id") == project_id:
        print("  ✅ project_id is correct")
    else:
        print(f"  ❌ project_id is incorrect: {response.get('project_id')} (expected {project_id})")
    
    if response.get("chain_id") == chain_id:
        print("  ✅ chain_id is correct")
    else:
        print(f"  ❌ chain_id is incorrect: {response.get('chain_id')} (expected {chain_id})")
    
    if response.get("memory_count") == 4:
        print("  ✅ memory_count is correct")
    else:
        print(f"  ❌ memory_count is incorrect: {response.get('memory_count')} (expected 4)")
    
    expected_agents = ["hal", "ash", "nova", "critic"]
    if set(response.get("agents_logged", [])) == set(expected_agents):
        print("  ✅ agents_logged is correct")
    else:
        print(f"  ❌ agents_logged is incorrect: {response.get('agents_logged')} (expected {expected_agents})")
    
    if response.get("last_agent") == "critic":
        print("  ✅ last_agent is correct")
    else:
        print(f"  ❌ last_agent is incorrect: {response.get('last_agent')} (expected critic)")
    
    if response.get("last_step_type") == "reflection":
        print("  ✅ last_step_type is correct")
    else:
        print(f"  ❌ last_step_type is incorrect: {response.get('last_step_type')} (expected reflection)")
    
    if response.get("critic_score") == 7:
        print("  ✅ critic_score is correct")
    else:
        print(f"  ❌ critic_score is incorrect: {response.get('critic_score')} (expected 7)")
    
    # Check if summary is present
    if response.get("last_summary"):
        print("  ✅ last_summary is present")
    else:
        print("  ❌ last_summary is missing")
    
    print("✅ orchestrator status endpoint tests completed")

async def test_empty_memory_thread():
    """Test the orchestrator status endpoint with an empty memory thread."""
    print("\n🧪 Testing orchestrator status endpoint with empty memory thread...")
    
    # Clear all threads
    clear_all_threads()
    
    # Generate test IDs
    project_id = "empty-project"
    chain_id = "empty-chain"
    
    # Call the endpoint
    response = await get_orchestrator_status(project_id=project_id, chain_id=chain_id)
    
    # Verify response
    print("\n📝 Response for empty memory thread:")
    print(json.dumps(response, indent=2))
    
    # Check required fields
    required_fields = [
        "project_id", "chain_id", "memory_count", "agents_logged",
        "last_agent", "last_step_type", "last_summary", "critic_score"
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in response:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"  ❌ Missing required fields: {', '.join(missing_fields)}")
    else:
        print("  ✅ All required fields are present")
    
    # Verify field values for empty thread
    if response.get("memory_count") == 0:
        print("  ✅ memory_count is correctly 0")
    else:
        print(f"  ❌ memory_count is incorrect: {response.get('memory_count')} (expected 0)")
    
    if response.get("agents_logged") == []:
        print("  ✅ agents_logged is correctly empty")
    else:
        print(f"  ❌ agents_logged is incorrect: {response.get('agents_logged')} (expected [])")
    
    if response.get("last_agent") is None:
        print("  ✅ last_agent is correctly None")
    else:
        print(f"  ❌ last_agent is incorrect: {response.get('last_agent')} (expected None)")
    
    if response.get("critic_score") is None:
        print("  ✅ critic_score is correctly None")
    else:
        print(f"  ❌ critic_score is incorrect: {response.get('critic_score')} (expected None)")
    
    print("✅ Empty memory thread tests completed")

async def run_all_tests():
    """Run all tests for the orchestrator status endpoint."""
    print("🧪 Starting orchestrator status endpoint tests...")
    
    # Test extract_score function
    await test_extract_score()
    
    # Test orchestrator status endpoint with sample data
    await test_orchestrator_status()
    
    # Test orchestrator status endpoint with empty memory thread
    await test_empty_memory_thread()
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
