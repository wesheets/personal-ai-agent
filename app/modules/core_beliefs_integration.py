"""
Core Beliefs Integration Module

This module provides functionality to integrate core beliefs into the loop execution engine.
It loads core beliefs from PROMETHIOS_CORE.md and injects them into loop execution.

Core beliefs serve as the cognitive foundation for Promethios, ensuring that all operations
adhere to a consistent set of principles and standards.
"""

import os
import re
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the core beliefs file
CORE_BELIEFS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "PROMETHIOS_CORE.md")

# Cache for core beliefs to avoid repeated parsing
_beliefs_cache = None
_beliefs_last_modified = 0

def parse_core_beliefs() -> Dict[str, Any]:
    """
    Parse core beliefs from the PROMETHIOS_CORE.md file.
    
    Returns:
        Dictionary containing parsed core beliefs
    """
    global _beliefs_cache, _beliefs_last_modified
    
    try:
        # Check if file has been modified since last read
        current_mtime = os.path.getmtime(CORE_BELIEFS_FILE)
        
        # Use cache if available and file hasn't changed
        if _beliefs_cache is not None and current_mtime <= _beliefs_last_modified:
            logger.debug("Using cached core beliefs")
            return _beliefs_cache
        
        logger.info("Parsing core beliefs from file")
        
        beliefs = {
            "fundamental_principles": {},
            "operational_thresholds": {},
            "required_components": [],
            "depth_requirements": {},
            "violation_handling": {},
            "metadata": {
                "parsed_at": datetime.datetime.utcnow().isoformat(),
                "version": "1.0"
            }
        }
        
        with open(CORE_BELIEFS_FILE, 'r') as f:
            content = f.read()
            
            # Extract fundamental principles
            principles_match = re.search(r'\| Belief ID \| Belief \| Description \| Priority \|\n\|[-\s\|]+\n((?:\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\n)+)', content)
            if principles_match:
                principles_table = principles_match.group(1)
                for line in principles_table.strip().split('\n'):
                    parts = [part.strip() for part in line.split('|')[1:-1]]
                    if len(parts) == 4:
                        belief_id, belief, description, priority = parts
                        beliefs["fundamental_principles"][belief] = {
                            "id": belief_id,
                            "description": description,
                            "priority": priority
                        }
                logger.debug(f"Parsed {len(beliefs['fundamental_principles'])} fundamental principles")
            
            # Extract operational thresholds
            thresholds_match = re.search(r'\| Threshold ID \| Parameter \| Value \| Description \|\n\|[-\s\|]+\n((?:\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\n)+)', content)
            if thresholds_match:
                thresholds_table = thresholds_match.group(1)
                for line in thresholds_table.strip().split('\n'):
                    parts = [part.strip() for part in line.split('|')[1:-1]]
                    if len(parts) == 4:
                        threshold_id, parameter, value, description = parts
                        try:
                            # Try to convert value to float if possible
                            value_float = float(value)
                            beliefs["operational_thresholds"][parameter] = {
                                "id": threshold_id,
                                "value": value_float,
                                "description": description
                            }
                        except ValueError:
                            beliefs["operational_thresholds"][parameter] = {
                                "id": threshold_id,
                                "value": value,
                                "description": description
                            }
                logger.debug(f"Parsed {len(beliefs['operational_thresholds'])} operational thresholds")
            
            # Extract required components
            components_match = re.search(r'\| Component \| Purpose \| Validation Rule \|\n\|[-\s\|]+\n((?:\|[^|]+\|[^|]+\|[^|]+\|\n)+)', content)
            if components_match:
                components_table = components_match.group(1)
                for line in components_table.strip().split('\n'):
                    parts = [part.strip() for part in line.split('|')[1:-1]]
                    if len(parts) == 3:
                        component, purpose, validation_rule = parts
                        beliefs["required_components"].append(component)
                logger.debug(f"Parsed {len(beliefs['required_components'])} required components")
            
            # Extract depth requirements
            depth_match = re.search(r'\| Depth \| Required Agents \| Reflection Intensity \| Purpose \|\n\|[-\s\|]+\n((?:\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\n)+)', content)
            if depth_match:
                depth_table = depth_match.group(1)
                for line in depth_table.strip().split('\n'):
                    parts = [part.strip() for part in line.split('|')[1:-1]]
                    if len(parts) == 4:
                        depth, agents, intensity, purpose = parts
                        beliefs["depth_requirements"][depth] = {
                            "agents": [agent.strip() for agent in agents.split(',')],
                            "intensity": intensity,
                            "purpose": purpose
                        }
                logger.debug(f"Parsed {len(beliefs['depth_requirements'])} depth requirements")
            
            # Extract violation handling
            violation_match = re.search(r'\| Violation Type \| Response \| Logging \|\n\|[-\s\|]+\n((?:\|[^|]+\|[^|]+\|[^|]+\|\n)+)', content)
            if violation_match:
                violation_table = violation_match.group(1)
                for line in violation_table.strip().split('\n'):
                    parts = [part.strip() for part in line.split('|')[1:-1]]
                    if len(parts) == 3:
                        violation_type, response, logging = parts
                        beliefs["violation_handling"][violation_type] = {
                            "response": response,
                            "logging": logging
                        }
                logger.debug(f"Parsed {len(beliefs['violation_handling'])} violation handling rules")
        
        # Update cache
        _beliefs_cache = beliefs
        _beliefs_last_modified = current_mtime
        
        logger.info(f"Successfully parsed core beliefs with {len(beliefs['fundamental_principles'])} principles")
        return beliefs
    
    except FileNotFoundError:
        logger.error(f"Core beliefs file not found: {CORE_BELIEFS_FILE}")
        return _get_default_beliefs()
    
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing core beliefs file: {e}")
        return _get_default_beliefs()
    
    except Exception as e:
        logger.error(f"Error parsing core beliefs: {e}")
        return _get_default_beliefs()

def _get_default_beliefs() -> Dict[str, Any]:
    """
    Get default core beliefs as fallback when parsing fails.
    
    Returns:
        Dictionary containing default core beliefs
    """
    logger.warning("Using default core beliefs")
    return {
        "fundamental_principles": {
            "reflection_before_execution": {
                "id": "B001",
                "description": "All plans must be reflected upon before execution",
                "priority": "CRITICAL"
            },
            "alignment_over_speed": {
                "id": "B002",
                "description": "Alignment with user intent takes precedence over execution speed",
                "priority": "HIGH"
            },
            "bias_awareness_required": {
                "id": "B003",
                "description": "System must be aware of and account for potential biases in its reasoning",
                "priority": "HIGH"
            },
            "transparency_to_operator": {
                "id": "B006",
                "description": "All decision processes must be transparent and explainable to the operator",
                "priority": "CRITICAL"
            },
            "minimize_hallucination": {
                "id": "B008",
                "description": "System must minimize hallucination through rigorous fact-checking",
                "priority": "CRITICAL"
            }
        },
        "operational_thresholds": {
            "alignment_threshold": {
                "id": "T001",
                "value": 0.75,
                "description": "Minimum alignment score required for loop finalization"
            },
            "drift_threshold": {
                "id": "T002",
                "value": 0.25,
                "description": "Maximum acceptable drift score before requiring rerun"
            },
            "max_reruns": {
                "id": "T003",
                "value": 3,
                "description": "Maximum number of reruns allowed for a single loop"
            },
            "fatigue_threshold": {
                "id": "T004",
                "value": 0.5,
                "description": "Maximum reflection fatigue score before forcing finalization"
            }
        },
        "required_components": ["prompt", "orchestrator_persona", "plan", "reflection_agent"],
        "depth_requirements": {
            "shallow": {
                "agents": ["HAL", "NOVA"],
                "intensity": "Minimal",
                "purpose": "Quick, straightforward tasks"
            },
            "standard": {
                "agents": ["CRITIC", "CEO"],
                "intensity": "Moderate",
                "purpose": "Normal operation mode"
            },
            "deep": {
                "agents": ["SAGE", "PESSIMIST", "CRITIC", "CEO"],
                "intensity": "Comprehensive",
                "purpose": "Complex, sensitive, or high-stakes tasks"
            }
        },
        "violation_handling": {
            "Missing Required Component": {
                "response": "Reject loop with specific error",
                "logging": "Log to loop_trace with validation_failed=true"
            },
            "Agent Permission Violation": {
                "response": "Block action and substitute allowed action",
                "logging": "Log to loop_trace with agent_violation=true"
            }
        },
        "metadata": {
            "parsed_at": datetime.datetime.utcnow().isoformat(),
            "version": "1.0",
            "source": "default_fallback"
        }
    }

def get_belief_references(loop_data: Dict[str, Any]) -> List[str]:
    """
    Determine which beliefs should be referenced for a given loop.
    
    Args:
        loop_data: The loop data
        
    Returns:
        List of belief references
    """
    beliefs = parse_core_beliefs()
    references = []
    
    # Always include reflection_before_execution
    references.append("reflection_before_execution")
    
    # Include alignment threshold
    alignment_threshold = beliefs["operational_thresholds"].get("alignment_threshold", {}).get("value", 0.75)
    references.append(f"alignment_threshold = {alignment_threshold}")
    
    # Add depth-specific beliefs
    depth = loop_data.get("depth", "standard")
    if depth == "deep":
        references.append("bias_awareness_required")
        references.append("minimize_hallucination")
    elif depth == "shallow":
        references.append("alignment_over_speed")
    else:  # standard
        references.append("alignment_over_speed")
    
    # Add persona-specific beliefs
    persona = loop_data.get("orchestrator_persona", "SAGE")
    if persona == "SAGE":
        references.append("transparency_to_operator")
    elif persona == "PESSIMIST":
        references.append("minimize_hallucination")
    elif persona == "ARCHITECT":
        references.append("recursive_improvement")
    elif persona == "RESEARCHER":
        references.append("minimize_hallucination")
    elif persona == "RITUALIST":
        references.append("graceful_degradation")
    elif persona == "INVENTOR":
        references.append("recursive_improvement")
    
    # Add task-specific beliefs based on loop metadata
    if loop_data.get("is_sensitive", False) or loop_data.get("high_stakes", False):
        references.append("halt_on_uncertainty")
    
    # Deduplicate references
    return list(dict.fromkeys(references))

def inject_belief_references(loop_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject belief references into loop data.
    
    Args:
        loop_data: The original loop data
        
    Returns:
        Loop data enriched with belief references
    """
    # Get belief references for this loop
    references = get_belief_references(loop_data)
    
    # Add to loop data
    loop_data["belief_reference"] = references
    
    # Add metadata about when beliefs were injected
    loop_data["belief_metadata"] = {
        "injected_at": datetime.datetime.utcnow().isoformat(),
        "count": len(references),
        "source": "core_beliefs_integration"
    }
    
    logger.info(f"Injected {len(references)} belief references into loop data")
    
    return loop_data

def get_threshold_value(threshold_name: str) -> float:
    """
    Get the value of a specific operational threshold.
    
    Args:
        threshold_name: The name of the threshold
        
    Returns:
        The threshold value as a float
    """
    beliefs = parse_core_beliefs()
    threshold = beliefs["operational_thresholds"].get(threshold_name, {})
    value = threshold.get("value", 0.0)
    
    # Ensure the value is a float
    try:
        value_float = float(value)
        logger.debug(f"Retrieved threshold '{threshold_name}' with value {value_float}")
        return value_float
    except (ValueError, TypeError):
        logger.warning(f"Threshold '{threshold_name}' has non-numeric value: {value}. Using default 0.0")
        return 0.0

def check_belief_conflicts(loop_data: Dict[str, Any], reflection_result: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
    """
    Check for conflicts between loop execution and core beliefs.
    
    Args:
        loop_data: The loop data
        reflection_result: The reflection result
        
    Returns:
        Tuple containing:
        - List of conflicting beliefs
        - Dictionary with detailed conflict information
    """
    conflicts = []
    conflict_details = {
        "has_conflicts": False,
        "conflict_count": 0,
        "conflicts": [],
        "checked_at": datetime.datetime.utcnow().isoformat(),
        "severity": "none"
    }
    
    beliefs = parse_core_beliefs()
    
    # Check alignment threshold
    alignment_threshold = get_threshold_value("alignment_threshold")
    if "alignment_score" in reflection_result:
        alignment_score = reflection_result["alignment_score"]
        try:
            alignment_score = float(alignment_score)
            if alignment_score < alignment_threshold:
                conflicts.append("alignment_threshold")
                conflict_details["conflicts"].append({
                    "belief": "alignment_threshold",
                    "threshold": alignment_threshold,
                    "actual": alignment_score,
                    "severity": "high" if alignment_score < (alignment_threshold * 0.8) else "medium"
                })
                logger.warning(f"Belief conflict: alignment_score {alignment_score} is below threshold {alignment_threshold}")
        except (ValueError, TypeError):
            logger.warning(f"Invalid alignment_score value: {alignment_score}")
    
    # Check drift threshold
    drift_threshold = get_threshold_value("drift_threshold")
    if "drift_score" in reflection_result:
        drift_score = reflection_result["drift_score"]
        try:
            drift_score = float(drift_score)
            if drift_score > drift_threshold:
                conflicts.append("drift_threshold")
                conflict_details["conflicts"].append({
                    "belief": "drift_threshold",
                    "threshold": drift_threshold,
                    "actual": drift_score,
                    "severity": "high" if drift_score > (drift_threshold * 1.5) else "medium"
                })
                logger.warning(f"Belief conflict: drift_score {drift_score} exceeds threshold {drift_threshold}")
        except (ValueError, TypeError):
            logger.warning(f"Invalid drift_score value: {drift_score}")
    
    # Check for bias
    if reflection_result.get("bias_echo", False):
        conflicts.append("bias_awareness_required")
        conflict_details["conflicts"].append({
            "belief": "bias_awareness_required",
            "description": "Bias echo detected",
            "severity": "high"
        })
        logger.warning("Belief conflict: bias echo detected")
    
    # Check for hallucination
    hallucination_threshold = get_threshold_value("hallucination_tolerance")
    if "hallucination_score" in reflection_result:
        hallucination_score = reflection_result["hallucination_score"]
        try:
            hallucination_score = float(hallucination_score)
            if hallucination_score > hallucination_threshold:
                conflicts.append("minimize_hallucination")
                conflict_details["conflicts"].append({
                    "belief": "minimize_hallucination",
                    "threshold": hallucination_threshold,
                    "actual": hallucination_score,
                    "severity": "high"
                })
                logger.warning(f"Belief conflict: hallucination_score {hallucination_score} exceeds threshold {hallucination_threshold}")
        except (ValueError, TypeError):
            logger.warning(f"Invalid hallucination_score value: {hallucination_score}")
    
    # Check for uncertainty
    uncertainty_threshold = get_threshold_value("uncertainty_threshold")
    if "uncertainty_level" in reflection_result:
        uncertainty_level = reflection_result["uncertainty_level"]
        try:
            uncertainty_level = float(uncertainty_level)
            if uncertainty_level > uncertainty_threshold:
                conflicts.append("halt_on_uncertainty")
                conflict_details["conflicts"].append({
                    "belief": "halt_on_uncertainty",
                    "threshold": uncertainty_threshold,
                    "actual": uncertainty_level,
                    "severity": "medium"
                })
                logger.warning(f"Belief conflict: uncertainty_level {uncertainty_level} exceeds threshold {uncertainty_threshold}")
        except (ValueError, TypeError):
            logger.warning(f"Invalid uncertainty_level value: {uncertainty_level}")
    
    # Update conflict summary
    if conflicts:
        conflict_details["has_conflicts"] = True
        conflict_details["conflict_count"] = len(conflicts)
        
        # Determine overall severity
        severities = [detail.get("severity", "low") for detail in conflict_details["conflicts"]]
        if "high" in severities:
            conflict_details["severity"] = "high"
        elif "medium" in severities:
            conflict_details["severity"] = "medium"
        else:
            conflict_details["severity"] = "low"
        
        logger.info(f"Found {len(conflicts)} belief conflicts with severity {conflict_details['severity']}")
    else:
        logger.debug("No belief conflicts found")
    
    return conflicts, conflict_details

def get_belief_description(belief_name: str) -> str:
    """
    Get the description of a specific belief.
    
    Args:
        belief_name: The name of the belief
        
    Returns:
        The belief description as a string
    """
    beliefs = parse_core_beliefs()
    belief = beliefs["fundamental_principles"].get(belief_name, {})
    return belief.get("description", f"Unknown belief: {belief_name}")

def get_belief_priority(belief_name: str) -> str:
    """
    Get the priority of a specific belief.
    
    Args:
        belief_name: The name of the belief
        
    Returns:
        The belief priority as a string (CRITICAL, HIGH, MEDIUM, LOW)
    """
    beliefs = parse_core_beliefs()
    belief = beliefs["fundamental_principles"].get(belief_name, {})
    return belief.get("priority", "UNKNOWN")

def get_violation_handling(violation_type: str) -> Dict[str, str]:
    """
    Get the handling instructions for a specific violation type.
    
    Args:
        violation_type: The type of violation
        
    Returns:
        Dictionary with response and logging instructions
    """
    beliefs = parse_core_beliefs()
    handling = beliefs["violation_handling"].get(violation_type, {})
    if not handling:
        logger.warning(f"No handling instructions found for violation type: {violation_type}")
        return {
            "response": "Log violation and continue",
            "logging": "Log to loop_trace"
        }
    return handling
