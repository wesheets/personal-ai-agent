"""
Agent Context Module

This module implements the functionality for retrieving agent context information.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Configure logging
logger = logging.getLogger("agent_context")

# In-memory storage for agent states and loop states
# In a production environment, this would be stored in a database
_agent_states: Dict[str, Dict[str, Any]] = {
    "ORCHESTRATOR": {
        "state": "active",
        "last_action": {
            "agent_id": "ORCHESTRATOR",
            "action_type": "plan",
            "timestamp": "2025-04-24T20:40:00Z",
            "status": "completed",
            "details": {
                "plan_id": "plan_456",
                "steps_created": 5
            }
        }
    },
    "CRITIC": {
        "state": "idle",
        "last_action": {
            "agent_id": "CRITIC",
            "action_type": "review",
            "timestamp": "2025-04-24T20:35:00Z",
            "status": "completed",
            "details": {
                "review_id": "rev_789",
                "issues_found": 2,
                "confidence": 0.85
            }
        }
    },
    "SAGE": {
        "state": "idle",
        "last_action": {
            "agent_id": "SAGE",
            "action_type": "analyze",
            "timestamp": "2025-04-24T20:30:00Z",
            "status": "completed",
            "details": {
                "analysis_id": "ana_123",
                "insights_found": 3
            }
        }
    }
}

_loop_states: Dict[str, Dict[str, Any]] = {
    "loop_12345": {
        "loop_id": "loop_12345",
        "current_step": 3,
        "total_steps": 5,
        "started_at": "2025-04-24T20:30:00Z",
        "last_updated": "2025-04-24T20:45:00Z",
        "state": "active",
        "active_agent": "ORCHESTRATOR"
    },
    "loop_67890": {
        "loop_id": "loop_67890",
        "current_step": 5,
        "total_steps": 5,
        "started_at": "2025-04-24T19:30:00Z",
        "last_updated": "2025-04-24T20:15:00Z",
        "state": "completed",
        "active_agent": None
    }
}

# Current active loop
_current_loop_id = "loop_12345"

def get_agent_context(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get context information for an agent.
    
    Args:
        request_data: Request data containing agent_id, loop_id, and include_memory_stats
        
    Returns:
        Dictionary containing the agent context information
    """
    try:
        agent_id = request_data.get("agent_id")
        loop_id = request_data.get("loop_id", _current_loop_id)
        include_memory_stats = request_data.get("include_memory_stats", True)
        
        # If agent_id is not provided, return context for all agents
        if not agent_id:
            return get_all_agents_context(loop_id, include_memory_stats)
        
        # Check if agent exists
        if agent_id not in _agent_states:
            return {
                "message": f"Agent not found: {agent_id}",
                "agent_id": agent_id,
                "loop_id": loop_id,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Get agent state
        agent_state = _agent_states[agent_id]
        
        # Get loop state if available
        loop_state = _loop_states.get(loop_id)
        
        # Get memory usage if requested
        memory_usage = get_memory_usage(agent_id) if include_memory_stats else None
        
        # Log the context retrieval to memory
        _log_context_retrieval(agent_id, loop_id)
        
        # Return the context
        return {
            "agent_id": agent_id,
            "state": agent_state["state"],
            "loop_state": loop_state,
            "last_action": agent_state.get("last_action"),
            "memory_usage": memory_usage,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error getting agent context: {str(e)}")
        return {
            "message": f"Failed to get agent context: {str(e)}",
            "agent_id": request_data.get("agent_id"),
            "loop_id": request_data.get("loop_id"),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def get_all_agents_context(loop_id: str, include_memory_stats: bool) -> Dict[str, Any]:
    """
    Get context information for all agents.
    
    Args:
        loop_id: Loop ID to get context for
        include_memory_stats: Whether to include memory usage statistics
        
    Returns:
        Dictionary containing context information for all agents
    """
    try:
        # Get loop state if available
        loop_state = _loop_states.get(loop_id)
        
        # Get all agent contexts
        agent_contexts = []
        for agent_id, agent_state in _agent_states.items():
            # Get memory usage if requested
            memory_usage = get_memory_usage(agent_id) if include_memory_stats else None
            
            agent_contexts.append({
                "agent_id": agent_id,
                "state": agent_state["state"],
                "last_action": agent_state.get("last_action"),
                "memory_usage": memory_usage
            })
        
        # Log the context retrieval to memory
        _log_context_retrieval("ALL", loop_id)
        
        # Return the context
        return {
            "loop_id": loop_id,
            "loop_state": loop_state,
            "agents": agent_contexts,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error getting all agents context: {str(e)}")
        return {
            "message": f"Failed to get all agents context: {str(e)}",
            "loop_id": loop_id,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def get_memory_usage(agent_id: str) -> Dict[str, Any]:
    """
    Get memory usage statistics for an agent.
    
    Args:
        agent_id: Agent ID to get memory usage for
        
    Returns:
        Dictionary containing memory usage statistics
    """
    # In a real implementation, this would query a memory service
    # For this implementation, we'll return mock data
    
    # Generate mock data based on agent ID
    if agent_id == "ORCHESTRATOR":
        return {
            "total_entries": 1250,
            "recent_entries": 42,
            "tags_count": {
                "conversation": 850,
                "plan_generated": 125,
                "agent_output": 275
            },
            "size_bytes": 2560000
        }
    elif agent_id == "CRITIC":
        return {
            "total_entries": 750,
            "recent_entries": 15,
            "tags_count": {
                "review": 500,
                "issue": 200,
                "recommendation": 50
            },
            "size_bytes": 1280000
        }
    elif agent_id == "SAGE":
        return {
            "total_entries": 500,
            "recent_entries": 10,
            "tags_count": {
                "analysis": 300,
                "insight": 150,
                "summary": 50
            },
            "size_bytes": 980000
        }
    else:
        return {
            "total_entries": 100,
            "recent_entries": 5,
            "tags_count": {
                "misc": 100
            },
            "size_bytes": 256000
        }

def _log_context_retrieval(agent_id: str, loop_id: str) -> None:
    """
    Log context retrieval to memory.
    
    Args:
        agent_id: Agent ID
        loop_id: Loop ID
    """
    try:
        # In a real implementation, this would write to a memory service
        log_entry = {
            "agent_id": agent_id,
            "loop_id": loop_id,
            "operation": "context_retrieval",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log to console for demonstration
        logger.info(f"Agent context retrieval logged: {json.dumps(log_entry)}")
        print(f"Logged to memory: agent_context_retrieval_{agent_id}_{loop_id}")
    
    except Exception as e:
        logger.error(f"Error logging context retrieval: {str(e)}")
