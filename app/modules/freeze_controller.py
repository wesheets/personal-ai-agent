"""
Freeze Controller Module

This module implements the freeze control capabilities for the Promethios system.
It determines when a loop should be frozen based on trust scores and contradiction thresholds.
"""

import logging
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger(__name__)

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
    
    # Check if trust score is explicitly set and below threshold
    trust_score = loop_plan.get("trust_score", 1.0)
    if isinstance(trust_score, (int, float)) and trust_score < 0.3:
        logger.warning(f"Low trust score detected: {trust_score}, freezing loop")
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
    
    # Check trust score
    trust_score = loop_plan.get("trust_score", 1.0)
    if isinstance(trust_score, (int, float)) and trust_score < 0.3:
        reasons.append(f"Low trust score: {trust_score}")
    
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
