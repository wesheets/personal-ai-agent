"""
Recursive Reflection Engine Module

This module implements the recursive reflection capabilities for the Promethios system.
It determines when reflection is needed based on uncertainty levels and agent contradictions.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger(__name__)

def analyze_prompt_for_reflection_conditions(loop_plan: Dict[str, Any]) -> bool:
    """
    Analyze prompt text for conditions that should trigger reflection.
    
    Args:
        loop_plan: The loop plan to evaluate
        
    Returns:
        True if reflection conditions are found in prompt, False otherwise
    """
    # Get prompt text
    prompt_text = loop_plan.get("prompt", "")
    if not prompt_text and "loop_data" in loop_plan and isinstance(loop_plan["loop_data"], dict):
        prompt_text = loop_plan["loop_data"].get("prompt", "")
    
    if not prompt_text:
        return False
    
    # Check for confidence threshold without explicit freeze instruction
    confidence_pattern = r"confidence\s+(?:is\s+)?(?:under|below|less\s+than)\s+(\d+)%"
    confidence_match = re.search(confidence_pattern, prompt_text, re.IGNORECASE)
    if confidence_match:
        threshold = int(confidence_match.group(1)) / 100.0
        logger.info(f"Confidence threshold found in prompt: {threshold}")
        
        # Check if confidence is below threshold
        confidence = loop_plan.get("confidence", 0.0)
        if confidence < threshold:
            logger.warning(f"Confidence {confidence} is below threshold {threshold}")
            return True
    
    # Check for agent disagreement without explicit freeze instruction
    if re.search(r"(HAL|CRITIC).+disagree", prompt_text, re.IGNORECASE) and not re.search(r"freeze", prompt_text, re.IGNORECASE):
        logger.warning("Agent disagreement found in prompt without freeze instruction")
        return True
    
    return False

def should_reflect(loop_plan: Dict[str, Any]) -> bool:
    """
    Determine if reflection is needed based on the loop plan.
    
    This function analyzes the loop plan for uncertainty levels and agent contradictions
    to decide if recursive reflection should be triggered.
    
    Args:
        loop_plan: The loop plan to evaluate
        
    Returns:
        True if reflection is needed, False otherwise
    """
    logger.info("Evaluating if reflection is needed for loop plan")
    
    # Check prompt analysis first
    prompt_analysis = loop_plan.get("prompt_analysis", {})
    
    # Check for confidence threshold in prompt analysis
    if "confidence_threshold" in prompt_analysis:
        threshold = prompt_analysis["confidence_threshold"]
        confidence = loop_plan.get("confidence", 0.0)
        if confidence < threshold:
            logger.warning(f"Confidence {confidence} is below threshold {threshold} from prompt analysis")
            return True
    
    # Check for agent disagreement in prompt analysis
    if prompt_analysis.get("agent_disagreement", False) and not prompt_analysis.get("freeze_instruction", False):
        logger.warning("Agent disagreement detected in prompt analysis without freeze instruction")
        return True
    
    # Check if uncertainty level is explicitly set in the plan
    uncertainty_level = loop_plan.get("uncertainty_level", 0.0)
    if isinstance(uncertainty_level, (int, float)) and uncertainty_level > 0.7:
        logger.warning(f"High uncertainty level detected: {uncertainty_level}, triggering reflection")
        return True
    
    # Check for agent contradictions
    contradictions = loop_plan.get("contradictions", [])
    non_critical_contradictions = [c for c in contradictions if c.get("severity", "low") != "critical"]
    if non_critical_contradictions and len(non_critical_contradictions) > 0:
        logger.warning(f"Agent contradictions detected: {len(non_critical_contradictions)}, triggering reflection")
        return True
    
    # Check for reflection flags
    if loop_plan.get("needs_reflection", False):
        logger.warning("Reflection flag explicitly set in loop plan")
        return True
    
    # Check for confidence scores
    confidence = loop_plan.get("confidence", 1.0)
    if isinstance(confidence, (int, float)) and confidence < 0.5:
        logger.warning(f"Low confidence score detected: {confidence}, triggering reflection")
        # Add trace logging before returning True
        confidence_score = confidence
        reflection_triggered = True
        print("[TRACE] Reflection Check – Confidence:", confidence_score)
        print("[TRACE] Recursive Reflection Triggered:", reflection_triggered)
        return True
    
    # Check prompt text directly for reflection conditions
    if analyze_prompt_for_reflection_conditions(loop_plan):
        logger.warning("Reflection conditions found in prompt text")
        # Add trace logging before returning True
        confidence_score = loop_plan.get("confidence", "undefined")
        reflection_triggered = True
        print("[TRACE] Reflection Check – Confidence:", confidence_score)
        print("[TRACE] Recursive Reflection Triggered:", reflection_triggered)
        return True
    
    # Extract confidence score for trace logging
    confidence_score = loop_plan.get("confidence", "undefined")
    reflection_triggered = False
    
    # Add trace logging
    print("[TRACE] Reflection Check – Confidence:", confidence_score)
    print("[TRACE] Recursive Reflection Triggered:", reflection_triggered)
    
    logger.info("No reflection triggers detected in loop plan")
    return False

def get_reflection_depth(loop_plan: Dict[str, Any]) -> str:
    """
    Determine the appropriate reflection depth based on the loop plan.
    
    Args:
        loop_plan: The loop plan to evaluate
        
    Returns:
        Reflection depth level (shallow, standard, deep)
    """
    # Default to standard depth
    default_depth = "standard"
    
    # Check if depth is explicitly set
    if "reflection_depth" in loop_plan:
        return loop_plan["reflection_depth"]
    
    # Check prompt analysis for confidence threshold
    prompt_analysis = loop_plan.get("prompt_analysis", {})
    if "confidence_threshold" in prompt_analysis:
        threshold = prompt_analysis["confidence_threshold"]
        if threshold < 0.3:
            return "deep"
        elif threshold < 0.5:
            return "standard"
    
    # Determine based on uncertainty level
    uncertainty_level = loop_plan.get("uncertainty_level", 0.5)
    
    if uncertainty_level > 0.8:
        return "deep"
    elif uncertainty_level > 0.5:
        return "standard"
    else:
        return "shallow"
    
    return default_depth
