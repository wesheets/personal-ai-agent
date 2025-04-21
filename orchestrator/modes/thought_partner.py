"""
Orchestrator Thought Partner Mode

This module implements the Thought Partner Mode for the Orchestrator, enabling it to act as a
Socratic co-architect by analyzing prompts, asking clarifying questions, suggesting refinements,
and storing prompt memory for future reference.

Functions:
- analyze_prompt: Analyzes a prompt to determine intent, confidence, tone, and ambiguity
- generate_reflection_questions: Generates Socratic-style questions based on prompt analysis
- store_prompt_analysis: Stores prompt analysis in memory
- get_last_prompt_analysis: Retrieves the latest prompt analysis from memory
"""

import re
import json
import datetime
from typing import List, Dict, Any, Optional

# Constants for confidence thresholds
HIGH_CONFIDENCE = 0.8
MEDIUM_CONFIDENCE = 0.5
LOW_CONFIDENCE = 0.3

# Common ambiguous phrases that might need clarification
AMBIGUOUS_PHRASES = [
    "simple", "easy", "user-friendly", "intuitive", "clean", "modern",
    "efficient", "fast", "responsive", "dynamic", "flexible", "scalable",
    "robust", "secure", "reliable", "maintainable", "extensible",
    "filter", "sort", "search", "display", "show", "view", "interface",
    "dashboard", "panel", "screen", "page", "form", "input", "output",
    "data", "information", "content", "feature", "functionality"
]

# Emotional tone indicators
EMOTIONAL_TONES = {
    "excited": ["!", "amazing", "great", "awesome", "excited", "thrilled"],
    "urgent": ["asap", "urgent", "immediately", "quickly", "soon", "deadline"],
    "frustrated": ["frustrated", "annoying", "problem", "issue", "fix", "broken"],
    "curious": ["curious", "wonder", "interested", "question", "how about", "what if"],
    "reflective": ["think", "consider", "reflect", "ponder", "maybe", "perhaps"],
    "decisive": ["must", "should", "need to", "have to", "definitely", "absolutely"]
}

# Question templates for different ambiguous phrases
QUESTION_TEMPLATES = {
    "simple": [
        "When you say 'simple', do you mean minimal in design, easy to use, or limited in functionality?",
        "Could you elaborate on what 'simple' means in this context? Is it about visual design, user interaction, or feature set?"
    ],
    "filter": [
        "What kind of filtering capabilities are you looking for? Fixed options, range selection, or something else?",
        "When you mention 'filter', are you thinking of time-based filters, category filters, or attribute-based filtering?"
    ],
    "interface": [
        "What are the most important aspects of the interface for you? Aesthetics, ease of use, or information density?",
        "Could you describe your ideal interface in terms of layout, components, and user flow?"
    ],
    "dashboard": [
        "What key metrics or information should be prominently displayed on this dashboard?",
        "Is this dashboard meant for quick glances or deep analysis? What level of interactivity should it have?"
    ],
    "data": [
        "What specific data points need to be captured, displayed, or analyzed in this system?",
        "How would you prioritize different types of data in terms of importance and visibility?"
    ],
    "user-friendly": [
        "What aspects of user-friendliness are most important for your target users?",
        "Could you describe a specific example of what you consider to be a user-friendly interaction?"
    ]
}

# Question templates for different confidence levels
CONFIDENCE_QUESTIONS = {
    "low": [
        "I'm not entirely clear on your requirements. Could you provide more specific details about what you're looking for?",
        "To better understand your needs, could you describe a specific scenario where this would be used?",
        "What problem are you ultimately trying to solve with this solution?"
    ],
    "medium": [
        "I have a general understanding of what you're looking for, but could you clarify a few points?",
        "To ensure we're aligned, could you confirm if my interpretation matches your intent?",
        "Are there any specific constraints or requirements I should be aware of?"
    ],
    "high": [
        "I have a good understanding of your requirements. Are there any additional aspects you'd like to emphasize?",
        "Is there anything important I might have missed in my interpretation?",
        "Do you have any preferences for how this should be implemented?"
    ]
}

def analyze_prompt(prompt: str) -> Dict[str, Any]:
    """
    Analyzes a prompt to determine intent, confidence, tone, and ambiguity.
    
    Args:
        prompt (str): The user's prompt to analyze
        
    Returns:
        Dict[str, Any]: Analysis results including interpreted intent, confidence score,
                        emotional tone, and ambiguous phrases
    """
    # Initialize the analysis result
    analysis = {
        "interpreted_intent": "",
        "confidence_score": 0.0,
        "emotional_tone": "neutral",
        "ambiguous_phrases": []
    }
    
    # Skip analysis for empty prompts
    if not prompt or len(prompt.strip()) == 0:
        analysis["confidence_score"] = 0.0
        return analysis
    
    # Normalize the prompt
    normalized_prompt = prompt.lower().strip()
    
    # Extract the main intent (simplified version - in a real implementation, this would use NLP)
    # For now, we'll use a simple heuristic to extract the first sentence as the intent
    sentences = re.split(r'[.!?]', normalized_prompt)
    if sentences:
        main_sentence = sentences[0].strip()
        # Clean up the intent and capitalize first letter
        intent = main_sentence.strip()
        if intent:
            analysis["interpreted_intent"] = intent[0].upper() + intent[1:]
    
    # Detect ambiguous phrases
    ambiguous_found = []
    for phrase in AMBIGUOUS_PHRASES:
        if phrase in normalized_prompt:
            ambiguous_found.append(phrase)
    analysis["ambiguous_phrases"] = ambiguous_found
    
    # Determine emotional tone
    tone_scores = {}
    for tone, indicators in EMOTIONAL_TONES.items():
        score = 0
        for indicator in indicators:
            if indicator in normalized_prompt:
                score += 1
        if score > 0:
            tone_scores[tone] = score
    
    if tone_scores:
        # Get the tone with the highest score
        dominant_tone = max(tone_scores.items(), key=lambda x: x[1])[0]
        analysis["emotional_tone"] = dominant_tone
    
    # Calculate confidence score based on various factors
    confidence = 0.5  # Start with medium confidence
    
    # Adjust based on prompt length (longer prompts tend to be more specific)
    if len(normalized_prompt) > 200:
        confidence += 0.1
    elif len(normalized_prompt) < 50:
        confidence -= 0.1
    
    # Adjust based on number of ambiguous phrases
    if len(ambiguous_found) > 3:
        confidence -= 0.2
    elif len(ambiguous_found) > 0:
        confidence -= 0.05 * len(ambiguous_found)  # Reduced penalty for ambiguous phrases
    
    # Adjust based on specificity indicators
    specificity_indicators = ["specifically", "exactly", "precisely", "in particular", "secure", "authentication", "token"]
    for indicator in specificity_indicators:
        if indicator in normalized_prompt:
            confidence += 0.05
    
    # Boost confidence for technical terms that indicate clarity
    technical_terms = ["api", "rest", "jwt", "database", "authentication", "endpoint", "function", "system", "module"]
    for term in technical_terms:
        if term in normalized_prompt:
            confidence += 0.03
    
    # Ensure confidence is within bounds
    confidence = max(0.0, min(1.0, confidence))
    analysis["confidence_score"] = round(confidence, 2)
    
    return analysis

def generate_reflection_questions(prompt_analysis: Dict[str, Any], max_questions: int = 3) -> List[str]:
    """
    Generates Socratic-style questions based on prompt analysis.
    
    Args:
        prompt_analysis (Dict[str, Any]): Analysis results from analyze_prompt
        max_questions (int, optional): Maximum number of questions to generate. Defaults to 3.
        
    Returns:
        List[str]: List of reflection questions
    """
    questions = []
    
    # Skip if analysis is empty or invalid
    if not prompt_analysis or "confidence_score" not in prompt_analysis:
        return questions
    
    # Add confidence-based questions
    confidence_score = prompt_analysis.get("confidence_score", 0.0)
    if confidence_score < LOW_CONFIDENCE:
        confidence_level = "low"
    elif confidence_score < HIGH_CONFIDENCE:
        confidence_level = "medium"
    else:
        confidence_level = "high"
    
    # Add a confidence-based question
    if CONFIDENCE_QUESTIONS.get(confidence_level):
        questions.append(CONFIDENCE_QUESTIONS[confidence_level][0])
    
    # Add questions based on ambiguous phrases
    ambiguous_phrases = prompt_analysis.get("ambiguous_phrases", [])
    for phrase in ambiguous_phrases:
        if phrase in QUESTION_TEMPLATES and len(questions) < max_questions:
            questions.append(QUESTION_TEMPLATES[phrase][0])
    
    # If we still need more questions, add domain-specific questions based on intent
    intent = prompt_analysis.get("interpreted_intent", "").lower()
    if len(questions) < max_questions:
        # UI/UX related intents
        if any(term in intent for term in ["ui", "interface", "design", "layout", "screen"]):
            questions.append("What specific user interactions are most important for this interface?")
        
        # Data related intents
        elif any(term in intent for term in ["data", "analytics", "dashboard", "report"]):
            questions.append("What insights are you hoping to gain from this data?")
        
        # Feature related intents
        elif any(term in intent for term in ["feature", "functionality", "capability"]):
            questions.append("How would you prioritize these features in terms of importance?")
        
        # Integration related intents
        elif any(term in intent for term in ["integrate", "connection", "api", "system"]):
            questions.append("What existing systems does this need to integrate with?")
    
    # If we still don't have enough questions, add a generic one
    if len(questions) < max_questions:
        questions.append("What would a successful implementation of this look like to you?")
    
    return questions[:max_questions]

def store_prompt_analysis(project_id: str, loop_id: int, analysis: Dict[str, Any], memory: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stores prompt analysis in memory for future reference.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        analysis (Dict[str, Any]): The prompt analysis to store
        memory (Dict[str, Any]): The memory object to update
        
    Returns:
        Dict[str, Any]: The updated memory object
    """
    # Skip if analysis is empty or invalid
    if not analysis or not isinstance(analysis, dict):
        return memory
    
    # Add timestamp to the analysis
    analysis_with_meta = analysis.copy()
    analysis_with_meta["timestamp"] = datetime.datetime.now().isoformat()
    analysis_with_meta["project_id"] = project_id
    analysis_with_meta["loop_id"] = loop_id
    
    # Initialize prompt_analysis section if it doesn't exist
    if "prompt_analysis" not in memory:
        memory["prompt_analysis"] = {}
    
    # Store in prompt_analysis section
    memory["prompt_analysis"][str(loop_id)] = analysis_with_meta
    
    # Also store in loop_trace if it exists
    if "loop_trace" in memory and str(loop_id) in memory["loop_trace"]:
        if "prompt_analysis" not in memory["loop_trace"][str(loop_id)]:
            memory["loop_trace"][str(loop_id)]["prompt_analysis"] = analysis_with_meta
    
    # Generate reflection questions and store them too
    reflection_questions = generate_reflection_questions(analysis)
    if reflection_questions:
        analysis_with_meta["reflection_questions"] = reflection_questions
    
    return memory

def get_last_prompt_analysis(project_id: str, memory: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Retrieves the latest prompt analysis from memory for a given project.
    
    Args:
        project_id (str): The project identifier
        memory (Dict[str, Any]): The memory object to retrieve from
        
    Returns:
        Optional[Dict[str, Any]]: The latest prompt analysis or None if not found
    """
    # Skip if memory is empty or invalid
    if not memory or not isinstance(memory, dict):
        return None
    
    # Skip if prompt_analysis section doesn't exist
    if "prompt_analysis" not in memory or not memory["prompt_analysis"]:
        return None
    
    # Find all analyses for the given project
    project_analyses = []
    for loop_id, analysis in memory["prompt_analysis"].items():
        if isinstance(analysis, dict) and analysis.get("project_id") == project_id:
            project_analyses.append(analysis)
    
    # Return None if no analyses found for the project
    if not project_analyses:
        return None
    
    # Sort by timestamp (newest first) and return the latest
    sorted_analyses = sorted(
        project_analyses,
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )
    
    return sorted_analyses[0] if sorted_analyses else None
