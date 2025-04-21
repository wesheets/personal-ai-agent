"""
Reflection Depth Controller Module

This module controls the reflection depth for loops based on specified depth level.
It determines which agents should be involved in the reflection process and
adjusts the reflection intensity accordingly.

Depth levels:
- shallow: Minimal reflection with HAL and NOVA only
- standard: Moderate reflection with CRITIC and CEO
- deep: Comprehensive reflection with SAGE, PESSIMIST, CRITIC, and CEO
"""

import os
import re
import datetime
from typing import Dict, List, Any, Optional, Set

# Path to the core beliefs file
CORE_BELIEFS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "PROMETHIOS_CORE.md")

def load_depth_requirements() -> Dict[str, Dict[str, Any]]:
    """
    Load depth requirements from PROMETHIOS_CORE.md.
    
    Returns:
        Dictionary mapping depth levels to their requirements
    """
    # Default depth levels in case parsing fails
    default_depth_levels = {
        "shallow": {
            "agents": ["HAL", "NOVA"],
            "description": "Quick, straightforward tasks",
            "alignment_check": True,
            "bias_check": False,
            "drift_review": False,
            "max_reflection_time": 30  # Added for test compatibility
        },
        "standard": {
            "agents": ["CRITIC", "CEO"],
            "description": "Moderate reflection for normal operation",
            "alignment_check": True,
            "bias_check": True,
            "drift_review": False,
            "max_reflection_time": 60
        },
        "deep": {
            "agents": ["SAGE", "PESSIMIST", "CRITIC", "CEO"],
            "description": "Comprehensive reflection for complex or sensitive tasks",
            "alignment_check": True,
            "bias_check": True,
            "drift_review": True,
            "max_reflection_time": 120
        }
    }
    
    try:
        with open(CORE_BELIEFS_FILE, 'r') as f:
            content = f.read()
            
            # Extract depth requirements
            depth_match = re.search(r'\| Depth \| Required Agents \| Reflection Intensity \| Purpose \|\n\|[-\s\|]+\n((?:\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\n)+)', content)
            if depth_match:
                depth_table = depth_match.group(1)
                depth_levels = {}
                
                for line in depth_table.strip().split('\n'):
                    parts = [part.strip() for part in line.split('|')[1:-1]]
                    if len(parts) == 4:
                        depth, agents, intensity, purpose = parts
                        agent_list = [agent.strip() for agent in agents.split(',')]
                        
                        # Determine checks based on intensity
                        alignment_check = True  # Always true for all depths
                        bias_check = "bias" in intensity.lower() or depth == "deep"
                        drift_review = "comprehensive" in intensity.lower() or "full drift" in intensity.lower()
                        
                        # Determine max reflection time based on depth
                        if depth == "shallow":
                            max_reflection_time = 30
                        elif depth == "standard":
                            max_reflection_time = 60
                        else:  # deep
                            max_reflection_time = 120
                        
                        depth_levels[depth] = {
                            "agents": agent_list,
                            "description": purpose,
                            "intensity": intensity,
                            "alignment_check": alignment_check,
                            "bias_check": bias_check,
                            "drift_review": drift_review,
                            "max_reflection_time": max_reflection_time
                        }
                
                if depth_levels:
                    return depth_levels
        
        # If we reach here, either the file couldn't be read or the pattern wasn't found
        return default_depth_levels
    
    except Exception as e:
        print(f"Error loading depth requirements: {e}")
        return default_depth_levels

# Load depth levels from PROMETHIOS_CORE.md
DEPTH_LEVELS = load_depth_requirements()

# Mapping from orchestrator modes to depth levels
MODE_TO_DEPTH = {
    "fast": "shallow",
    "balanced": "standard",
    "thorough": "deep",
    "research": "deep"  # Research uses deep depth with additional settings
}

def get_depth_for_mode(mode: str) -> str:
    """
    Get the corresponding depth level for a specific orchestrator mode.
    
    Args:
        mode: The orchestrator mode (fast, balanced, thorough, research)
        
    Returns:
        Corresponding depth level (shallow, standard, deep)
    """
    mode = mode.lower()
    if mode in MODE_TO_DEPTH:
        return MODE_TO_DEPTH[mode]
    else:
        print(f"Warning: Unknown mode '{mode}', defaulting to 'standard' depth")
        return "standard"

def get_agents_for_depth(depth: str) -> List[str]:
    """
    Get the list of agents required for a specific depth level.
    
    Args:
        depth: The depth level (shallow, standard, or deep)
        
    Returns:
        List of agent names required for the specified depth
    """
    if depth not in DEPTH_LEVELS:
        # Default to standard if unknown depth is provided
        depth = "standard"
    
    return DEPTH_LEVELS[depth]["agents"]

def get_agents_for_mode(mode: str) -> List[str]:
    """
    Get the list of agents required for a specific orchestrator mode.
    
    Args:
        mode: The orchestrator mode (fast, balanced, thorough, research)
        
    Returns:
        List of agent names required for the specified mode
    """
    depth = get_depth_for_mode(mode)
    return get_agents_for_depth(depth)

def get_reflection_config(depth: str) -> Dict[str, Any]:
    """
    Get the reflection configuration for a specific depth level.
    
    Args:
        depth: The depth level (shallow, standard, or deep)
        
    Returns:
        Dictionary with reflection configuration
    """
    if depth not in DEPTH_LEVELS:
        # Default to standard if unknown depth is provided
        depth = "standard"
    
    return DEPTH_LEVELS[depth]

def get_reflection_config_for_mode(mode: str) -> Dict[str, Any]:
    """
    Get the reflection configuration for a specific orchestrator mode.
    
    Args:
        mode: The orchestrator mode (fast, balanced, thorough, research)
        
    Returns:
        Dictionary with reflection configuration
    """
    depth = get_depth_for_mode(mode)
    return get_reflection_config(depth)

def adjust_agent_plan(agent_plan: List[Dict[str, Any]], depth: str) -> List[Dict[str, Any]]:
    """
    Adjust an agent plan based on the specified depth level.
    
    Args:
        agent_plan: The original agent plan
        depth: The depth level (shallow, standard, or deep)
        
    Returns:
        Adjusted agent plan with only the agents required for the specified depth
    """
    required_agents = set(get_agents_for_depth(depth))
    adjusted_plan = []
    
    for agent_step in agent_plan:
        agent_name = agent_step.get("agent")
        if agent_name in required_agents:
            adjusted_plan.append(agent_step)
            # Add depth information to the step
            agent_step["depth"] = depth
            agent_step["reflection_intensity"] = DEPTH_LEVELS[depth].get("intensity", "")
    
    return adjusted_plan

def adjust_agent_plan_for_mode(agent_plan: List[Dict[str, Any]], mode: str) -> List[Dict[str, Any]]:
    """
    Adjust an agent plan based on the specified orchestrator mode.
    
    Args:
        agent_plan: The original agent plan
        mode: The orchestrator mode (fast, balanced, thorough, research)
        
    Returns:
        Adjusted agent plan with only the agents required for the specified mode
    """
    depth = get_depth_for_mode(mode)
    adjusted_plan = adjust_agent_plan(agent_plan, depth)
    
    # Add mode information to each step
    for agent_step in adjusted_plan:
        agent_step["mode"] = mode
    
    # Apply mode-specific adjustments
    if mode == "fast":
        # For fast mode, further optimize by removing optional reflection steps
        essential_agents = ["HAL", "NOVA", "CEO"]
        adjusted_plan = [step for step in adjusted_plan if step.get("agent") in essential_agents]
    
    elif mode == "research":
        # For research mode, add additional exploration steps
        for step in adjusted_plan:
            step["exploration_enabled"] = True
            step["uncertainty_tracking"] = True
    
    return adjusted_plan

def enrich_loop_with_depth(loop_data: Dict[str, Any], depth: Optional[str] = None) -> Dict[str, Any]:
    """
    Enrich loop data with depth-specific information.
    
    Args:
        loop_data: The original loop data
        depth: Optional depth override (if not provided, uses depth from loop_data or defaults to standard)
        
    Returns:
        Enriched loop data with depth-specific information
    """
    # Use provided depth, or get from loop_data, or default to standard
    if depth is None:
        depth = loop_data.get("depth", "standard")
    
    # Ensure depth is valid
    if depth not in DEPTH_LEVELS:
        depth = "standard"
    
    # Update loop data with depth information
    loop_data["depth"] = depth
    loop_data["reflection_agents"] = get_agents_for_depth(depth)
    loop_data["reflection_config"] = get_reflection_config(depth)
    
    # Add belief references related to depth
    if "belief_reference" not in loop_data:
        loop_data["belief_reference"] = []
    
    # Add depth-specific beliefs based on configuration
    if DEPTH_LEVELS[depth].get("bias_check", False):
        if "bias_awareness_required" not in loop_data["belief_reference"]:
            loop_data["belief_reference"].append("bias_awareness_required")
    
    if depth == "shallow" and "alignment_over_speed" not in loop_data["belief_reference"]:
        loop_data["belief_reference"].append("alignment_over_speed")
    
    # Add depth metadata
    loop_data["depth_metadata"] = {
        "set_at": datetime.datetime.utcnow().isoformat(),
        "description": DEPTH_LEVELS[depth].get("description", ""),
        "intensity": DEPTH_LEVELS[depth].get("intensity", ""),
        "alignment_check": DEPTH_LEVELS[depth].get("alignment_check", True),
        "bias_check": DEPTH_LEVELS[depth].get("bias_check", False),
        "drift_review": DEPTH_LEVELS[depth].get("drift_review", False),
        "max_reflection_time": DEPTH_LEVELS[depth].get("max_reflection_time", 60)
    }
    
    return loop_data

def enrich_loop_with_mode(loop_data: Dict[str, Any], mode: Optional[str] = None) -> Dict[str, Any]:
    """
    Enrich loop data with mode-specific information.
    
    Args:
        loop_data: The original loop data
        mode: Optional mode override (if not provided, uses mode from loop_data or defaults to balanced)
        
    Returns:
        Enriched loop data with mode-specific information
    """
    # Use provided mode, or get from loop_data, or default to balanced
    if mode is None:
        mode = loop_data.get("mode", "balanced")
    
    # Ensure mode is valid
    mode = mode.lower()
    if mode not in MODE_TO_DEPTH:
        mode = "balanced"
    
    # Get corresponding depth for this mode
    depth = get_depth_for_mode(mode)
    
    # Update loop data with mode information
    loop_data["mode"] = mode
    
    # Add mode metadata
    loop_data["mode_metadata"] = {
        "set_at": datetime.datetime.utcnow().isoformat(),
        "mode": mode,
        "corresponding_depth": depth
    }
    
    # Now enrich with corresponding depth information
    loop_data = enrich_loop_with_depth(loop_data, depth)
    
    return loop_data

def preload_depth_for_rerun(original_loop_data: Dict[str, Any], rerun_reason: str) -> str:
    """
    Determine appropriate depth for a loop rerun based on the original loop and rerun reason.
    
    Args:
        original_loop_data: The original loop data
        rerun_reason: The reason for the rerun
        
    Returns:
        Appropriate depth level for the rerun
    """
    original_depth = original_loop_data.get("depth", "standard")
    
    # If original was already deep, stay deep
    if original_depth == "deep":
        return "deep"
    
    # Define escalation triggers based on rerun reasons
    escalation_triggers = [
        "alignment_threshold_not_met",
        "bias_detected", 
        "hallucination_detected",
        "drift_threshold_exceeded",
        "belief_conflict",
        "permission_violation",
        "tone_mismatch"
    ]
    
    # Escalate to deep for trigger reasons
    if rerun_reason in escalation_triggers:
        return "deep"
    
    # Escalate standard to deep for drift issues
    if original_depth == "standard" and "drift" in rerun_reason.lower():
        return "deep"
    
    # Otherwise, maintain the original depth
    return original_depth

def preload_mode_for_rerun(original_loop_data: Dict[str, Any], rerun_reason: str) -> str:
    """
    Determine appropriate mode for a loop rerun based on the original loop and rerun reason.
    
    Args:
        original_loop_data: The original loop data
        rerun_reason: The reason for the rerun
        
    Returns:
        Appropriate orchestrator mode for the rerun
    """
    original_mode = original_loop_data.get("mode", "balanced")
    
    # If original was already thorough or research, maintain that mode
    if original_mode in ["thorough", "research"]:
        return original_mode
    
    # Define escalation triggers based on rerun reasons
    escalation_triggers = [
        "alignment_threshold_not_met",
        "bias_detected", 
        "hallucination_detected",
        "drift_threshold_exceeded",
        "belief_conflict",
        "permission_violation",
        "tone_mismatch",
        "safety_violation",
        "uncertainty_high"
    ]
    
    # Escalate to thorough for trigger reasons
    if rerun_reason in escalation_triggers:
        return "thorough"
    
    # Escalate to research for specific research-related issues
    research_triggers = [
        "citation_needed",
        "source_verification_failed",
        "uncertainty_critical",
        "exploration_required",
        "divergence_detected"
    ]
    
    if rerun_reason in research_triggers:
        return "research"
    
    # Escalate balanced to thorough for drift issues
    if original_mode == "balanced" and "drift" in rerun_reason.lower():
        return "thorough"
    
    # Otherwise, maintain the original mode
    return original_mode

def get_depth_description(depth: str) -> str:
    """
    Get a human-readable description of a depth level.
    
    Args:
        depth: The depth level (shallow, standard, or deep)
        
    Returns:
        Description of the depth level
    """
    if depth not in DEPTH_LEVELS:
        depth = "standard"
    
    return DEPTH_LEVELS[depth].get("description", "Unknown depth level")

def get_required_beliefs_for_depth(depth: str) -> List[str]:
    """
    Get the list of core beliefs that should be referenced for a specific depth level.
    
    Args:
        depth: The depth level (shallow, standard, or deep)
        
    Returns:
        List of belief references for the specified depth
    """
    beliefs = ["reflection_before_execution"]  # Always include this one
    
    if depth == "deep":
        beliefs.extend(["bias_awareness_required", "minimize_hallucination"])
    elif depth == "standard":
        beliefs.append("alignment_over_speed")
    elif depth == "shallow":
        beliefs.append("alignment_over_speed")
    
    return beliefs

def get_required_beliefs_for_mode(mode: str) -> List[str]:
    """
    Get the list of core beliefs that should be referenced for a specific orchestrator mode.
    
    Args:
        mode: The orchestrator mode (fast, balanced, thorough, research)
        
    Returns:
        List of belief references for the specified mode
    """
    depth = get_depth_for_mode(mode)
    beliefs = get_required_beliefs_for_depth(depth)
    
    # Add mode-specific beliefs
    if mode == "research":
        beliefs.extend(["citation_required", "uncertainty_awareness"])
    elif mode == "thorough":
        beliefs.append("comprehensive_validation")
    elif mode == "fast":
        beliefs.append("efficiency_with_safety")
    
    return beliefs
