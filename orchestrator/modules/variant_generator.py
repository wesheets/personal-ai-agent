"""
Thought Variant Generator

This module generates multiple plan variations before executing, providing
alternative approaches with different tones, risk levels, and belief alignment scores.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import random

def generate_plan_variants(
    original_plan: Dict[str, Any],
    loop_id: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates multiple variations of a plan with different tones and approaches.
    
    Args:
        original_plan (Dict[str, Any]): The original plan to create variations from
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Dictionary containing the original plan and its variants
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "variants_count": 2,
            "tone_options": ["safe", "ambitious", "creative", "analytical", "cautious"],
            "min_belief_score": 0.6
        }
    
    # Skip generation if disabled
    if not config.get("enabled", True):
        return {
            "original_plan": original_plan,
            "variants": []
        }
    
    # Extract configuration options
    variants_count = min(config.get("variants_count", 2), 3)  # Cap at 3 variants
    tone_options = config.get("tone_options", ["safe", "ambitious", "creative", "analytical", "cautious"])
    min_belief_score = config.get("min_belief_score", 0.6)
    
    # Generate variants
    variants = []
    used_tones = set()
    
    for i in range(variants_count):
        # Create a variant
        variant = _create_plan_variant(
            original_plan,
            tone_options,
            used_tones,
            min_belief_score
        )
        
        # Add variant ID
        variant["plan_id"] = f"plan_{chr(97 + i)}"  # plan_a, plan_b, etc.
        
        # Add to variants list
        variants.append(variant)
        
        # Track used tone
        used_tones.add(variant["tone"])
    
    # Return original plan and variants
    return {
        "original_plan": original_plan,
        "variants": variants
    }

def _create_plan_variant(
    original_plan: Dict[str, Any],
    tone_options: List[str],
    used_tones: set,
    min_belief_score: float
) -> Dict[str, Any]:
    """
    Creates a single plan variant with a different tone and approach.
    
    Args:
        original_plan (Dict[str, Any]): The original plan
        tone_options (List[str]): Available tone options
        used_tones (set): Set of already used tones
        min_belief_score (float): Minimum belief alignment score
        
    Returns:
        Dict[str, Any]: A plan variant
    """
    # Select a tone that hasn't been used yet
    available_tones = [tone for tone in tone_options if tone not in used_tones]
    if not available_tones:
        available_tones = tone_options
    
    tone = random.choice(available_tones)
    
    # Calculate a belief score based on the tone
    # More conservative tones have higher belief scores
    belief_score_modifiers = {
        "safe": 0.15,
        "cautious": 0.1,
        "analytical": 0.05,
        "creative": -0.05,
        "ambitious": -0.1
    }
    
    base_belief_score = random.uniform(min_belief_score, 0.95)
    modifier = belief_score_modifiers.get(tone, 0)
    belief_score = min(max(base_belief_score + modifier, min_belief_score), 0.98)
    
    # Create variant with modified steps based on tone
    variant = {
        "tone": tone,
        "belief_score": round(belief_score, 2),
        "steps": _modify_steps_for_tone(original_plan.get("steps", []), tone)
    }
    
    return variant

def _modify_steps_for_tone(
    original_steps: List[Dict[str, Any]],
    tone: str
) -> List[Dict[str, Any]]:
    """
    Modifies plan steps based on the selected tone.
    
    Args:
        original_steps (List[Dict[str, Any]]): The original plan steps
        tone (str): The tone to apply
        
    Returns:
        List[Dict[str, Any]]: Modified plan steps
    """
    # Create a deep copy of the original steps
    modified_steps = []
    
    # Tone-specific modifications
    for step in original_steps:
        modified_step = step.copy()
        
        # Apply tone-specific modifications
        if tone == "safe":
            # Add verification steps
            if "verify" not in modified_step.get("description", "").lower():
                modified_step["description"] = f"{modified_step.get('description', '')} with careful verification"
        
        elif tone == "ambitious":
            # Make steps more aggressive/optimistic
            modified_step["description"] = modified_step.get("description", "").replace(
                "check", "quickly assess"
            ).replace(
                "verify", "confirm"
            ).replace(
                "carefully", "efficiently"
            )
        
        elif tone == "creative":
            # Add creative approaches
            modified_step["description"] = modified_step.get("description", "").replace(
                "implement", "creatively implement"
            ).replace(
                "create", "design and create"
            ).replace(
                "analyze", "explore and analyze"
            )
        
        elif tone == "analytical":
            # Add analytical components
            modified_step["description"] = modified_step.get("description", "").replace(
                "implement", "systematically implement"
            ).replace(
                "create", "methodically create"
            ).replace(
                "check", "thoroughly analyze"
            )
        
        elif tone == "cautious":
            # Add cautious elements
            modified_step["description"] = modified_step.get("description", "").replace(
                "implement", "carefully implement"
            ).replace(
                "create", "cautiously create"
            ).replace(
                "check", "meticulously verify"
            )
        
        modified_steps.append(modified_step)
    
    return modified_steps

def store_plan_variants(
    loop_id: str,
    variants_data: Dict[str, Any],
    memory: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Stores plan variants in memory.
    
    Args:
        loop_id (str): The loop identifier
        variants_data (Dict[str, Any]): The variants data to store
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Dict[str, Any]: Updated memory with plan variants
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Extract variants
    variants = variants_data.get("variants", [])
    
    # Create loop variants entry
    loop_variants = {
        "loop_id": loop_id,
        "loop_variants": [
            {
                "plan_id": variant["plan_id"],
                "tone": variant["tone"],
                "belief_score": variant["belief_score"]
            }
            for variant in variants
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Initialize loop_variants array if it doesn't exist
    if "loop_variants" not in updated_memory:
        updated_memory["loop_variants"] = []
    
    # Add loop variants to memory
    updated_memory["loop_variants"].append(loop_variants)
    
    return updated_memory

def process_plan_with_variant_generator(
    plan: Dict[str, Any],
    loop_id: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Processes a plan with the variant generator.
    
    Args:
        plan (Dict[str, Any]): The plan to process
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the processing, including updated memory with plan variants
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "variants_count": 2,
            "tone_options": ["safe", "ambitious", "creative", "analytical", "cautious"],
            "min_belief_score": 0.6
        }
    
    # Skip processing if disabled
    if not config.get("enabled", True):
        return {
            "status": "skipped",
            "memory": memory,
            "message": "Variant generator is disabled",
            "variants_count": 0
        }
    
    # Generate plan variants
    variants_data = generate_plan_variants(plan, loop_id, memory, config)
    
    # Store variants in memory
    updated_memory = store_plan_variants(loop_id, variants_data, memory)
    
    # Return result
    variants_count = len(variants_data.get("variants", []))
    return {
        "status": "generated",
        "memory": updated_memory,
        "message": f"Generated {variants_count} plan variants",
        "variants_count": variants_count,
        "variants_data": variants_data
    }
