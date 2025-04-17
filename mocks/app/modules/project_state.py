
import os
import json
import time

def read_project_state(project_id):
    """
    Read the current state of a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the project state
    """
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
    """
    Update specific fields in the project state.
    
    Args:
        project_id: The project identifier
        patch_dict: Dict containing fields to update
        
    Returns:
        Dict containing the updated project state
    """
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
