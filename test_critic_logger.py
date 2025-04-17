"""
Test script for CRITIC agent logger functionality
"""

import json
import sys
import os
from app.modules.agent_runner import run_critic_agent

def test_critic_logger():
    """Test CRITIC agent logger functionality"""
    print("Testing CRITIC agent logger functionality...")
    
    # Test parameters
    project_id = "smart_sync_test_001"
    task = "Review the UI structure and backend scaffold."
    tools = ["memory_writer"]
    
    # Run CRITIC agent
    result = run_critic_agent(task, project_id, tools)
    
    # Print result
    print("\nCRITIC agent result:")
    print(json.dumps(result, indent=2))
    
    # Verify result structure
    assert "status" in result, "Result should contain 'status' field"
    
    if "project_state" in result:
        print("\n✅ Project state included in result")
    else:
        print("\n❌ Project state not included in result")
    
    if "files_created" in result:
        print("✅ files_created field included in result")
    else:
        print("❌ files_created field not included in result")
    
    if "actions_taken" in result:
        print("✅ actions_taken field included in result")
    else:
        print("❌ actions_taken field not included in result")
    
    if "notes" in result:
        print("✅ notes field included in result")
    else:
        print("❌ notes field not included in result")
    
    print("\nTest completed successfully!")
    return result

if __name__ == "__main__":
    test_critic_logger()
