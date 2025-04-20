"""
Agent Action Trace Logger Module

This module provides functionality to track every action an agent takes during a loop,
tying it back to the contract it received, the file it created, the outcome it logged,
and the exact timestamp it completed the task.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def log_agent_execution(project_id: str, agent_name: str, contract_id: str, 
                       file: str, status: str, notes: Optional[str] = None) -> dict:
    """
    Logs an agent execution action with contract references, file status, and timestamps.
    
    Args:
        project_id (str): The project identifier
        agent_name (str): The agent that performed the action
        contract_id (str): The contract ID reference
        file (str): The file that was affected
        status (str): The status of the action (e.g., "complete", "failed", "in_progress")
        notes (str, optional): Additional notes about the action
        
    Returns:
        dict: The logged action with timestamp added
    """
    # Extract loop_id from contract_id (assuming format "loop_XXX_agent_contract")
    loop_id = None
    if contract_id and "_" in contract_id:
        parts = contract_id.split("_")
        if len(parts) > 1 and parts[0] == "loop":
            try:
                loop_id = int(parts[1])
            except ValueError:
                pass
    
    if not loop_id:
        # Fallback - generate a placeholder loop_id
        loop_id = int(datetime.utcnow().timestamp()) % 1000
    
    # Create the action object
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    action = {
        "loop_id": loop_id,
        "agent": agent_name,
        "file": file,
        "contract_id": contract_id,
        "status": status,
        "timestamp": timestamp
    }
    
    # Add notes if provided
    if notes:
        action["notes"] = notes
    
    # Log to loop trace memory
    log_to_memory(project_id, {
        "loop_trace": [action]
    })
    
    # Log to agent-specific trace memory
    log_to_memory(project_id, {
        "agent_trace": {
            agent_name: [action]
        }
    })
    
    # Log to chat (optional)
    status_emoji = get_status_emoji(status)
    message = f"{status_emoji} Agent {agent_name.upper()} {status} on {file}"
    if notes:
        message += f": {notes}"
    
    log_to_chat(project_id, {
        "role": "orchestrator",
        "message": message,
        "timestamp": timestamp
    })
    
    return action

def log_agent_push(project_id: str, agent_name: str, branch: str, 
                  commit_message: str, pr_link: Optional[str] = None) -> dict:
    """
    Logs a Git operation performed by an agent.
    
    Args:
        project_id (str): The project identifier
        agent_name (str): The agent that performed the Git operation
        branch (str): The Git branch name
        commit_message (str): The commit message
        pr_link (str, optional): The pull request link
        
    Returns:
        dict: The logged Git operation with timestamp added
    """
    # Create the action object
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    action = {
        "agent": agent_name,
        "branch": branch,
        "commit": commit_message,
        "status": "pushed",
        "timestamp": timestamp
    }
    
    # Add PR link if provided
    if pr_link:
        action["pr"] = pr_link
    
    # Extract loop_id and file from branch name if possible
    # Assuming format "feature/agent-{agent}-loop{loop_id}-{filename}"
    loop_id = None
    file = None
    
    if branch and "-loop" in branch:
        try:
            # Extract loop_id
            loop_parts = branch.split("-loop")
            if len(loop_parts) > 1:
                loop_id_part = loop_parts[1].split("-")[0]
                loop_id = int(loop_id_part)
                
                # Extract file
                if "-" in loop_parts[1]:
                    file_part = loop_parts[1].split("-", 1)[1]
                    if "." in file_part:
                        file = file_part
                    else:
                        # Handle case where file extension might be missing
                        file = file_part
        except (ValueError, IndexError):
            pass
    
    # Add loop_id and file if extracted
    if loop_id:
        action["loop_id"] = loop_id
    
    if file:
        action["file"] = file
    
    # Log to loop trace memory if loop_id is available
    if loop_id:
        log_to_memory(project_id, {
            "loop_trace": [action]
        })
    
    # Log to agent-specific trace memory
    log_to_memory(project_id, {
        "agent_trace": {
            agent_name: [action]
        }
    })
    
    # Log to git_operations memory
    log_to_memory(project_id, {
        "git_operations": [action]
    })
    
    # Log to chat
    emoji = "🔄" if not pr_link else "🔀"
    message = f"{emoji} Agent {agent_name.upper()} pushed to branch '{branch}'"
    if pr_link:
        message += f" and created PR: {pr_link}"
    
    log_to_chat(project_id, {
        "role": "orchestrator",
        "message": message,
        "timestamp": timestamp
    })
    
    return action

def get_agent_actions(project_id: str, agent_name: str, 
                     limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retrieves all actions for a specific agent.
    
    Args:
        project_id (str): The project identifier
        agent_name (str): The agent name
        limit (int, optional): Maximum number of actions to return
        
    Returns:
        list: List of agent actions
    """
    # In a real implementation, this would retrieve data from a database or file
    # For now, we'll just print a message and return an empty list
    print(f"Retrieving actions for agent {agent_name} in project {project_id}")
    print(f"Limit: {limit if limit else 'None'}")
    
    # Return an empty list for demonstration
    return []

def get_loop_agent_actions(project_id: str, loop_id: int, 
                          agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves all actions for a specific loop, optionally filtered by agent.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        agent_name (str, optional): The agent name to filter by
        
    Returns:
        list: List of agent actions for the specified loop
    """
    # In a real implementation, this would retrieve data from a database or file
    # For now, we'll just print a message and return an empty list
    print(f"Retrieving actions for loop {loop_id} in project {project_id}")
    if agent_name:
        print(f"Filtered by agent: {agent_name}")
    
    # Return an empty list for demonstration
    return []

def get_file_actions(project_id: str, file_path: str, 
                    agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves all actions for a specific file, optionally filtered by agent.
    
    Args:
        project_id (str): The project identifier
        file_path (str): The file path
        agent_name (str, optional): The agent name to filter by
        
    Returns:
        list: List of agent actions for the specified file
    """
    # In a real implementation, this would retrieve data from a database or file
    # For now, we'll just print a message and return an empty list
    print(f"Retrieving actions for file {file_path} in project {project_id}")
    if agent_name:
        print(f"Filtered by agent: {agent_name}")
    
    # Return an empty list for demonstration
    return []

def get_status_emoji(status: str) -> str:
    """
    Returns an emoji representation of a status.
    
    Args:
        status (str): The status string
        
    Returns:
        str: An emoji representing the status
    """
    status_emojis = {
        "complete": "✅",
        "failed": "❌",
        "in_progress": "🔄",
        "blocked": "⛔",
        "warning": "⚠️",
        "pushed": "🔄",
        "merged": "🔀"
    }
    
    return status_emojis.get(status.lower(), "ℹ️")

def log_to_memory(project_id: str, data: dict):
    """
    Logs data to project memory.
    
    Args:
        project_id (str): The project ID
        data (dict): The data to log
    """
    # In a real implementation, this would store data in a database or file
    print(f"Logging to memory for project {project_id}:")
    print(json.dumps(data, indent=2))

def log_to_chat(project_id: str, message: dict):
    """
    Logs a message to the chat.
    
    Args:
        project_id (str): The project ID
        message (dict): The message to log
    """
    # In a real implementation, this would add the message to the chat
    print(f"Logging to chat for project {project_id}:")
    print(json.dumps(message, indent=2))

if __name__ == "__main__":
    # Example usage
    project_id = "lifetree_001"
    
    # Log an agent execution
    execution = log_agent_execution(
        project_id=project_id,
        agent_name="nova",
        contract_id="loop_032_nova_contract",
        file="ContactForm.jsx",
        status="complete",
        notes="Validation passed. File committed."
    )
    print("\nLogged agent execution:")
    print(json.dumps(execution, indent=2))
    
    # Log an agent push
    push = log_agent_push(
        project_id=project_id,
        agent_name="hal",
        branch="feature/agent-hal-loop32-loginform",
        commit_message="feat: HAL creates LoginForm.jsx",
        pr_link="https://github.com/example/repo/pull/34"
    )
    print("\nLogged agent push:")
    print(json.dumps(push, indent=2))
    
    # Get agent actions
    actions = get_agent_actions(project_id, "nova", limit=5)
    print(f"\nRetrieved {len(actions)} actions for NOVA")
    
    # Get loop agent actions
    loop_actions = get_loop_agent_actions(project_id, 32, agent_name="hal")
    print(f"\nRetrieved {len(loop_actions)} actions for loop 32, agent HAL")
    
    # Get file actions
    file_actions = get_file_actions(project_id, "ContactForm.jsx")
    print(f"\nRetrieved {len(file_actions)} actions for file ContactForm.jsx")
