"""
Agent Dispatch Module

This module handles the dispatching of agents for various tasks,
enforcing permissions and logging violations.
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from app.modules.agent_permission_validator import (
    validate_agent_action,
    get_substitute_action,
    log_violation,
    enforce_agent_permissions
)

class AgentDispatcher:
    """
    Class for dispatching agents and enforcing permissions.
    """
    
    def __init__(self, loop_id: str):
        """
        Initialize the agent dispatcher.
        
        Args:
            loop_id: The ID of the current loop
        """
        self.loop_id = loop_id
        self.violations = []
    
    def dispatch(self, agent: str, action: str, **kwargs) -> Tuple[Any, bool]:
        """
        Dispatch an agent to perform an action, enforcing permissions.
        
        Args:
            agent: The name of the agent
            action: The action to perform
            **kwargs: Additional arguments for the action
            
        Returns:
            Tuple containing:
            - Result of the action
            - Boolean indicating whether a permission violation occurred
        """
        # Enforce permissions
        is_allowed, violation, substitute = enforce_agent_permissions(agent, action, self.loop_id)
        
        if not is_allowed:
            # Log violation
            self.violations.append(violation)
            
            if substitute:
                # Use substitute action
                print(f"WARNING: Agent {agent} attempted unauthorized action {action}. Using substitute {substitute} instead.")
                return self._execute_action(agent, substitute, **kwargs), True
            else:
                # No substitute available, return error
                print(f"ERROR: Agent {agent} attempted unauthorized action {action} and no substitute is available.")
                return {"error": f"Agent {agent} is not authorized to perform action {action}"}, True
        
        # Action is allowed, execute it
        return self._execute_action(agent, action, **kwargs), False
    
    def _execute_action(self, agent: str, action: str, **kwargs) -> Any:
        """
        Execute an agent action.
        
        Args:
            agent: The name of the agent
            action: The action to perform
            **kwargs: Additional arguments for the action
            
        Returns:
            Result of the action
        """
        # In a real implementation, this would dispatch to the actual agent implementation
        # For now, we'll return a mock result
        return {
            "agent": agent,
            "action": action,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_violations(self) -> List[Dict[str, Any]]:
        """
        Get all permission violations that occurred during dispatch.
        
        Returns:
            List of violation records
        """
        return self.violations

def create_dispatcher(loop_id: str) -> AgentDispatcher:
    """
    Create an agent dispatcher for a specific loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        AgentDispatcher instance
    """
    return AgentDispatcher(loop_id)

def dispatch_agent(loop_id: str, agent: str, action: str, **kwargs) -> Tuple[Any, List[Dict[str, Any]]]:
    """
    Dispatch an agent for a one-time action, enforcing permissions.
    
    Args:
        loop_id: The ID of the current loop
        agent: The name of the agent
        action: The action to perform
        **kwargs: Additional arguments for the action
        
    Returns:
        Tuple containing:
        - Result of the action
        - List of any permission violations that occurred
    """
    dispatcher = create_dispatcher(loop_id)
    result, violation_occurred = dispatcher.dispatch(agent, action, **kwargs)
    
    return result, dispatcher.get_violations() if violation_occurred else []
