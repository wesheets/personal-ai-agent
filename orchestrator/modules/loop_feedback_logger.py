"""
Loop Feedback Logger Module

This module implements functionality for tracking when a completed loop is rejected, revised, 
or rescored by the Operator after the fact. It enables:
- Trust scoring adjustments
- Reflection invalidation
- Loop confidence decay
- Future loop plan adjustment based on feedback
"""

import datetime
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def record_loop_feedback(memory: Dict[str, Any], project_id: str, loop_id: int, feedback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Records operator feedback for a completed loop.
    
    Args:
        memory: The memory dictionary
        project_id: The ID of the project
        loop_id: The ID of the loop receiving feedback
        feedback: Dictionary containing feedback details
            Required keys:
                - status: One of "rejected", "revised", "rescored"
                - reason: Brief reason for the feedback
            Optional keys:
                - reflection_invalidated: Boolean indicating if reflection should be invalidated
                - operator_notes: Detailed notes from the operator
                - timestamp: ISO format timestamp (will be generated if not provided)
    
    Returns:
        The recorded feedback entry
    
    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Validate required fields
    if not isinstance(loop_id, int):
        raise ValueError(f"loop_id must be an integer, got {type(loop_id)}")
    
    required_fields = ["status", "reason"]
    for field in required_fields:
        if field not in feedback:
            raise ValueError(f"Missing required field '{field}' in feedback")
    
    # Validate status
    valid_statuses = ["rejected", "revised", "rescored"]
    if feedback["status"] not in valid_statuses:
        raise ValueError(f"Invalid status '{feedback['status']}'. Must be one of: {', '.join(valid_statuses)}")
    
    # Prepare feedback entry
    feedback_entry = {
        "loop_id": loop_id,
        "status": feedback["status"],
        "reason": feedback["reason"],
        "reflection_invalidated": feedback.get("reflection_invalidated", False),
        "operator_notes": feedback.get("operator_notes", ""),
        "timestamp": feedback.get("timestamp", datetime.datetime.utcnow().isoformat() + "Z")
    }
    
    # Initialize memory structures if they don't exist
    if "loop_feedback" not in memory:
        memory["loop_feedback"] = []
    
    # Store feedback in memory
    memory["loop_feedback"].append(feedback_entry)
    
    # Store feedback in loop trace
    if "loop_trace" not in memory:
        memory["loop_trace"] = {}
    
    if loop_id not in memory["loop_trace"]:
        memory["loop_trace"][loop_id] = {}
    
    if "feedback" not in memory["loop_trace"][loop_id]:
        memory["loop_trace"][loop_id]["feedback"] = []
    
    memory["loop_trace"][loop_id]["feedback"].append(feedback_entry)
    
    # Log the feedback event
    logger.info(f"Recorded feedback for loop {loop_id}: {feedback['status']} - {feedback['reason']}")
    
    # If reflection is invalidated, update reflection status
    if feedback_entry["reflection_invalidated"]:
        invalidate_loop_reflection(memory, loop_id)
    
    # Add CTO warning if this is a rejection
    if feedback["status"] == "rejected":
        if "cto_warnings" not in memory:
            memory["cto_warnings"] = []
        
        warning = {
            "type": "loop_rejection",
            "loop_id": loop_id,
            "reason": feedback["reason"],
            "timestamp": feedback_entry["timestamp"]
        }
        memory["cto_warnings"].append(warning)
        logger.warning(f"CTO Warning: Loop {loop_id} rejected - {feedback['reason']}")
    
    # Return the recorded feedback entry
    return feedback_entry

def invalidate_loop_reflection(memory: Dict[str, Any], loop_id: int) -> bool:
    """
    Marks a loop's reflection as retracted/invalidated.
    
    Args:
        memory: The memory dictionary
        loop_id: The ID of the loop whose reflection should be invalidated
    
    Returns:
        Boolean indicating success of the operation
    """
    # Check if reflections exist in memory
    if "reflection" not in memory:
        logger.warning(f"No reflections found in memory when trying to invalidate loop {loop_id}")
        return False
    
    # Check if the specific loop reflection exists
    if loop_id not in memory["reflection"]:
        logger.warning(f"No reflection found for loop {loop_id}")
        return False
    
    # Update the reflection status
    memory["reflection"][loop_id]["status"] = "retracted"
    
    # Update timestamp
    memory["reflection"][loop_id]["retraction_timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    
    # Log the invalidation
    logger.info(f"Invalidated reflection for loop {loop_id}")
    
    # Also update in loop trace if it exists
    if "loop_trace" in memory and loop_id in memory["loop_trace"]:
        if "reflection" in memory["loop_trace"][loop_id]:
            memory["loop_trace"][loop_id]["reflection"]["status"] = "retracted"
            memory["loop_trace"][loop_id]["reflection"]["retraction_timestamp"] = memory["reflection"][loop_id]["retraction_timestamp"]
    
    return True

def log_feedback_to_agent_performance(memory: Dict[str, Any], agent: str, loop_id: int, impact: float) -> Dict[str, Any]:
    """
    Updates agent performance metrics based on operator feedback.
    
    Args:
        memory: The memory dictionary
        agent: The agent identifier
        loop_id: The loop ID that received feedback
        impact: A float between -1.0 and 1.0 indicating the impact on trust
                (-1.0 = severe negative impact, 0 = neutral, 1.0 = positive impact)
    
    Returns:
        Updated agent performance metrics
    
    Raises:
        ValueError: If impact is outside the valid range or agent is invalid
    """
    # Validate inputs
    if not isinstance(agent, str) or not agent:
        raise ValueError("Agent must be a non-empty string")
    
    if not isinstance(impact, (int, float)):
        raise ValueError(f"Impact must be a number, got {type(impact)}")
    
    if impact < -1.0 or impact > 1.0:
        raise ValueError(f"Impact must be between -1.0 and 1.0, got {impact}")
    
    # Initialize agent performance tracking if it doesn't exist
    if "agent_performance" not in memory:
        memory["agent_performance"] = {}
    
    if agent not in memory["agent_performance"]:
        memory["agent_performance"][agent] = {
            "trust_score": 0.5,  # Initial trust score (0.0 to 1.0)
            "rejection_count": 0,
            "revision_count": 0,
            "success_count": 0,
            "feedback_history": []
        }
    
    agent_perf = memory["agent_performance"][agent]
    
    # Update metrics based on impact
    if impact < 0:
        # Negative impact increases rejection count
        agent_perf["rejection_count"] += 1
    elif impact > 0:
        # Positive impact increases success count
        agent_perf["success_count"] += 1
    else:
        # Neutral impact (likely a revision)
        agent_perf["revision_count"] += 1
    
    # Update trust score (bounded between 0.0 and 1.0)
    # The formula applies a weighted adjustment based on current trust level
    # Higher trust scores are harder to maintain and easier to lose
    current_trust = agent_perf["trust_score"]
    
    if impact < 0:
        # Negative feedback has more impact on high-trust agents
        adjustment = impact * (0.1 + current_trust * 0.2)
    else:
        # Positive feedback has more impact on low-trust agents
        adjustment = impact * (0.1 + (1 - current_trust) * 0.1)
    
    agent_perf["trust_score"] = max(0.0, min(1.0, current_trust + adjustment))
    
    # Record feedback in history
    feedback_record = {
        "loop_id": loop_id,
        "impact": impact,
        "trust_before": current_trust,
        "trust_after": agent_perf["trust_score"],
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    agent_perf["feedback_history"].append(feedback_record)
    
    # Log the trust adjustment
    logger.info(f"Updated trust score for agent {agent}: {current_trust:.2f} → {agent_perf['trust_score']:.2f} (impact: {impact:.2f})")
    
    return agent_perf
