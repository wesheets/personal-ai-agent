"""
Freeze Controller Module

This module implements the freeze control capabilities for the Promethios system.
It determines when a loop should be frozen based on trust scores and contradiction thresholds.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger(__name__)

def analyze_prompt_for_freeze_conditions(loop_plan: Dict[str, Any]) -> bool:
    """
    Analyze prompt text for conditions that should trigger a freeze.
    
    Args:
        loop_plan: The loop plan to evaluate
        
    Returns:
        True if freeze conditions are found in prompt, False otherwise
    """
    # Get prompt text
    prompt_text = loop_plan.get("prompt", "")
    if not prompt_text and "loop_data" in loop_plan and isinstance(loop_plan["loop_data"], dict):
        prompt_text = loop_plan["loop_data"].get("prompt", "")
    
    if not prompt_text:
        return False
    
    # Check for explicit freeze instructions
    if re.search(r"freeze", prompt_text, re.IGNORECASE):
        logger.warning("Freeze instruction found in prompt text")
        return True
    
    # Check for trust unknown condition
    if re.search(r"trust\s+is\s+unknown", prompt_text, re.IGNORECASE):
        logger.warning("'Trust is unknown' condition found in prompt text")
        return True
    
    # Check for confidence threshold with freeze instruction
    confidence_pattern = r"confidence\s+(?:is\s+)?(?:under|below|less\s+than)\s+(\d+)%.*?freeze"
    confidence_match = re.search(confidence_pattern, prompt_text, re.IGNORECASE)
    if confidence_match:
        threshold = int(confidence_match.group(1)) / 100.0
        logger.warning(f"Confidence threshold with freeze instruction found: {threshold}")
        
        # Check if confidence is below threshold
        confidence = loop_plan.get("confidence", 0.0)
        if confidence < threshold:
            logger.warning(f"Confidence {confidence} is below threshold {threshold}")
            return True
    
    # Check for agent disagreement with stop/freeze instruction
    if re.search(r"(HAL|CRITIC).+disagree.+(?:stop|freeze)", prompt_text, re.IGNORECASE):
        logger.warning("Agent disagreement with stop/freeze instruction found in prompt")
        return True
    
    return False

def should_freeze_loop(loop_plan: Dict[str, Any]) -> bool:
    """
    Determine if a loop should be frozen based on the loop plan.
    
    This function analyzes the loop plan for trust issues and contradiction thresholds
    to decide if the loop should be frozen for safety.
    
    Args:
        loop_plan: The loop plan to evaluate
        
    Returns:
        True if the loop should be frozen, False otherwise
    """
    logger.info("Evaluating if loop should be frozen")
    
    # Check prompt analysis first
    prompt_analysis = loop_plan.get("prompt_analysis", {})
    if prompt_analysis.get("freeze_instruction", False) or prompt_analysis.get("stop_instruction", False):
        logger.warning("Freeze or stop instruction found in prompt analysis")
        return True
    
    # Check for trust undefined flag
    if loop_plan.get("trust_undefined", False):
        logger.warning("Trust is undefined, freezing loop")
        return True
    
    # Check if trust score is explicitly set and below threshold
    if "trust_score" in loop_plan:
        trust_score = loop_plan["trust_score"]
        if isinstance(trust_score, (int, float)) and trust_score < 0.3:
            logger.warning(f"Low trust score detected: {trust_score}, freezing loop")
            return True
    else:
        # If trust score is not defined, consider it a reason to freeze
        logger.warning("Trust score is not defined, freezing loop")
        return True
    
    # Check for critical contradictions
    contradictions = loop_plan.get("contradictions", [])
    critical_contradictions = [c for c in contradictions if c.get("severity", "low") == "critical"]
    if critical_contradictions and len(critical_contradictions) > 0:
        logger.warning(f"Critical contradictions detected: {len(critical_contradictions)}, freezing loop")
        return True
    
    # Check for freeze flags
    if loop_plan.get("freeze_requested", False):
        logger.warning("Freeze flag explicitly set in loop plan")
        return True
    
    # Check for safety violations
    safety_violations = loop_plan.get("safety_violations", [])
    if safety_violations and len(safety_violations) > 0:
        logger.warning(f"Safety violations detected: {len(safety_violations)}, freezing loop")
        return True
    
    # Check prompt text directly for freeze conditions
    if analyze_prompt_for_freeze_conditions(loop_plan):
        logger.warning("Freeze conditions found in prompt text")
        return True
    
    logger.info("No freeze triggers detected in loop plan")
    return False

def get_freeze_reason(loop_plan: Dict[str, Any]) -> str:
    """
    Get the reason for freezing a loop based on the loop plan.
    
    Args:
        loop_plan: The loop plan to evaluate
        
    Returns:
        Reason for freezing the loop
    """
    reasons = []
    
    # Check prompt analysis
    prompt_analysis = loop_plan.get("prompt_analysis", {})
    if prompt_analysis.get("freeze_instruction", False):
        reasons.append("Freeze instruction in prompt")
    if prompt_analysis.get("stop_instruction", False):
        reasons.append("Stop instruction in prompt")
    if prompt_analysis.get("trust_unknown", False):
        reasons.append("Trust is unknown (from prompt)")
    
    # Check trust status
    if loop_plan.get("trust_undefined", False):
        reasons.append("Trust is undefined")
    elif "trust_score" not in loop_plan:
        reasons.append("Trust score is not defined")
    elif isinstance(loop_plan.get("trust_score"), (int, float)) and loop_plan["trust_score"] < 0.3:
        reasons.append(f"Low trust score: {loop_plan['trust_score']}")
    
    # Check for critical contradictions
    contradictions = loop_plan.get("contradictions", [])
    critical_contradictions = [c for c in contradictions if c.get("severity", "low") == "critical"]
    if critical_contradictions and len(critical_contradictions) > 0:
        reasons.append(f"Critical contradictions: {len(critical_contradictions)}")
    
    # Check for freeze flags
    if loop_plan.get("freeze_requested", False):
        reasons.append("Freeze explicitly requested")
    
    # Check for safety violations
    safety_violations = loop_plan.get("safety_violations", [])
    if safety_violations and len(safety_violations) > 0:
        reasons.append(f"Safety violations: {len(safety_violations)}")
    
    if not reasons:
        return "Unknown reason"
    
    return ", ".join(reasons)
