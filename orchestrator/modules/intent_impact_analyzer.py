"""
Intent-Impact Emotional Feedback Analyzer

This module compares operator intent versus emotional result of loop,
detecting mismatches between intended tone and actual impact.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

def analyze_intent_impact(
    loop_id: str,
    prompt: str,
    summary: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyzes the intent of a prompt versus the impact of the loop summary.
    
    Args:
        loop_id (str): The loop identifier
        prompt (str): The original user prompt
        summary (str): The loop summary
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Analysis results with intent-impact mismatch detection
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "confidence_delta_threshold": 0.15,
            "tone_mismatch_threshold": 0.6
        }
    
    # Skip analysis if disabled
    if not config.get("enabled", True):
        return {
            "loop_id": loop_id,
            "analysis_status": "skipped",
            "message": "Intent-impact analysis is disabled"
        }
    
    # Extract intent tone from prompt
    intent_tone, intent_confidence = _extract_intent_tone(prompt)
    
    # Extract impact tone from summary
    summary_tone, summary_confidence = _extract_summary_tone(summary)
    
    # Calculate confidence delta
    confidence_delta = summary_confidence - intent_confidence
    
    # Determine if there's a mismatch
    has_mismatch = _detect_tone_mismatch(
        intent_tone, 
        summary_tone, 
        confidence_delta,
        config.get("confidence_delta_threshold", 0.15),
        config.get("tone_mismatch_threshold", 0.6)
    )
    
    # Generate recommendation if there's a mismatch
    recommendation = None
    if has_mismatch:
        recommendation = _generate_recommendation(intent_tone, summary_tone, confidence_delta)
    
    # Create analysis result
    analysis_result = {
        "loop_id": loop_id,
        "intent_tone": intent_tone,
        "summary_tone": summary_tone,
        "intent_confidence": round(intent_confidence, 2),
        "summary_confidence": round(summary_confidence, 2),
        "impact_confidence_delta": round(confidence_delta, 2),
        "has_mismatch": has_mismatch,
        "analysis_status": "completed",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Add recommendation if there's a mismatch
    if recommendation:
        analysis_result["recommendation"] = recommendation
    
    return analysis_result

def _extract_intent_tone(prompt: str) -> Tuple[str, float]:
    """
    Extracts the intended tone from a user prompt.
    
    Args:
        prompt (str): The user prompt
        
    Returns:
        Tuple[str, float]: Extracted tone and confidence score
    """
    # Convert prompt to lowercase for case-insensitive matching
    prompt_lower = prompt.lower()
    
    # Define tone indicators and their weights
    tone_indicators = {
        "reflective": ["reflect", "consider", "think about", "ponder", "contemplate"],
        "analytical": ["analyze", "examine", "investigate", "assess", "evaluate"],
        "creative": ["create", "design", "imagine", "innovate", "brainstorm"],
        "instructive": ["explain", "teach", "show me", "guide", "instruct"],
        "decisive": ["decide", "choose", "determine", "select", "pick"],
        "curious": ["curious", "wonder", "interested", "question", "explore"],
        "urgent": ["urgent", "immediately", "asap", "quickly", "hurry"],
        "cautious": ["careful", "cautious", "safe", "risk", "concern"]
    }
    
    # Score each tone based on indicators
    tone_scores = {}
    for tone, indicators in tone_indicators.items():
        score = 0.0
        for indicator in indicators:
            if indicator in prompt_lower:
                score += 0.2
        tone_scores[tone] = min(score, 0.9)  # Cap at 0.9
    
    # Add scores based on other features
    
    # Question marks indicate curiosity
    question_count = prompt.count("?")
    if question_count > 0:
        tone_scores["curious"] = min(tone_scores.get("curious", 0) + 0.1 * question_count, 0.9)
    
    # Exclamation marks indicate urgency or decisiveness
    exclamation_count = prompt.count("!")
    if exclamation_count > 0:
        tone_scores["urgent"] = min(tone_scores.get("urgent", 0) + 0.1 * exclamation_count, 0.9)
        tone_scores["decisive"] = min(tone_scores.get("decisive", 0) + 0.05 * exclamation_count, 0.9)
    
    # Length of prompt can indicate reflective or analytical intent
    word_count = len(prompt.split())
    if word_count > 100:
        tone_scores["reflective"] = min(tone_scores.get("reflective", 0) + 0.2, 0.9)
        tone_scores["analytical"] = min(tone_scores.get("analytical", 0) + 0.1, 0.9)
    elif word_count < 20:
        tone_scores["urgent"] = min(tone_scores.get("urgent", 0) + 0.1, 0.9)
    
    # Get the highest scoring tone
    if not tone_scores:
        return "neutral", 0.5
    
    max_tone = max(tone_scores.items(), key=lambda x: x[1])
    
    # If no strong indicators, default to neutral
    if max_tone[1] < 0.2:
        return "neutral", 0.5
    
    return max_tone[0], max_tone[1]

def _extract_summary_tone(summary: str) -> Tuple[str, float]:
    """
    Extracts the tone from a loop summary.
    
    Args:
        summary (str): The loop summary
        
    Returns:
        Tuple[str, float]: Extracted tone and confidence score
    """
    # Convert summary to lowercase for case-insensitive matching
    summary_lower = summary.lower()
    
    # Define tone indicators and their weights
    tone_indicators = {
        "reflective": ["reflected", "considered", "thought about", "pondered", "contemplated"],
        "analytical": ["analyzed", "examined", "investigated", "assessed", "evaluated"],
        "creative": ["created", "designed", "imagined", "innovated", "brainstormed"],
        "instructive": ["explained", "taught", "showed", "guided", "instructed"],
        "decisive": ["decided", "chose", "determined", "selected", "picked"],
        "vague": ["possibly", "perhaps", "might", "could be", "seems like"],
        "confident": ["definitely", "certainly", "clearly", "absolutely", "without doubt"],
        "cautious": ["carefully", "cautiously", "safely", "risk", "concern"]
    }
    
    # Score each tone based on indicators
    tone_scores = {}
    for tone, indicators in tone_indicators.items():
        score = 0.0
        for indicator in indicators:
            if indicator in summary_lower:
                score += 0.15
        tone_scores[tone] = min(score, 0.9)  # Cap at 0.9
    
    # Add scores based on other features
    
    # Length of summary can indicate analytical or vague tone
    word_count = len(summary.split())
    if word_count > 200:
        tone_scores["analytical"] = min(tone_scores.get("analytical", 0) + 0.2, 0.9)
    elif word_count < 50:
        tone_scores["vague"] = min(tone_scores.get("vague", 0) + 0.2, 0.9)
    
    # Use of first person indicates reflective tone
    if "i " in summary_lower or "we " in summary_lower:
        tone_scores["reflective"] = min(tone_scores.get("reflective", 0) + 0.2, 0.9)
    
    # Use of second person indicates instructive tone
    if "you " in summary_lower or "your " in summary_lower:
        tone_scores["instructive"] = min(tone_scores.get("instructive", 0) + 0.2, 0.9)
    
    # Get the highest scoring tone
    if not tone_scores:
        return "neutral", 0.5
    
    max_tone = max(tone_scores.items(), key=lambda x: x[1])
    
    # If no strong indicators, default to neutral
    if max_tone[1] < 0.2:
        return "neutral", 0.5
    
    return max_tone[0], max_tone[1]

def _detect_tone_mismatch(
    intent_tone: str,
    summary_tone: str,
    confidence_delta: float,
    confidence_delta_threshold: float,
    tone_mismatch_threshold: float
) -> bool:
    """
    Detects if there's a mismatch between intent and summary tones.
    
    Args:
        intent_tone (str): The intended tone
        summary_tone (str): The summary tone
        confidence_delta (float): Difference in confidence scores
        confidence_delta_threshold (float): Threshold for confidence delta
        tone_mismatch_threshold (float): Threshold for tone mismatch
        
    Returns:
        bool: True if there's a mismatch, False otherwise
    """
    # Direct tone mismatches that are concerning
    concerning_mismatches = {
        "reflective": ["vague", "decisive"],
        "analytical": ["vague", "creative"],
        "creative": ["analytical", "cautious"],
        "instructive": ["vague", "reflective"],
        "decisive": ["vague", "cautious"],
        "curious": ["decisive", "instructive"],
        "urgent": ["reflective", "cautious"],
        "cautious": ["decisive", "creative"]
    }
    
    # Check for direct tone mismatch
    if intent_tone in concerning_mismatches and summary_tone in concerning_mismatches[intent_tone]:
        return True
    
    # Check for significant confidence drop
    if confidence_delta < -confidence_delta_threshold:
        return True
    
    # Check if summary tone is vague
    if summary_tone == "vague" and intent_tone != "vague":
        return True
    
    return False

def _generate_recommendation(intent_tone: str, summary_tone: str, confidence_delta: float) -> str:
    """
    Generates a recommendation based on the detected mismatch.
    
    Args:
        intent_tone (str): The intended tone
        summary_tone (str): The summary tone
        confidence_delta (float): Difference in confidence scores
        
    Returns:
        str: Recommendation for addressing the mismatch
    """
    # Handle significant confidence drop
    if confidence_delta < -0.3:
        return "Rerun SAGE to reclarify loop purpose"
    
    # Handle vague summary
    if summary_tone == "vague":
        return "Increase specificity in response and rerun with ARCHITECT mode"
    
    # Handle specific tone mismatches
    if intent_tone == "reflective" and summary_tone in ["decisive", "instructive"]:
        return "Switch to SAGE mode to better match reflective intent"
    
    if intent_tone == "analytical" and summary_tone in ["creative", "vague"]:
        return "Switch to RESEARCHER mode for more analytical approach"
    
    if intent_tone == "creative" and summary_tone in ["analytical", "cautious"]:
        return "Switch to INVENTOR mode for more creative solutions"
    
    if intent_tone == "urgent" and summary_tone in ["reflective", "cautious"]:
        return "Prioritize direct answers with ARCHITECT mode"
    
    # Default recommendation
    return "Review tone alignment and adjust mode accordingly"

def store_intent_impact_analysis(
    analysis_result: Dict[str, Any],
    memory: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Stores intent-impact analysis results in memory.
    
    Args:
        analysis_result (Dict[str, Any]): The analysis result to store
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Dict[str, Any]: Updated memory with intent-impact analysis
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Initialize intent_impact_analysis if it doesn't exist
    if "intent_impact_analysis" not in updated_memory:
        updated_memory["intent_impact_analysis"] = []
    
    # Add analysis result to memory
    updated_memory["intent_impact_analysis"].append(analysis_result)
    
    # If there's a mismatch, also store in intent_impact_mismatch
    if analysis_result.get("has_mismatch", False):
        # Initialize intent_impact_mismatch if it doesn't exist
        if "intent_impact_mismatch" not in updated_memory:
            updated_memory["intent_impact_mismatch"] = []
        
        # Create mismatch entry
        mismatch_entry = {
            "loop_id": analysis_result["loop_id"],
            "intent_tone": analysis_result["intent_tone"],
            "summary_tone": analysis_result["summary_tone"],
            "impact_confidence_delta": analysis_result["impact_confidence_delta"],
            "recommendation": analysis_result.get("recommendation", "Review tone alignment"),
            "timestamp": analysis_result["timestamp"]
        }
        
        # Add mismatch entry to memory
        updated_memory["intent_impact_mismatch"].append(mismatch_entry)
    
    return updated_memory

def process_loop_with_intent_impact_analyzer(
    loop_id: str,
    prompt: str,
    summary: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Processes a loop with the intent-impact emotional feedback analyzer.
    
    Args:
        loop_id (str): The loop identifier
        prompt (str): The original user prompt
        summary (str): The loop summary
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Result of the processing, including updated memory with intent-impact analysis
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "confidence_delta_threshold": 0.15,
            "tone_mismatch_threshold": 0.6
        }
    
    # Skip processing if disabled
    if not config.get("enabled", True):
        return {
            "status": "skipped",
            "memory": memory,
            "message": "Intent-impact analyzer is disabled"
        }
    
    # Analyze intent-impact
    analysis_result = analyze_intent_impact(loop_id, prompt, summary, memory, config)
    
    # Store analysis in memory
    updated_memory = store_intent_impact_analysis(analysis_result, memory)
    
    # Determine message based on analysis
    if analysis_result.get("has_mismatch", False):
        message = f"Intent-impact mismatch detected: {analysis_result['intent_tone']} intent vs {analysis_result['summary_tone']} summary"
        if "recommendation" in analysis_result:
            message += f", recommendation: {analysis_result['recommendation']}"
    else:
        message = f"Intent-impact analysis completed: {analysis_result['intent_tone']} intent aligns with {analysis_result['summary_tone']} summary"
    
    # Return result
    return {
        "status": "analyzed",
        "memory": updated_memory,
        "message": message,
        "has_mismatch": analysis_result.get("has_mismatch", False),
        "analysis_result": analysis_result
    }
