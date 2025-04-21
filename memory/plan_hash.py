"""
Plan Hash Module

This module provides functionality for generating and comparing hashes of plans
to identify similar patterns and prevent repeated failures.
"""

import hashlib
import json
from typing import Dict, List, Any, Optional

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
    
    # Apply a non-linear scaling to increase similarity scores
    # This gives more weight to matching bits, making similar plans appear more similar
    raw_similarity = matches / 256
    
    # Apply non-linear scaling to boost similarity scores
    # This formula increases scores in the middle range while preserving 0.0 and 1.0
    boosted_similarity = raw_similarity ** 0.5
    
    return boosted_similarity

def get_rejected_plans(memory: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Retrieves rejected plans from memory.
    
    Args:
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        List[Dict[str, Any]]: List of rejected plans with their hashes
    """
    return memory.get("rejected_plans", [])

def find_similar_plans(
    plan_hash: str, 
    memory: Dict[str, Any],
    similarity_threshold: float = 0.85
) -> List[Dict[str, Any]]:
    """
    Finds plans in memory that are similar to the given hash.
    
    Args:
        plan_hash (str): Hash of the plan to compare
        memory (Dict[str, Any]): The memory dictionary
        similarity_threshold (float): Threshold above which plans are considered similar
        
    Returns:
        List[Dict[str, Any]]: List of similar plans with similarity scores
    """
    rejected_plans = get_rejected_plans(memory)
    similar_plans = []
    
    for plan in rejected_plans:
        plan_hash_from_memory = plan.get("hash", "")
        if not plan_hash_from_memory:
            continue
            
        similarity = get_plan_similarity(plan_hash, plan_hash_from_memory)
        
        if similarity >= similarity_threshold:
            similar_plans.append({
                "plan": plan,
                "similarity_score": similarity
            })
    
    # Sort by similarity score (highest first)
    similar_plans.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return similar_plans
