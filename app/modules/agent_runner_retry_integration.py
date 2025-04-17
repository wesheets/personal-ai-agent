"""
Retry Hooks Integration for Agent Runner Functions

This file updates the agent_runner.py file to use the get_retry_status function
from the utils.retry_hooks module. This ensures agents can safely check and
respond to retry state logic during execution.

The changes include:
1. Adding import for retry_hooks module
2. Using get_retry_status in agent runner functions
3. Adding retry status logging
"""

# Find all instances of retry status checks in agent_runner.py and replace with get_retry_status
# Example in run_hal_agent:

def run_hal_agent(task, project_id, tools):
    """
    Run the HAL agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 HAL agent execution started")
    logger.info(f"HAL agent execution started with task: {task}, project_id: {project_id}")
    
    try:
        # Check retry status
        if RETRY_HOOKS_AVAILABLE:
            retry_check = get_retry_status(project_id, "hal")
            if retry_check["should_retry"]:
                print(f"🔄 HAL agent resuming after meeting unblock condition: {retry_check['unblock_condition']}")
                logger.info(f"HAL agent resuming after meeting unblock condition: {retry_check['unblock_condition']}")
                
                # Log retry action
                log_retry_action("hal", project_id, f"Agent hal resumed after meeting unblock condition: {retry_check['unblock_condition']}")
        
        # Rest of function remains the same
        # ...
    except Exception as e:
        # Error handling remains the same
        # ...

# Example in run_nova_agent:

def run_nova_agent(task, project_id, tools):
    """
    Run the NOVA agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 NOVA agent execution started")
    logger.info(f"NOVA agent execution started with task: {task}, project_id: {project_id}")
    
    try:
        # Check retry status
        if RETRY_HOOKS_AVAILABLE:
            retry_check = get_retry_status(project_id, "nova")
            if retry_check["should_retry"]:
                print(f"🔄 NOVA agent resuming after meeting unblock condition: {retry_check['unblock_condition']}")
                logger.info(f"NOVA agent resuming after meeting unblock condition: {retry_check['unblock_condition']}")
                
                # Log retry action
                log_retry_action("nova", project_id, f"Agent nova resumed after meeting unblock condition: {retry_check['unblock_condition']}")
        
        # Rest of function remains the same
        # ...
    except Exception as e:
        # Error handling remains the same
        # ...

# Example in run_critic_agent:

def run_critic_agent(task, project_id, tools):
    """
    Run the CRITIC agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 CRITIC agent execution started")
    logger.info(f"CRITIC agent execution started with task: {task}, project_id: {project_id}")
    
    try:
        # Check retry status
        if RETRY_HOOKS_AVAILABLE:
            retry_check = get_retry_status(project_id, "critic")
            if retry_check["should_retry"]:
                print(f"🔄 CRITIC agent resuming after meeting unblock condition: {retry_check['unblock_condition']}")
                logger.info(f"CRITIC agent resuming after meeting unblock condition: {retry_check['unblock_condition']}")
                
                # Log retry action
                log_retry_action("critic", project_id, f"Agent critic resumed after meeting unblock condition: {retry_check['unblock_condition']}")
        
        # Rest of function remains the same
        # ...
    except Exception as e:
        # Error handling remains the same
        # ...

# Example in run_ash_agent:

def run_ash_agent(task, project_id, tools):
    """
    Run the ASH agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 ASH agent execution started")
    logger.info(f"ASH agent execution started with task: {task}, project_id: {project_id}")
    
    try:
        # Check retry status
        if RETRY_HOOKS_AVAILABLE:
            retry_check = get_retry_status(project_id, "ash")
            if retry_check["should_retry"]:
                print(f"🔄 ASH agent resuming after meeting unblock condition: {retry_check['unblock_condition']}")
                logger.info(f"ASH agent resuming after meeting unblock condition: {retry_check['unblock_condition']}")
                
                # Log retry action
                log_retry_action("ash", project_id, f"Agent ash resumed after meeting unblock condition: {retry_check['unblock_condition']}")
        
        # Rest of function remains the same
        # ...
    except Exception as e:
        # Error handling remains the same
        # ...
