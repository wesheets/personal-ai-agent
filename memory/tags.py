"""
Memory Tags Module

This module defines standard memory tags used throughout the system,
including bias tags for the Pessimist Agent.
"""

from typing import Dict, List, Any

# Standard memory tags
MEMORY_TAGS = {
    "priority": ["high", "medium", "low"],
    "status": ["pending", "in_progress", "completed", "blocked", "failed"],
    "type": ["task", "conversation", "decision", "reflection", "plan"],
    "visibility": ["public", "private", "restricted"],
    "source": ["user", "agent", "system", "external"]
}

# Bias tags for Pessimist Agent
BIAS_TAGS = {
    # Optimism-related biases
    "optimism_bias": {
        "description": "Tendency to overestimate positive outcomes and underestimate negative ones",
        "indicators": ["successfully", "easily", "quickly", "perfectly", "completely"],
        "severity": "medium"
    },
    "vague_summary": {
        "description": "Using imprecise language to obscure lack of concrete progress",
        "indicators": ["made progress", "worked on", "continued", "advanced", "moved forward"],
        "severity": "medium"
    },
    "overconfidence": {
        "description": "Excessive certainty in abilities or outcomes despite evidence",
        "indicators": ["definitely", "certainly", "absolutely", "without any issues", "guaranteed"],
        "severity": "high"
    },
    
    # Feedback-related biases
    "feedback_dismissal": {
        "description": "Ignoring or minimizing negative feedback",
        "indicators": ["minor issue", "small problem", "not significant", "easily fixed"],
        "severity": "high"
    },
    
    # Planning-related biases
    "timeline_compression": {
        "description": "Unrealistic compression of time needed for tasks",
        "indicators": ["quickly", "rapidly", "fast", "immediate", "instant"],
        "severity": "medium"
    },
    "scope_creep": {
        "description": "Expanding scope without acknowledging increased complexity",
        "indicators": ["also added", "additionally", "expanded", "enhanced", "extra features"],
        "severity": "medium"
    },
    
    # Achievement-related biases
    "achievement_inflation": {
        "description": "Exaggerating the significance of accomplishments",
        "indicators": ["groundbreaking", "revolutionary", "exceptional", "outstanding", "remarkable"],
        "severity": "medium"
    },
    
    # Risk-related biases
    "complexity_underestimation": {
        "description": "Underestimating the complexity of tasks or problems",
        "indicators": ["simple", "straightforward", "basic", "elementary", "trivial"],
        "severity": "high"
    },
    "risk_blindness": {
        "description": "Failing to acknowledge or address potential risks",
        "indicators": ["no risks", "no issues", "no problems", "smooth", "seamless"],
        "severity": "high"
    }
}

def get_bias_tag_list() -> List[str]:
    """
    Returns a list of all available bias tags.
    
    Returns:
        List[str]: List of bias tag names
    """
    return list(BIAS_TAGS.keys())

def get_bias_tag_info(tag_name: str) -> Dict[str, Any]:
    """
    Returns information about a specific bias tag.
    
    Args:
        tag_name (str): Name of the bias tag
        
    Returns:
        Dict[str, Any]: Information about the bias tag or empty dict if not found
    """
    return BIAS_TAGS.get(tag_name, {})

def get_bias_indicators() -> Dict[str, List[str]]:
    """
    Returns a mapping of bias tags to their indicator phrases.
    
    Returns:
        Dict[str, List[str]]: Mapping of bias tags to indicator phrases
    """
    return {tag: info["indicators"] for tag, info in BIAS_TAGS.items()}

def get_bias_severity(tag_name: str) -> str:
    """
    Returns the severity level of a specific bias tag.
    
    Args:
        tag_name (str): Name of the bias tag
        
    Returns:
        str: Severity level ("low", "medium", "high") or "unknown" if not found
    """
    tag_info = BIAS_TAGS.get(tag_name, {})
    return tag_info.get("severity", "unknown")
