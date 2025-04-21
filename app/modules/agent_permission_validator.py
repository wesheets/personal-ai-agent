"""
Agent Permission Validator Module

This module provides functionality to validate agent actions against their permission registry.
It ensures that agents only perform actions they are allowed to, and logs violations.

The permission system is a key part of the cognitive control layer, ensuring that
agents only perform actions within their defined scope and capabilities.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the agent permissions file
PERMISSIONS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "agent_permissions.json")

# Cache for permissions to avoid repeated file reads
_permissions_cache = None
_permissions_last_modified = 0

def load_agent_permissions() -> Dict[str, List[str]]:
    """
    Load agent permissions from the JSON file.
    
    Returns:
        Dictionary mapping agent names to lists of allowed actions
    """
    global _permissions_cache, _permissions_last_modified
    
    try:
        # Check if file has been modified since last read
        current_mtime = os.path.getmtime(PERMISSIONS_FILE)
        
        # Use cache if available and file hasn't changed
        if _permissions_cache is not None and current_mtime <= _permissions_last_modified:
            return _permissions_cache
        
        # Read permissions from file
        with open(PERMISSIONS_FILE, 'r') as f:
            permissions = json.load(f)
            
        # Update cache
        _permissions_cache = permissions
        _permissions_last_modified = current_mtime
        
        logger.info(f"Loaded agent permissions for {len(permissions)} agents")
        return permissions
    
    except FileNotFoundError:
        logger.error(f"Agent permissions file not found: {PERMISSIONS_FILE}")
        # Return default permissions as fallback
        return {
            "SAGE": ["reflect", "question", "analyze_prompt", "generate_plan"],
            "HAL": ["generate_code", "debug_code", "explain_code"],
            "PESSIMIST": ["analyze_summary", "tag_tone", "identify_bias"],
            "CRITIC": ["score_summary", "evaluate_quality", "provide_feedback"],
            "CEO": ["evaluate_alignment", "assess_business_impact", "review_strategy"]
        }
    
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing agent permissions file: {e}")
        # Return empty permissions as fallback
        return {}
    
    except Exception as e:
        logger.error(f"Error loading agent permissions: {e}")
        # Return empty permissions as fallback
        return {}

def check_permission(agent: str, action: str) -> bool:
    """
    Check if an agent is allowed to perform a specific action.
    
    Args:
        agent: The name of the agent
        action: The action to check
        
    Returns:
        Boolean indicating whether the action is allowed
    """
    permissions = load_agent_permissions()
    
    # If agent not in permissions, assume no permissions
    if agent not in permissions:
        logger.warning(f"Agent '{agent}' not found in permissions registry")
        return False
    
    # Check if action is allowed
    allowed_actions = permissions[agent]
    return action in allowed_actions

def validate_agent_action(agent: str, action: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validate whether an agent is allowed to perform a specific action.
    
    Args:
        agent: The name of the agent
        action: The action to validate
        
    Returns:
        Tuple containing:
        - Boolean indicating whether the action is allowed
        - Optional dictionary with violation details if not allowed
    """
    is_allowed = check_permission(agent, action)
    if is_allowed:
        # Action is allowed
        logger.debug(f"Agent '{agent}' authorized to perform action '{action}'")
        return True, None
    
    # Action is not allowed, prepare violation details
    permissions = load_agent_permissions()
    allowed_actions = permissions.get(agent, [])
    
    violation = {
        "agent": agent,
        "attempted_action": action,
        "allowed_actions": allowed_actions,
        "timestamp": datetime.utcnow().isoformat(),
        "loop_id": "unknown",  # Will be updated by caller
        "violation_type": "unknown_agent" if agent not in permissions else "unauthorized_action",
        "severity": "high" if agent not in permissions else "medium"
    }
    
    logger.warning(f"Agent '{agent}' attempted unauthorized action '{action}'")
    return False, violation

def get_substitute_action(agent: str, attempted_action: str) -> Optional[Dict[str, Any]]:
    """
    Get a substitute action when an agent attempts an unauthorized action.
    
    Args:
        agent: The name of the agent
        attempted_action: The unauthorized action that was attempted
        
    Returns:
        A dictionary with substitute action details, or None if no substitute is available
    """
    permissions = load_agent_permissions()
    
    # If agent not in permissions, no substitute available
    if agent not in permissions:
        logger.warning(f"Cannot find substitute action for unknown agent '{agent}'")
        return None
    
    allowed_actions = permissions[agent]
    if not allowed_actions:
        logger.warning(f"Agent '{agent}' has no allowed actions for substitution")
        return None
    
    # Try to find a semantically similar action if possible
    # This is a simple implementation that could be enhanced with more sophisticated matching
    similar_actions = []
    for action in allowed_actions:
        # Check if the attempted action is a substring of an allowed action
        if attempted_action.lower() in action.lower():
            similar_actions.append(action)
    
    if similar_actions:
        substitute_action = similar_actions[0]
        reason = "semantically_similar"
        logger.info(f"Found semantically similar substitute '{substitute_action}' for agent '{agent}' instead of '{attempted_action}'")
    else:
        # If no similar action found, return the first allowed action as a fallback
        substitute_action = allowed_actions[0]
        reason = "fallback"
        logger.info(f"Using fallback substitute '{substitute_action}' for agent '{agent}' instead of '{attempted_action}'")
    
    return {
        "action": substitute_action,
        "reason": reason,
        "original_action": attempted_action,
        "agent": agent,
        "timestamp": datetime.utcnow().isoformat()
    }

def log_violation(violation: Dict[str, Any], loop_id: str) -> Dict[str, Any]:
    """
    Update a violation record with loop_id and return it for logging.
    
    Args:
        violation: The violation record
        loop_id: The ID of the loop where the violation occurred
        
    Returns:
        Updated violation record
    """
    violation["loop_id"] = loop_id
    violation["logged_at"] = datetime.utcnow().isoformat()
    
    # Log the violation
    logger.warning(
        f"Permission violation in loop {loop_id}: "
        f"Agent '{violation['agent']}' attempted unauthorized action '{violation['attempted_action']}'"
    )
    
    # In a production system, this would also write to a database or monitoring system
    
    return violation

def enforce_agent_permissions(agent: str, action: str, loop_id: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Enforce agent permissions by validating an action and providing a substitute if needed.
    
    Args:
        agent: The name of the agent
        action: The action to validate
        loop_id: The ID of the current loop
        
    Returns:
        Tuple containing:
        - Boolean indicating whether the action is allowed
        - Optional violation record if not allowed
        - Optional substitute action if not allowed
    """
    is_allowed, violation = validate_agent_action(agent, action)
    
    if not is_allowed:
        # Update violation with loop_id
        violation = log_violation(violation, loop_id)
        
        # Get substitute action
        substitute = get_substitute_action(agent, action)
        if substitute:
            violation["substituted_action"] = substitute["action"]
            violation["resolution"] = "substituted"
            logger.info(f"Substituting action '{substitute['action']}' for agent '{agent}' in loop {loop_id}")
        else:
            violation["resolution"] = "blocked"
            logger.warning(f"Blocking action '{action}' for agent '{agent}' in loop {loop_id} (no substitute available)")
        
        # Add belief reference for transparency
        violation["belief_reference"] = "transparency_to_operator"
        
        # Add timestamp for when enforcement occurred
        violation["enforced_at"] = datetime.utcnow().isoformat()
        
        return False, violation, substitute
    
    # Log successful authorization
    logger.debug(f"Authorized: Agent '{agent}' performing '{action}' in loop {loop_id}")
    return True, None, None

def get_all_allowed_actions() -> Dict[str, Set[str]]:
    """
    Get a dictionary of all allowed actions for each agent.
    
    Returns:
        Dictionary mapping agent names to sets of allowed actions
    """
    permissions = load_agent_permissions()
    result = {}
    
    for agent, actions in permissions.items():
        result[agent] = set(actions)
    
    return result

def is_action_allowed_for_any_agent(action: str) -> bool:
    """
    Check if an action is allowed for any agent.
    
    Args:
        action: The action to check
        
    Returns:
        Boolean indicating whether the action is allowed for any agent
    """
    permissions = load_agent_permissions()
    
    for agent, allowed_actions in permissions.items():
        if action in allowed_actions:
            return True
    
    return False

def get_agents_allowed_for_action(action: str) -> List[str]:
    """
    Get a list of agents that are allowed to perform a specific action.
    
    Args:
        action: The action to check
        
    Returns:
        List of agent names allowed to perform the action
    """
    permissions = load_agent_permissions()
    allowed_agents = []
    
    for agent, allowed_actions in permissions.items():
        if action in allowed_actions:
            allowed_agents.append(agent)
    
    return allowed_agents
