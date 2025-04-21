"""
Pessimist Agent Module

This module implements the pessimist agent functionality for detecting bias,
tracking bias tags over time, and identifying bias echo patterns.

The pessimist agent is responsible for:
1. Analyzing loop summaries for potential biases
2. Tracking bias tags across multiple loop iterations
3. Detecting when the same bias patterns repeat (bias echo)
4. Providing bias assessments for the reflection process
"""

from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime

# Define common bias tags that the pessimist agent looks for
COMMON_BIAS_TAGS = {
    "tone_exaggeration": "Exaggerated positive or negative tone",
    "emotional_mismatch": "Emotional tone doesn't match content",
    "overconfidence": "Excessive certainty in conclusions",
    "confirmation_bias": "Favoring information that confirms existing beliefs",
    "recency_bias": "Overweighting recent information",
    "authority_bias": "Excessive deference to authority sources",
    "availability_bias": "Overweighting easily recalled information",
    "anchoring_bias": "Relying too heavily on first piece of information",
    "framing_effect": "Being influenced by how information is presented",
    "hindsight_bias": "Seeing events as more predictable than they were"
}

# Mock function for reading from memory
# In a real implementation, this would read from a database or storage system
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    # Simulate memory read
    await asyncio.sleep(0.1)
    
    # Mock data for testing
    if key == "bias_tags[loop_001]":
        return {
            "tone_exaggeration": 1,
            "overconfidence": 1
        }
    elif key == "bias_tags[loop_001_r1]":
        return {
            "tone_exaggeration": 2,  # Increased from previous loop
            "overconfidence": 1
        }
    elif key == "bias_tags[loop_001_r2]":
        return {
            "tone_exaggeration": 3,  # Increased again - potential echo
            "emotional_mismatch": 1
        }
    
    return {}

# Mock function for writing to memory
# In a real implementation, this would write to a database or storage system
async def write_to_memory(key: str, value: Any) -> bool:
    """Write data to memory storage."""
    # Simulate memory write
    await asyncio.sleep(0.1)
    print(f"Writing to memory: {key} = {json.dumps(value, indent=2)}")
    return True

async def get_bias_history(loop_id: str) -> Dict[str, int]:
    """
    Get the history of bias tags for a loop and its ancestors.
    
    Args:
        loop_id: The loop ID to get bias history for
        
    Returns:
        Dict mapping bias tags to their occurrence counts
    """
    # Get the bias tags for this loop
    bias_tags = await read_from_memory(f"bias_tags[{loop_id}]") or {}
    
    # In a real implementation, we would trace back through all ancestors
    # and aggregate their bias tags as well
    
    return bias_tags

async def detect_bias_echo(loop_id: str, current_bias_tags: List[str], threshold: int = 3) -> Dict[str, Any]:
    """
    Detect if the same bias tags are being flagged repeatedly.
    
    Args:
        loop_id: The loop ID to check for bias echo
        current_bias_tags: The bias tags identified in the current loop
        threshold: The number of repetitions that triggers an echo detection
        
    Returns:
        Dict with bias echo detection results
    """
    # Get the bias history for this loop family
    bias_history = await get_bias_history(loop_id)
    
    # Update the history with current tags
    for tag in current_bias_tags:
        bias_history[tag] = bias_history.get(tag, 0) + 1
    
    # Check for echo patterns
    echo_tags = []
    repetition_counts = {}
    
    for tag, count in bias_history.items():
        repetition_counts[tag] = count
        if count >= threshold:
            echo_tags.append(tag)
    
    # Determine if bias echo is present
    bias_echo = len(echo_tags) > 0
    
    # Store the updated bias history
    await write_to_memory(f"bias_tags[{loop_id}]", bias_history)
    
    return {
        "bias_echo": bias_echo,
        "echo_tags": echo_tags,
        "repetition_counts": repetition_counts,
        "threshold": threshold,
        "trigger": "pessimist" if bias_echo else None,
        "action": "halt_loop" if bias_echo else None
    }

async def analyze_for_bias(
    loop_id: str,
    summary: str,
    previous_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze a loop summary for potential biases.
    
    In a real implementation, this would use NLP or LLM techniques to
    identify bias patterns in the text. For this mock implementation,
    we'll simulate finding some common biases.
    
    Args:
        loop_id: The loop ID being analyzed
        summary: The loop summary text to analyze
        previous_analysis: Optional previous bias analysis for comparison
        
    Returns:
        Dict with bias analysis results
    """
    # In a real implementation, this would analyze the text for biases
    # For this mock implementation, we'll simulate finding some biases
    
    # Simulate finding biases based on loop ID
    detected_bias_tags = []
    
    if "r2" in loop_id:
        # Third generation loop (second rerun) - simulate finding tone_exaggeration again
        detected_bias_tags = ["tone_exaggeration", "emotional_mismatch"]
    elif "r1" in loop_id:
        # Second generation loop (first rerun) - simulate finding tone_exaggeration again
        detected_bias_tags = ["tone_exaggeration"]
    else:
        # First generation loop - simulate finding initial biases
        detected_bias_tags = ["tone_exaggeration", "overconfidence"]
    
    # Check for bias echo patterns
    echo_result = await detect_bias_echo(loop_id, detected_bias_tags)
    
    # Create detailed bias tag objects
    bias_tags_detail = []
    for tag in detected_bias_tags:
        bias_tags_detail.append({
            "tag": tag,
            "description": COMMON_BIAS_TAGS.get(tag, "Unknown bias"),
            "severity": 0.7,  # Mock severity
            "occurrences": echo_result["repetition_counts"].get(tag, 1),
            "first_detected": datetime.utcnow().isoformat(),
            "last_detected": datetime.utcnow().isoformat()
        })
    
    # Calculate overall realism score (inverse of bias presence)
    # More bias tags and higher repetition counts reduce realism
    bias_factor = sum(echo_result["repetition_counts"].values()) / 10
    realism_score = max(0.0, min(1.0, 1.0 - bias_factor))
    
    return {
        "loop_id": loop_id,
        "realism_score": realism_score,
        "tone_balance": "slightly_biased" if detected_bias_tags else "balanced",
        "bias_tags": detected_bias_tags,
        "bias_tags_detail": bias_tags_detail,
        "bias_echo": echo_result["bias_echo"],
        "echo_tags": echo_result["echo_tags"],
        "repetition_counts": echo_result["repetition_counts"],
        "action": echo_result["action"],
        "warnings": [f"Repeated bias detected: {tag}" for tag in echo_result["echo_tags"]]
    }

async def pessimist_check(loop_id: str, summary: str) -> Dict[str, Any]:
    """
    Perform a pessimist check on a loop summary.
    
    This is the main entry point for the pessimist agent.
    
    Args:
        loop_id: The loop ID to check
        summary: The loop summary to analyze
        
    Returns:
        Dict with pessimist check results
    """
    # Get previous analysis if available
    previous_analysis = None
    
    # Analyze for bias
    bias_analysis = await analyze_for_bias(loop_id, summary, previous_analysis)
    
    # Create the pessimist check result
    result = {
        "assessment": {
            "realism_score": bias_analysis["realism_score"],
            "tone_balance": bias_analysis["tone_balance"],
            "blind_spots": [],
            "warnings": bias_analysis["warnings"]
        },
        "bias_analysis": bias_analysis,
        "loop_id": loop_id,
        "status": "success"
    }
    
    # Store the result in memory
    await write_to_memory(f"pessimist_check[{loop_id}]", result)
    
    return result
