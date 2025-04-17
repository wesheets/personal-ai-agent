#!/usr/bin/env python3
"""
Mock implementation of agent_runner dependencies for testing.
This script creates mock versions of imported modules to allow tests to run.
"""

import os
import sys
import json

# Create mocks directory
os.makedirs("mocks", exist_ok=True)

# Create mock modules
os.makedirs("mocks/app/modules", exist_ok=True)
os.makedirs("mocks/app/core", exist_ok=True)
os.makedirs("mocks/toolkit", exist_ok=True)

# Create __init__.py files
open("mocks/app/__init__.py", "w").close()
open("mocks/app/modules/__init__.py", "w").close()
open("mocks/app/core/__init__.py", "w").close()
open("mocks/toolkit/__init__.py", "w").close()

# Create mock memory_thread.py
with open("mocks/app/modules/memory_thread.py", "w") as f:
    f.write("""
async def add_memory_thread(memory_entry):
    print(f"Mock: add_memory_thread called with {memory_entry}")
    return {"status": "success", "memory_id": "mock-memory-id"}
""")

# Create mock memory_writer.py
with open("mocks/app/modules/memory_writer.py", "w") as f:
    f.write("""
def write_memory(memory_data):
    print(f"Mock: write_memory called with {memory_data}")
    return {"status": "success", "memory_id": "mock-memory-id"}
""")

# Create mock file_writer.py
with open("mocks/toolkit/file_writer.py", "w") as f:
    f.write("""
def write_file(project_id, file_path, content):
    print(f"Mock: write_file called with project_id={project_id}, file_path={file_path}")
    return {"status": "success", "file_path": file_path}
""")

# Create mock registry.py
with open("mocks/toolkit/registry.py", "w") as f:
    f.write("""
def get_toolkit(agent_id, domain):
    return ["mock_tool"]

def get_agent_role(agent_id):
    return "mock_role"

def format_tools_prompt(tools):
    return "Mock tools prompt"

def format_nova_prompt(tools, themes):
    return "Mock NOVA prompt"

def get_agent_themes(agent_id):
    return ["mock_theme"]
""")

# Create mock project_state.py
with open("mocks/app/modules/project_state.py", "w") as f:
    f.write("""
import os
import json
import time

def read_project_state(project_id):
    \"\"\"
    Read the current state of a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the project state
    \"\"\"
    try:
        # Check if project state file exists
        file_path = f"project_states/{project_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        
        # Return default state if file doesn't exist
        return {
            "project_id": project_id,
            "status": "new",
            "files_created": [],
            "agents_involved": [],
            "latest_agent_action": {},
            "next_recommended_step": "",
            "tool_usage": {},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    except Exception as e:
        print(f"Error reading project state: {str(e)}")
        return {
            "project_id": project_id,
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

def update_project_state(project_id, patch_dict):
    \"\"\"
    Update specific fields in the project state.
    
    Args:
        project_id: The project identifier
        patch_dict: Dict containing fields to update
        
    Returns:
        Dict containing the updated project state
    \"\"\"
    try:
        # Read current state
        current_state = read_project_state(project_id)
        
        # Update fields
        for key, value in patch_dict.items():
            if key == "files_created" and isinstance(value, list):
                # Append to files_created without duplicates
                if "files_created" not in current_state:
                    current_state["files_created"] = []
                
                for file_path in value:
                    if file_path not in current_state["files_created"]:
                        current_state["files_created"].append(file_path)
            elif key == "agents_involved" and isinstance(value, list):
                # Append to agents_involved without duplicates
                if "agents_involved" not in current_state:
                    current_state["agents_involved"] = []
                
                for agent in value:
                    if agent not in current_state["agents_involved"]:
                        current_state["agents_involved"].append(agent)
            elif key == "tool_usage" and isinstance(value, dict):
                # Update tool_usage counters
                if "tool_usage" not in current_state:
                    current_state["tool_usage"] = {}
                
                for tool, count in value.items():
                    if tool in current_state["tool_usage"]:
                        current_state["tool_usage"][tool] += count
                    else:
                        current_state["tool_usage"][tool] = count
            else:
                # Direct update for other fields
                current_state[key] = value
        
        # Update timestamp
        current_state["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        # Ensure project_states directory exists
        os.makedirs("project_states", exist_ok=True)
        
        # Write updated state
        with open(f"project_states/{project_id}.json", "w") as f:
            json.dump(current_state, f, indent=2)
        
        return {"status": "success", "project_id": project_id}
    except Exception as e:
        print(f"Error updating project state: {str(e)}")
        return {"status": "error", "project_id": project_id, "error": str(e)}
""")

print("✅ Mock modules created for testing")
