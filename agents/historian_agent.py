"""
Historian Agent for detecting memory drift and belief alignment.

This module implements a passive cognitive drift agent that:
1. Scans completed loop summaries
2. Compares them against orchestrator_beliefs.json
3. Scores alignment and logs forgotten beliefs over time
4. Injects alerts into memory without interrupting loops
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

def generate_belief_alignment_score(loop_summary: str, beliefs: List[str]) -> float:
    """
    Compares summary text against beliefs to determine alignment.
    
    Args:
        loop_summary (str): The text of the loop summary
        beliefs (List[str]): List of system beliefs to check against
        
    Returns:
        float: Alignment score between 0.0 (no alignment) and 1.0 (perfect alignment)
    """
    if not loop_summary or not beliefs:
        return 0.0
    
    # Normalize the loop summary text
    normalized_summary = loop_summary.lower()
    
    # Track matches for each belief
    belief_matches = []
    
    for belief in beliefs:
        # Normalize the belief
        normalized_belief = belief.lower()
        
        # Check for exact matches
        exact_match = normalized_belief in normalized_summary
        
        # Check for partial exact matches (at least 50% of the belief appears as a continuous string)
        partial_exact_match = False
        if not exact_match:
            belief_words = normalized_belief.split()
            half_length = max(3, len(belief_words) // 2)
            
            for i in range(len(belief_words) - half_length + 1):
                phrase = ' '.join(belief_words[i:i+half_length])
                if phrase in normalized_summary:
                    partial_exact_match = True
                    break
        
        # Check for semantic matches (key terms from the belief)
        belief_terms = set(re.findall(r'\b\w+\b', normalized_belief))
        significant_terms = {term for term in belief_terms if len(term) > 3}
        
        if not significant_terms:
            significant_terms = belief_terms
        
        matched_terms = sum(1 for term in significant_terms if term in normalized_summary)
        term_match_ratio = matched_terms / len(significant_terms) if significant_terms else 0
        
        # Calculate match score for this belief
        if exact_match:
            match_score = 1.0
        elif partial_exact_match:
            # Partial exact matches get a high score
            match_score = 0.85
        else:
            # Weight term matches more heavily to produce higher scores
            # Use a progressive scale: more matches = disproportionately higher score
            if term_match_ratio > 0.5:
                # Boost scores that are already good
                match_score = 0.5 + (term_match_ratio - 0.5) * 2.0
            else:
                match_score = term_match_ratio * 1.8  # Increased weight from 1.5 to 1.8
        
        # Ensure score doesn't exceed 1.0
        match_score = min(1.0, match_score)
        
        belief_matches.append(match_score)
    
    # Calculate overall alignment score
    if not belief_matches:
        return 0.0
    
    # Average the match scores across all beliefs
    alignment_score = sum(belief_matches) / len(belief_matches)
    
    return alignment_score

def detect_forgotten_beliefs(recent_loops: List[dict], beliefs: List[str]) -> List[str]:
    """
    Tracks which beliefs haven't been referenced in the last N loops.
    
    Args:
        recent_loops (List[dict]): List of recent loop summaries
        beliefs (List[str]): List of system beliefs to check against
        
    Returns:
        List[str]: List of beliefs that haven't been referenced
    """
    if not recent_loops or not beliefs:
        return beliefs
    
    # Track which beliefs have been referenced
    referenced_beliefs = set()
    
    # Check each loop summary for references to beliefs
    for loop in recent_loops:
        loop_summary = loop.get("summary", "")
        if not loop_summary:
            continue
        
        # Check each belief against this loop summary
        for belief in beliefs:
            # If we've already found this belief referenced, skip checking it again
            if belief in referenced_beliefs:
                continue
            
            # Calculate alignment score for this specific belief
            belief_score = generate_belief_alignment_score(loop_summary, [belief])
            
            # If the score is above threshold, consider it referenced
            if belief_score > 0.3:  # Threshold for considering a belief referenced
                referenced_beliefs.add(belief)
    
    # Return beliefs that weren't referenced
    forgotten_beliefs = [belief for belief in beliefs if belief not in referenced_beliefs]
    
    return forgotten_beliefs

def generate_historian_alert(loop_id: str, missing_beliefs: List[str], 
                            alignment_score: float, memory: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates and injects a historian alert into memory.
    
    Args:
        loop_id (str): ID of the current loop
        missing_beliefs (List[str]): List of beliefs not referenced in recent loops
        alignment_score (float): Overall belief alignment score
        memory (Dict[str, Any]): The current memory state
        
    Returns:
        Dict[str, Any]: Updated memory with historian alert
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Generate suggestion based on alignment score
    suggestion = "System beliefs are well-aligned with recent operations"
    if alignment_score < 0.3:
        suggestion = "Rerun Sage for system realignment - significant drift detected"
    elif alignment_score < 0.6:
        suggestion = "Consider reviewing system beliefs for potential updates"
    
    # Create the alert
    alert = {
        "loop_id": loop_id,
        "alert_type": "belief_drift_detected" if missing_beliefs else "belief_alignment_check",
        "missing_beliefs": missing_beliefs,
        "loop_belief_alignment_score": alignment_score,
        "suggestion": suggestion,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add alert to memory
    if "historian_alerts" not in updated_memory:
        updated_memory["historian_alerts"] = []
    
    updated_memory["historian_alerts"].append(alert)
    
    # Add a CTO warning if alignment is very low
    if alignment_score < 0.3 and missing_beliefs:
        if "cto_warnings" not in updated_memory:
            updated_memory["cto_warnings"] = []
        
        warning = {
            "type": "belief_drift",
            "loop_id": loop_id,
            "message": f"Significant belief drift detected. {len(missing_beliefs)} beliefs not referenced recently.",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        updated_memory["cto_warnings"].append(warning)
    
    return updated_memory

def analyze_loop_summary(loop_id: str, loop_summary: str, recent_loops: List[dict], 
                        beliefs: List[str], memory: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to analyze a loop summary and update memory with historian alerts.
    
    Args:
        loop_id (str): ID of the current loop
        loop_summary (str): The text of the loop summary
        recent_loops (List[dict]): List of recent loop summaries
        beliefs (List[str]): List of system beliefs to check against
        memory (Dict[str, Any]): The current memory state
        
    Returns:
        Dict[str, Any]: Updated memory with historian alerts
    """
    # Generate alignment score for the current loop
    alignment_score = generate_belief_alignment_score(loop_summary, beliefs)
    
    # Detect forgotten beliefs across recent loops
    forgotten_beliefs = detect_forgotten_beliefs(recent_loops, beliefs)
    
    # Generate and inject historian alert
    updated_memory = generate_historian_alert(loop_id, forgotten_beliefs, alignment_score, memory)
    
    return updated_memory
