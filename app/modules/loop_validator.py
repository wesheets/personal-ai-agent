"""
Loop Validator Module

This module provides functionality to validate loop structures before execution.
It ensures that every loop meets the minimum requirements defined in PROMETHIOS_CORE.md.

The validator checks for:
1. Presence of required components (prompt, orchestrator_persona, plan, reflection_agent)
2. Validity of orchestrator_persona
3. Minimum plan steps
4. Appropriate reflection agents based on depth

If validation fails, the loop is rejected with a specific reason.
"""

import json
import os
import re
import datetime
from typing import Dict, List, Any, Optional, Tuple

# Path to the core beliefs file
CORE_BELIEFS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "PROMETHIOS_CORE.md")

def load_core_beliefs() -> Dict[str, Any]:
    """
    Load core beliefs and standards from PROMETHIOS_CORE.md.
    
    Returns:
        Dictionary containing parsed core beliefs and requirements
    """
    beliefs = {
        "required_components": [],
        "allowed_personas": ["SAGE", "ARCHITECT", "RESEARCHER", "RITUALIST", "INVENTOR", "HAL", "NOVA", "PESSIMIST", "CRITIC", "CEO"],
        "min_plan_steps": 3,
        "depth_requirements": {
            "shallow": ["HAL", "NOVA"],
            "standard": ["CRITIC", "CEO"],
            "deep": ["SAGE", "PESSIMIST", "CRITIC", "CEO"]
        },
        "operational_thresholds": {}
    }
    
    try:
        with open(CORE_BELIEFS_FILE, 'r') as f:
            content = f.read()
            
            # Extract required components
            components_match = re.search(r'\| Component \| Purpose \| Validation Rule \|\n\|[-\s\|]+\n((?:\|[^|]+\|[^|]+\|[^|]+\|\n)+)', content)
            if components_match:
                components_table = components_match.group(1)
                beliefs["required_components"] = []
                for line in components_table.strip().split('\n'):
                    parts = [part.strip() for part in line.split('|')[1:-1]]
                    if len(parts) == 3:
                        component, purpose, validation_rule = parts
                        beliefs["required_components"].append(component)
            
            # Extract depth requirements
            depth_match = re.search(r'\| Depth \| Required Agents \| Reflection Intensity \| Purpose \|\n\|[-\s\|]+\n((?:\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\n)+)', content)
            if depth_match:
                depth_table = depth_match.group(1)
                beliefs["depth_requirements"] = {}
                for line in depth_table.strip().split('\n'):
                    parts = [part.strip() for part in line.split('|')[1:-1]]
                    if len(parts) == 4:
                        depth, agents, intensity, purpose = parts
                        beliefs["depth_requirements"][depth] = [agent.strip() for agent in agents.split(',')]
            
            # Extract operational thresholds
            thresholds_match = re.search(r'\| Threshold ID \| Parameter \| Value \| Description \|\n\|[-\s\|]+\n((?:\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\n)+)', content)
            if thresholds_match:
                thresholds_table = thresholds_match.group(1)
                beliefs["operational_thresholds"] = {}
                for line in thresholds_table.strip().split('\n'):
                    parts = [part.strip() for part in line.split('|')[1:-1]]
                    if len(parts) == 4:
                        threshold_id, parameter, value, description = parts
                        try:
                            # Try to convert value to float if possible
                            value_float = float(value)
                            beliefs["operational_thresholds"][parameter] = value_float
                        except ValueError:
                            beliefs["operational_thresholds"][parameter] = value
            
            # If no required components were found, use default
            if not beliefs["required_components"]:
                beliefs["required_components"] = ["prompt", "orchestrator_persona", "plan", "reflection_agent"]
            
            # If no depth requirements were found, use default
            if not beliefs["depth_requirements"]:
                beliefs["depth_requirements"] = {
                    "shallow": ["HAL", "NOVA"],
                    "standard": ["CRITIC", "CEO"],
                    "deep": ["SAGE", "PESSIMIST", "CRITIC", "CEO"]
                }
            
            return beliefs
    
    except Exception as e:
        print(f"Error loading core beliefs: {e}")
        # Return default beliefs as fallback
        return {
            "required_components": ["prompt", "orchestrator_persona", "plan", "reflection_agent"],
            "allowed_personas": ["SAGE", "ARCHITECT", "RESEARCHER", "RITUALIST", "INVENTOR", "HAL", "NOVA", "PESSIMIST", "CRITIC", "CEO"],
            "min_plan_steps": 3,
            "depth_requirements": {
                "shallow": ["HAL", "NOVA"],
                "standard": ["CRITIC", "CEO"],
                "deep": ["SAGE", "PESSIMIST", "CRITIC", "CEO"]
            },
            "operational_thresholds": {
                "alignment_threshold": 0.75,
                "drift_threshold": 0.25
            }
        }

def validate_loop(loop_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Validate a loop against the requirements defined in PROMETHIOS_CORE.md.
    
    Args:
        loop_data: Dictionary containing loop data
        
    Returns:
        Tuple containing:
        - Boolean indicating whether validation passed
        - Optional string with reason for failure
        - Dictionary with validation details
    """
    core_beliefs = load_core_beliefs()
    validation_result = {
        "loop_validation": "passed",
        "checked_components": [],
        "missing_components": [],
        "belief_reference": []
    }
    
    # Check for required components
    for component in core_beliefs["required_components"]:
        validation_result["checked_components"].append(component)
        if component not in loop_data or not loop_data[component]:
            validation_result["missing_components"].append(component)
            validation_result["loop_validation"] = "failed"
            return False, f"missing {component}", validation_result
    
    # Validate orchestrator_persona
    if loop_data["orchestrator_persona"] not in core_beliefs["allowed_personas"]:
        validation_result["loop_validation"] = "failed"
        return False, f"invalid persona: {loop_data['orchestrator_persona']}", validation_result
    
    # Validate plan has minimum steps
    if "plan" in loop_data and isinstance(loop_data["plan"], list):
        if len(loop_data["plan"]) < core_beliefs["min_plan_steps"]:
            validation_result["loop_validation"] = "failed"
            return False, f"plan has fewer than {core_beliefs['min_plan_steps']} steps", validation_result
    
    # Validate reflection agents based on depth
    depth = loop_data.get("depth", "standard")
    required_agents = core_beliefs["depth_requirements"].get(depth, [])
    
    if "reflection_agent" in loop_data:
        reflection_agents = loop_data["reflection_agent"]
        if isinstance(reflection_agents, str):
            reflection_agents = [reflection_agents]
        
        for required_agent in required_agents:
            if required_agent not in reflection_agents:
                validation_result["loop_validation"] = "failed"
                return False, f"missing required agent for {depth} depth: {required_agent}", validation_result
    
    # Add belief references
    alignment_threshold = core_beliefs["operational_thresholds"].get("alignment_threshold", 0.75)
    validation_result["belief_reference"] = ["reflection_before_execution", f"alignment_threshold = {alignment_threshold}"]
    
    # Add depth-specific beliefs
    if depth == "deep":
        validation_result["belief_reference"].append("bias_awareness_required")
    elif depth == "shallow":
        validation_result["belief_reference"].append("alignment_over_speed")
    
    # Add persona-specific beliefs
    persona = loop_data.get("orchestrator_persona")
    if persona == "SAGE":
        validation_result["belief_reference"].append("transparency_to_operator")
    elif persona == "PESSIMIST":
        validation_result["belief_reference"].append("minimize_hallucination")
    
    # Add validation metadata
    validation_result["validation_timestamp"] = datetime.datetime.utcnow().isoformat()
    validation_result["validation_version"] = "1.0"
    
    return True, None, validation_result

def validate_and_enrich_loop(loop_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a loop and enrich it with belief references if valid.
    
    Args:
        loop_data: Dictionary containing loop data
        
    Returns:
        Enriched loop data if valid, or original data with validation failure information
    """
    is_valid, reason, validation_result = validate_loop(loop_data)
    
    # Add validation results to loop data
    loop_data["loop_validation"] = validation_result["loop_validation"]
    loop_data["validation_timestamp"] = validation_result.get("validation_timestamp")
    loop_data["validation_version"] = validation_result.get("validation_version", "1.0")
    
    if not is_valid:
        loop_data["validation_reason"] = reason
        loop_data["missing_components"] = validation_result.get("missing_components", [])
        # Log validation failure
        print(f"Loop validation failed: {reason}")
    else:
        # Enrich with belief references
        loop_data["belief_reference"] = validation_result["belief_reference"]
        loop_data["checked_components"] = validation_result.get("checked_components", [])
    
    return loop_data
