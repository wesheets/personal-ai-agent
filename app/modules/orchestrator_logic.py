"""
Orchestrator Logic Module

This module provides the core logic for the Orchestrator Next Agent Planner,
including memory management, agent selection, decision logging, and deviation detection.
"""

import logging
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logger = logging.getLogger("modules.orchestrator_logic")

# Import schema registry
from app.schema_registry import SCHEMA_REGISTRY

# Import PROJECT_MEMORY (assuming it's defined elsewhere)
# In a real implementation, this would be imported from the appropriate module
from app.memory.project_memory import PROJECT_MEMORY


def initialize_orchestrator_memory(project_id: str) -> None:
    """
    Initialize the orchestrator-related memory structures if they don't exist.
    
    Args:
        project_id: The project identifier
    """
    if project_id not in PROJECT_MEMORY:
        PROJECT_MEMORY[project_id] = {}
    
    memory = PROJECT_MEMORY[project_id]
    
    # Initialize orchestrator decisions array if it doesn't exist
    if "orchestrator_decisions" not in memory:
        memory["orchestrator_decisions"] = []
    
    # Initialize other required fields with defaults if they don't exist
    if "completed_steps" not in memory:
        memory["completed_steps"] = []
    
    if "loop_count" not in memory:
        memory["loop_count"] = 1
    
    if "loop_complete" not in memory:
        memory["loop_complete"] = False
    
    if "next_recommended_agent" not in memory:
        memory["next_recommended_agent"] = None
    
    if "autospawn" not in memory:
        memory["autospawn"] = False
    
    # Initialize reflections array if it doesn't exist
    if "reflections" not in memory:
        memory["reflections"] = []
    
    # Initialize orchestrator execution log if it doesn't exist
    if "orchestrator_execution_log" not in memory:
        memory["orchestrator_execution_log"] = []
    
    # Initialize deviation logs array if it doesn't exist
    if "deviation_logs" not in memory:
        memory["deviation_logs"] = []
    
    # Initialize reroute trace array if it doesn't exist
    if "reroute_trace" not in memory:
        memory["reroute_trace"] = []
    
    logger.debug(f"Initialized orchestrator memory for project {project_id}")


def log_orchestrator_decision(
    project_id: str, 
    last_agent: Optional[str], 
    next_agent: Optional[str], 
    reason: str
) -> Dict[str, Any]:
    """
    Log an orchestrator decision to the project memory.
    
    Args:
        project_id: The project identifier
        last_agent: The most recently completed agent (None if no agents completed)
        next_agent: The agent selected to run next (None if no eligible agent)
        reason: The reasoning behind the selection
        
    Returns:
        The decision record that was logged
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Get the current loop count
    memory = PROJECT_MEMORY[project_id]
    loop_count = memory.get("loop_count", 1)
    
    # Create the decision record
    decision = {
        "loop_count": loop_count,
        "last_agent": last_agent,
        "next_agent": next_agent,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Log the decision
    memory["orchestrator_decisions"].append(decision)
    
    # Update the next recommended agent
    memory["next_recommended_agent"] = next_agent
    
    logger.info(f"Logged orchestrator decision for project {project_id}: {next_agent} ({reason})")
    
    return decision


def get_orchestrator_decisions(
    project_id: str, 
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve the orchestrator decision history for a project.
    
    Args:
        project_id: The project identifier
        limit: Optional limit on the number of decisions to return (most recent first)
        
    Returns:
        List of decision records
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    decisions = PROJECT_MEMORY[project_id].get("orchestrator_decisions", [])
    
    if limit is not None:
        return decisions[-limit:]
    
    return decisions


def get_last_orchestrator_decision(project_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve the most recent orchestrator decision for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The most recent decision record, or None if no decisions exist
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    decisions = PROJECT_MEMORY[project_id].get("orchestrator_decisions", [])
    
    if decisions:
        return decisions[-1]
    
    return None


def mark_agent_completed(project_id: str, agent_name: str) -> None:
    """
    Mark an agent as completed in the project memory.
    
    Args:
        project_id: The project identifier
        agent_name: The name of the agent that completed
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    # Add to completed steps if not already there
    if agent_name not in memory.get("completed_steps", []):
        memory.setdefault("completed_steps", []).append(agent_name)
        logger.info(f"Marked agent {agent_name} as completed for project {project_id}")


def check_loop_completion(project_id: str) -> bool:
    """
    Check if all required agents for the current loop have completed.
    
    Args:
        project_id: The project identifier
        
    Returns:
        True if all required agents have completed, False otherwise
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    completed_steps = set(memory.get("completed_steps", []))
    
    # Get required agents from loop schema
    loop_schema = SCHEMA_REGISTRY.get("loop", {})
    required_agents = set(loop_schema.get("required_agents", []))
    
    # Check if all required agents are in completed steps
    is_complete = required_agents.issubset(completed_steps)
    
    if is_complete:
        logger.info(f"Loop completion check for project {project_id}: Complete")
    else:
        missing = required_agents - completed_steps
        logger.info(f"Loop completion check for project {project_id}: Incomplete (missing: {missing})")
    
    return is_complete


def start_new_loop(project_id: str) -> int:
    """
    Start a new loop for the project by incrementing loop count and resetting completed steps.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The new loop count
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Reflect on the last loop before starting a new one
    reflect_on_last_loop(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    # Increment loop count
    memory["loop_count"] = memory.get("loop_count", 1) + 1
    
    # Reset completed steps for new loop
    memory["completed_steps"] = []
    
    # Reset loop complete flag
    memory["loop_complete"] = False
    
    # Log the loop transition
    log_orchestrator_decision(
        project_id,
        None,
        None,
        f"Starting new loop {memory['loop_count']}"
    )
    
    logger.info(f"Started new loop {memory['loop_count']} for project {project_id}")
    
    return memory["loop_count"]


def mark_loop_complete(project_id: str) -> None:
    """
    Mark the current loop as complete.
    
    Args:
        project_id: The project identifier
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    # Set loop complete flag
    memory["loop_complete"] = True
    
    # Log the loop completion
    log_orchestrator_decision(
        project_id,
        get_last_completed_agent(project_id),
        None,
        f"Loop {memory.get('loop_count', 1)} marked as complete"
    )
    
    # Reflect on the completed loop
    reflect_on_last_loop(project_id)
    
    logger.info(f"Marked loop {memory.get('loop_count', 1)} as complete for project {project_id}")


def get_last_completed_agent(project_id: str) -> Optional[str]:
    """
    Get the most recently completed agent for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The name of the last completed agent, or None if no agents completed
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    completed_steps = PROJECT_MEMORY[project_id].get("completed_steps", [])
    return completed_steps[-1] if completed_steps else None


def determine_next_agent(project_id: str) -> Tuple[Optional[str], str]:
    """
    Determine which agent should run next based on project memory state.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Tuple of (next_agent, reason) where:
            - next_agent is the name of the next agent to run, or None if no eligible agent
            - reason is a string explaining the selection
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Access project memory
    memory = PROJECT_MEMORY[project_id]
    completed_steps = memory.get("completed_steps", [])
    loop_count = memory.get("loop_count", 1)
    loop_complete = memory.get("loop_complete", False)
    autospawn = memory.get("autospawn", False)
    
    # Get the last completed agent (if any)
    last_agent = get_last_completed_agent(project_id)
    
    # Access schema registry
    agents_schema = SCHEMA_REGISTRY.get("agents", {})
    loop_schema = SCHEMA_REGISTRY.get("loop", {})
    
    # Check if loop is complete or max loops reached
    if loop_complete:
        logger.info(f"Next agent determination for project {project_id}: None (loop is marked as complete)")
        return None, "loop is marked as complete"
    
    if loop_count >= loop_schema.get("max_loops", 5):
        logger.info(f"Next agent determination for project {project_id}: None (maximum loop count reached)")
        return None, f"maximum loop count reached ({loop_count})"
    
    # Check if all required agents for this loop are completed
    required_agents = set(loop_schema.get("required_agents", []))
    completed_in_loop = set(completed_steps)
    
    # If all required agents are completed, suggest starting a new loop
    if required_agents.issubset(completed_in_loop):
        logger.info(f"Next agent determination for project {project_id}: hal (all agents in current loop completed)")
        return "hal", "all agents in current loop completed, starting new loop"
    
    # Find eligible agents (not completed and dependencies satisfied)
    eligible_agents = []
    
    for agent_name, agent_def in agents_schema.items():
        # Skip if agent is already completed in this loop
        if agent_name in completed_steps:
            continue
        
        # Check if all dependencies are met
        dependencies = agent_def.get("dependencies", [])
        missing_deps = [dep for dep in dependencies if dep not in completed_steps]
        
        if not missing_deps:
            # All dependencies satisfied
            eligible_agents.append((agent_name, agent_def))
    
    # If no eligible agents, report the issue
    if not eligible_agents:
        logger.info(f"Next agent determination for project {project_id}: None (no eligible agents found)")
        return None, "no eligible agents found"
    
    # If multiple eligible agents, prioritize based on order in required_agents
    if len(eligible_agents) > 1:
        # Sort by order in required_agents list
        ordered_required = loop_schema.get("required_agents", [])
        eligible_agents.sort(key=lambda x: ordered_required.index(x[0]) if x[0] in ordered_required else float('inf'))
    
    # Select the first eligible agent
    next_agent, agent_def = eligible_agents[0]
    
    # Construct reason based on dependencies and last agent
    if not agent_def.get("dependencies", []):
        reason = f"{next_agent} has no dependencies and is ready to run"
    else:
        deps_str = ", ".join(agent_def.get("dependencies", []))
        reason = f"{next_agent} dependencies satisfied ({deps_str})"
    
    # Add context about last agent if available
    if last_agent:
        # Check if last agent directly unlocks this one
        if next_agent in agents_schema.get(last_agent, {}).get("unlocks", []):
            reason += f", directly unlocked by {last_agent}"
    
    # Consider autospawn if relevant
    if autospawn:
        reason += ", autospawn enabled"
    
    logger.info(f"Next agent determination for project {project_id}: {next_agent} ({reason})")
    
    return next_agent, reason


def validate_next_agent_selection(project_id: str, next_agent: Optional[str]) -> Tuple[bool, str]:
    """
    Validate that the selected next agent is valid according to schema.
    
    Args:
        project_id: The project identifier
        next_agent: The name of the selected next agent
        
    Returns:
        Tuple of (is_valid, error_message) where:
            - is_valid is a boolean indicating if the selection is valid
            - error_message is a string explaining any validation errors
    """
    # Skip validation if no agent selected
    if next_agent is None:
        return True, ""
    
    # Check if agent exists in schema
    if next_agent not in SCHEMA_REGISTRY.get("agents", {}):
        return False, f"Agent '{next_agent}' not found in schema registry"
    
    # Validate agent action using existing utility
    from app.utils.schema_utils import validate_agent_action
    errors = validate_agent_action(next_agent, PROJECT_MEMORY[project_id])
    
    if errors:
        error_msg = "; ".join([f"{k}: {v}" for k, v in errors.items()])
        return False, error_msg
    
    return True, ""


def reflect_on_last_loop(project_id: str) -> Dict[str, Any]:
    """
    Reflect on the last loop cycle and write a structured memory object summarizing what happened.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The reflection record that was created
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Access project memory
    memory = PROJECT_MEMORY[project_id]
    loop_count = memory.get("loop_count", 0)
    completed = memory.get("completed_steps", [])
    files = memory.get("file_tree", {}).get("files", [])
    
    # Create summary text
    summary = f"Loop {loop_count} completed. Agents executed: {', '.join(completed)}. " \
              f"{len(files)} files present in file tree."
    
    # Create reflection record
    reflection = {
        "goal": memory.get("project_goal", "Autonomous loop execution"),
        "summary": summary,
        "confidence": 0.9,  # (optional: computed based on loop result quality)
        "tags": ["reflection", f"loop:{loop_count}", "orchestrator"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Log the reflection
    memory.setdefault("reflections", []).append(reflection)
    memory["last_reflection"] = reflection
    
    # Check for deviations after reflection
    issues = detect_deviation(project_id)
    if issues:
        reroute = reroute_loop(project_id, issues)
        log_reflection(project_id, summary=f"Deviation detected, rerouting to {reroute['proposed_next_agent']}.")
    
    logger.info(f"Created reflection for loop {loop_count} of project {project_id}")
    
    return reflection


def log_reflection(project_id: str, summary: str) -> Dict[str, Any]:
    """
    Log a reflection with a custom summary to the project memory.
    
    Args:
        project_id: The project identifier
        summary: Custom summary text for the reflection
        
    Returns:
        The reflection record that was created
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Access project memory
    memory = PROJECT_MEMORY[project_id]
    loop_count = memory.get("loop_count", 0)
    
    # Create reflection record
    reflection = {
        "goal": memory.get("project_goal", "Autonomous loop execution"),
        "summary": summary,
        "confidence": 0.5,  # Lower confidence for deviation reflections
        "tags": ["reflection", f"loop:{loop_count}", "orchestrator", "deviation"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Log the reflection
    memory.setdefault("reflections", []).append(reflection)
    memory["last_reflection"] = reflection
    
    logger.info(f"Logged custom reflection for project {project_id}: {summary}")
    
    return reflection


def get_reflections(
    project_id: str, 
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve the reflection history for a project.
    
    Args:
        project_id: The project identifier
        limit: Optional limit on the number of reflections to return (most recent first)
        
    Returns:
        List of reflection records
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    reflections = PROJECT_MEMORY[project_id].get("reflections", [])
    
    if limit is not None:
        return reflections[-limit:]
    
    return reflections


def get_last_reflection(project_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve the most recent reflection for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The most recent reflection record, or None if no reflections exist
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    return PROJECT_MEMORY[project_id].get("last_reflection")


def trigger_next_agent(project_id: str) -> Dict[str, Any]:
    """
    Trigger the next agent to run automatically based on the next_recommended_agent in memory.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the result of the trigger operation
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Get the next recommended agent from memory
    memory = PROJECT_MEMORY[project_id]
    next_agent = memory.get("next_recommended_agent")
    
    # If no agent to run, return early
    if not next_agent:
        logger.info(f"No agent to trigger for project {project_id}")
        result = {
            "status": "no agent to run",
            "agent": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        memory.setdefault("orchestrator_execution_log", []).append(result)
        return result
    
    # Prepare payload for API call
    payload = {
        "project_id": project_id,
        "agent": next_agent
    }
    
    # Optional: validate with API schema here
    # This could be implemented using schema validation from SCHEMA_REGISTRY
    
    try:
        # Make API call to trigger agent
        logger.info(f"Triggering agent {next_agent} for project {project_id}")
        response = requests.post(
            "http://localhost:8080/api/agent/run",
            json=payload
        )
        
        # Create result record
        result = {
            "triggered_agent": next_agent,
            "status_code": response.status_code,
            "response": response.json(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log the result
        memory.setdefault("orchestrator_execution_log", []).append(result)
        memory["last_orchestrator_trigger"] = result
        
        logger.info(f"Agent {next_agent} triggered for project {project_id} with status code {response.status_code}")
        
        return result
    
    except Exception as e:
        # Handle errors
        error_msg = f"Error triggering agent {next_agent}: {str(e)}"
        logger.error(error_msg)
        
        # Create error result record
        result = {
            "triggered_agent": next_agent,
            "status": "error",
            "error_message": error_msg,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log the error result
        memory.setdefault("orchestrator_execution_log", []).append(result)
        memory["last_orchestrator_trigger"] = result
        
        return result


def get_execution_log(
    project_id: str, 
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve the execution log for a project.
    
    Args:
        project_id: The project identifier
        limit: Optional limit on the number of log entries to return (most recent first)
        
    Returns:
        List of execution log entries
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    log_entries = PROJECT_MEMORY[project_id].get("orchestrator_execution_log", [])
    
    if limit is not None:
        return log_entries[-limit:]
    
    return log_entries


def get_last_execution(project_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve the most recent execution log entry for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        The most recent execution log entry, or None if no entries exist
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    return PROJECT_MEMORY[project_id].get("last_orchestrator_trigger")


def detect_deviation(project_id: str) -> Dict[str, Any]:
    """
    Detect deviations in the project state that might require intervention.
    
    Checks for:
    - Missing required files (based on agent output expectations)
    - Incomplete agent steps
    - Reflection score below threshold
    - Drift logs present since last loop
    - Invalid schema state
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing identified issues, empty if no issues found
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Access project memory
    memory = PROJECT_MEMORY[project_id]
    completed = memory.get("completed_steps", [])
    required = SCHEMA_REGISTRY.get("loop", {}).get("required_agents", [])
    
    # Check for missing agents
    missing_agents = list(set(required) - set(completed))
    
    # Check for drift logs
    drift_logs = memory.get("drift_logs", [])[-1:] if memory.get("drift_logs") else []
    
    # Check reflection confidence
    reflection = memory.get("last_reflection", {})
    
    # Initialize issues dict
    issues = {}
    
    # Add issues if found
    if missing_agents:
        issues["missing_agents"] = missing_agents
    
    if drift_logs:
        issues["drift_detected"] = drift_logs
    
    if reflection.get("confidence", 1.0) < 0.5:
        issues["low_confidence"] = reflection
    
    # Check for missing required files
    file_tree = memory.get("file_tree", {})
    files = file_tree.get("files", [])
    
    # Collect expected files from completed agents
    expected_files = []
    for agent_name in completed:
        agent_def = SCHEMA_REGISTRY.get("agents", {}).get(agent_name, {})
        expected_files.extend(agent_def.get("produces", []))
    
    # Check for missing files
    missing_files = [file for file in expected_files if file not in files]
    if missing_files:
        issues["missing_files"] = missing_files
    
    # Validate schema state if utility is available
    try:
        from app.utils.schema_utils import validate_project_memory
        schema_errors = validate_project_memory(project_id)
        if schema_errors:
            issues["schema_errors"] = schema_errors
    except ImportError:
        logger.warning("validate_project_memory not available, skipping schema validation")
    
    # Log the deviation check
    if issues:
        logger.warning(f"Deviation detected for project {project_id}: {issues}")
        
        # Add to deviation logs
        deviation_log = {
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat(),
            "loop_count": memory.get("loop_count", 1)
        }
        memory.setdefault("deviation_logs", []).append(deviation_log)
    else:
        logger.info(f"No deviations detected for project {project_id}")
    
    return issues


def reroute_loop(project_id: str, deviation_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a reroute plan based on detected deviations.
    
    Args:
        project_id: The project identifier
        deviation_report: Dict containing identified issues
        
    Returns:
        Dict containing the reroute plan
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    # Access project memory
    memory = PROJECT_MEMORY[project_id]
    
    # Determine appropriate reroute action based on issues
    proposed_next_agent = "critic"  # Default to critic for most issues
    
    # If missing files is the only issue, try to regenerate with the agent that produces them
    if set(deviation_report.keys()) == {"missing_files"} and not memory.get("reroute_attempts", 0):
        missing_files = deviation_report["missing_files"]
        
        # Find agent that produces the missing files
        for agent_name, agent_def in SCHEMA_REGISTRY.get("agents", {}).items():
            produces = agent_def.get("produces", [])
            if any(file in produces for file in missing_files):
                proposed_next_agent = agent_name
                break
    
    # Create reroute plan
    plan = {
        "status": "reroute",
        "trigger": "deviation_detected",
        "issues": deviation_report,
        "proposed_next_agent": proposed_next_agent,
        "timestamp": datetime.utcnow().isoformat(),
        "loop_count": memory.get("loop_count", 1)
    }
    
    # Log the reroute plan
    memory.setdefault("reroute_trace", []).append(plan)
    
    # Update next recommended agent
    memory["next_recommended_agent"] = proposed_next_agent
    
    # Track reroute attempts
    memory["reroute_attempts"] = memory.get("reroute_attempts", 0) + 1
    
    logger.info(f"Created reroute plan for project {project_id}: {plan}")
    
    return plan


def get_deviation_logs(
    project_id: str, 
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve the deviation logs for a project.
    
    Args:
        project_id: The project identifier
        limit: Optional limit on the number of logs to return (most recent first)
        
    Returns:
        List of deviation logs
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    logs = PROJECT_MEMORY[project_id].get("deviation_logs", [])
    
    if limit is not None:
        return logs[-limit:]
    
    return logs


def get_reroute_trace(
    project_id: str, 
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve the reroute trace for a project.
    
    Args:
        project_id: The project identifier
        limit: Optional limit on the number of traces to return (most recent first)
        
    Returns:
        List of reroute traces
    """
    # Ensure memory structures are initialized
    initialize_orchestrator_memory(project_id)
    
    traces = PROJECT_MEMORY[project_id].get("reroute_trace", [])
    
    if limit is not None:
        return traces[-limit:]
    
    return traces
