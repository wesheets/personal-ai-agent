"""
Reflection Fatigue Scoring Module

This module implements reflection fatigue scoring to prevent loops from
endlessly rerunning without making meaningful improvements.

Fatigue increases when:
- Loops rerun without improving alignment or drift scores
- The same issues are repeatedly flagged
- Multiple reruns occur in a short time period

When fatigue exceeds a threshold, loops are forced to finalize unless
manually overridden by an operator.
"""

from typing import Dict, Any, Optional, List
import asyncio
import json
from datetime import datetime

# Configuration for fatigue scoring
FATIGUE_CONFIG = {
    "base_increment": 0.15,           # Base fatigue increase per rerun
    "improvement_threshold": 0.05,    # Minimum improvement to avoid fatigue
    "decay_rate": 0.05,               # Rate at which fatigue decays over time
    "critical_threshold": 0.5,        # Threshold at which to force finalization
    "max_fatigue": 1.0                # Maximum possible fatigue score
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
            "alignment_score": 0.72,
            "drift_score": 0.28,
            "reflection_fatigue": 0.0
        }
    elif key == "loop_trace[loop_001_r1]":
        return {
            "loop_id": "loop_001_r1",
            "rerun_of": "loop_001",
            "status": "completed",
            "timestamp": "2025-04-21T12:30:00Z",
            "alignment_score": 0.74,  # Slight improvement
            "drift_score": 0.26,      # Slight improvement
            "reflection_fatigue": 0.1
        }
    elif key == "loop_trace[loop_001_r2]":
        return {
            "loop_id": "loop_001_r2",
            "rerun_of": "loop_001_r1",
            "status": "completed",
            "timestamp": "2025-04-21T13:00:00Z",
            "alignment_score": 0.73,  # No improvement (slight regression)
            "drift_score": 0.27,      # No improvement (slight regression)
            "reflection_fatigue": 0.25
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

async def get_previous_loop_trace(loop_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the trace of the previous loop (the one this loop is a rerun of).
    
    Args:
        loop_id: The current loop ID
        
    Returns:
        The previous loop trace, or None if this is the first loop
    """
    # Get the current loop trace
    current_trace = await read_from_memory(f"loop_trace[{loop_id}]")
    
    if not current_trace or not current_trace.get("rerun_of"):
        return None
    
    # Get the previous loop trace
    previous_loop_id = current_trace["rerun_of"]
    previous_trace = await read_from_memory(f"loop_trace[{previous_loop_id}]")
    
    return previous_trace

def calculate_improvement(current_value: float, previous_value: float, is_alignment: bool = True) -> float:
    """
    Calculate the improvement between two values.
    
    For alignment scores, higher is better.
    For drift scores, lower is better.
    
    Args:
        current_value: The current value
        previous_value: The previous value
        is_alignment: Whether this is an alignment score (True) or drift score (False)
        
    Returns:
        The improvement value (positive means improvement, negative means regression)
    """
    if is_alignment:
        # For alignment, higher is better
        return current_value - previous_value
    else:
        # For drift, lower is better
        return previous_value - current_value

async def calculate_fatigue_score(
    loop_id: str,
    alignment_score: float,
    drift_score: float,
    previous_fatigue: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculate the reflection fatigue score for a loop.
    
    Fatigue increases when:
    - Loops rerun without improving alignment or drift scores
    - Multiple reruns occur in a short time period
    
    Args:
        loop_id: The loop ID to calculate fatigue for
        alignment_score: The current alignment score
        drift_score: The current drift score
        previous_fatigue: Optional previous fatigue score
        
    Returns:
        Dict with fatigue calculation results
    """
    # Get the previous loop trace
    previous_trace = await get_previous_loop_trace(loop_id)
    
    # Initialize fatigue variables
    base_fatigue = previous_fatigue if previous_fatigue is not None else 0.0
    fatigue_increment = 0.0
    fatigue_increased = False
    improvement_detected = False
    
    # If this is a rerun, calculate improvement and fatigue
    if previous_trace:
        # Calculate improvements
        alignment_improvement = calculate_improvement(
            alignment_score, 
            previous_trace.get("alignment_score", 0.0),
            is_alignment=True
        )
        
        drift_improvement = calculate_improvement(
            drift_score, 
            previous_trace.get("drift_score", 1.0),
            is_alignment=False
        )
        
        # Check if there was meaningful improvement
        alignment_improved = alignment_improvement >= FATIGUE_CONFIG["improvement_threshold"]
        drift_improved = drift_improvement >= FATIGUE_CONFIG["improvement_threshold"]
        improvement_detected = alignment_improved or drift_improved
        
        # Calculate fatigue increment
        if not improvement_detected:
            # No improvement, increase fatigue
            fatigue_increment = FATIGUE_CONFIG["base_increment"]
            fatigue_increased = True
        else:
            # Improvement detected, apply decay
            fatigue_increment = -FATIGUE_CONFIG["decay_rate"]
            fatigue_increased = False
    
    # Calculate the new fatigue score
    new_fatigue = max(0.0, min(FATIGUE_CONFIG["max_fatigue"], base_fatigue + fatigue_increment))
    
    # Check if we've exceeded the critical threshold
    threshold_exceeded = new_fatigue >= FATIGUE_CONFIG["critical_threshold"]
    
    return {
        "reflection_fatigue": new_fatigue,
        "previous_fatigue": base_fatigue,
        "fatigue_increment": fatigue_increment,
        "fatigue_increased": fatigue_increased,
        "improvement_detected": improvement_detected,
        "threshold_exceeded": threshold_exceeded,
        "critical_threshold": FATIGUE_CONFIG["critical_threshold"],
        "force_finalize": threshold_exceeded
    }

async def update_loop_with_fatigue(
    loop_id: str,
    fatigue_result: Dict[str, Any]
) -> bool:
    """
    Update a loop trace with fatigue information.
    
    Args:
        loop_id: The loop ID to update
        fatigue_result: The fatigue calculation result
        
    Returns:
        True if successful, False otherwise
    """
    # Get the current loop trace
    trace = await read_from_memory(f"loop_trace[{loop_id}]")
    
    if not trace:
        return False
    
    # Update the trace with fatigue information
    trace["reflection_fatigue"] = fatigue_result["reflection_fatigue"]
    trace["fatigue_increased"] = fatigue_result["fatigue_increased"]
    trace["force_finalize"] = trace.get("force_finalize", False) or fatigue_result["force_finalize"]
    
    # Write the updated trace back to memory
    return await write_to_memory(f"loop_trace[{loop_id}]", trace)

async def process_reflection_fatigue(
    loop_id: str,
    alignment_score: float,
    drift_score: float,
    override_fatigue: bool = False
) -> Dict[str, Any]:
    """
    Process reflection fatigue for a loop.
    
    This is the main entry point for fatigue scoring.
    
    Args:
        loop_id: The loop ID to process
        alignment_score: The current alignment score
        drift_score: The current drift score
        override_fatigue: Whether to override fatigue-based finalization
        
    Returns:
        Dict with fatigue processing results
    """
    # Get the current loop trace
    trace = await read_from_memory(f"loop_trace[{loop_id}]")
    
    # Get the previous fatigue score if available
    previous_fatigue = trace.get("reflection_fatigue", 0.0) if trace else 0.0
    
    # Calculate the new fatigue score
    fatigue_result = await calculate_fatigue_score(
        loop_id,
        alignment_score,
        drift_score,
        previous_fatigue
    )
    
    # Apply override if provided
    if override_fatigue and fatigue_result["threshold_exceeded"]:
        fatigue_result["force_finalize"] = False
        fatigue_result["overridden"] = True
    
    # Update the loop trace with the new fatigue information
    await update_loop_with_fatigue(loop_id, fatigue_result)
    
    return fatigue_result
