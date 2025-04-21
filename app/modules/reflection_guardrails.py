"""
Reflection Guardrails Integration Module

This module integrates all reflection guardrail components to ensure they work
together seamlessly to prevent endless reruns, track bias repetition, detect
fatigue, and enforce reflection integrity.

It serves as the main entry point for the reflection guardrails system and
coordinates the interaction between different components.
"""

from typing import Dict, Any, Optional, List
import asyncio
import json
from datetime import datetime

from app.modules.post_loop_summary_handler import process_loop_reflection
from app.modules.rerun_decision_engine import make_rerun_decision
from app.modules.pessimist_bias_tracking import track_bias
from app.modules.reflection_fatigue_scoring import process_reflection_fatigue
from app.modules.rerun_reasoning_logger import log_rerun_reasoning, log_finalization_reasoning

# Mock function for reading from memory
# In a real implementation, this would read from a database or storage system
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    # Simulate memory read
    await asyncio.sleep(0.1)
    return None

# Mock function for writing to memory
# In a real implementation, this would write to a database or storage system
async def write_to_memory(key: str, value: Any) -> bool:
    """Write data to memory storage."""
    # Simulate memory write
    await asyncio.sleep(0.1)
    print(f"Writing to memory: {key} = {json.dumps(value, indent=2)}")
    return True

async def process_loop_completion(
    loop_id: str,
    reflection_status: str,
    orchestrator_persona: Optional[str] = None,
    override_fatigue: bool = False,
    override_max_reruns: bool = False,
    override_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a loop completion event with all reflection guardrails.
    
    This is the main entry point for the reflection guardrails system.
    
    The function:
    1. Processes loop reflection to gather agent outputs
    2. Tracks bias tags and detects repetition
    3. Calculates reflection fatigue
    4. Makes a rerun decision based on all factors
    5. Logs detailed reasoning about the decision
    
    Args:
        loop_id: The ID of the completed loop
        reflection_status: The status of the reflection (must be 'done')
        orchestrator_persona: Optional persona to use for reflection
        override_fatigue: Whether to override fatigue-based finalization
        override_max_reruns: Whether to override max reruns limit
        override_by: Who performed the override
        
    Returns:
        Dict with the complete processing result
    """
    # Validate reflection status
    if reflection_status != "done":
        return {
            "status": "error",
            "message": "Invalid reflection status. Must be 'done'.",
            "loop_id": loop_id
        }
    
    # Process loop reflection
    reflection_result = await process_loop_reflection(
        loop_id,
        override_fatigue,
        override_max_reruns,
        override_by
    )
    
    # Extract bias tags for tracking
    bias_tags = []
    if "agent_results" in reflection_result and "pessimist" in reflection_result["agent_results"]:
        pessimist_result = reflection_result["agent_results"]["pessimist"]
        if "bias_analysis" in pessimist_result and "bias_tags_detail" in pessimist_result["bias_analysis"]:
            bias_tags = pessimist_result["bias_analysis"]["bias_tags_detail"]
    
    # Track bias if tags are available
    if bias_tags:
        bias_tracking_result = await track_bias(loop_id, bias_tags)
        
        # Update reflection result with bias tracking information
        reflection_result["bias_echo"] = bias_tracking_result["bias_echo"]
        reflection_result["repeated_tags"] = bias_tracking_result["repeated_tags"]
        reflection_result["repetition_counts"] = bias_tracking_result["repetition_counts"]
    
    # Make rerun decision
    decision_result = await make_rerun_decision(
        loop_id,
        override_fatigue,
        override_max_reruns,
        override_by
    )
    
    # Create the complete result
    result = {
        "status": "success",
        "loop_id": loop_id,
        "reflection_result": reflection_result,
        "decision_result": decision_result,
        "orchestrator_persona": orchestrator_persona or reflection_result.get("reflection_persona"),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Store the complete result
    await write_to_memory(f"loop_completion[{loop_id}]", result)
    
    return result

async def get_guardrails_status(loop_id: str) -> Dict[str, Any]:
    """
    Get the current status of all reflection guardrails for a loop.
    
    Args:
        loop_id: The loop ID to get status for
        
    Returns:
        Dict with the guardrails status
    """
    # Get the loop trace
    loop_trace = await read_from_memory(f"loop_trace[{loop_id}]")
    
    if not loop_trace:
        return {
            "status": "error",
            "message": f"Loop trace not found for {loop_id}",
            "loop_id": loop_id
        }
    
    # Get the reflection result
    reflection_result = await read_from_memory(f"loop_summary[{loop_id}]")
    
    # Create the guardrails status
    status = {
        "loop_id": loop_id,
        "rerun_count": loop_trace.get("rerun_count", 0),
        "max_reruns": loop_trace.get("max_reruns", 3),
        "rerun_limit_reached": loop_trace.get("rerun_count", 0) >= loop_trace.get("max_reruns", 3),
        "bias_echo": loop_trace.get("bias_echo", False),
        "reflection_fatigue": loop_trace.get("reflection_fatigue", 0.0),
        "fatigue_threshold_exceeded": loop_trace.get("reflection_fatigue", 0.0) >= 0.5,
        "force_finalize": loop_trace.get("force_finalize", False),
        "rerun_reason": loop_trace.get("rerun_reason"),
        "rerun_trigger": loop_trace.get("rerun_trigger", []),
        "overridden_by": loop_trace.get("overridden_by")
    }
    
    # Add reflection result information if available
    if reflection_result:
        status["alignment_score"] = reflection_result.get("alignment_score")
        status["drift_score"] = reflection_result.get("drift_score")
        status["summary_valid"] = reflection_result.get("summary_valid")
        status["reflection_persona"] = reflection_result.get("reflection_persona")
    
    return {
        "status": "success",
        "guardrails_status": status
    }

async def override_guardrails(
    loop_id: str,
    override_fatigue: bool = False,
    override_max_reruns: bool = False,
    override_by: str = "operator",
    override_reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Override reflection guardrails for a loop.
    
    Args:
        loop_id: The loop ID to override guardrails for
        override_fatigue: Whether to override fatigue-based finalization
        override_max_reruns: Whether to override max reruns limit
        override_by: Who performed the override
        override_reason: Optional reason for the override
        
    Returns:
        Dict with the override result
    """
    # Get the loop trace
    loop_trace = await read_from_memory(f"loop_trace[{loop_id}]")
    
    if not loop_trace:
        return {
            "status": "error",
            "message": f"Loop trace not found for {loop_id}",
            "loop_id": loop_id
        }
    
    # Apply overrides
    if override_fatigue:
        loop_trace["fatigue_override"] = True
    
    if override_max_reruns:
        loop_trace["max_reruns_override"] = True
    
    if override_fatigue or override_max_reruns:
        loop_trace["overridden_by"] = override_by
        loop_trace["override_reason"] = override_reason or "Manual override by operator"
        loop_trace["force_finalize"] = False
        
        # Store the updated trace
        await write_to_memory(f"loop_trace[{loop_id}]", loop_trace)
    
    return {
        "status": "success",
        "loop_id": loop_id,
        "override_fatigue": override_fatigue,
        "override_max_reruns": override_max_reruns,
        "overridden_by": override_by,
        "override_reason": override_reason or "Manual override by operator"
    }
