"""
Agent Retry and Recovery Module

This module provides functionality for agent retry and recovery flow,
allowing agents who were blocked to auto-retry when dependencies are cleared.
"""
import logging
import json
import os
import time
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger("app.modules.agent_retry")

# Import project_state for tracking project status
try:
    from app.modules.project_state import update_project_state, read_project_state
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    print("❌ project_state import failed")

class AgentRetryManager:
    """
    Manages retry and recovery flow for agents.
    """
    def __init__(self):
        self.retry_registry = {}
        
    def register_blocked_agent(self, project_id: str, agent_id: str, 
                              blocked_due_to: str, unblock_condition: str) -> Dict[str, Any]:
        """
        Register a blocked agent for future retry.
        
        Args:
            project_id: The project identifier
            agent_id: The agent identifier (e.g., "critic", "nova")
            blocked_due_to: The dependency that caused the block (e.g., "nova", "hal")
            unblock_condition: The condition that would unblock the agent (e.g., "frontend created")
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            # Create registry entry if it doesn't exist
            if project_id not in self.retry_registry:
                self.retry_registry[project_id] = {}
            
            # Register the blocked agent
            self.retry_registry[project_id][agent_id] = {
                "blocked_due_to": blocked_due_to,
                "unblock_condition": unblock_condition,
                "registered_at": time.time(),
                "retry_count": 0,
                "last_retry": None,
                "status": "blocked"
            }
            
            # Update project state with block information
            if PROJECT_STATE_AVAILABLE:
                block_data = {
                    "blocked_agents": {
                        agent_id: {
                            "blocked_due_to": blocked_due_to,
                            "unblock_condition": unblock_condition,
                            "registered_at": time.time()
                        }
                    }
                }
                update_project_state(project_id, block_data)
            
            logger.info(f"Agent {agent_id} registered as blocked for project {project_id}")
            print(f"🔄 Agent {agent_id} registered as blocked for project {project_id}")
            
            return {
                "status": "success",
                "message": f"Agent {agent_id} registered for retry when {blocked_due_to} completes {unblock_condition}",
                "project_id": project_id,
                "agent_id": agent_id
            }
            
        except Exception as e:
            error_msg = f"Error registering blocked agent {agent_id} for project {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "agent_id": agent_id,
                "error": str(e)
            }
    
    def check_for_unblocked_agents(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Check for agents that can be unblocked based on current project state.
        
        Args:
            project_id: The project identifier
            
        Returns:
            List of agents that can be unblocked
        """
        try:
            unblocked_agents = []
            
            # Check if project exists in registry
            if project_id not in self.retry_registry:
                logger.info(f"No blocked agents found for project {project_id}")
                return unblocked_agents
            
            # Read current project state
            if not PROJECT_STATE_AVAILABLE:
                logger.error("Project state not available, cannot check for unblocked agents")
                return unblocked_agents
            
            project_state = read_project_state(project_id)
            agents_involved = project_state.get("agents_involved", [])
            
            # Check each blocked agent
            for agent_id, agent_data in self.retry_registry[project_id].items():
                if agent_data["status"] == "blocked":
                    blocked_due_to = agent_data["blocked_due_to"]
                    
                    # Check if blocking dependency is now resolved
                    if blocked_due_to in agents_involved:
                        # Mark agent as unblocked
                        self.retry_registry[project_id][agent_id]["status"] = "unblocked"
                        self.retry_registry[project_id][agent_id]["unblocked_at"] = time.time()
                        
                        unblocked_agents.append({
                            "agent_id": agent_id,
                            "blocked_due_to": blocked_due_to,
                            "unblock_condition": agent_data["unblock_condition"],
                            "blocked_duration": time.time() - agent_data["registered_at"]
                        })
                        
                        logger.info(f"Agent {agent_id} unblocked for project {project_id}")
                        print(f"✅ Agent {agent_id} unblocked for project {project_id}")
            
            # Update project state with unblocked agents
            if unblocked_agents and PROJECT_STATE_AVAILABLE:
                unblocked_data = {
                    "unblocked_agents": {
                        agent["agent_id"]: {
                            "unblocked_at": time.time(),
                            "previously_blocked_due_to": agent["blocked_due_to"]
                        } for agent in unblocked_agents
                    }
                }
                update_project_state(project_id, unblocked_data)
            
            return unblocked_agents
            
        except Exception as e:
            error_msg = f"Error checking for unblocked agents for project {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return []
    
    def mark_agent_retry_attempted(self, project_id: str, agent_id: str, 
                                  success: bool = True) -> Dict[str, Any]:
        """
        Mark an agent retry as attempted.
        
        Args:
            project_id: The project identifier
            agent_id: The agent identifier
            success: Whether the retry was successful
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            # Check if project and agent exist in registry
            if (project_id not in self.retry_registry or 
                agent_id not in self.retry_registry[project_id]):
                error_msg = f"Agent {agent_id} not found in retry registry for project {project_id}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id,
                    "agent_id": agent_id
                }
            
            # Update retry information
            self.retry_registry[project_id][agent_id]["retry_count"] += 1
            self.retry_registry[project_id][agent_id]["last_retry"] = time.time()
            
            if success:
                # Mark as completed if successful
                self.retry_registry[project_id][agent_id]["status"] = "completed"
                
                # Remove from blocked_agents in project state
                if PROJECT_STATE_AVAILABLE:
                    project_state = read_project_state(project_id)
                    blocked_agents = project_state.get("blocked_agents", {})
                    
                    if agent_id in blocked_agents:
                        del blocked_agents[agent_id]
                        
                        update_project_state(project_id, {
                            "blocked_agents": blocked_agents
                        })
                
                logger.info(f"Agent {agent_id} retry successful for project {project_id}")
                print(f"✅ Agent {agent_id} retry successful for project {project_id}")
            else:
                # Mark as failed if unsuccessful
                self.retry_registry[project_id][agent_id]["status"] = "retry_failed"
                logger.info(f"Agent {agent_id} retry failed for project {project_id}")
                print(f"❌ Agent {agent_id} retry failed for project {project_id}")
            
            return {
                "status": "success",
                "message": f"Agent {agent_id} retry {'successful' if success else 'failed'} for project {project_id}",
                "project_id": project_id,
                "agent_id": agent_id,
                "retry_count": self.retry_registry[project_id][agent_id]["retry_count"]
            }
            
        except Exception as e:
            error_msg = f"Error marking agent retry for {agent_id} in project {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "agent_id": agent_id,
                "error": str(e)
            }
    
    def get_retry_status(self, project_id: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the retry status for a project or specific agent.
        
        Args:
            project_id: The project identifier
            agent_id: Optional agent identifier to get status for a specific agent
            
        Returns:
            Dict containing the retry status
        """
        try:
            # Check if project exists in registry
            if project_id not in self.retry_registry:
                return {
                    "status": "success",
                    "project_id": project_id,
                    "message": f"No retry information found for project {project_id}",
                    "retry_data": {}
                }
            
            # Return status for specific agent if requested
            if agent_id:
                if agent_id not in self.retry_registry[project_id]:
                    return {
                        "status": "success",
                        "project_id": project_id,
                        "agent_id": agent_id,
                        "message": f"No retry information found for agent {agent_id} in project {project_id}",
                        "retry_data": {}
                    }
                
                return {
                    "status": "success",
                    "project_id": project_id,
                    "agent_id": agent_id,
                    "message": f"Retry information for agent {agent_id} in project {project_id}",
                    "retry_data": self.retry_registry[project_id][agent_id]
                }
            
            # Return status for all agents in the project
            return {
                "status": "success",
                "project_id": project_id,
                "message": f"Retry information for project {project_id}",
                "retry_data": self.retry_registry[project_id]
            }
            
        except Exception as e:
            error_msg = f"Error getting retry status for project {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "agent_id": agent_id,
                "error": str(e)
            }

# Create a singleton instance
retry_manager = AgentRetryManager()

def register_blocked_agent(project_id: str, agent_id: str, 
                          blocked_due_to: str, unblock_condition: str) -> Dict[str, Any]:
    """
    Register a blocked agent for future retry.
    
    Args:
        project_id: The project identifier
        agent_id: The agent identifier (e.g., "critic", "nova")
        blocked_due_to: The dependency that caused the block (e.g., "nova", "hal")
        unblock_condition: The condition that would unblock the agent (e.g., "frontend created")
        
    Returns:
        Dict containing the result of the operation
    """
    return retry_manager.register_blocked_agent(project_id, agent_id, blocked_due_to, unblock_condition)

def check_for_unblocked_agents(project_id: str) -> List[Dict[str, Any]]:
    """
    Check for agents that can be unblocked based on current project state.
    
    Args:
        project_id: The project identifier
        
    Returns:
        List of agents that can be unblocked
    """
    return retry_manager.check_for_unblocked_agents(project_id)

def mark_agent_retry_attempted(project_id: str, agent_id: str, 
                              success: bool = True) -> Dict[str, Any]:
    """
    Mark an agent retry as attempted.
    
    Args:
        project_id: The project identifier
        agent_id: The agent identifier
        success: Whether the retry was successful
        
    Returns:
        Dict containing the result of the operation
    """
    return retry_manager.mark_agent_retry_attempted(project_id, agent_id, success)

def get_retry_status(project_id: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the retry status for a project or specific agent.
    
    Args:
        project_id: The project identifier
        agent_id: Optional agent identifier to get status for a specific agent
        
    Returns:
        Dict containing the retry status
    """
    return retry_manager.get_retry_status(project_id, agent_id)
