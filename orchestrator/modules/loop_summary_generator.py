"""
Loop Summary Generator Module

This module provides functionality to generate, store, and retrieve summaries of completed loops.
It creates concise, human-readable summaries that capture what was planned, what was built,
who contributed, and what changed during the loop execution.
"""

import json
import re
import html
from datetime import datetime
from typing import Dict, List, Optional, Any

def generate_loop_summary(project_id: str, loop_id: int, memory: Dict[str, Any]) -> str:
    """
    Generates a concise, human-readable summary of a completed loop.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        memory (Dict[str, Any]): The memory dictionary containing loop data
        
    Returns:
        str: A formatted summary of the loop
    """
    # Initialize summary components
    summary_parts = []
    
    # Get loop data from memory
    loop_trace = memory.get("loop_trace", {}).get(str(loop_id), {})
    agent_actions = memory.get("agent_actions", {}).get(str(loop_id), [])
    loop_plan = memory.get("loop_plans", [])
    loop_plan = next((plan for plan in loop_plan if plan.get("loop_id") == loop_id), {})
    
    # Get loop status
    loop_status = loop_trace.get("status", "unknown")
    status_emoji = _get_status_emoji(loop_status)
    
    # Add loop ID and status to summary
    summary_parts.append(f"Loop {loop_id} Summary: {status_emoji}")
    
    # Add plan information
    goals = loop_plan.get("goals", [])
    if goals:
        # Use the first goal as the main plan description
        # Sanitize the goal text to prevent injection
        sanitized_goal = _sanitize_text(goals[0])
        summary_parts.append(f"• Plan: \"{sanitized_goal}\"")
    
    # Add agent information
    agents = loop_plan.get("agents", [])
    agent_selection_trace = loop_plan.get("agent_selection_trace", [])
    
    if agents:
        # Create a mapping of agent roles based on selection trace
        agent_roles = {}
        for entry in agent_selection_trace:
            agent = entry.get("agent")
            if agent and agent in agents:
                # Extract role from reason if available
                reason = entry.get("reason", "").lower()
                if "ui" in reason or "design" in reason or "frontend" in reason:
                    agent_roles[agent] = "UI"
                elif "api" in reason or "backend" in reason or "data" in reason:
                    agent_roles[agent] = "backend"
                elif "validation" in reason or "critic" in agent:
                    agent_roles[agent] = "validation"
                elif "system" in reason:
                    agent_roles[agent] = "system"
        
        # Format agent list with roles
        agent_list = []
        for agent in agents:
            # Sanitize agent name
            sanitized_agent = _sanitize_text(agent)
            role = agent_roles.get(agent, "")
            if role:
                agent_list.append(f"{sanitized_agent} ({role})")
            else:
                agent_list.append(sanitized_agent)
        
        summary_parts.append(f"• Agents: {', '.join(agent_list)}")
    
    # Add file information
    files = loop_plan.get("planned_files", [])
    if files:
        # Limit to at most 3 files for conciseness
        # Sanitize file names
        sanitized_files = [_sanitize_text(file) for file in files[:3]]
        if len(files) > 3:
            sanitized_files.append("...")
        summary_parts.append(f"• Files: {', '.join(sanitized_files)}")
    
    # Add key events from agent actions
    key_events = _extract_key_events(agent_actions, loop_trace)
    for event in key_events:
        summary_parts.append(f"• {event}")
    
    # Add operator feedback if available
    operator_feedback = loop_trace.get("operator_feedback", {})
    if operator_feedback:
        feedback_status = operator_feedback.get("status")
        if feedback_status == "accepted":
            summary_parts.append("• Operator accepted the result.")
        elif feedback_status == "rejected":
            reason = operator_feedback.get("reason", "No reason provided")
            # Sanitize reason
            sanitized_reason = _sanitize_text(reason)
            summary_parts.append(f"• Operator rejected the result: \"{sanitized_reason}\"")
        elif feedback_status == "modified":
            summary_parts.append("• Operator accepted with modifications.")
    
    # Add link to previous loop if this was a rerouted loop
    rerouted_from = loop_trace.get("rerouted_from")
    if rerouted_from:
        summary_parts.append(f"• Rerouted from Loop {rerouted_from}.")
    
    # Join all parts with newlines
    return "\n".join(summary_parts)

def store_loop_summary(project_id: str, loop_id: int, summary: str, memory: Dict[str, Any]) -> None:
    """
    Stores a loop summary in memory and loop trace.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        summary (str): The formatted loop summary
        memory (Dict[str, Any]): The memory dictionary to update
    """
    # Get current timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Initialize loop_summaries if it doesn't exist
    if "loop_summaries" not in memory:
        memory["loop_summaries"] = {}
    
    # Store summary in loop_summaries
    memory["loop_summaries"][str(loop_id)] = {
        "summary": summary,
        "timestamp": timestamp,
        "project_id": project_id
    }
    
    # Store summary in loop_trace
    if "loop_trace" not in memory:
        memory["loop_trace"] = {}
    
    if str(loop_id) not in memory["loop_trace"]:
        memory["loop_trace"][str(loop_id)] = {}
    
    memory["loop_trace"][str(loop_id)]["summary"] = {
        "text": summary,
        "timestamp": timestamp
    }
    
    # Optionally add to chat_messages
    chat_message = {
        "role": "orchestrator",
        "message": f"Loop {loop_id} completed. Summary:\n{summary}",
        "timestamp": timestamp,
        "loop_id": loop_id
    }
    
    if "chat_messages" not in memory:
        memory["chat_messages"] = []
    
    memory["chat_messages"].append(chat_message)

def get_loop_summary(project_id: str, loop_id: int, memory: Dict[str, Any]) -> Optional[str]:
    """
    Retrieves a loop summary by loop ID.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        memory (Dict[str, Any]): The memory dictionary containing summaries
        
    Returns:
        Optional[str]: The formatted loop summary or None if not found
    """
    # Try to get from loop_summaries first
    loop_summaries = memory.get("loop_summaries", {})
    loop_summary = loop_summaries.get(str(loop_id))
    
    if loop_summary:
        return loop_summary.get("summary")
    
    # If not found, try to get from loop_trace
    loop_trace = memory.get("loop_trace", {}).get(str(loop_id), {})
    summary_data = loop_trace.get("summary")
    
    if summary_data:
        return summary_data.get("text")
    
    # If still not found, generate a new summary
    if _loop_exists(loop_id, memory):
        summary = generate_loop_summary(project_id, loop_id, memory)
        store_loop_summary(project_id, loop_id, summary, memory)
        return summary
    
    return None

def _get_status_emoji(status: str) -> str:
    """
    Returns an emoji representing the loop status.
    
    Args:
        status (str): The loop status
        
    Returns:
        str: An emoji representing the status
    """
    status_lower = status.lower()
    
    if status_lower == "completed" or status_lower == "accepted":
        return "✅"
    elif status_lower == "rejected":
        return "❌"
    elif status_lower == "rerouted" or status_lower == "modified":
        return "🔄"
    elif status_lower == "in_progress":
        return "⏳"
    else:
        return "ℹ️"

def _extract_key_events(agent_actions: List[Dict[str, Any]], loop_trace: Dict[str, Any]) -> List[str]:
    """
    Extracts key events from agent actions and loop trace.
    
    Args:
        agent_actions (List[Dict[str, Any]]): List of agent actions
        loop_trace (Dict[str, Any]): Loop trace data
        
    Returns:
        List[str]: List of key event descriptions
    """
    key_events = []
    
    # Look for CRITIC rejections
    critic_rejections = [
        action for action in agent_actions 
        if action.get("agent") == "critic" and action.get("action_type") == "rejection"
    ]
    
    for rejection in critic_rejections:
        reason = rejection.get("details", {}).get("reason", "unspecified reason")
        # Sanitize reason
        sanitized_reason = _sanitize_text(reason)
        fixed_by = None
        
        # Look for fixes after the rejection
        rejection_time = rejection.get("timestamp", "")
        fix_actions = [
            action for action in agent_actions
            if action.get("timestamp", "") > rejection_time and action.get("action_type") == "fix"
        ]
        
        if fix_actions:
            fixed_by = fix_actions[0].get("agent", "").upper()
        
        if fixed_by:
            key_events.append(f"CRITIC flagged a {sanitized_reason}, fixed by {fixed_by}.")
        else:
            key_events.append(f"CRITIC flagged a {sanitized_reason}.")
    
    # Look for CTO interventions
    cto_actions = [
        action for action in agent_actions
        if action.get("agent") == "cto"
    ]
    
    if cto_actions:
        key_events.append(f"CTO intervened {len(cto_actions)} times.")
    
    # Look for plan deviations
    plan_deviations = loop_trace.get("plan_deviations", [])
    if plan_deviations:
        key_events.append(f"Plan deviated {len(plan_deviations)} times.")
    
    # Limit to 3 key events for conciseness
    return key_events[:3]

def _loop_exists(loop_id: int, memory: Dict[str, Any]) -> bool:
    """
    Checks if a loop exists in memory.
    
    Args:
        loop_id (int): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        bool: True if the loop exists, False otherwise
    """
    # Check in loop_trace
    if str(loop_id) in memory.get("loop_trace", {}):
        return True
    
    # Check in loop_plans
    loop_plans = memory.get("loop_plans", [])
    for plan in loop_plans:
        if plan.get("loop_id") == loop_id:
            return True
    
    # Check in agent_actions
    if str(loop_id) in memory.get("agent_actions", {}):
        return True
    
    return False

def _sanitize_text(text: str) -> str:
    """
    Sanitizes text to prevent injection attacks.
    
    Args:
        text (str): The text to sanitize
        
    Returns:
        str: The sanitized text
    """
    if not isinstance(text, str):
        return str(text)
    
    # HTML escape to prevent XSS
    sanitized = html.escape(text)
    
    # Remove potential script tags and other dangerous patterns
    sanitized = re.sub(r'<script.*?>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
    
    # Remove SQL injection patterns
    sanitized = re.sub(r';\s*DROP\s+TABLE', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r';\s*DELETE\s+FROM', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized
