"""
Agent Git Protocol Enforcer Module

This module provides functionality to ensure all agents follow a strict Git push and pull request protocol,
including standardized branch creation, schema-validated commit structure, and PR naming that maps to
loop + agent task.
"""

import json
import os
import sys
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def generate_branch_name(agent: str, loop_id: int, file: str) -> str:
    """
    Generates a standardized branch name for an agent's task.
    
    Args:
        agent (str): The agent identifier (e.g., "hal", "nova", "critic")
        loop_id (int): The loop identifier
        file (str): The file being worked on
        
    Returns:
        str: A standardized branch name (e.g., "feature/agent-hal-loop32-loginform")
    """
    # Sanitize inputs
    agent = agent.lower().strip()
    
    # Remove file extension if present
    if "." in file:
        file_base = file.split(".")[0]
    else:
        file_base = file
    
    # Convert file to lowercase and remove any special characters
    file_slug = re.sub(r'[^a-z0-9]', '', file_base.lower())
    
    # Generate branch name
    branch_name = f"feature/agent-{agent}-loop{loop_id}-{file_slug}"
    
    return branch_name

def validate_commit_message(commit_msg: str, agent: str, loop_id: int) -> bool:
    """
    Validates that a commit message follows the required format and matches the agent's task.
    
    Args:
        commit_msg (str): The commit message to validate
        agent (str): The agent identifier
        loop_id (int): The loop identifier
        
    Returns:
        bool: True if the commit message is valid, False otherwise
    """
    # Standardize agent name to uppercase
    agent_upper = agent.upper()
    
    # Define the expected format pattern
    # Format: "feat: AGENT builds/creates/implements FILE in Loop X"
    pattern = rf'^feat: {agent_upper} (builds|creates|implements|adds|updates|fixes) .+ in Loop {loop_id}$'
    
    # Check if the commit message matches the pattern
    if re.match(pattern, commit_msg):
        return True
    
    # Check for wrong loop ID
    wrong_loop_pattern = rf'^feat: {agent_upper} (builds|creates|implements|adds|updates|fixes) .+ in Loop \d+$'
    if re.match(wrong_loop_pattern, commit_msg):
        # If it mentions a loop but with the wrong ID, reject it
        return False
    
    # Alternative format: "feat: AGENT builds/creates/implements FILE"
    alt_pattern = rf'^feat: {agent_upper} (builds|creates|implements|adds|updates|fixes) .+$'
    
    # If it matches the alternative pattern but doesn't mention the loop, it's still acceptable
    # but not ideal
    if re.match(alt_pattern, commit_msg):
        print(f"Warning: Commit message doesn't mention Loop {loop_id}. Recommended format: 'feat: {agent_upper} builds FILE in Loop {loop_id}'")
        return True
    
    return False

def log_pr_metadata(project_id: str, agent: str, branch: str, pr_url: str, 
                   loop_id: int, file: str, status: str = "open") -> dict:
    """
    Logs pull request metadata to memory and traces.
    
    Args:
        project_id (str): The project identifier
        agent (str): The agent identifier
        branch (str): The branch name
        pr_url (str): The pull request URL
        loop_id (int): The loop identifier
        file (str): The file being worked on
        status (str, optional): The PR status (default: "open")
        
    Returns:
        dict: The logged PR metadata
    """
    # Create timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create PR metadata object
    pr_metadata = {
        "agent": agent,
        "branch": branch,
        "pr_url": pr_url,
        "loop_id": loop_id,
        "file": file,
        "status": status,
        "timestamp": timestamp
    }
    
    # Generate PR title
    pr_title = f"Loop {loop_id} – {agent.upper()} File Contribution: {file}"
    pr_metadata["pr_title"] = pr_title
    
    # Generate PR body
    pr_body = f"Contract received from Orchestrator. Output validated. Pushed by {agent.upper()} for Operator review."
    pr_metadata["pr_body"] = pr_body
    
    # Log to agent trace memory
    log_to_memory(project_id, {
        "agent_trace": {
            agent: [{
                "type": "pr_created",
                "pr": pr_metadata
            }]
        }
    })
    
    # Log to loop trace memory
    log_to_memory(project_id, {
        "loop_trace": [{
            "type": "pr_created",
            "agent": agent,
            "pr": pr_metadata
        }]
    })
    
    # Log to git operations memory
    log_to_memory(project_id, {
        "git_operations": [{
            "type": "pr_created",
            "agent": agent,
            "pr": pr_metadata
        }]
    })
    
    # Log to chat
    emoji = "🔀"
    message = f"{emoji} Agent {agent.upper()} created PR for Loop {loop_id}: {pr_title}"
    message += f"\n{pr_url}"
    
    log_to_chat(project_id, {
        "role": "orchestrator",
        "message": message,
        "timestamp": timestamp
    })
    
    return pr_metadata

def enforce_branch_from_main(current_branch: str) -> Tuple[bool, str]:
    """
    Ensures that branches are created from the main branch.
    
    Args:
        current_branch (str): The current branch name
        
    Returns:
        tuple: (is_valid, message)
    """
    # If we're already on a feature branch, that's an error
    if current_branch.startswith("feature/"):
        suggestion = "git checkout main && git pull"
        return False, f"Error: Cannot create a feature branch from another feature branch. Please use: {suggestion}"
    
    # If we're not on main, that's an error
    if current_branch != "main":
        suggestion = "git checkout main && git pull"
        return False, f"Error: Branches must be created from main. Please use: {suggestion}"
    
    return True, "Branch will be created from main"

def validate_branch_name(branch: str) -> Tuple[bool, str]:
    """
    Validates that a branch name follows the required format.
    
    Args:
        branch (str): The branch name to validate
        
    Returns:
        tuple: (is_valid, message)
    """
    # Define the expected format pattern
    pattern = r'^feature/agent-[a-z]+-loop\d+-[a-z0-9]+$'
    
    # Check if the branch name matches the pattern
    if re.match(pattern, branch):
        return True, "Branch name is valid"
    
    # If not, provide a helpful error message
    return False, "Invalid branch name. Expected format: feature/agent-{agent}-loop{id}-{file}"

def suggest_pr_title(agent: str, loop_id: int, file: str) -> str:
    """
    Suggests a standardized PR title for an agent's task.
    
    Args:
        agent (str): The agent identifier
        loop_id (int): The loop identifier
        file (str): The file being worked on
        
    Returns:
        str: A standardized PR title
    """
    return f"Loop {loop_id} – {agent.upper()} File Contribution: {file}"

def suggest_pr_body(agent: str) -> str:
    """
    Suggests a standardized PR body for an agent's task.
    
    Args:
        agent (str): The agent identifier
        
    Returns:
        str: A standardized PR body
    """
    return f"Contract received from Orchestrator. Output validated. Pushed by {agent.upper()} for Operator review."

def get_current_branch() -> str:
    """
    Gets the current Git branch.
    
    Returns:
        str: The current branch name
    """
    try:
        # Run git command to get current branch
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # If the command fails, return an empty string
        return ""

def extract_info_from_branch(branch: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """
    Extracts agent, loop_id, and file information from a branch name.
    
    Args:
        branch (str): The branch name
        
    Returns:
        tuple: (agent, loop_id, file)
    """
    # Check if branch name matches the expected format
    pattern = r'^feature/agent-([a-z]+)-loop(\d+)-([a-z0-9]+)$'
    match = re.match(pattern, branch)
    
    if match:
        agent = match.group(1)
        loop_id = int(match.group(2))
        file = match.group(3)
        return agent, loop_id, file
    
    return None, None, None

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
    agent = "hal"
    loop_id = 32
    file = "LoginForm.jsx"
    
    # Generate branch name
    branch = generate_branch_name(agent, loop_id, file)
    print(f"Generated branch name: {branch}")
    
    # Validate commit message
    commit_msg = f"feat: HAL builds LoginForm.jsx in Loop {loop_id}"
    is_valid = validate_commit_message(commit_msg, agent, loop_id)
    print(f"Commit message is valid: {is_valid}")
    
    # Log PR metadata
    pr_url = "https://github.com/example/repo/pull/34"
    pr_metadata = log_pr_metadata(project_id, agent, branch, pr_url, loop_id, file)
    print("\nLogged PR metadata:")
    print(json.dumps(pr_metadata, indent=2))
    
    # Enforce branch from main
    current_branch = "main"
    is_valid, message = enforce_branch_from_main(current_branch)
    print(f"\nBranch from main check: {is_valid} - {message}")
    
    # Validate branch name
    is_valid, message = validate_branch_name(branch)
    print(f"\nBranch name validation: {is_valid} - {message}")
    
    # Suggest PR title and body
    pr_title = suggest_pr_title(agent, loop_id, file)
    pr_body = suggest_pr_body(agent)
    print(f"\nSuggested PR title: {pr_title}")
    print(f"Suggested PR body: {pr_body}")
