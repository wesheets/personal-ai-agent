"""
Pessimist Bias Tracking Module

This module implements comprehensive bias tracking functionality for the pessimist agent,
allowing it to track bias tags across multiple loop iterations and detect patterns
of repeated bias.

The module maintains a history of bias occurrences, their severity, and their impact
on loop execution, enabling the system to detect when it's repeating the same mistakes.
"""

from typing import Dict, Any, List, Optional, Set
import asyncio
import json
from datetime import datetime

# Define bias tag categories for better organization
BIAS_CATEGORIES = {
    "cognitive": [
        "confirmation_bias",
        "anchoring_bias",
        "availability_bias",
        "hindsight_bias",
        "overconfidence",
        "recency_bias"
    ],
    "emotional": [
        "tone_exaggeration",
        "emotional_mismatch",
        "emotional_reasoning"
    ],
    "social": [
        "authority_bias",
        "groupthink",
        "stereotyping",
        "in_group_bias"
    ],
    "structural": [
        "framing_effect",
        "selection_bias",
        "sampling_bias",
        "survivorship_bias"
    ]
}

# Flatten the categories into a single set for easy lookup
ALL_BIAS_TAGS: Set[str] = set()
for category_tags in BIAS_CATEGORIES.values():
    ALL_BIAS_TAGS.update(category_tags)

# Mock function for reading from memory
# In a real implementation, this would read from a database or storage system
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    # Simulate memory read
    await asyncio.sleep(0.1)
    
    # Mock data for testing
    if key == "bias_history":
        return {
            "tone_exaggeration": {
                "occurrences": 3,
                "first_detected": "2025-04-20T10:00:00Z",
                "last_detected": "2025-04-21T14:30:00Z",
                "loops_affected": ["loop_001", "loop_001_r1", "loop_001_r2"],
                "severity_trend": [0.6, 0.7, 0.8],
                "category": "emotional"
            },
            "overconfidence": {
                "occurrences": 2,
                "first_detected": "2025-04-20T10:00:00Z",
                "last_detected": "2025-04-21T12:15:00Z",
                "loops_affected": ["loop_001", "loop_001_r1"],
                "severity_trend": [0.5, 0.4],
                "category": "cognitive"
            }
        }
    elif key.startswith("bias_tags["):
        loop_id = key.split("[")[1].split("]")[0]
        if loop_id == "loop_001":
            return {
                "tone_exaggeration": 1,
                "overconfidence": 1
            }
        elif loop_id == "loop_001_r1":
            return {
                "tone_exaggeration": 2,
                "overconfidence": 2
            }
        elif loop_id == "loop_001_r2":
            return {
                "tone_exaggeration": 3,
                "emotional_mismatch": 1
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

def get_bias_category(bias_tag: str) -> str:
    """
    Get the category of a bias tag.
    
    Args:
        bias_tag: The bias tag to categorize
        
    Returns:
        The category name, or "unknown" if not found
    """
    for category, tags in BIAS_CATEGORIES.items():
        if bias_tag in tags:
            return category
    return "unknown"

async def get_bias_history() -> Dict[str, Any]:
    """
    Get the global bias history across all loops.
    
    Returns:
        Dict mapping bias tags to their history
    """
    return await read_from_memory("bias_history") or {}

async def update_bias_history(
    loop_id: str,
    bias_tags: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Update the global bias history with new bias tags.
    
    Args:
        loop_id: The loop ID where these biases were detected
        bias_tags: List of bias tag objects with tag, severity, etc.
        
    Returns:
        The updated bias history
    """
    # Get the current bias history
    bias_history = await get_bias_history()
    
    # Current timestamp for updates
    now = datetime.utcnow().isoformat()
    
    # Update the history with new bias tags
    for bias_tag_obj in bias_tags:
        tag = bias_tag_obj["tag"]
        severity = bias_tag_obj["severity"]
        
        # If this is a new bias tag, initialize its history
        if tag not in bias_history:
            bias_history[tag] = {
                "occurrences": 0,
                "first_detected": now,
                "last_detected": now,
                "loops_affected": [],
                "severity_trend": [],
                "category": get_bias_category(tag)
            }
        
        # Update the bias tag history
        bias_history[tag]["occurrences"] += 1
        bias_history[tag]["last_detected"] = now
        
        if loop_id not in bias_history[tag]["loops_affected"]:
            bias_history[tag]["loops_affected"].append(loop_id)
        
        bias_history[tag]["severity_trend"].append(severity)
    
    # Store the updated bias history
    await write_to_memory("bias_history", bias_history)
    
    return bias_history

async def get_loop_bias_tags(loop_id: str) -> Dict[str, int]:
    """
    Get the bias tags for a specific loop.
    
    Args:
        loop_id: The loop ID to get bias tags for
        
    Returns:
        Dict mapping bias tags to their occurrence counts
    """
    return await read_from_memory(f"bias_tags[{loop_id}]") or {}

async def update_loop_bias_tags(
    loop_id: str,
    bias_tags: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Update the bias tags for a specific loop.
    
    Args:
        loop_id: The loop ID to update
        bias_tags: List of bias tag objects with tag, severity, etc.
        
    Returns:
        Dict mapping bias tags to their updated occurrence counts
    """
    # Get the current bias tags for this loop
    loop_bias_tags = await get_loop_bias_tags(loop_id)
    
    # Update the counts
    for bias_tag_obj in bias_tags:
        tag = bias_tag_obj["tag"]
        loop_bias_tags[tag] = loop_bias_tags.get(tag, 0) + 1
    
    # Store the updated bias tags
    await write_to_memory(f"bias_tags[{loop_id}]", loop_bias_tags)
    
    return loop_bias_tags

async def detect_bias_repetition(
    loop_id: str,
    bias_tags: List[Dict[str, Any]],
    threshold: int = 3
) -> Dict[str, Any]:
    """
    Detect if the same bias tags are being flagged repeatedly across loops.
    
    Args:
        loop_id: The current loop ID
        bias_tags: List of bias tag objects with tag, severity, etc.
        threshold: The number of repetitions that triggers an echo detection
        
    Returns:
        Dict with bias repetition detection results
    """
    # Get the global bias history
    bias_history = await get_bias_history()
    
    # Update the loop-specific bias tags
    loop_bias_tags = await update_loop_bias_tags(loop_id, bias_tags)
    
    # Update the global bias history
    bias_history = await update_bias_history(loop_id, bias_tags)
    
    # Check for repetition patterns
    repeated_tags = []
    repetition_counts = {}
    
    for bias_tag_obj in bias_tags:
        tag = bias_tag_obj["tag"]
        
        # Get the history for this tag
        tag_history = bias_history.get(tag, {})
        occurrences = tag_history.get("occurrences", 0)
        
        repetition_counts[tag] = occurrences
        
        if occurrences >= threshold:
            repeated_tags.append(tag)
    
    # Determine if bias repetition is present
    bias_repetition = len(repeated_tags) > 0
    
    return {
        "bias_repetition": bias_repetition,
        "repeated_tags": repeated_tags,
        "repetition_counts": repetition_counts,
        "threshold": threshold,
        "bias_echo": bias_repetition,  # For compatibility with existing code
        "trigger": "pessimist" if bias_repetition else None,
        "action": "halt_loop" if bias_repetition else None
    }

async def track_bias(
    loop_id: str,
    bias_tags: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Track bias tags for a loop and update all relevant history.
    
    This is the main entry point for bias tracking.
    
    Args:
        loop_id: The loop ID to track bias for
        bias_tags: List of bias tag objects with tag, severity, etc.
        
    Returns:
        Dict with bias tracking results
    """
    # Detect bias repetition
    repetition_result = await detect_bias_repetition(loop_id, bias_tags)
    
    # Create the tracking result
    result = {
        "loop_id": loop_id,
        "bias_tags": [tag_obj["tag"] for tag_obj in bias_tags],
        "bias_tags_detail": bias_tags,
        "bias_repetition": repetition_result["bias_repetition"],
        "repeated_tags": repetition_result["repeated_tags"],
        "repetition_counts": repetition_result["repetition_counts"],
        "bias_echo": repetition_result["bias_echo"],
        "action": repetition_result["action"]
    }
    
    # Store the result in memory
    await write_to_memory(f"bias_tracking[{loop_id}]", result)
    
    return result

async def get_bias_statistics() -> Dict[str, Any]:
    """
    Get statistics about bias across all loops.
    
    Returns:
        Dict with bias statistics
    """
    # Get the global bias history
    bias_history = await get_bias_history()
    
    # Calculate statistics
    total_biases = len(bias_history)
    total_occurrences = sum(tag_history.get("occurrences", 0) for tag_history in bias_history.values())
    
    # Count biases by category
    category_counts = {}
    for tag, tag_history in bias_history.items():
        category = tag_history.get("category", "unknown")
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Find most common biases
    most_common = sorted(
        [(tag, tag_history.get("occurrences", 0)) for tag, tag_history in bias_history.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    return {
        "total_biases": total_biases,
        "total_occurrences": total_occurrences,
        "category_counts": category_counts,
        "most_common": most_common
    }
