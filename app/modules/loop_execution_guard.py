"""
Loop Execution Guard Module

This module implements a safety layer that checks conditions before accepting a loop plan.
It integrates with the recursive reflection engine, freeze controller, and trust score evaluator
to ensure loops adhere to safety constraints and trigger appropriate interventions when needed.
"""

import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Import required modules with safe fallbacks
try:
    from app.modules.recursive_reflection_engine import should_reflect
except ImportError:
    logger.warning("Failed to import should_reflect from recursive_reflection_engine, using fallback")
    def should_reflect(loop_plan):
        logger.info("Using fallback should_reflect function")
        return False

try:
    from app.modules.freeze_controller import should_freeze_loop
except ImportError:
    logger.warning("Failed to import should_freeze_loop from freeze_controller, using fallback")
    def should_freeze_loop(loop_plan):
        logger.info("Using fallback should_freeze_loop function")
        return False

try:
    from app.modules.trust_score_evaluator import evaluate_trust_delta
except ImportError:
    logger.warning("Failed to import evaluate_trust_delta from trust_score_evaluator, using fallback")
    def evaluate_trust_delta(loop_plan):
        logger.info("Using fallback evaluate_trust_delta function")
        return 0.0

def loop_execution_guard(loop_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check conditions before accepting a loop plan.
    
    This function serves as a safety layer that integrates with the recursive reflection engine,
    freeze controller, and trust score evaluator to ensure loops adhere to safety constraints
    and trigger appropriate interventions when needed.
    
    Args:
        loop_plan: The loop plan to evaluate
        
    Returns:
        Dictionary with status and additional information:
        - {"status": "ok"} if the loop plan is acceptable
        - {"status": "frozen", "reason": "..."} if the loop should be frozen
        - {"status": "reflection-triggered", "action": "...", "reason": "..."} if reflection is needed
    """
    logger.info("Evaluating loop plan with execution guard")
    
    # Check if the loop should be frozen
    if should_freeze_loop(loop_plan):
        logger.warning("Loop execution guard: Freezing loop due to trust or contradiction threshold")
        return {"status": "frozen", "reason": "Trust or contradiction threshold triggered"}

    # Check if reflection is needed
    if should_reflect(loop_plan):
        logger.info("Loop execution guard: Triggering recursive reflection")
        return {
            "status": "reflection-triggered",
            "action": "recursive_reflection",
            "reason": "Uncertainty or agent contradiction detected"
        }
    
    # Evaluate trust delta for logging purposes
    trust_delta = evaluate_trust_delta(loop_plan)
    logger.info(f"Loop execution guard: Trust delta for loop plan: {trust_delta}")
    
    # If all checks pass, return OK status
    logger.info("Loop execution guard: Loop plan accepted")
    return {"status": "ok"}
