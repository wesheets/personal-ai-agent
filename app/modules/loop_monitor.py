"""
Loop Monitor Module

This module provides functionality for monitoring agent execution times
and detecting frozen agents that exceed their timeout thresholds.
It integrates with the project_state module to track agent execution
and detect when agents run longer than their allowed timeout.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from app.schema_registry import SCHEMA_REGISTRY
from app.modules.project_state import read_project_state, update_project_state

# Configure logging
logger = logging.getLogger("app.modules.loop_monitor")

def log_agent_execution_start(project_id: str, agent: str) -> Dict[str, Any]:
    """
    Logs the start of an agent execution.
    
    Args:
        project_id: The ID of the project
        agent: The name of the agent (e.g., "hal", "nova")
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Get current timestamp
        now = datetime.utcnow().isoformat()
        
        # Read current project state
        project_state = read_project_state(project_id)
        
        # Initialize agent_execution_log if it doesn't exist
        if "agent_execution_log" not in project_state:
            project_state["agent_execution_log"] = []
        
        # Add execution start entry
        execution_entry = {
            "agent": agent,
            "start_time": now,
            "status": "running",
            "loop": project_state.get("loop_count", 0)
        }
        
        # Update project state
        project_state["agent_execution_log"].append(execution_entry)
        project_state["current_agent"] = agent
        project_state["last_agent_triggered_at"] = now
        
        # Write updated state
        result = update_project_state(project_id, {
            "agent_execution_log": project_state["agent_execution_log"],
            "current_agent": agent,
            "last_agent_triggered_at": now
        })
        
        logger.info(f"Agent execution start logged for {agent} in project {project_id}")
        return result
    
    except Exception as e:
        error_msg = f"Error logging agent execution start for {agent} in project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def log_agent_execution_complete(project_id: str, agent: str, status: str = "completed") -> Dict[str, Any]:
    """
    Logs the completion of an agent execution.
    
    Args:
        project_id: The ID of the project
        agent: The name of the agent (e.g., "hal", "nova")
        status: The completion status (e.g., "completed", "error", "timeout")
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Get current timestamp
        now = datetime.utcnow().isoformat()
        
        # Read current project state
        project_state = read_project_state(project_id)
        
        # Find the most recent execution entry for this agent
        execution_log = project_state.get("agent_execution_log", [])
        updated = False
        
        for i in range(len(execution_log) - 1, -1, -1):
            entry = execution_log[i]
            if entry["agent"] == agent and entry["status"] == "running":
                # Calculate duration
                start_time = datetime.fromisoformat(entry["start_time"])
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                # Update entry
                execution_log[i]["end_time"] = now
                execution_log[i]["status"] = status
                execution_log[i]["duration"] = duration
                updated = True
                break
        
        if not updated:
            # If no running entry was found, create a new completed entry
            execution_log.append({
                "agent": agent,
                "start_time": now,  # Approximate
                "end_time": now,
                "status": status,
                "duration": 0,
                "loop": project_state.get("loop_count", 0)
            })
        
        # Update project state
        result = update_project_state(project_id, {
            "agent_execution_log": execution_log,
            "current_agent": None,
            "last_completed_agent": agent
        })
        
        logger.info(f"Agent execution completion logged for {agent} in project {project_id} with status {status}")
        return result
    
    except Exception as e:
        error_msg = f"Error logging agent execution completion for {agent} in project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def check_for_frozen_agents(project_id: str) -> List[Dict[str, Any]]:
    """
    Checks for agents that have exceeded their execution timeout.
    
    Args:
        project_id: The ID of the project to check
        
    Returns:
        List of frozen agents with their details
    """
    try:
        now = datetime.utcnow()
        project_state = read_project_state(project_id)
        execution_log = project_state.get("agent_execution_log", [])
        frozen = []

        for entry in execution_log:
            # Only check entries with "running" status
            if entry.get("status") != "running":
                continue
                
            agent = entry["agent"]
            
            # Skip if agent is not in schema registry
            if agent not in SCHEMA_REGISTRY.get("agents", {}):
                logger.warning(f"Agent {agent} not found in schema registry, skipping timeout check")
                continue
                
            start_time = datetime.fromisoformat(entry["start_time"])
            timeout = SCHEMA_REGISTRY["agents"][agent].get("timeout_seconds", 30)

            if (now - start_time).total_seconds() > timeout:
                frozen_entry = {
                    "agent": agent,
                    "duration": (now - start_time).total_seconds(),
                    "timeout": timeout,
                    "loop": entry.get("loop", project_state.get("loop_count", 0)),
                    "start_time": entry["start_time"]
                }
                frozen.append(frozen_entry)
                
                # Mark the agent as timed out in the execution log
                entry["status"] = "timeout"
                entry["end_time"] = now.isoformat()
                entry["duration"] = (now - start_time).total_seconds()

        if frozen:
            # Log the timeout alert
            loop_alerts = project_state.get("loop_alerts", [])
            loop_alerts.append({
                "type": "timeout",
                "timestamp": now.isoformat(),
                "frozen_agents": frozen
            })
            
            # Update project state with timeout information
            update_project_state(project_id, {
                "agent_execution_log": execution_log,
                "loop_alerts": loop_alerts,
                "has_frozen_agents": True
            })
            
            logger.warning(f"Detected {len(frozen)} frozen agents in project {project_id}: {[f['agent'] for f in frozen]}")

        return frozen
        
    except Exception as e:
        error_msg = f"Error checking for frozen agents in project {project_id}: {str(e)}"
        logger.error(error_msg)
        return []

def get_agent_execution_status(project_id: str, agent: Optional[str] = None) -> Dict[str, Any]:
    """
    Gets the execution status for all agents or a specific agent.
    
    Args:
        project_id: The ID of the project
        agent: Optional name of a specific agent to check
        
    Returns:
        Dict containing execution status information
    """
    try:
        project_state = read_project_state(project_id)
        execution_log = project_state.get("agent_execution_log", [])
        
        if agent:
            # Filter for specific agent
            agent_entries = [entry for entry in execution_log if entry["agent"] == agent]
            return {
                "agent": agent,
                "executions": agent_entries,
                "current_status": agent_entries[-1]["status"] if agent_entries else "never_run"
            }
        else:
            # Group by agent
            agent_status = {}
            for entry in execution_log:
                agent_name = entry["agent"]
                if agent_name not in agent_status:
                    agent_status[agent_name] = []
                agent_status[agent_name].append(entry)
            
            # Get current status for each agent
            current_status = {}
            for agent_name, entries in agent_status.items():
                current_status[agent_name] = entries[-1]["status"] if entries else "never_run"
            
            return {
                "project_id": project_id,
                "agent_executions": agent_status,
                "current_status": current_status,
                "has_frozen_agents": project_state.get("has_frozen_agents", False),
                "loop_alerts": project_state.get("loop_alerts", [])
            }
    
    except Exception as e:
        error_msg = f"Error getting agent execution status for project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def reset_frozen_agents(project_id: str) -> Dict[str, Any]:
    """
    Resets the status of frozen agents to allow them to be run again.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        project_state = read_project_state(project_id)
        execution_log = project_state.get("agent_execution_log", [])
        reset_count = 0
        
        # Find and reset any frozen agents
        for entry in execution_log:
            if entry.get("status") == "timeout":
                entry["status"] = "reset_after_timeout"
                reset_count += 1
        
        # Update project state
        result = update_project_state(project_id, {
            "agent_execution_log": execution_log,
            "has_frozen_agents": False
        })
        
        logger.info(f"Reset {reset_count} frozen agents in project {project_id}")
        return {
            "status": "success",
            "message": f"Reset {reset_count} frozen agents",
            "reset_count": reset_count,
            "project_id": project_id
        }
    
    except Exception as e:
        error_msg = f"Error resetting frozen agents for project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }
