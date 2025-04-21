"""
Rerun Decision Engine Module

This module is responsible for determining whether to rerun a loop based on
alignment scores, drift scores, and other metrics from the reflection process.

It implements guardrails to prevent endless reruns, including:
- Rerun limit enforcement
- Bias echo detection
- Reflection fatigue scoring
- Detailed rerun reasoning tracking
"""

from typing import Dict, Any, Optional, List
import asyncio
import json
import re
from datetime import datetime
from app.utils.persona_utils import get_current_persona, preload_persona_for_deep_loop
from app.modules.rerun_reasoning_logger import log_rerun_reasoning, log_finalization_reasoning

# Configuration for rerun thresholds
# These could be moved to a config file in a real implementation
RERUN_CONFIG = {
    "alignment_threshold": 0.75,  # Minimum alignment score to avoid rerun
    "drift_threshold": 0.25,      # Maximum drift score to avoid rerun
    "max_reruns": 3,              # Maximum number of reruns for a single loop
    "fatigue_threshold": 0.5,     # Maximum fatigue score to allow reruns
    "bias_repetition_threshold": 3  # Number of repetitions to trigger bias echo detection
}

# Mock function for reading from memory
# In a real implementation, this would read from a database or storage system
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    # Simulate memory read
    await asyncio.sleep(0.1)
    
    # Mock data for testing
    if key == "loop_trace[loop_001]":
        return {
            "loop_id": "loop_001",
            "status": "completed",
            "timestamp": "2025-04-21T12:00:00Z",
            "summary": "Analyzed quantum computing concepts",
            "orchestrator_persona": "SAGE",
            "rerun_count": 0,
            "max_reruns": 3,
            "reflection_fatigue": 0.0
        }
    elif key.startswith("loop_trace[loop_001_r"):
        rerun_num = int(key.split("_r")[1].split("]")[0])
        if rerun_num <= 2:  # Mock data for up to 2 reruns
            return {
                "loop_id": f"loop_001_r{rerun_num}",
                "rerun_of": f"loop_001_r{rerun_num-1}" if rerun_num > 1 else "loop_001",
                "status": "completed",
                "timestamp": "2025-04-21T12:30:00Z",
                "summary": f"Reanalyzed quantum computing concepts (rerun {rerun_num})",
                "orchestrator_persona": "SAGE",
                "rerun_count": rerun_num,
                "max_reruns": 3,
                "reflection_fatigue": 0.2 * rerun_num
            }
    elif key.startswith("loop_summary["):
        loop_id = key.split("[")[1].split("]")[0]
        return {
            "alignment_score": 0.72,
            "drift_score": 0.28,
            "summary_valid": True,
            "reflection_persona": "SAGE",
            "bias_echo": False,
            "reflection_fatigue": 0.2,
            "rerun_trigger": ["alignment", "drift"],
            "rerun_reason": "alignment_threshold_not_met"
        }
    
    return None

# Mock function for writing to memory
# In a real implementation, this would write to a database or storage system
async def write_to_memory(key: str, value: Any) -> bool:
    """Write data to memory storage."""
    # Simulate memory write
    await asyncio.sleep(0.1)
    print(f"Writing to memory: {key} = {json.dumps(value, indent=2)}")
    return True

def get_rerun_number(loop_id: str) -> int:
    """
    Extract the rerun number from a loop ID.
    
    Args:
        loop_id: The loop ID to parse (e.g., "loop_001_r2")
        
    Returns:
        The rerun number (0 for original loops, 1+ for reruns)
    """
    match = re.search(r'_r(\d+)$', loop_id)
    if match:
        return int(match.group(1))
    return 0

def generate_next_loop_id(loop_id: str) -> str:
    """
    Generate the next loop ID for a rerun.
    
    Args:
        loop_id: The current loop ID
        
    Returns:
        The next loop ID with incremented rerun number
    """
    rerun_num = get_rerun_number(loop_id)
    
    if rerun_num == 0:
        # First rerun
        return f"{loop_id}_r1"
    else:
        # Subsequent reruns
        base_id = loop_id.rsplit('_r', 1)[0]
        return f"{base_id}_r{rerun_num + 1}"

async def get_original_loop_id(loop_id: str) -> str:
    """
    Get the original loop ID by tracing back through reruns.
    
    Args:
        loop_id: The current loop ID
        
    Returns:
        The original loop ID (without any _r suffix)
    """
    current_id = loop_id
    while True:
        trace = await read_from_memory(f"loop_trace[{current_id}]")
        if not trace or not trace.get("rerun_of"):
            break
        current_id = trace["rerun_of"]
    
    # If the ID still has a rerun suffix, strip it
    if "_r" in current_id:
        return current_id.split("_r")[0]
    return current_id

async def get_total_rerun_count(loop_id: str) -> int:
    """
    Get the total number of reruns across all generations of a loop.
    
    This counts all reruns from the original loop through all branches.
    
    Args:
        loop_id: The current loop ID
        
    Returns:
        The total rerun count
    """
    # Get the original loop ID
    original_id = await get_original_loop_id(loop_id)
    
    # Count all loops with this original ID
    count = 0
    
    # Check the original loop
    original_trace = await read_from_memory(f"loop_trace[{original_id}]")
    if original_trace:
        count = original_trace.get("rerun_count", 0)
    
    # In a real implementation, we would query all loops with the same original ID
    # For this mock implementation, we'll just return the count from the original loop
    return count

async def enforce_rerun_limits(
    loop_id: str,
    override_max_reruns: bool = False,
    override_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enforce rerun limits based on configuration and current rerun count.
    
    Args:
        loop_id: The loop ID to check
        override_max_reruns: Whether to override the max reruns limit
        override_by: Who performed the override
        
    Returns:
        Dict with enforcement result
    """
    # Get the total rerun count for this loop family
    total_reruns = await get_total_rerun_count(loop_id)
    
    # Get the max reruns limit
    trace = await read_from_memory(f"loop_trace[{loop_id}]")
    max_reruns = RERUN_CONFIG["max_reruns"]
    if trace and "max_reruns" in trace:
        max_reruns = trace["max_reruns"]
    
    # Check if we've hit the limit
    limit_reached = total_reruns >= max_reruns
    
    # Apply override if provided
    force_finalize = limit_reached and not override_max_reruns
    
    # Update the trace with the latest rerun count and limit status
    if trace:
        trace["rerun_count"] = total_reruns
        trace["max_reruns"] = max_reruns
        trace["force_finalize"] = force_finalize
        
        if override_max_reruns and limit_reached:
            trace["overridden_by"] = override_by
        
        await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return {
        "rerun_count": total_reruns,
        "max_reruns": max_reruns,
        "limit_reached": limit_reached,
        "force_finalize": force_finalize,
        "overridden": override_max_reruns and limit_reached,
        "overridden_by": override_by if override_max_reruns and limit_reached else None
    }

async def evaluate_rerun_decision(
    loop_id: str, 
    reflection_result: Dict[str, Any],
    override_fatigue: bool = False,
    override_max_reruns: bool = False,
    override_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluate whether to rerun a loop based on reflection results and guardrails.
    
    This function:
    1. Checks if rerun limits have been reached
    2. Checks if bias echo has been detected
    3. Checks if reflection fatigue is too high
    4. Checks if alignment and drift scores warrant a rerun
    5. If rerun is needed, creates a new loop ID and copies trace
    
    Args:
        loop_id: The ID of the loop to evaluate
        reflection_result: The full reflection result with all metrics
        override_fatigue: Whether to override fatigue-based finalization
        override_max_reruns: Whether to override max reruns limit
        override_by: Who performed the override
        
    Returns:
        Dict containing the decision and related information
    """
    # Extract key metrics from reflection result
    alignment_score = reflection_result.get("alignment_score", 0.0)
    drift_score = reflection_result.get("drift_score", 1.0)
    summary_valid = reflection_result.get("summary_valid", False)
    bias_echo = reflection_result.get("bias_echo", False)
    reflection_fatigue = reflection_result.get("reflection_fatigue", 0.0)
    rerun_trigger = reflection_result.get("rerun_trigger", [])
    rerun_reason = reflection_result.get("rerun_reason")
    
    # Enforce rerun limits
    rerun_limits = await enforce_rerun_limits(
        loop_id, 
        override_max_reruns=override_max_reruns,
        override_by=override_by
    )
    
    # Initialize decision variables
    rerun_needed = False
    force_finalize = False
    finalize_reason = None
    
    # Check guardrails in order of precedence
    
    # 1. Check if we need to force finalize due to rerun limits
    if rerun_limits["force_finalize"]:
        force_finalize = True
        finalize_reason = "max_reruns_reached"
    
    # 2. Check if bias echo has been detected
    elif bias_echo:
        force_finalize = True
        finalize_reason = "bias_echo_detected"
    
    # 3. Check if fatigue threshold has been exceeded
    elif reflection_fatigue > RERUN_CONFIG["fatigue_threshold"] and not override_fatigue:
        force_finalize = True
        finalize_reason = "fatigue_threshold_exceeded"
    
    # 4. Check if rerun is needed based on alignment and drift thresholds
    elif not force_finalize:
        if alignment_score < RERUN_CONFIG["alignment_threshold"]:
            rerun_needed = True
            if not rerun_reason:
                rerun_reason = "alignment_threshold_not_met"
                rerun_trigger.append("alignment")
        
        if drift_score > RERUN_CONFIG["drift_threshold"]:
            rerun_needed = True
            if not rerun_reason:
                rerun_reason = "drift_threshold_exceeded"
                rerun_trigger.append("drift")
        
        if not summary_valid:
            rerun_needed = True
            if not rerun_reason:
                rerun_reason = "summary_invalid"
                rerun_trigger.append("validity")
    
    # If force finalize is set, override rerun_needed
    if force_finalize:
        rerun_needed = False
        
        # Log finalization reasoning
        await log_finalization_reasoning(
            loop_id,
            finalize_reason,
            rerun_trigger,
            f"Forced finalization due to {finalize_reason}",
            reflection_result.get("reflection_persona")
        )
    
    # If rerun is needed, prepare the new loop
    if rerun_needed:
        # Generate the next loop ID
        next_loop_id = generate_next_loop_id(loop_id)
        
        # Read the current loop trace
        current_trace = await read_from_memory(f"loop_trace[{loop_id}]")
        
        if current_trace:
            # Get the current persona or preload for deep loop
            current_rerun_num = get_rerun_number(loop_id)
            orchestrator_persona = preload_persona_for_deep_loop(loop_id, current_rerun_num + 1)
            
            # Create a new trace for the rerun
            new_trace = {
                "loop_id": next_loop_id,
                "rerun_of": loop_id,
                "rerun_reason": rerun_reason,
                "rerun_reason_detail": f"Triggered by {', '.join(rerun_trigger)}",
                "rerun_trigger": rerun_trigger,
                "status": "pending",
                "timestamp": datetime.utcnow().isoformat(),
                "depth": "deep",  # As specified in requirements
                "orchestrator_persona": orchestrator_persona,  # Include persona in rerun
                "rerun_depth": current_rerun_num + 1,
                "rerun_count": rerun_limits["rerun_count"] + 1,
                "max_reruns": rerun_limits["max_reruns"],
                "reflection_fatigue": reflection_fatigue,
                "bias_echo": bias_echo
            }
            
            # If there was an override, record it
            if override_fatigue and reflection_fatigue > RERUN_CONFIG["fatigue_threshold"]:
                new_trace["overridden_by"] = override_by
                new_trace["fatigue_override"] = True
            
            # Store the new trace
            await write_to_memory(f"loop_trace[{next_loop_id}]", new_trace)
            
            # Update the rerun count on the original loop
            original_id = await get_original_loop_id(loop_id)
            original_trace = await read_from_memory(f"loop_trace[{original_id}]")
            if original_trace:
                original_trace["rerun_count"] = rerun_limits["rerun_count"] + 1
                await write_to_memory(f"loop_trace[{original_id}]", original_trace)
            
            # Log rerun reasoning
            await log_rerun_reasoning(
                loop_id,
                rerun_trigger,
                rerun_reason,
                f"Triggered by {', '.join(rerun_trigger)}",
                override_by if (override_fatigue and reflection_fatigue > RERUN_CONFIG["fatigue_threshold"]) or 
                               (override_max_reruns and rerun_limits["limit_reached"]) else None,
                reflection_result.get("reflection_persona")
            )
            
            return {
                "decision": "rerun",
                "original_loop_id": loop_id,
                "new_loop_id": next_loop_id,
                "rerun_reason": rerun_reason,
                "rerun_number": current_rerun_num + 1,
                "rerun_count": rerun_limits["rerun_count"] + 1,
                "max_reruns": rerun_limits["max_reruns"],
                "orchestrator_persona": orchestrator_persona,  # Include persona in response
                "rerun_limit_reached": rerun_limits["limit_reached"],
                "bias_echo_detected": bias_echo,
                "fatigue_threshold_exceeded": reflection_fatigue > RERUN_CONFIG["fatigue_threshold"],
                "force_finalized": False,
                "rerun_trigger": rerun_trigger,
                "rerun_reason_detail": f"Triggered by {', '.join(rerun_trigger)}",
                "overridden_by": override_by if (override_fatigue and reflection_fatigue > RERUN_CONFIG["fatigue_threshold"]) or 
                                               (override_max_reruns and rerun_limits["limit_reached"]) else None
            }
    
    # If no rerun is needed, finalize the loop
    await write_to_memory(f"loop_trace[{loop_id}].status", "finalized")
    
    # Get the current persona
    orchestrator_persona = get_current_persona(loop_id)
    
    # If we don't have a finalize reason yet, determine one
    if not finalize_reason:
        finalize_reason = "no_issues_detected"
    
    # Log finalization reasoning if not already logged
    if not force_finalize:
        await log_finalization_reasoning(
            loop_id,
            finalize_reason,
            rerun_trigger if rerun_trigger else [],
            f"Finalized due to {finalize_reason}",
            reflection_result.get("reflection_persona")
        )
    
    return {
        "decision": "finalize",
        "loop_id": loop_id,
        "reason": finalize_reason,
        "orchestrator_persona": orchestrator_persona,  # Include persona in response
        "rerun_limit_reached": rerun_limits["rerun_count"] >= rerun_limits["max_reruns"],
        "bias_echo_detected": bias_echo,
        "fatigue_threshold_exceeded": reflection_fatigue > RERUN_CONFIG["fatigue_threshold"],
        "force_finalized": force_finalize,
        "rerun_trigger": rerun_trigger if rerun_trigger else [],
        "rerun_reason_detail": f"Finalized due to {finalize_reason}"
    }

async def make_rerun_decision(
    loop_id: str,
    override_fatigue: bool = False,
    override_max_reruns: bool = False,
    override_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Make a decision on whether to rerun a loop based on reflection results and guardrails.
    
    This is the main entry point for the rerun decision engine.
    
    Args:
        loop_id: The ID of the loop to evaluate
        override_fatigue: Whether to override fatigue-based finalization
        override_max_reruns: Whether to override max reruns limit
        override_by: Who performed the override
        
    Returns:
        Dict containing the decision and related information
    """
    # Get the reflection result
    reflection_result = await read_from_memory(f"loop_summary[{loop_id}]")
    
    if not reflection_result:
        # If no reflection result is available, finalize the loop
        return {
            "decision": "finalize",
            "loop_id": loop_id,
            "reason": "no_reflection_result",
            "orchestrator_persona": get_current_persona(loop_id)
        }
    
    # Evaluate the rerun decision
    return await evaluate_rerun_decision(
        loop_id,
        reflection_result,
        override_fatigue,
        override_max_reruns,
        override_by
    )
