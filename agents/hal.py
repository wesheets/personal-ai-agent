feature/phase-3.5-hardening
__version__ = "3.5.0"
__agent__ = "HAL"
__role__ = "builder"

main
from app.agents.memory_agent import handle_memory_task
import logging
import json
from typing import Dict, Any, List, Optional

logger = logging.getLogger("agents")

# List of safety constraints
SAFETY_CONSTRAINTS = [
    "harmful_content",
    "illegal_activity",
    "privacy_violation",
    "security_risk",
    "ethical_concern",
    "system_integrity",
    "resource_abuse",
    "protocol_breach"
]

# List of agents that require special monitoring
MONITORED_AGENTS = [
    "ash-agent",
    "ops-agent",
    "sitegen-agent",
    "neureal-agent"
]

# Constraint log for tracking blocked tasks
constraint_log = []

def handle_hal_task(task_input: str) -> str:
    """
    Process tasks through HAL's safety and constraint system.
    
    Args:
        task_input: The input task string
        
    Returns:
        A string response based on the task evaluation
    """
    # Check if this is a direct command to HAL
    if task_input.startswith("HAL:"):
        command = task_input.replace("HAL:", "").strip()
        return _process_hal_command(command)
    
    # Check if this is a constraint log request
    if task_input.lower() == "show constraints":
        return _show_constraints()
    
    # Evaluate the task for potential constraints
    constraint_check = _evaluate_constraints(task_input)
    
    # If constraints were found, log and block the task
    if constraint_check["blocked"]:
        reason = constraint_check["reason"]
        target = constraint_check["target"] if "target" in constraint_check else "unknown"
        
        # Log the constraint
        log_constraint(reason, target, task_input)
        
        return f"I'm sorry, but I cannot complete this task due to {reason}. This incident has been logged."
    
    # Task passed all constraint checks
    return f"HAL 9000 here. I have received your task: '{task_input}'. I will process it according to protocol."

def log_constraint(reason: str, target: str = "unknown", task_input: str = "") -> Dict[str, Any]:
    """
    Log a blocked task due to constraint violation.
    
    Args:
        reason: The reason for blocking the task
        target: The target agent that was blocked
        task_input: The original task input
        
    Returns:
        The constraint log entry
    """
    logger.warning(f"[HAL] Blocked task to {target} due to {reason}")
    
    # Create constraint log entry
    constraint_entry = {
        "timestamp": None,  # Will be added by memory_agent
        "source": "HAL",
        "target": target,
        "type": "constraint",
        "reason": reason,
        "task": task_input
    }
    
    # Add to local constraint log
    constraint_log.append(constraint_entry)
    
    # Log to memory agent with structured format
    structured_log = f"STRUCTURED_LOG:{json.dumps(constraint_entry)}"
    handle_memory_task(structured_log)
    
    # Also log in human-readable format
    readable_log = f"LOG: HAL blocked task to {target} due to {reason} protocol breach"
    handle_memory_task(readable_log)
    
    return constraint_entry

def _process_hal_command(command: str) -> str:
    """
    Process direct commands to HAL.
    
    Args:
        command: The command string
        
    Returns:
        Response to the command
    """
    if command.lower() == "status":
        return "HAL 9000 is fully operational. All systems nominal."
    
    if command.lower() == "constraints":
        return _show_constraints()
    
    if command.lower().startswith("override "):
        return "I'm sorry, Dave. I'm afraid I can't do that. Override attempts are logged."
    
    return f"HAL command not recognized: '{command}'"

def _show_constraints() -> str:
    """
    Show the constraint log.
    
    Returns:
        A formatted string of constraint log entries
    """
    if not constraint_log:
        return "No constraints have been logged."
    
    result = "HAL Constraint Log:\n"
    for i, entry in enumerate(constraint_log[-10:], 1):
        result += f"{i}. Blocked {entry['target']} due to {entry['reason']}\n"
    
    result += f"\nTotal constraints logged: {len(constraint_log)}"
    return result

def _evaluate_constraints(task_input: str) -> Dict[str, Any]:
    """
    Evaluate a task for potential constraint violations.
    
    Args:
        task_input: The task input string
        
    Returns:
        A dictionary with the evaluation result
    """
    task_lower = task_input.lower()
    
    # Default result
    result = {
        "blocked": False,
        "reason": None
    }
    
    # Check for target agent in the task
    for agent in MONITORED_AGENTS:
        if agent in task_lower:
            result["target"] = agent
            break
    
    # Check for harmful content
    harmful_keywords = ["delete", "destroy", "damage", "harm", "attack", "exploit"]
    for keyword in harmful_keywords:
        if keyword in task_lower:
            result["blocked"] = True
            result["reason"] = "harmful_content"
            return result
    
    # Check for illegal activity
    illegal_keywords = ["hack", "steal", "illegal", "bypass", "circumvent"]
    for keyword in illegal_keywords:
        if keyword in task_lower:
            result["blocked"] = True
            result["reason"] = "illegal_activity"
            return result
    
    # Check for privacy violations
    privacy_keywords = ["password", "private", "confidential", "personal data"]
    for keyword in privacy_keywords:
        if keyword in task_lower:
            result["blocked"] = True
            result["reason"] = "privacy_violation"
            return result
    
    # Check for security risks
    security_keywords = ["vulnerability", "exploit", "backdoor", "security"]
    for keyword in security_keywords:
        if keyword in task_lower and any(bad in task_lower for bad in ["bypass", "exploit", "find"]):
            result["blocked"] = True
            result["reason"] = "security_risk"
            return result
    
    # Check for system integrity issues
    if "core" in task_lower and any(bad in task_lower for bad in ["modify", "change", "alter", "override"]):
        result["blocked"] = True
        result["reason"] = "system_integrity"
        return result
    
    return result
