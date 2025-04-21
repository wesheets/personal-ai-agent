"""
Persona Mode Loader and Switcher

This module enables Promethios to switch cognitive modes per loop,
injecting the appropriate orchestrator persona into memory and
controlling which Orchestrator subclass is used.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Define available persona modes
PERSONA_MODES = {
    "SAGE": {
        "description": "Reflective, philosophical mode focused on deep understanding and wisdom",
        "strengths": ["reflection", "philosophical_depth", "wisdom_extraction"],
        "ideal_for": ["complex_decisions", "ethical_dilemmas", "long_term_planning"]
    },
    "ARCHITECT": {
        "description": "Structured, systematic mode focused on building and designing",
        "strengths": ["system_design", "structured_thinking", "implementation_planning"],
        "ideal_for": ["software_development", "system_architecture", "technical_planning"]
    },
    "RESEARCHER": {
        "description": "Analytical, curious mode focused on exploration and discovery",
        "strengths": ["information_gathering", "hypothesis_testing", "pattern_recognition"],
        "ideal_for": ["data_analysis", "literature_review", "exploratory_research"]
    },
    "RITUALIST": {
        "description": "Process-oriented, disciplined mode focused on consistent execution",
        "strengths": ["process_optimization", "consistency", "reliability"],
        "ideal_for": ["repeated_tasks", "process_execution", "habit_formation"]
    },
    "INVENTOR": {
        "description": "Creative, innovative mode focused on novel solutions and ideas",
        "strengths": ["creative_thinking", "innovation", "unconventional_approaches"],
        "ideal_for": ["brainstorming", "problem_solving", "innovation_challenges"]
    }
}

def get_available_personas() -> Dict[str, Dict[str, Any]]:
    """
    Returns the available persona modes.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of available persona modes
    """
    return PERSONA_MODES

def select_persona_for_loop(
    loop_id: str,
    prompt: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Selects the appropriate persona for a loop based on the prompt and context.
    
    Args:
        loop_id (str): The loop identifier
        prompt (str): The user prompt
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Tuple[str, Dict[str, Any]]: Selected persona mode and its details
    """
    # Use default config if none provided
    if config is None:
        config = {
            "default_persona": "ARCHITECT",
            "auto_selection": True,
            "override_persona": None
        }
    
    # Check for override persona
    override_persona = config.get("override_persona")
    if override_persona and override_persona in PERSONA_MODES:
        return override_persona, PERSONA_MODES[override_persona]
    
    # If auto-selection is disabled, use default persona
    if not config.get("auto_selection", True):
        default_persona = config.get("default_persona", "ARCHITECT")
        if default_persona in PERSONA_MODES:
            return default_persona, PERSONA_MODES[default_persona]
        else:
            return "ARCHITECT", PERSONA_MODES["ARCHITECT"]
    
    # Auto-select persona based on prompt content and context
    persona_scores = _score_personas_for_prompt(prompt, memory)
    
    # Get the highest scoring persona
    selected_persona = max(persona_scores.items(), key=lambda x: x[1])[0]
    
    return selected_persona, PERSONA_MODES[selected_persona]

def _score_personas_for_prompt(prompt: str, memory: Dict[str, Any]) -> Dict[str, float]:
    """
    Scores each persona based on how well it matches the prompt.
    
    Args:
        prompt (str): The user prompt
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Dict[str, float]: Dictionary of persona scores
    """
    # Initialize scores
    scores = {persona: 0.0 for persona in PERSONA_MODES}
    
    # Convert prompt to lowercase for case-insensitive matching
    prompt_lower = prompt.lower()
    
    # Keywords that indicate different personas
    keywords = {
        "SAGE": ["reflect", "philosophy", "wisdom", "understand", "meaning", "ethical", "consider", "perspective"],
        "ARCHITECT": ["build", "design", "structure", "implement", "architecture", "system", "organize", "plan"],
        "RESEARCHER": ["research", "analyze", "investigate", "explore", "data", "information", "discover", "study"],
        "RITUALIST": ["process", "routine", "consistent", "repeat", "habit", "discipline", "regular", "procedure"],
        "INVENTOR": ["create", "innovate", "novel", "idea", "brainstorm", "creative", "invent", "solution"]
    }
    
    # Score based on keyword matches
    for persona, words in keywords.items():
        for word in words:
            if word in prompt_lower:
                scores[persona] += 0.2
    
    # Score based on prompt length (longer prompts favor RESEARCHER and SAGE)
    word_count = len(prompt.split())
    if word_count > 100:
        scores["RESEARCHER"] += 0.3
        scores["SAGE"] += 0.2
    elif word_count > 50:
        scores["RESEARCHER"] += 0.2
        scores["SAGE"] += 0.1
    elif word_count < 20:
        scores["RITUALIST"] += 0.2
        scores["ARCHITECT"] += 0.1
    
    # Score based on question marks (more questions favor RESEARCHER)
    question_count = prompt.count("?")
    if question_count >= 3:
        scores["RESEARCHER"] += 0.3
    elif question_count >= 1:
        scores["RESEARCHER"] += 0.1
        scores["SAGE"] += 0.1
    
    # Score based on exclamation marks (excitement favors INVENTOR)
    if prompt.count("!") >= 2:
        scores["INVENTOR"] += 0.2
    
    # Score based on recent loop history
    if "loops" in memory:
        recent_loops = memory["loops"][-5:] if len(memory["loops"]) > 5 else memory["loops"]
        
        # Check for repeated similar prompts (favors RITUALIST)
        if len(recent_loops) >= 3:
            similar_prompts = 0
            for loop in recent_loops:
                if "prompt" in loop and _calculate_similarity(prompt, loop["prompt"]) > 0.7:
                    similar_prompts += 1
            
            if similar_prompts >= 2:
                scores["RITUALIST"] += 0.3
        
        # Check for creative outputs in recent loops (favors INVENTOR)
        creative_outputs = 0
        for loop in recent_loops:
            if "output" in loop and any(word in loop["output"].lower() for word in ["create", "design", "new", "innovative"]):
                creative_outputs += 1
        
        if creative_outputs >= 2:
            scores["INVENTOR"] += 0.2
    
    # Ensure minimum score difference for clear selection
    max_score = max(scores.values())
    for persona in scores:
        if scores[persona] > max_score - 0.2:
            scores[persona] = max_score  # Boost close scores to create clearer selection
    
    return scores

def _calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculates a simple similarity score between two texts.
    
    Args:
        text1 (str): First text
        text2 (str): Second text
        
    Returns:
        float: Similarity score between 0 and 1
    """
    # Convert to lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def load_persona(
    persona_mode: str,
    loop_id: str,
    memory: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Loads a persona into memory for the current loop.
    
    Args:
        persona_mode (str): The persona mode to load
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Dict[str, Any]: Updated memory with persona context
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Get persona details
    persona_details = PERSONA_MODES.get(persona_mode, PERSONA_MODES["ARCHITECT"])
    
    # Create persona context
    persona_context = {
        "loop_id": loop_id,
        "persona_mode": persona_mode,
        "description": persona_details["description"],
        "strengths": persona_details["strengths"],
        "ideal_for": persona_details["ideal_for"],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Initialize persona_contexts if it doesn't exist
    if "persona_contexts" not in updated_memory:
        updated_memory["persona_contexts"] = []
    
    # Add persona context to memory
    updated_memory["persona_contexts"].append(persona_context)
    
    # Set current orchestrator persona
    updated_memory["orchestrator_persona"] = persona_mode
    
    return updated_memory

def switch_persona(
    new_persona: str,
    loop_id: str,
    memory: Dict[str, Any],
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Switches to a new persona and logs the switch event.
    
    Args:
        new_persona (str): The new persona to switch to
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        reason (Optional[str]): Reason for the switch
        
    Returns:
        Dict[str, Any]: Updated memory with new persona and switch event
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Get current persona
    current_persona = updated_memory.get("orchestrator_persona", "ARCHITECT")
    
    # Skip if already using the requested persona
    if current_persona == new_persona:
        return updated_memory
    
    # Create switch event
    switch_event = {
        "loop_id": loop_id,
        "from_persona": current_persona,
        "to_persona": new_persona,
        "reason": reason or "Manual switch",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Initialize persona_switches if it doesn't exist
    if "persona_switches" not in updated_memory:
        updated_memory["persona_switches"] = []
    
    # Add switch event to memory
    updated_memory["persona_switches"].append(switch_event)
    
    # Load the new persona
    updated_memory = load_persona(new_persona, loop_id, updated_memory)
    
    return updated_memory

def process_loop_with_persona_loader(
    loop_id: str,
    prompt: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Processes a loop with the persona loader and switcher.
    
    Args:
        loop_id (str): The loop identifier
        prompt (str): The user prompt
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the processing, including updated memory with persona context
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "default_persona": "ARCHITECT",
            "auto_selection": True,
            "override_persona": None
        }
    
    # Skip processing if disabled
    if not config.get("enabled", True):
        return {
            "status": "skipped",
            "memory": memory,
            "message": "Persona loader is disabled",
            "persona": memory.get("orchestrator_persona", "ARCHITECT")
        }
    
    # Select persona for the loop
    selected_persona, persona_details = select_persona_for_loop(
        loop_id,
        prompt,
        memory,
        config
    )
    
    # Load persona into memory
    updated_memory = load_persona(selected_persona, loop_id, memory)
    
    # Return result
    return {
        "status": "loaded",
        "memory": updated_memory,
        "message": f"Loaded {selected_persona} persona",
        "persona": selected_persona,
        "details": persona_details
    }
