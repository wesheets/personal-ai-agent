"""
Rerun Reasoning Logger Module

This module is responsible for logging detailed reasoning about loop reruns,
including what triggered the rerun, the specific reason, and any operator overrides.

This information is stored in the loop trace and summary to provide transparency
and traceability for the reflection process.
"""

from typing import Dict, Any, Optional, List
import asyncio
import json
from datetime import datetime

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
            "timestamp": "2025-04-21T12:00:00Z"
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

async def log_rerun_reasoning(
    loop_id: str,
    rerun_trigger: List[str],
    rerun_reason: str,
    rerun_reason_detail: Optional[str] = None,
    overridden_by: Optional[str] = None,
    reflection_persona: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log detailed reasoning about a loop rerun.
    
    Args:
        loop_id: The loop ID being rerun
        rerun_trigger: List of components that triggered the rerun (e.g., ["ceo", "pessimist"])
        rerun_reason: The high-level reason for the rerun (e.g., "belief_conflict")
        rerun_reason_detail: Optional detailed explanation of the rerun reason
        overridden_by: Optional identifier of who overrode the rerun decision
        reflection_persona: Optional persona used for reflection
        
    Returns:
        Dict with the logged reasoning information
    """
    # Create the reasoning metadata
    reasoning = {
        "rerun_trigger": rerun_trigger,
        "rerun_reason": rerun_reason,
        "rerun_reason_detail": rerun_reason_detail or f"Triggered by {', '.join(rerun_trigger)}",
        "timestamp": datetime.utcnow().isoformat(),
        "reflection_persona": reflection_persona
    }
    
    # Add override information if applicable
    if overridden_by:
        reasoning["overridden_by"] = overridden_by
    
    # Get the current loop trace
    trace = await read_from_memory(f"loop_trace[{loop_id}]")
    
    if trace:
        # Update the trace with the reasoning information
        trace["rerun_trigger"] = rerun_trigger
        trace["rerun_reason"] = rerun_reason
        trace["rerun_reason_detail"] = reasoning["rerun_reason_detail"]
        
        if overridden_by:
            trace["overridden_by"] = overridden_by
        
        if reflection_persona:
            trace["reflection_persona"] = reflection_persona
        
        # Write the updated trace back to memory
        await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    # Also store the reasoning in a dedicated location for easier retrieval
    await write_to_memory(f"rerun_reasoning[{loop_id}]", reasoning)
    
    return reasoning

async def log_finalization_reasoning(
    loop_id: str,
    finalize_reason: str,
    finalize_trigger: Optional[List[str]] = None,
    finalize_reason_detail: Optional[str] = None,
    reflection_persona: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log detailed reasoning about a loop finalization.
    
    Args:
        loop_id: The loop ID being finalized
        finalize_reason: The high-level reason for finalization (e.g., "max_reruns_reached")
        finalize_trigger: Optional list of components that triggered finalization
        finalize_reason_detail: Optional detailed explanation of the finalization reason
        reflection_persona: Optional persona used for reflection
        
    Returns:
        Dict with the logged reasoning information
    """
    # Create the reasoning metadata
    reasoning = {
        "finalize_reason": finalize_reason,
        "finalize_trigger": finalize_trigger or [],
        "finalize_reason_detail": finalize_reason_detail or f"Finalized due to {finalize_reason}",
        "timestamp": datetime.utcnow().isoformat(),
        "reflection_persona": reflection_persona
    }
    
    # Get the current loop trace
    trace = await read_from_memory(f"loop_trace[{loop_id}]")
    
    if trace:
        # Update the trace with the reasoning information
        trace["finalize_reason"] = finalize_reason
        trace["finalize_trigger"] = reasoning["finalize_trigger"]
        trace["finalize_reason_detail"] = reasoning["finalize_reason_detail"]
        
        if reflection_persona:
            trace["reflection_persona"] = reflection_persona
        
        # Write the updated trace back to memory
        await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    # Also store the reasoning in a dedicated location for easier retrieval
    await write_to_memory(f"finalize_reasoning[{loop_id}]", reasoning)
    
    return reasoning

async def add_reasoning_to_summary(
    loop_id: str,
    summary_key: str,
    reasoning_type: str,
    reasoning_data: Dict[str, Any]
) -> bool:
    """
    Add reasoning information to a loop summary.
    
    Args:
        loop_id: The loop ID
        summary_key: The memory key for the summary (e.g., "loop_summary[loop_001]")
        reasoning_type: The type of reasoning ("rerun" or "finalize")
        reasoning_data: The reasoning data to add
        
    Returns:
        True if successful, False otherwise
    """
    # Get the current summary
    summary = await read_from_memory(summary_key)
    
    if not summary:
        return False
    
    # Add the reasoning information to the summary
    if reasoning_type == "rerun":
        summary["rerun_reasoning"] = reasoning_data
    else:
        summary["finalize_reasoning"] = reasoning_data
    
    # Write the updated summary back to memory
    return await write_to_memory(summary_key, summary)

async def get_rerun_reasoning(loop_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the rerun reasoning for a loop.
    
    Args:
        loop_id: The loop ID to get reasoning for
        
    Returns:
        The rerun reasoning, or None if not found
    """
    return await read_from_memory(f"rerun_reasoning[{loop_id}]")

async def get_finalization_reasoning(loop_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the finalization reasoning for a loop.
    
    Args:
        loop_id: The loop ID to get reasoning for
        
    Returns:
        The finalization reasoning, or None if not found
    """
    return await read_from_memory(f"finalize_reasoning[{loop_id}]")
