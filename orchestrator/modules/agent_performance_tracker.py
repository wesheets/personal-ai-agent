"""
Agent Performance Tracker Module

This module provides functionality to track agent performance across loops and compute
dynamic trust scores based on validation results, CRITIC feedback, operator overrides,
successful loop completion, and rejection rates.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def update_agent_performance(project_id: str, agent: str, loop_id: int, result: dict) -> dict:
    """
    Stores agent performance data for a specific loop.
    
    Args:
        project_id (str): The project identifier
        agent (str): The agent name
        loop_id (int): The loop identifier
        result (dict): Performance result data containing metrics like:
                      - schema_passed (bool): Whether schema validation passed
                      - was_rerouted (bool): Whether the task was rerouted by CRITIC
                      - operator_approved (bool): Whether operator approved the output
                      - files_created (int): Number of files created
                      - rejections (int): Number of rejections
                      
    Returns:
        dict: The logged performance data with timestamp added
    """
    # Create timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create the performance data object
    performance_data = {
        "agent": agent,
        "loop_id": loop_id,
        "timestamp": timestamp
    }
    
    # Add all result metrics
    for key, value in result.items():
        performance_data[key] = value
    
    # Ensure required fields exist with defaults if not provided
    if "schema_passed" not in performance_data:
        performance_data["schema_passed"] = False
    
    if "was_rerouted" not in performance_data:
        performance_data["was_rerouted"] = False
    
    if "operator_approved" not in performance_data:
        performance_data["operator_approved"] = False
    
    if "files_created" not in performance_data:
        performance_data["files_created"] = 0
    
    if "rejections" not in performance_data:
        performance_data["rejections"] = 0
    
    # Log to agent performance memory
    log_to_memory(project_id, {
        "agent_performance": {
            agent: [performance_data]
        }
    })
    
    # Log to loop trace memory
    log_to_memory(project_id, {
        "loop_trace": [{
            "type": "agent_performance",
            "loop_id": loop_id,
            "agent": agent,
            "performance": performance_data,
            "timestamp": timestamp
        }]
    })
    
    # Calculate and update trust score
    calculate_trust_score(project_id, agent)
    
    # Log to chat (optional)
    status_emoji = "✅" if performance_data.get("schema_passed", False) else "⚠️"
    message = f"{status_emoji} Performance data recorded for {agent.upper()} in Loop {loop_id}"
    
    log_to_chat(project_id, {
        "role": "orchestrator",
        "message": message,
        "timestamp": timestamp
    })
    
    return performance_data

def calculate_trust_score(project_id: str, agent: str) -> float:
    """
    Calculates a trust score for an agent based on their performance history.
    
    Args:
        project_id (str): The project identifier
        agent (str): The agent name
        
    Returns:
        float: The calculated trust score (0.0 - 1.0)
    """
    # Get agent performance history
    performance_history = get_agent_performance_history(project_id, agent)
    
    # If no history, return default trust score
    if not performance_history:
        default_score = 0.5  # Neutral trust score for new agents
        
        # Update agent status with default trust score
        log_to_memory(project_id, {
            "agent_status": {
                agent: {
                    "trust_score": default_score,
                    "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            }
        })
        
        return default_score
    
    # Calculate metrics from performance history
    total_loops = len(performance_history)
    validation_passes = sum(1 for p in performance_history if p.get("schema_passed", False))
    reroutes = sum(1 for p in performance_history if p.get("was_rerouted", False))
    operator_approvals = sum(1 for p in performance_history if p.get("operator_approved", False))
    total_rejections = sum(p.get("rejections", 0) for p in performance_history)
    total_files = sum(p.get("files_created", 0) for p in performance_history)
    
    # Calculate individual factor scores
    validation_score = validation_passes / total_loops if total_loops > 0 else 0.5
    reroute_factor = 1.0 - (reroutes / total_loops if total_loops > 0 else 0.0)
    approval_score = operator_approvals / total_loops if total_loops > 0 else 0.5
    rejection_factor = 1.0 - (min(1.0, total_rejections / max(1, total_files)) if total_files > 0 else 0.0)
    
    # Weight factors
    weights = {
        "validation": 0.35,
        "reroute": 0.25,
        "approval": 0.25,
        "rejection": 0.15
    }
    
    # Calculate weighted trust score
    trust_score = (
        weights["validation"] * validation_score +
        weights["reroute"] * reroute_factor +
        weights["approval"] * approval_score +
        weights["rejection"] * rejection_factor
    )
    
    # Ensure score is within bounds
    trust_score = max(0.0, min(1.0, trust_score))
    
    # Update agent status with calculated trust score
    log_to_memory(project_id, {
        "agent_status": {
            agent: {
                "trust_score": trust_score,
                "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
    })
    
    return trust_score

def get_agent_report(project_id: str, agent: str) -> dict:
    """
    Returns a comprehensive trust profile for an agent.
    
    Args:
        project_id (str): The project identifier
        agent (str): The agent name
        
    Returns:
        dict: The agent's trust profile
    """
    # Get agent performance history
    performance_history = get_agent_performance_history(project_id, agent)
    
    # Get current trust score
    trust_score, last_updated = get_current_trust_score(project_id, agent)
    
    # If no history, return basic report
    if not performance_history:
        return {
            "agent": agent,
            "trust_score": trust_score,
            "last_updated": last_updated,
            "loops_participated": 0,
            "validation_pass_rate": 0.0,
            "reroute_count": 0,
            "operator_rejections": 0,
            "files_created": 0
        }
    
    # Calculate metrics from performance history
    total_loops = len(performance_history)
    validation_passes = sum(1 for p in performance_history if p.get("schema_passed", False))
    reroutes = sum(1 for p in performance_history if p.get("was_rerouted", False))
    total_rejections = sum(p.get("rejections", 0) for p in performance_history)
    total_files = sum(p.get("files_created", 0) for p in performance_history)
    
    # Calculate rates
    validation_pass_rate = validation_passes / total_loops if total_loops > 0 else 0.0
    
    # Create comprehensive report
    report = {
        "agent": agent,
        "trust_score": trust_score,
        "last_updated": last_updated,
        "loops_participated": total_loops,
        "validation_pass_rate": validation_pass_rate,
        "reroute_count": reroutes,
        "operator_rejections": total_rejections,
        "files_created": total_files
    }
    
    # Add recent performance entries (last 5)
    recent_entries = sorted(
        performance_history, 
        key=lambda x: x.get("timestamp", ""), 
        reverse=True
    )[:5]
    
    report["recent_performance"] = recent_entries
    
    # Add trend analysis
    if total_loops >= 3:
        # Calculate trend by comparing first half and second half
        mid_point = total_loops // 2
        sorted_history = sorted(performance_history, key=lambda x: x.get("loop_id", 0))
        
        first_half = sorted_history[:mid_point]
        second_half = sorted_history[mid_point:]
        
        first_half_passes = sum(1 for p in first_half if p.get("schema_passed", False))
        second_half_passes = sum(1 for p in second_half if p.get("schema_passed", False))
        
        first_half_rate = first_half_passes / len(first_half) if first_half else 0
        second_half_rate = second_half_passes / len(second_half) if second_half else 0
        
        trend = "improving" if second_half_rate > first_half_rate else "declining" if second_half_rate < first_half_rate else "stable"
        report["trend"] = trend
    
    return report

def get_agent_performance_history(project_id: str, agent: str) -> List[Dict[str, Any]]:
    """
    Retrieves the performance history for an agent.
    
    Args:
        project_id (str): The project identifier
        agent (str): The agent name
        
    Returns:
        list: The agent's performance history
    """
    # In a real implementation, this would retrieve data from a database or file
    # For now, we'll just print a message and return an empty list
    print(f"Retrieving performance history for agent {agent} in project {project_id}")
    
    # Return an empty list for demonstration
    return []

def get_current_trust_score(project_id: str, agent: str) -> Tuple[float, str]:
    """
    Retrieves the current trust score for an agent.
    
    Args:
        project_id (str): The project identifier
        agent (str): The agent name
        
    Returns:
        tuple: (trust_score, last_updated)
    """
    # In a real implementation, this would retrieve data from a database or file
    # For now, we'll return a default value
    default_score = 0.5  # Neutral trust score
    current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return default_score, current_time

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
    
    # Update agent performance
    performance = update_agent_performance(
        project_id=project_id,
        agent="hal",
        loop_id=33,
        result={
            "schema_passed": True,
            "was_rerouted": False,
            "operator_approved": True,
            "files_created": 1,
            "rejections": 0
        }
    )
    print("\nUpdated agent performance:")
    print(json.dumps(performance, indent=2))
    
    # Calculate trust score
    trust_score = calculate_trust_score(project_id, "hal")
    print(f"\nCalculated trust score for HAL: {trust_score}")
    
    # Get agent report
    report = get_agent_report(project_id, "hal")
    print("\nAgent report for HAL:")
    print(json.dumps(report, indent=2))
