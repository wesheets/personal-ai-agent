"""
Loop Controller Module

This module provides functionality to control the loop execution flow,
including post-loop evaluation with the Pessimist Agent.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.pessimist_agent import process_loop_summary

def evaluate_loop_with_pessimist(
    project_id: str,
    loop_id: int,
    memory: Dict[str, Any],
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Evaluates a loop summary using the Pessimist Agent.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        memory (Dict[str, Any]): The memory dictionary containing loop data
        config (Dict[str, Any], optional): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the evaluation with status and any alerts
    """
    # Default configuration
    default_config = {
        "enabled": True,
        "evaluation_threshold": 0.6,  # Only evaluate loops with confidence above this
        "auto_inject_alerts": True
    }
    
    # Merge with provided config
    if config:
        for key, value in config.items():
            default_config[key] = value
    
    config = default_config
    
    # Skip if disabled
    if not config["enabled"]:
        return {
            "status": "skipped",
            "reason": "Pessimist Agent evaluation disabled in configuration",
            "loop_id": loop_id
        }
    
    # Get loop summary
    loop_summary = ""
    loop_summaries = memory.get("loop_summaries", {})
    if str(loop_id) in loop_summaries:
        loop_summary = loop_summaries[str(loop_id)].get("summary", "")
    
    # Get loop trace for feedback
    loop_trace = memory.get("loop_trace", {}).get(str(loop_id), {})
    
    # Get operator feedback
    operator_feedback = loop_trace.get("operator_feedback", [])
    if not isinstance(operator_feedback, list):
        operator_feedback = [operator_feedback] if operator_feedback else []
    
    # Get plan confidence score if available
    plan_confidence_score = None
    loop_plans = memory.get("loop_plans", [])
    for plan in loop_plans:
        if plan.get("loop_id") == loop_id:
            plan_confidence_score = plan.get("confidence_score")
            break
    
    # Skip if no summary
    if not loop_summary:
        return {
            "status": "skipped",
            "reason": "No loop summary found",
            "loop_id": loop_id
        }
    
    # Process the loop summary with the Pessimist Agent
    updated_memory = process_loop_summary(
        str(loop_id),
        loop_summary,
        operator_feedback,
        memory.copy(),
        plan_confidence_score
    )
    
    # Check if any alerts were generated
    pessimist_alerts = updated_memory.get("pessimist_alerts", [])
    
    # Find alerts for this loop
    loop_alerts = [alert for alert in pessimist_alerts if alert.get("loop_id") == str(loop_id)]
    
    # If no alerts were generated, return success with no alerts
    if not loop_alerts:
        return {
            "status": "success",
            "message": "No bias detected in loop summary",
            "loop_id": loop_id,
            "alerts": []
        }
    
    # If auto-inject is enabled, update the original memory
    if config["auto_inject_alerts"]:
        # Initialize pessimist_alerts if it doesn't exist
        if "pessimist_alerts" not in memory:
            memory["pessimist_alerts"] = []
        
        # Add new alerts
        for alert in loop_alerts:
            memory["pessimist_alerts"].append(alert)
        
        # Update loop summary metadata if it exists
        if "loop_summaries" in memory and str(loop_id) in memory["loop_summaries"]:
            if "metadata" not in memory["loop_summaries"][str(loop_id)]:
                memory["loop_summaries"][str(loop_id)]["metadata"] = {}
            
            if "bias_tags" not in memory["loop_summaries"][str(loop_id)]["metadata"]:
                memory["loop_summaries"][str(loop_id)]["metadata"]["bias_tags"] = []
            
            # Add bias tags to metadata
            for alert in loop_alerts:
                memory["loop_summaries"][str(loop_id)]["metadata"]["bias_tags"].extend(alert.get("bias_tags", []))
            
            # Remove duplicates
            memory["loop_summaries"][str(loop_id)]["metadata"]["bias_tags"] = list(
                set(memory["loop_summaries"][str(loop_id)]["metadata"]["bias_tags"])
            )
    
    # Log to chat
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    for alert in loop_alerts:
        alert_type = alert.get("alert_type", "unknown")
        bias_tags = alert.get("bias_tags", [])
        suggestion = alert.get("suggestion", "")
        
        chat_message = {
            "role": "pessimist",
            "message": f"⚠️ Loop {loop_id} alert: {alert_type}. Detected: {', '.join(bias_tags)}. {suggestion}",
            "timestamp": timestamp,
            "loop_id": loop_id
        }
        
        if "chat_messages" not in memory:
            memory["chat_messages"] = []
        
        memory["chat_messages"].append(chat_message)
    
    return {
        "status": "alert",
        "message": f"Bias detected in loop {loop_id} summary",
        "loop_id": loop_id,
        "alerts": loop_alerts
    }

def post_loop_evaluation(project_id: str, loop_id: int, memory: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Performs post-loop evaluation including Pessimist Agent analysis.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        memory (Dict[str, Any]): The memory dictionary containing loop data
        config (Dict[str, Any], optional): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the post-loop evaluation
    """
    # Initialize results
    results = {
        "loop_id": loop_id,
        "evaluations": []
    }
    
    # Run Pessimist Agent evaluation
    pessimist_result = evaluate_loop_with_pessimist(project_id, loop_id, memory, config)
    results["evaluations"].append({
        "agent": "pessimist",
        "result": pessimist_result
    })
    
    # Add timestamp
    results["timestamp"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Store evaluation results in memory
    if "loop_evaluations" not in memory:
        memory["loop_evaluations"] = {}
    
    memory["loop_evaluations"][str(loop_id)] = results
    
    return results
