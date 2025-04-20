"""
Orchestrator Logic Module

This module provides the core logic for the Orchestrator Next Agent Planner,
including memory management, agent selection, and decision logging.
"""

import logging
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
    
    logger.info(f"Created reflection for loop {loop_count} of project {project_id}")
    
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
