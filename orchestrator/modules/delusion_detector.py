"""
Delusion Detection Module

This module provides functionality to detect repeated plan patterns that have previously failed,
helping to prevent the system from falling into loops of similar failed approaches.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

def generate_plan_hash(plan: Dict[str, Any]) -> str:
    """
    Generates a hash for a plan to identify similar plans.
    
    Args:
        plan (Dict[str, Any]): The plan to hash
        
    Returns:
        str: A hash string that uniquely identifies the plan structure
    """
    # Extract key elements from the plan that define its structure
    plan_elements = {
        "steps": [step.get("description", "") for step in plan.get("steps", [])],
        "goal": plan.get("goal", ""),
        "approach": plan.get("approach", "")
    }
    
    # Convert to a stable string representation
    plan_str = json.dumps(plan_elements, sort_keys=True)
    
    # Generate hash
    hash_obj = hashlib.sha256(plan_str.encode())
    return hash_obj.hexdigest()

def get_plan_similarity(hash1: str, hash2: str) -> float:
    """
    Calculates similarity between two plan hashes.
    
    Args:
        hash1 (str): First plan hash
        hash2 (str): Second plan hash
        
    Returns:
        float: Similarity score between 0.0 and 1.0
    """
    # If hashes are identical, return 1.0
    if hash1 == hash2:
        return 1.0
    
    # Convert hashes to binary representation
    bin1 = bin(int(hash1, 16))[2:].zfill(256)
    bin2 = bin(int(hash2, 16))[2:].zfill(256)
    
    # Count matching bits
    matches = sum(b1 == b2 for b1, b2 in zip(bin1, bin2))
    
    # Apply a stronger non-linear scaling to increase similarity scores
    raw_similarity = matches / 256
    
    # Apply cubic root scaling to significantly boost similarity scores
    # This formula dramatically increases scores in the middle range
    boosted_similarity = raw_similarity ** (1/3)
    
    return boosted_similarity

def compare_to_rejected_hashes(
    current_hash: str, 
    rejected_plans: List[Dict[str, Any]],
    similarity_threshold: float = 0.85
) -> Optional[Dict[str, Any]]:
    """
    Compares a plan hash to previously rejected plan hashes.
    
    Args:
        current_hash (str): Hash of the current plan
        rejected_plans (List[Dict[str, Any]]): List of previously rejected plans with their hashes
        similarity_threshold (float): Threshold above which plans are considered similar
        
    Returns:
        Optional[Dict[str, Any]]: Most similar rejected plan if similarity is above threshold, None otherwise
    """
    most_similar = None
    highest_similarity = 0.0
    
    for rejected_plan in rejected_plans:
        rejected_hash = rejected_plan.get("hash", "")
        if not rejected_hash:
            continue
        
        similarity = get_plan_similarity(current_hash, rejected_hash)
        
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_similar = rejected_plan
    
    if highest_similarity >= similarity_threshold:
        return {
            "rejected_plan": most_similar,
            "similarity_score": highest_similarity
        }
    
    return None

def inject_delusion_warning(
    memory: Dict[str, Any],
    loop_id: str,
    similar_plan: Dict[str, Any],
    similarity_score: float
) -> Dict[str, Any]:
    """
    Injects a delusion warning into memory.
    
    Args:
        memory (Dict[str, Any]): The memory dictionary to update
        loop_id (str): The current loop identifier
        similar_plan (Dict[str, Any]): The similar rejected plan
        similarity_score (float): The similarity score
        
    Returns:
        Dict[str, Any]: Updated memory dictionary
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Initialize delusion_alerts if it doesn't exist
    if "delusion_alerts" not in updated_memory:
        updated_memory["delusion_alerts"] = []
    
    # Create alert
    timestamp = datetime.utcnow().isoformat()
    similar_loop_id = similar_plan.get("loop_id", "unknown")
    failure_reason = similar_plan.get("failure_reason", "unknown reason")
    
    alert = {
        "loop_id": loop_id,
        "warning_type": "plan_repetition",
        "message": f"This plan resembles Loop {similar_loop_id}, which failed due to {failure_reason}.",
        "similarity_score": similarity_score,
        "timestamp": timestamp,
        "similar_loop_id": similar_loop_id,
        "failure_reason": failure_reason
    }
    
    # Add alert to delusion_alerts
    updated_memory["delusion_alerts"].append(alert)
    
    # Update loop metadata if it exists
    if "loop_trace" in updated_memory and loop_id in updated_memory["loop_trace"]:
        if "warnings" not in updated_memory["loop_trace"][loop_id]:
            updated_memory["loop_trace"][loop_id]["warnings"] = []
        
        updated_memory["loop_trace"][loop_id]["warnings"].append({
            "type": "delusion_warning",
            "timestamp": timestamp,
            "details": alert
        })
    
    return updated_memory

def detect_plan_delusion(
    plan: Dict[str, Any],
    loop_id: str,
    memory: Dict[str, Any],
    similarity_threshold: float = 0.85
) -> Dict[str, Any]:
    """
    Detects if a plan is similar to previously rejected plans and injects a warning if necessary.
    
    Args:
        plan (Dict[str, Any]): The plan to check
        loop_id (str): The current loop identifier
        memory (Dict[str, Any]): The memory dictionary
        similarity_threshold (float): Threshold above which plans are considered similar
        
    Returns:
        Dict[str, Any]: Updated memory dictionary, with warnings if delusion detected
    """
    # Generate hash for current plan
    current_hash = generate_plan_hash(plan)
    
    # Get rejected plans from memory
    rejected_plans = memory.get("rejected_plans", [])
    
    # Compare to rejected plans
    similar_result = compare_to_rejected_hashes(
        current_hash, 
        rejected_plans,
        similarity_threshold
    )
    
    # If similar plan found, inject warning
    if similar_result:
        similar_plan = similar_result["rejected_plan"]
        similarity_score = similar_result["similarity_score"]
        
        return inject_delusion_warning(
            memory,
            loop_id,
            similar_plan,
            similarity_score
        )
    
    # If no similar plan found, return memory unchanged
    return memory

def store_rejected_plan(
    plan: Dict[str, Any],
    loop_id: str,
    failure_reason: str,
    memory: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Stores a rejected plan in memory for future comparison.
    
    Args:
        plan (Dict[str, Any]): The rejected plan
        loop_id (str): The loop identifier
        failure_reason (str): The reason the plan failed
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Dict[str, Any]: Updated memory dictionary
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Initialize rejected_plans if it doesn't exist
    if "rejected_plans" not in updated_memory:
        updated_memory["rejected_plans"] = []
    
    # Generate hash for plan
    plan_hash = generate_plan_hash(plan)
    
    # Create rejected plan entry
    rejected_plan = {
        "loop_id": loop_id,
        "hash": plan_hash,
        "failure_reason": failure_reason,
        "timestamp": datetime.utcnow().isoformat(),
        "plan_summary": {
            "goal": plan.get("goal", ""),
            "steps_count": len(plan.get("steps", [])),
            "approach": plan.get("approach", "")
        }
    }
    
    # Add to rejected_plans
    updated_memory["rejected_plans"].append(rejected_plan)
    
    return updated_memory
