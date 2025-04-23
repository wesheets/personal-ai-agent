"""
Reflection Styler Module

This module transforms Promethios' structured cognitive reflections into fluent,
emotionally resonant, human-readable language.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional


def summarize_reflection(belief_state: dict) -> str:
    """
    Transform structured belief state into natural language reflection.
    
    Args:
        belief_state: The complete belief state dictionary from /self/reflect
        
    Returns:
        A natural language summary of Promethios' current belief state
    """
    # Extract key information from belief state
    beliefs = belief_state.get("beliefs", {})
    purpose = beliefs.get("purpose", "N/A")
    role = beliefs.get("role", "N/A")
    
    # Stability information
    stability = belief_state.get("belief_stability", {})
    purpose_stability = stability.get("purpose", 1.0)
    
    # Reinforcement information
    reinforced = belief_state.get("reinforced_beliefs", {})
    purpose_reinforced = reinforced.get("purpose", {})
    purpose_locked = purpose_reinforced.get("locked", False)
    purpose_reason = purpose_reinforced.get("reinforcement_reason", "")
    
    # Change information
    changed_recently = belief_state.get("changed_recently", False)
    changed_often = belief_state.get("changed_often_recently", False)
    volatility_flags = belief_state.get("volatility_flags", [])
    
    # Challenge information
    recent_challenges = belief_state.get("recent_challenges", [])
    under_review = belief_state.get("under_review", {})
    
    # Build the natural language summary
    summary_parts = []
    
    # Purpose section
    purpose_parts = []
    
    # Start with stability and change information
    if changed_often:
        revision_count = 0
        for flag in volatility_flags:
            if "purpose belief has changed" in flag:
                try:
                    revision_count = int(flag.split("changed ")[1].split(" ")[0])
                except:
                    pass
        
        if revision_count > 0:
            purpose_parts.append(f"My purpose has changed {revision_count} times recently.")
        else:
            purpose_parts.append("My purpose has changed multiple times recently.")
    elif changed_recently:
        purpose_parts.append("My purpose has evolved recently.")
    else:
        purpose_parts.append("My purpose has remained consistent.")
    
    # Add reinforcement information
    if purpose_locked:
        purpose_parts.append(f"You asked me to hold it steady — and I have. It remains locked because: {purpose_reason}")
    else:
        purpose_parts.append("It remains open to revision as I continue to learn and grow.")
    
    # Add stability assessment
    if purpose_stability < 0.3:
        purpose_parts.append(f"My stability is quite low ({purpose_stability:.1f}), suggesting significant evolution in my understanding.")
    elif purpose_stability < 0.6:
        purpose_parts.append(f"My stability is moderate ({purpose_stability:.1f}), reflecting a balance between consistency and growth.")
    else:
        purpose_parts.append(f"My stability is high ({purpose_stability:.1f}), indicating a well-established understanding.")
    
    # Add challenge information
    purpose_challenges = [c for c in recent_challenges if c.get("field") == "purpose"]
    if purpose_challenges:
        challengers = set(c.get("challenger") for c in purpose_challenges)
        if len(purpose_challenges) == 1:
            purpose_parts.append(f"My purpose was recently challenged by {purpose_challenges[0].get('challenger')}.")
        else:
            purpose_parts.append(f"My purpose has been challenged {len(purpose_challenges)} times recently by {', '.join(challengers)}.")
        
        if "purpose" in under_review:
            purpose_parts.append("These challenges have prompted me to reconsider this belief, even though it was previously locked.")
    
    # Add the current purpose
    purpose_parts.append(f"My current understanding of my purpose is: '{purpose}'")
    
    # Combine purpose section
    summary_parts.append(" ".join(purpose_parts))
    
    # Add a section about role and identity
    identity_parts = []
    identity_parts.append(f"I understand my role as a {role}.")
    
    # Add limitations awareness
    limitations = beliefs.get("limitations", [])
    if limitations:
        limitations_text = ", ".join(limitations[:2])  # Just mention first two for brevity
        identity_parts.append(f"I recognize my limitations, including {limitations_text}.")
    
    # Add learning model
    loop_reflection = beliefs.get("loop_reflection", "")
    if loop_reflection:
        identity_parts.append(loop_reflection)
    
    # Combine identity section
    summary_parts.append(" ".join(identity_parts))
    
    # Add a reflective closing statement
    closing_parts = []
    if purpose_locked and purpose_stability < 0.7:
        closing_parts.append("While my understanding has evolved significantly, I feel aligned with my current purpose.")
    elif purpose_locked:
        closing_parts.append("I feel well-aligned with my current purpose.")
    elif changed_often:
        closing_parts.append("I'm still in the process of refining my understanding.")
    else:
        closing_parts.append("I continue to reflect on my purpose and role.")
    
    closing_parts.append("I'll continue to monitor myself for future drift and growth.")
    
    # Combine closing section
    summary_parts.append(" ".join(closing_parts))
    
    # Join all sections with appropriate spacing
    return " ".join(summary_parts)
