"""
Loop Controller Module

This module provides functionality to control loop execution, including
delusion detection, failure debugging, belief alignment tracking, and CEO insights.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import delusion detection and debugger agent modules
from orchestrator.modules.delusion_detector import detect_plan_delusion, store_rejected_plan
from agents.debugger_agent import debug_loop_failure
from agents.historian_agent import analyze_loop_summary
from agents.ceo_agent import analyze_loop_with_ceo_agent
from memory.belief_reference import load_beliefs_from_file, get_recent_loops

def evaluate_plan_with_delusion_detector(
    plan: Dict[str, Any],
    loop_id: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluates a plan using the delusion detector to check for similarity to failed plans.
    
    Args:
        plan (Dict[str, Any]): The plan to evaluate
        loop_id (str): The current loop identifier
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the evaluation, including updated memory if warnings were injected
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "similarity_threshold": 0.85
        }
    
    # Skip evaluation if disabled
    if not config.get("enabled", True):
        return {
            "status": "skipped",
            "memory": memory,
            "message": "Delusion detection is disabled"
        }
    
    # Get similarity threshold from config
    similarity_threshold = config.get("similarity_threshold", 0.85)
    
    # Detect delusions
    updated_memory = detect_plan_delusion(
        plan,
        loop_id,
        memory,
        similarity_threshold
    )
    
    # Check if warnings were injected
    has_warnings = False
    if "delusion_alerts" in updated_memory:
        for alert in updated_memory["delusion_alerts"]:
            if alert["loop_id"] == loop_id:
                has_warnings = True
                break
    
    # Return result
    if has_warnings:
        return {
            "status": "warning",
            "memory": updated_memory,
            "message": "Potential delusion detected in plan"
        }
    else:
        return {
            "status": "ok",
            "memory": updated_memory,
            "message": "No delusions detected"
        }

def register_failed_plan(
    plan: Dict[str, Any],
    loop_id: str,
    failure_reason: str,
    memory: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Registers a failed plan in memory for future delusion detection.
    
    Args:
        plan (Dict[str, Any]): The failed plan
        loop_id (str): The loop identifier
        failure_reason (str): The reason the plan failed
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Dict[str, Any]: Updated memory dictionary
    """
    return store_rejected_plan(plan, loop_id, failure_reason, memory)

def debug_failure_with_debugger_agent(
    loop_id: str,
    failure_logs: str,
    memory: Dict[str, Any],
    loop_context: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Debugs a loop failure using the debugger agent.
    
    Args:
        loop_id (str): The loop identifier
        failure_logs (str): The failure logs from the loop
        memory (Dict[str, Any]): The memory dictionary
        loop_context (Optional[Dict[str, Any]]): Context information about the loop
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the debugging, including updated memory with debugger report
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "auto_reroute": False
        }
    
    # Skip debugging if disabled
    if not config.get("enabled", True):
        return {
            "status": "skipped",
            "memory": memory,
            "message": "Debugger agent is disabled"
        }
    
    # Use empty context if none provided
    if loop_context is None:
        loop_context = {}
    
    # Debug failure
    updated_memory = debug_loop_failure(loop_id, failure_logs, memory, loop_context)
    
    # Get the latest debugger report
    latest_report = None
    if "debugger_reports" in updated_memory:
        for report in updated_memory["debugger_reports"]:
            if report["loop_id"] == loop_id:
                if latest_report is None or report["timestamp"] > latest_report["timestamp"]:
                    latest_report = report
    
    # Return result
    if latest_report:
        return {
            "status": "debugged",
            "memory": updated_memory,
            "message": f"Failure debugged: {latest_report['failure_type']}",
            "report": latest_report,
            "auto_reroute": config.get("auto_reroute", False)
        }
    else:
        return {
            "status": "error",
            "memory": updated_memory,
            "message": "Failed to generate debugger report"
        }

def analyze_loop_with_historian_agent(
    loop_id: str,
    loop_summary: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyzes a loop summary using the historian agent to track belief alignment.
    
    Args:
        loop_id (str): The loop identifier
        loop_summary (str): The summary text of the completed loop
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the analysis, including updated memory with historian alerts
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "beliefs_file": "orchestrator_beliefs.json",
            "recent_loops_count": 10
        }
    
    # Skip analysis if disabled
    if not config.get("enabled", True):
        return {
            "status": "skipped",
            "memory": memory,
            "message": "Historian agent is disabled"
        }
    
    # Load beliefs from file
    beliefs_file = config.get("beliefs_file", "orchestrator_beliefs.json")
    beliefs = load_beliefs_from_file(beliefs_file)
    
    if not beliefs:
        return {
            "status": "error",
            "memory": memory,
            "message": f"Failed to load beliefs from {beliefs_file}"
        }
    
    # Get recent loops
    recent_loops_count = config.get("recent_loops_count", 10)
    recent_loops = get_recent_loops(memory, recent_loops_count)
    
    # Analyze loop summary
    updated_memory = analyze_loop_summary(loop_id, loop_summary, recent_loops, beliefs, memory)
    
    # Check if alerts were generated
    has_alerts = False
    if "historian_alerts" in updated_memory:
        for alert in updated_memory["historian_alerts"]:
            if alert["loop_id"] == loop_id:
                has_alerts = True
                alignment_score = alert["loop_belief_alignment_score"]
                missing_beliefs = len(alert["missing_beliefs"])
                break
    
    # Return result
    if has_alerts:
        return {
            "status": "analyzed",
            "memory": updated_memory,
            "message": f"Loop analyzed: alignment score {alignment_score:.2f}, {missing_beliefs} missing beliefs"
        }
    else:
        return {
            "status": "error",
            "memory": updated_memory,
            "message": "Failed to generate historian alert"
        }

def handle_loop_execution(
    plan: Dict[str, Any],
    loop_id: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Handles loop execution with delusion detection.
    
    Args:
        plan (Dict[str, Any]): The plan to execute
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the execution
    """
    # Use default config if none provided
    if config is None:
        config = {
            "delusion_detection": {
                "enabled": True,
                "similarity_threshold": 0.85,
                "block_execution": False
            }
        }
    
    # Evaluate plan with delusion detector
    delusion_config = config.get("delusion_detection", {"enabled": True})
    evaluation_result = evaluate_plan_with_delusion_detector(
        plan,
        loop_id,
        memory,
        delusion_config
    )
    
    # Check if execution should be blocked due to delusion
    if (evaluation_result["status"] == "warning" and 
            delusion_config.get("block_execution", False)):
        return {
            "status": "blocked",
            "memory": evaluation_result["memory"],
            "message": "Loop execution blocked due to potential delusion"
        }
    
    # Return result with updated memory
    return {
        "status": "proceed",
        "memory": evaluation_result["memory"],
        "message": evaluation_result["message"]
    }

def handle_loop_failure(
    loop_id: str,
    failure_logs: str,
    plan: Dict[str, Any],
    failure_reason: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Handles loop failure with debugging and plan registration.
    
    Args:
        loop_id (str): The loop identifier
        failure_logs (str): The failure logs from the loop
        plan (Dict[str, Any]): The failed plan
        failure_reason (str): The reason the plan failed
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the failure handling
    """
    # Use default config if none provided
    if config is None:
        config = {
            "debugger_agent": {
                "enabled": True,
                "auto_reroute": False
            },
            "store_failed_plans": True
        }
    
    # Store failed plan if enabled
    if config.get("store_failed_plans", True):
        memory = register_failed_plan(plan, loop_id, failure_reason, memory)
    
    # Debug failure with debugger agent
    debugger_config = config.get("debugger_agent", {"enabled": True})
    loop_context = {
        "plan": plan,
        "failure_reason": failure_reason
    }
    
    debug_result = debug_failure_with_debugger_agent(
        loop_id,
        failure_logs,
        memory,
        loop_context,
        debugger_config
    )
    
    # Return result
    return debug_result

def process_loop_with_ceo_agent(
    loop_id: str,
    loop_summary: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyzes a loop summary using the CEO agent to evaluate alignment with system beliefs
    and track operator satisfaction.
    
    Args:
        loop_id (str): The loop identifier
        loop_summary (str): The summary text of the completed loop
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the analysis, including updated memory with CEO insights
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "beliefs_file": "orchestrator_beliefs.json",
            "alignment_threshold": 0.6,
            "recent_loops_count": 10,
            "review_window_size": 5
        }
    
    # Skip analysis if disabled
    if not config.get("enabled", True):
        return {
            "status": "skipped",
            "memory": memory,
            "message": "CEO agent is disabled"
        }
    
    # Load beliefs from file
    beliefs_file = config.get("beliefs_file", "orchestrator_beliefs.json")
    beliefs = load_beliefs_from_file(beliefs_file)
    
    if not beliefs:
        return {
            "status": "error",
            "memory": memory,
            "message": f"Failed to load beliefs from {beliefs_file}"
        }
    
    # Analyze loop summary with CEO agent
    updated_memory = analyze_loop_with_ceo_agent(
        loop_id,
        loop_summary,
        beliefs,
        memory,
        config
    )
    
    # Check if insights were generated
    has_insights = False
    if "ceo_insights" in updated_memory:
        for insight in updated_memory["ceo_insights"]:
            if insight["loop_id"] == loop_id:
                has_insights = True
                alignment_score = insight["alignment_score"]
                insight_type = insight["insight_type"]
                break
    
    # Return result
    if has_insights:
        return {
            "status": "analyzed",
            "memory": updated_memory,
            "message": f"Loop analyzed by CEO: {insight_type} with alignment score {alignment_score:.2f}"
        }
    else:
        return {
            "status": "ok",
            "memory": updated_memory,
            "message": "No CEO insights generated (alignment within acceptable threshold)"
        }

def handle_loop_completion(
    loop_id: str,
    loop_summary: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Handles loop completion with historian agent and CEO agent analysis.
    
    Args:
        loop_id (str): The loop identifier
        loop_summary (str): The summary text of the completed loop
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the completion handling
    """
    # Use default config if none provided
    if config is None:
        config = {
            "historian_agent": {
                "enabled": True,
                "beliefs_file": "orchestrator_beliefs.json",
                "recent_loops_count": 10
            },
            "ceo_agent": {
                "enabled": True,
                "beliefs_file": "orchestrator_beliefs.json",
                "alignment_threshold": 0.6,
                "recent_loops_count": 10,
                "review_window_size": 5
            }
        }
    
    # Analyze loop with historian agent
    historian_config = config.get("historian_agent", {"enabled": True})
    historian_result = analyze_loop_with_historian_agent(
        loop_id,
        loop_summary,
        memory,
        historian_config
    )
    
    # Update memory with historian analysis results
    memory = historian_result["memory"]
    
    # Analyze loop with CEO agent
    ceo_config = config.get("ceo_agent", {"enabled": True})
    ceo_result = process_loop_with_ceo_agent(
        loop_id,
        loop_summary,
        memory,
        ceo_config
    )
    
    # Combine results
    combined_result = {
        "status": "completed",
        "memory": ceo_result["memory"],
        "message": f"Historian: {historian_result['message']}; CEO: {ceo_result['message']}"
    }
    
    # Return combined result
    return combined_result
