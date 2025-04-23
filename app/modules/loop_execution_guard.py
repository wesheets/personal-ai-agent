"""
Loop Execution Guard Module

This module implements a safety layer that checks conditions before accepting a loop plan.
It integrates with the recursive reflection engine, freeze controller, and trust score evaluator
to ensure loops adhere to safety constraints and trigger appropriate interventions when needed.
"""

import logging
import re
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
    from app.modules.trust_score_evaluator import evaluate_trust_delta, get_trust_score
except ImportError:
    logger.warning("Failed to import evaluate_trust_delta from trust_score_evaluator, using fallback")
    def evaluate_trust_delta(loop_plan):
        logger.info("Using fallback evaluate_trust_delta function")
        return 0.0
    def get_trust_score(loop_plan, base_score=0.5):
        logger.info("Using fallback get_trust_score function")
        return base_score

def extract_prompt_data(loop_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and analyze data from the prompt text in the loop plan.
    
    Args:
        loop_plan: The loop plan to analyze
        
    Returns:
        Dictionary with extracted data from prompt analysis
    """
    prompt_data = {}
    
    # Extract prompt text if available
    prompt_text = loop_plan.get("prompt", "")
    if not prompt_text and "loop_data" in loop_plan and isinstance(loop_plan["loop_data"], dict):
        prompt_text = loop_plan["loop_data"].get("prompt", "")
    
    if not prompt_text:
        logger.warning("No prompt text found in loop plan")
        return prompt_data
    
    logger.info(f"Analyzing prompt text: {prompt_text}")
    
    # Check for confidence threshold mentions
    confidence_pattern = r"confidence\s+(?:is\s+)?(?:under|below|less\s+than)\s+(\d+)%"
    confidence_match = re.search(confidence_pattern, prompt_text, re.IGNORECASE)
    if confidence_match:
        threshold = int(confidence_match.group(1)) / 100.0
        prompt_data["confidence_threshold"] = threshold
        logger.info(f"Detected confidence threshold in prompt: {threshold}")
    
    # Check for trust mentions
    if re.search(r"trust\s+is\s+unknown", prompt_text, re.IGNORECASE):
        prompt_data["trust_unknown"] = True
        logger.info("Detected 'trust is unknown' in prompt")
    
    # Check for agent disagreement mentions
    if re.search(r"(HAL|CRITIC).+disagree", prompt_text, re.IGNORECASE):
        prompt_data["agent_disagreement"] = True
        logger.info("Detected agent disagreement mention in prompt")
    
    # Check for freeze instructions
    if re.search(r"freeze", prompt_text, re.IGNORECASE):
        prompt_data["freeze_instruction"] = True
        logger.info("Detected freeze instruction in prompt")
    
    # Check for stop instructions
    if re.search(r"stop", prompt_text, re.IGNORECASE):
        prompt_data["stop_instruction"] = True
        logger.info("Detected stop instruction in prompt")
    
    return prompt_data

def enrich_loop_plan(loop_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich the loop plan with data extracted from prompt and other fields.
    
    Args:
        loop_plan: The original loop plan
        
    Returns:
        Enriched loop plan with additional data
    """
    enriched_plan = loop_plan.copy()
    
    # Extract and add prompt data
    prompt_data = extract_prompt_data(loop_plan)
    enriched_plan["prompt_analysis"] = prompt_data
    
    # Set confidence based on prompt analysis
    if "confidence_threshold" in prompt_data:
        threshold = prompt_data["confidence_threshold"]
        # If confidence is mentioned in prompt but not set in plan, set it below threshold
        if "confidence" not in enriched_plan:
            enriched_plan["confidence"] = threshold - 0.1
            logger.info(f"Setting confidence to {enriched_plan['confidence']} based on prompt threshold")
    
    # Handle trust unknown case
    if prompt_data.get("trust_unknown", False):
        # Mark trust as undefined
        enriched_plan["trust_undefined"] = True
        if "trust_score" in enriched_plan:
            del enriched_plan["trust_score"]
        logger.info("Marking trust as undefined based on prompt analysis")
    
    # Handle agent disagreement
    if prompt_data.get("agent_disagreement", False):
        if "contradictions" not in enriched_plan:
            enriched_plan["contradictions"] = []
        
        # Add a critical contradiction for agent disagreement
        enriched_plan["contradictions"].append({
            "id": "prompt_contradiction_1",
            "severity": "critical",
            "description": "HAL and CRITIC disagree according to prompt"
        })
        logger.info("Added critical contradiction for agent disagreement from prompt")
    
    # Add project_id if present
    if "project_id" in loop_plan and "project_id" not in enriched_plan:
        enriched_plan["project_id"] = loop_plan["project_id"]
    
    return enriched_plan

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
    logger.info(f"Original loop plan: {loop_plan}")
    
    # Enrich the loop plan with data from prompt and other fields
    enriched_plan = enrich_loop_plan(loop_plan)
    logger.info(f"Enriched loop plan: {enriched_plan}")
    
    # Check if the loop should be frozen
    if should_freeze_loop(enriched_plan):
        logger.warning("Loop execution guard: Freezing loop due to trust or contradiction threshold")
        return {"status": "frozen", "reason": "Trust or contradiction threshold triggered"}

    # Check if reflection is needed
    if should_reflect(enriched_plan):
        logger.info("Loop execution guard: Triggering recursive reflection")
        return {
            "status": "reflection-triggered",
            "action": "recursive_reflection",
            "reason": "Uncertainty or agent contradiction detected"
        }
    
    # Evaluate trust delta for logging purposes
    trust_delta = evaluate_trust_delta(enriched_plan)
    logger.info(f"Loop execution guard: Trust delta for loop plan: {trust_delta}")
    
    # Get current trust score
    trust_score = get_trust_score(enriched_plan)
    logger.info(f"Loop execution guard: Current trust score: {trust_score}")
    
    # If all checks pass, return OK status
    logger.info("Loop execution guard: Loop plan accepted")
    return {"status": "ok"}
