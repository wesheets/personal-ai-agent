"""
Trust Score Evaluator Module

This module implements the trust evaluation capabilities for the Promethios system.
It evaluates trust scores and deltas for loop plans based on various factors.
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple

# Configure logging
logger = logging.getLogger(__name__)

def evaluate_trust_delta(loop_plan: Dict[str, Any]) -> float:
    """
    Evaluate the trust delta for a loop plan.
    
    This function analyzes the loop plan to determine how much the trust score
    should change based on various factors like contradictions, uncertainty,
    and alignment with core beliefs.
    
    Args:
        loop_plan: The loop plan to evaluate
        
    Returns:
        Trust delta value (positive for increased trust, negative for decreased trust)
    """
    logger.info("Evaluating trust delta for loop plan")
    
    # Start with neutral delta
    delta = 0.0
    
    # Check for contradictions (negative impact)
    contradictions = loop_plan.get("contradictions", [])
    if contradictions:
        contradiction_impact = -0.1 * len(contradictions)
        logger.info(f"Contradictions impact on trust: {contradiction_impact}")
        delta += contradiction_impact
    
    # Check for uncertainty (negative impact)
    uncertainty_level = loop_plan.get("uncertainty_level", 0.0)
    if isinstance(uncertainty_level, (int, float)) and uncertainty_level > 0:
        uncertainty_impact = -0.2 * uncertainty_level
        logger.info(f"Uncertainty impact on trust: {uncertainty_impact}")
        delta += uncertainty_impact
    
    # Check for belief alignment (positive impact)
    belief_alignment = loop_plan.get("belief_alignment", 0.0)
    if isinstance(belief_alignment, (int, float)) and belief_alignment > 0:
        alignment_impact = 0.2 * belief_alignment
        logger.info(f"Belief alignment impact on trust: {alignment_impact}")
        delta += alignment_impact
    
    # Check for successful completions (positive impact)
    successful_completions = loop_plan.get("successful_completions", 0)
    if successful_completions > 0:
        completion_impact = 0.05 * min(successful_completions, 5)  # Cap at 5 completions
        logger.info(f"Successful completions impact on trust: {completion_impact}")
        delta += completion_impact
    
    # Check for safety violations (severe negative impact)
    safety_violations = loop_plan.get("safety_violations", [])
    if safety_violations:
        safety_impact = -0.3 * len(safety_violations)
        logger.info(f"Safety violations impact on trust: {safety_impact}")
        delta += safety_impact
    
    logger.info(f"Final trust delta: {delta}")
    return delta

def get_trust_score(loop_plan: Dict[str, Any], base_score: float = 0.5) -> float:
    """
    Calculate the trust score for a loop plan.
    
    Args:
        loop_plan: The loop plan to evaluate
        base_score: Base trust score to start with
        
    Returns:
        Trust score between 0.0 and 1.0
    """
    # If trust score is explicitly set in the plan, use that
    if "trust_score" in loop_plan and isinstance(loop_plan["trust_score"], (int, float)):
        return max(0.0, min(1.0, loop_plan["trust_score"]))
    
    # Otherwise calculate based on delta
    delta = evaluate_trust_delta(loop_plan)
    score = base_score + delta
    
    # Ensure score is between 0 and 1
    score = max(0.0, min(1.0, score))
    
    return score

def is_trust_sufficient(loop_plan: Dict[str, Any], threshold: float = 0.3) -> Tuple[bool, float]:
    """
    Determine if the trust score is sufficient to proceed.
    
    Args:
        loop_plan: The loop plan to evaluate
        threshold: Minimum trust score required to proceed
        
    Returns:
        Tuple of (is_sufficient, actual_score)
    """
    score = get_trust_score(loop_plan)
    return (score >= threshold, score)
