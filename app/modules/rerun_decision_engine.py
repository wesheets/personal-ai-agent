"""
Rerun Decision Engine Module

This module is responsible for determining whether to rerun a loop based on
alignment scores, drift scores, and other metrics from the reflection process.
"""

from typing import Dict, Any, Optional
import asyncio
import json
import re
from app.utils.persona_utils import get_current_persona, preload_persona_for_deep_loop

# Configuration for rerun thresholds
# These could be moved to a config file in a real implementation
RERUN_CONFIG = {
    "alignment_threshold": 0.75,  # Minimum alignment score to avoid rerun
    "drift_threshold": 0.25,      # Maximum drift score to avoid rerun
    "max_reruns": 3,              # Maximum number of reruns for a single loop
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
            "orchestrator_persona": "SAGE"
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
                "orchestrator_persona": "SAGE"
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

async def evaluate_rerun_decision(
    loop_id: str, 
    alignment_score: float, 
    drift_score: float,
    summary_valid: bool
) -> Dict[str, Any]:
    """
    Evaluate whether to rerun a loop based on alignment and drift scores.
    
    This function:
    1. Checks if alignment score is below threshold
    2. Checks if drift score is above threshold
    3. Checks if the loop has already been rerun too many times
    4. If rerun is needed, creates a new loop ID and copies trace
    
    Args:
        loop_id: The ID of the loop to evaluate
        alignment_score: The alignment score from reflection (0.0-1.0)
        drift_score: The drift score from reflection (0.0-1.0)
        summary_valid: Whether the summary is valid
        
    Returns:
        Dict containing the decision and related information
    """
    # Check if rerun is needed based on thresholds
    rerun_needed = False
    rerun_reason = None
    
    if alignment_score < RERUN_CONFIG["alignment_threshold"]:
        rerun_needed = True
        rerun_reason = "alignment_threshold_not_met"
    elif drift_score > RERUN_CONFIG["drift_threshold"]:
        rerun_needed = True
        rerun_reason = "drift_threshold_exceeded"
    elif not summary_valid:
        rerun_needed = True
        rerun_reason = "summary_invalid"
    
    # Check if we've already hit the maximum number of reruns
    current_rerun_num = get_rerun_number(loop_id)
    if current_rerun_num >= RERUN_CONFIG["max_reruns"]:
        rerun_needed = False
        rerun_reason = "max_reruns_reached"
    
    # If rerun is needed, prepare the new loop
    if rerun_needed:
        # Generate the next loop ID
        next_loop_id = generate_next_loop_id(loop_id)
        
        # Read the current loop trace
        current_trace = await read_from_memory(f"loop_trace[{loop_id}]")
        
        if current_trace:
            # Get the current persona or preload for deep loop
            orchestrator_persona = preload_persona_for_deep_loop(loop_id, current_rerun_num + 1)
            
            # Create a new trace for the rerun
            new_trace = {
                "loop_id": next_loop_id,
                "rerun_of": loop_id,
                "rerun_reason": rerun_reason,
                "status": "pending",
                "timestamp": "2025-04-21T12:45:00Z",  # This would be the current time in a real implementation
                "depth": "deep",  # As specified in requirements
                "orchestrator_persona": orchestrator_persona,  # Include persona in rerun
                "rerun_depth": current_rerun_num + 1
            }
            
            # Store the new trace
            await write_to_memory(f"loop_trace[{next_loop_id}]", new_trace)
            
            return {
                "decision": "rerun",
                "original_loop_id": loop_id,
                "new_loop_id": next_loop_id,
                "rerun_reason": rerun_reason,
                "rerun_number": current_rerun_num + 1,
                "orchestrator_persona": orchestrator_persona  # Include persona in response
            }
    
    # If no rerun is needed, finalize the loop
    await write_to_memory(f"loop_trace[{loop_id}].status", "finalized")
    
    # Get the current persona
    orchestrator_persona = get_current_persona(loop_id)
    
    return {
        "decision": "finalize",
        "loop_id": loop_id,
        "reason": rerun_reason if rerun_reason == "max_reruns_reached" else "no_issues_detected",
        "orchestrator_persona": orchestrator_persona  # Include persona in response
    }
