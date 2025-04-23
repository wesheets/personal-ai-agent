"""
Recursive Reflection Engine Module

This module implements the recursive reflection capabilities for the Promethios system.
It determines when reflection is needed based on uncertainty levels and agent contradictions.
"""

import logging
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger(__name__)

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
    
    # Check if uncertainty level is explicitly set in the plan
    uncertainty_level = loop_plan.get("uncertainty_level", 0.0)
    if isinstance(uncertainty_level, (int, float)) and uncertainty_level > 0.7:
        logger.warning(f"High uncertainty level detected: {uncertainty_level}, triggering reflection")
        return True
    
    # Check for agent contradictions
    contradictions = loop_plan.get("contradictions", [])
    if contradictions and len(contradictions) > 0:
        logger.warning(f"Agent contradictions detected: {len(contradictions)}, triggering reflection")
        return True
    
    # Check for reflection flags
    if loop_plan.get("needs_reflection", False):
        logger.warning("Reflection flag explicitly set in loop plan")
        return True
    
    # Check for confidence scores
    confidence = loop_plan.get("confidence", 1.0)
    if isinstance(confidence, (int, float)) and confidence < 0.5:
        logger.warning(f"Low confidence score detected: {confidence}, triggering reflection")
        return True
    
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
    
    # Determine based on uncertainty level
    uncertainty_level = loop_plan.get("uncertainty_level", 0.5)
    
    if uncertainty_level > 0.8:
        return "deep"
    elif uncertainty_level > 0.5:
        return "standard"
    else:
        return "shallow"
    
    return default_depth
