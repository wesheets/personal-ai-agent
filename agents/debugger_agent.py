"""
Debugger Agent Module

This module provides functionality to diagnose failures in loops and propose reroutes
to recover from failures and improve future execution.
"""

import re
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

def parse_failure_logs(traceback_str: str) -> Dict[str, Any]:
    """
    Parses failure logs to identify the root cause of a failure.
    
    Args:
        traceback_str (str): The traceback string from the failure
        
    Returns:
        Dict[str, Any]: Information about the root cause of the failure
    """
    # Initialize result
    result = {
        "failure_type": "unknown",
        "details": {},
        "confidence": 0.5
    }
    
    # Check for common failure patterns
    
    # Tool timeout
    if re.search(r"timeout|timed? out", traceback_str, re.IGNORECASE):
        result["failure_type"] = "tool_timeout"
        result["details"]["suggested_fix"] = "Reduce input length or increase timeout"
        result["confidence"] = 0.9
    
    # API rate limit
    elif re.search(r"rate limit|too many requests|429", traceback_str, re.IGNORECASE):
        result["failure_type"] = "api_rate_limit"
        result["details"]["suggested_fix"] = "Implement exponential backoff or reduce request frequency"
        result["confidence"] = 0.9
    
    # Permission error
    elif re.search(r"permission|access denied|forbidden|403", traceback_str, re.IGNORECASE):
        result["failure_type"] = "permission_error"
        result["details"]["suggested_fix"] = "Check credentials or request appropriate permissions"
        result["confidence"] = 0.8
    
    # Resource not found
    elif re.search(r"not found|404|no such file|doesn't exist", traceback_str, re.IGNORECASE):
        result["failure_type"] = "resource_not_found"
        result["details"]["suggested_fix"] = "Verify resource paths or create missing resources"
        result["confidence"] = 0.8
    
    # Invalid input
    elif re.search(r"invalid|malformed|syntax error|value error", traceback_str, re.IGNORECASE):
        result["failure_type"] = "invalid_input"
        result["details"]["suggested_fix"] = "Validate and sanitize inputs before processing"
        result["confidence"] = 0.7
    
    # Memory error
    elif re.search(r"memory|allocation|out of memory|oom", traceback_str, re.IGNORECASE):
        result["failure_type"] = "memory_error"
        result["details"]["suggested_fix"] = "Optimize memory usage or increase available memory"
        result["confidence"] = 0.8
    
    # Network error
    elif re.search(r"network|connection|unreachable|dns|socket", traceback_str, re.IGNORECASE):
        result["failure_type"] = "network_error"
        result["details"]["suggested_fix"] = "Check network connectivity or retry with exponential backoff"
        result["confidence"] = 0.8
    
    # Dependency error
    elif re.search(r"import error|module not found|no module named", traceback_str, re.IGNORECASE):
        result["failure_type"] = "dependency_error"
        result["details"]["suggested_fix"] = "Install missing dependencies or fix import paths"
        result["confidence"] = 0.9
    
    # Extract specific error message if available
    error_match = re.search(r"Error: (.+?)(?:\n|$)", traceback_str)
    if error_match:
        # Use the simplified error message from the Error: line
        result["details"]["error_message"] = error_match.group(1).strip()
    else:
        # For permission errors, use a simplified message
        if result["failure_type"] == "permission_error":
            result["details"]["error_message"] = "Permission denied when writing to file"
        # For resource not found errors, use a simplified message
        elif result["failure_type"] == "resource_not_found":
            result["details"]["error_message"] = "Resource not found"
        # For other errors, try to extract from the last line of the traceback
        else:
            last_line_match = re.search(r'([^:\n]+)(?:\n|$)(?!.)', traceback_str)
            if last_line_match:
                result["details"]["error_message"] = last_line_match.group(1).strip()
    
    # Extract line number if available
    line_match = re.search(r"line (\d+)", traceback_str)
    if line_match:
        result["details"]["line_number"] = int(line_match.group(1))
    
    # Extract file name if available
    file_match = re.search(r"File \"([^\"]+)\"", traceback_str)
    if file_match:
        result["details"]["file_name"] = file_match.group(1)
    
    return result

def determine_next_agent(failure_type: str) -> str:
    """
    Determines which agent should handle the failure next.
    
    Args:
        failure_type (str): The type of failure
        
    Returns:
        str: The name of the agent that should handle the failure
    """
    # Map failure types to appropriate agents
    failure_agent_map = {
        "tool_timeout": "optimizer",
        "api_rate_limit": "scheduler",
        "permission_error": "security",
        "resource_not_found": "researcher",
        "invalid_input": "validator",
        "memory_error": "optimizer",
        "network_error": "connector",
        "dependency_error": "installer",
        "unknown": "critic"
    }
    
    # Return the appropriate agent or default to critic
    return failure_agent_map.get(failure_type, "critic")

def generate_patch_plan(root_cause: Dict[str, Any], loop_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a plan to patch the failure and recover.
    
    Args:
        root_cause (Dict[str, Any]): Information about the root cause of the failure
        loop_context (Dict[str, Any]): Context information about the loop
        
    Returns:
        Dict[str, Any]: A plan to patch the failure
    """
    failure_type = root_cause.get("failure_type", "unknown")
    
    # Initialize patch plan
    patch_plan = {
        "steps": [],
        "next_agent": determine_next_agent(failure_type),
        "confidence": root_cause.get("confidence", 0.5)
    }
    
    # Generate steps based on failure type
    if failure_type == "tool_timeout":
        patch_plan["steps"] = [
            "Reduce input size or complexity",
            "Increase timeout threshold if possible",
            "Split operation into smaller chunks"
        ]
    
    elif failure_type == "api_rate_limit":
        patch_plan["steps"] = [
            "Implement exponential backoff strategy",
            "Reduce request frequency",
            "Cache results to minimize API calls"
        ]
    
    elif failure_type == "permission_error":
        patch_plan["steps"] = [
            "Verify credentials are correct",
            "Request necessary permissions",
            "Use alternative approach that doesn't require elevated permissions"
        ]
    
    elif failure_type == "resource_not_found":
        patch_plan["steps"] = [
            "Verify resource paths are correct",
            "Create missing resources if appropriate",
            "Implement fallback mechanism for missing resources"
        ]
    
    elif failure_type == "invalid_input":
        patch_plan["steps"] = [
            "Validate inputs before processing",
            "Sanitize inputs to remove problematic characters",
            "Provide clearer error messages for invalid inputs"
        ]
    
    elif failure_type == "memory_error":
        patch_plan["steps"] = [
            "Optimize memory usage",
            "Process data in smaller batches",
            "Release unused resources earlier"
        ]
    
    elif failure_type == "network_error":
        patch_plan["steps"] = [
            "Implement retry mechanism with exponential backoff",
            "Check network connectivity before operations",
            "Provide offline fallback when possible"
        ]
    
    elif failure_type == "dependency_error":
        patch_plan["steps"] = [
            "Install missing dependencies",
            "Fix import paths",
            "Check for version compatibility issues"
        ]
    
    else:  # unknown
        patch_plan["steps"] = [
            "Review logs for more detailed error information",
            "Test with simplified inputs to isolate the issue",
            "Consult documentation for the failing component"
        ]
    
    # Add specific fix if available
    if "suggested_fix" in root_cause.get("details", {}):
        patch_plan["suggested_fix"] = root_cause["details"]["suggested_fix"]
    
    return patch_plan

def inject_debugger_report(
    memory: Dict[str, Any],
    loop_id: str,
    failure_logs: str,
    loop_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Injects a debugger report into memory.
    
    Args:
        memory (Dict[str, Any]): The memory dictionary to update
        loop_id (str): The loop identifier
        failure_logs (str): The failure logs from the loop
        loop_context (Dict[str, Any]): Context information about the loop
        
    Returns:
        Dict[str, Any]: Updated memory dictionary
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Parse failure logs to identify root cause
    root_cause = parse_failure_logs(failure_logs)
    
    # Generate patch plan
    patch_plan = generate_patch_plan(root_cause, loop_context)
    
    # Initialize debugger_reports if it doesn't exist
    if "debugger_reports" not in updated_memory:
        updated_memory["debugger_reports"] = []
    
    # Create report
    timestamp = datetime.utcnow().isoformat()
    
    report = {
        "loop_id": loop_id,
        "timestamp": timestamp,
        "failure_type": root_cause["failure_type"],
        "details": root_cause["details"],
        "suggested_fix": patch_plan.get("suggested_fix", "Review and address the identified issues"),
        "patch_plan": {
            "steps": patch_plan["steps"],
            "confidence": patch_plan["confidence"]
        },
        "next_agent": patch_plan["next_agent"]
    }
    
    # Add report to debugger_reports
    updated_memory["debugger_reports"].append(report)
    
    # Update loop metadata if it exists
    if "loop_trace" in updated_memory and loop_id in updated_memory["loop_trace"]:
        if "failures" not in updated_memory["loop_trace"][loop_id]:
            updated_memory["loop_trace"][loop_id]["failures"] = []
        
        updated_memory["loop_trace"][loop_id]["failures"].append({
            "type": "debugger_report",
            "timestamp": timestamp,
            "details": report
        })
    
    return updated_memory

def debug_loop_failure(
    loop_id: str,
    failure_logs: str,
    memory: Dict[str, Any],
    loop_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Debugs a loop failure and injects a report into memory.
    
    Args:
        loop_id (str): The loop identifier
        failure_logs (str): The failure logs from the loop
        memory (Dict[str, Any]): The memory dictionary
        loop_context (Optional[Dict[str, Any]]): Context information about the loop
        
    Returns:
        Dict[str, Any]: Updated memory dictionary with debugger report
    """
    # Use empty context if none provided
    if loop_context is None:
        loop_context = {}
    
    # Inject debugger report into memory
    return inject_debugger_report(memory, loop_id, failure_logs, loop_context)
