"""
Test script for CRITIC agent with specified payload
"""

import json
import sys
import os
import requests

def test_critic_with_payload():
    """Test CRITIC agent with specified payload"""
    print("Testing CRITIC agent with specified payload...")
    
    # Test parameters from requirements
    payload = {
        "agent_id": "critic",
        "project_id": "smart_sync_test_001",
        "task": "Review the UI structure and backend scaffold.",
        "tools": ["memory_writer"]
    }
    
    # Print payload
    print("\nTest payload:")
    print(json.dumps(payload, indent=2))
    
    # Create a mock response to simulate API call
    # Since we can't directly call the API endpoint, we'll simulate it
    # by calling the run_critic_agent function directly
    from app.modules.agent_runner import run_critic_agent
    
    result = run_critic_agent(
        task=payload["task"],
        project_id=payload["project_id"],
        tools=payload["tools"]
    )
    
    # Print result
    print("\nCRITIC agent result:")
    print(json.dumps(result, indent=2))
    
    # Verify result structure
    assert "status" in result, "Result should contain 'status' field"
    
    # Check for required fields
    required_fields = ["project_state", "files_created", "actions_taken", "notes"]
    for field in required_fields:
        if field in result:
            print(f"✅ {field} field included in result")
        else:
            print(f"❌ {field} field not included in result")
    
    # Check if project_state includes critic in agents_involved
    if "project_state" in result:
        agents_involved = result["project_state"].get("agents_involved", [])
        if "critic" in agents_involved:
            print("✅ project_state.agents_involved includes 'critic'")
        else:
            print("❌ project_state.agents_involved does not include 'critic'")
    
    print("\nTest completed successfully!")
    return result

if __name__ == "__main__":
    test_critic_with_payload()
