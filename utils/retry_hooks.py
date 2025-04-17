"""
Retry Hooks Utility Module

This module provides utility functions for handling agent retry logic,
allowing agents to check and respond to retry state during execution.
"""

def get_retry_status(project_id: str, agent_id: str):
    """
    Get the retry status for a specific agent in a project.
    
    Args:
        project_id: The project identifier
        agent_id: The agent identifier
        
    Returns:
        Dict containing retry status information:
        - should_retry: Whether the agent should retry
        - unblock_condition: Condition that would unblock the agent
        - last_block_reason: Reason the agent was last blocked
    """
    try:
        from memory.project_state import read_project_state
        state = read_project_state(project_id)

        # Fallback structure
        retry_info = state.get("retry_hooks", {}).get(agent_id, {})

        return {
            "should_retry": retry_info.get("enabled", False),
            "unblock_condition": retry_info.get("unblock_condition", None),
            "last_block_reason": retry_info.get("blocked_due_to", None)
        }
    except Exception as e:
        # Provide safe fallback if anything goes wrong
        print(f"Error getting retry status: {str(e)}")
        return {
            "should_retry": False,
            "unblock_condition": None,
            "last_block_reason": None
        }

def log_retry_action(agent_id: str, project_id: str, action: str):
    """
    Log a retry-related action to the project memory.
    
    Args:
        agent_id: The agent identifier
        project_id: The project identifier
        action: Description of the retry action
    """
    try:
        from app.modules.memory_writer import write_memory
        
        write_memory({
            "agent": agent_id,
            "project_id": project_id,
            "tool_used": "retry_hook",
            "action": action
        })
    except Exception as e:
        # Silently fail if memory writing is not available
        print(f"Error logging retry action: {str(e)}")
