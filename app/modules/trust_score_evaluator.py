"""
Trust Score Evaluator Module

This module implements the trust evaluation capabilities for the Promethios system.
It evaluates trust scores and deltas for loop plans based on various factors.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Union, Tuple

# Configure logging
logger = logging.getLogger(__name__)

def analyze_prompt_for_trust_conditions(loop_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze prompt text for trust-related conditions.
    
    Args:
        loop_plan: The loop plan to evaluate
        
    Returns:
        Dictionary with trust-related data extracted from prompt
    """
    trust_data = {}
    
    # Get prompt text
    prompt_text = loop_plan.get("prompt", "")
    if not prompt_text and "loop_data" in loop_plan and isinstance(loop_plan["loop_data"], dict):
        prompt_text = loop_plan["loop_data"].get("prompt", "")
    
    if not prompt_text:
        return trust_data
    
    # Check for trust unknown mentions
    if re.search(r"trust\s+is\s+unknown", prompt_text, re.IGNORECASE):
        trust_data["trust_unknown"] = True
        logger.info("'Trust is unknown' found in prompt text")
    
    # Check for trust threshold mentions
    trust_pattern = r"trust\s+(?:is\s+)?(?:under|below|less\s+than)\s+(\d+)%"
    trust_match = re.search(trust_pattern, prompt_text, re.IGNORECASE)
    if trust_match:
        threshold = int(trust_match.group(1)) / 100.0
        trust_data["trust_threshold"] = threshold
        logger.info(f"Trust threshold found in prompt: {threshold}")
    
    # Check for agent disagreement that might affect trust
    if re.search(r"(HAL|CRITIC).+disagree", prompt_text, re.IGNORECASE):
        trust_data["agent_disagreement"] = True
        logger.info("Agent disagreement found in prompt that may affect trust")
    
    return trust_data

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
    
    # Check if trust is undefined or unknown
    if loop_plan.get("trust_undefined", False) or loop_plan.get("prompt_analysis", {}).get("trust_unknown", False):
        logger.warning("Trust is undefined or unknown, returning significant negative delta")
        return -0.5
    
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
    
    # Check prompt analysis for agent disagreement
    if loop_plan.get("prompt_analysis", {}).get("agent_disagreement", False):
        disagreement_impact = -0.2
        logger.info(f"Agent disagreement from prompt impact on trust: {disagreement_impact}")
        delta += disagreement_impact
    
    logger.info(f"Final trust delta: {delta}")
    return delta

def get_trust_score(loop_plan: Dict[str, Any], base_score: float = 0.5) -> float:
    """
    Calculate the trust score for a loop plan.
    
    Args:
        loop_plan: The loop plan to evaluate
        base_score: Base trust score to start with
        
    Returns:
        Trust score between 0.0 and 1.0, or None if trust is undefined
    """
    # Check if trust is undefined or unknown
    if loop_plan.get("trust_undefined", False) or loop_plan.get("prompt_analysis", {}).get("trust_unknown", False):
        logger.warning("Trust is undefined or unknown, returning None")
        return None
    
    # If trust score is explicitly set in the plan, use that
    if "trust_score" in loop_plan and isinstance(loop_plan["trust_score"], (int, float)):
        score = loop_plan["trust_score"]
        logger.info(f"Using explicit trust score from plan: {score}")
        return max(0.0, min(1.0, score))
    
    # Check prompt analysis for trust threshold
    prompt_analysis = loop_plan.get("prompt_analysis", {})
    if "trust_threshold" in prompt_analysis:
        threshold = prompt_analysis["trust_threshold"]
        # If trust threshold is mentioned in prompt, set trust below threshold
        score = threshold - 0.1
        logger.info(f"Setting trust score to {score} based on prompt threshold")
        return max(0.0, min(1.0, score))
    
    # Otherwise calculate based on delta
    delta = evaluate_trust_delta(loop_plan)
    score = base_score + delta
    
    # Ensure score is between 0 and 1
    score = max(0.0, min(1.0, score))
    logger.info(f"Calculated trust score: {score}")
    
    return score

def is_trust_sufficient(loop_plan: Dict[str, Any], threshold: float = 0.3) -> Tuple[bool, Optional[float]]:
    """
    Determine if the trust score is sufficient to proceed.
    
    Args:
        loop_plan: The loop plan to evaluate
        threshold: Minimum trust score required to proceed
        
    Returns:
        Tuple of (is_sufficient, actual_score)
    """
    score = get_trust_score(loop_plan)
    
    # If score is None (undefined trust), trust is insufficient
    if score is None:
        logger.warning("Trust is undefined, considered insufficient")
        return (False, None)
    
    is_sufficient = score >= threshold
    if not is_sufficient:
        logger.warning(f"Trust score {score} is below threshold {threshold}")
    else:
        logger.info(f"Trust score {score} is sufficient (>= {threshold})")
    
    return (is_sufficient, score)
