"""
Utility for scanning loop text against system beliefs.

This module provides functions to compare loop summaries with system beliefs
and determine which beliefs are being referenced or forgotten over time.
"""

import json
import re
from typing import Dict, List, Any, Tuple, Set

def load_beliefs_from_file(beliefs_file_path: str) -> List[str]:
    """
    Loads system beliefs from the orchestrator_beliefs.json file.
    
    Args:
        beliefs_file_path (str): Path to the beliefs JSON file
        
    Returns:
        List[str]: List of system beliefs
    """
    try:
        with open(beliefs_file_path, 'r') as f:
            beliefs_data = json.load(f)
            
        # Extract beliefs from the loaded data
        if isinstance(beliefs_data, dict) and 'beliefs' in beliefs_data:
            return beliefs_data['beliefs']
        elif isinstance(beliefs_data, list):
            return beliefs_data
        else:
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def extract_belief_keywords(belief: str) -> Set[str]:
    """
    Extracts significant keywords from a belief statement.
    
    Args:
        belief (str): The belief statement
        
    Returns:
        Set[str]: Set of significant keywords
    """
    # Normalize the belief
    normalized_belief = belief.lower()
    
    # Extract all words
    all_words = set(re.findall(r'\b\w+\b', normalized_belief))
    
    # Filter out common stop words
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when',
        'at', 'from', 'by', 'for', 'with', 'about', 'against', 'between',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'to', 'of', 'in', 'on', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
        'doing', 'can', 'could', 'should', 'would', 'may', 'might', 'must',
        'will', 'shall'
    }
    
    # Keep only significant words (not stop words and longer than 3 characters)
    significant_words = {word for word in all_words if word not in stop_words and len(word) > 3}
    
    # If no significant words found, return all words
    if not significant_words:
        return all_words
    
    return significant_words

def scan_text_for_belief(text: str, belief: str) -> float:
    """
    Scans text for references to a specific belief.
    
    Args:
        text (str): The text to scan
        belief (str): The belief to look for
        
    Returns:
        float: Match score between 0.0 (no match) and 1.0 (perfect match)
    """
    if not text or not belief:
        return 0.0
    
    # Normalize text
    normalized_text = text.lower()
    normalized_belief = belief.lower()
    
    # Check for exact match
    if normalized_belief in normalized_text:
        return 1.0
    
    # Extract keywords from belief
    belief_keywords = extract_belief_keywords(belief)
    
    # Count how many keywords are found in the text
    matched_keywords = sum(1 for keyword in belief_keywords if keyword in normalized_text)
    
    # Calculate match score
    if not belief_keywords:
        return 0.0
    
    match_score = matched_keywords / len(belief_keywords)
    
    return match_score

def get_recent_loops(memory: Dict[str, Any], count: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieves recent loop summaries from memory.
    
    Args:
        memory (Dict[str, Any]): The memory state
        count (int): Number of recent loops to retrieve
        
    Returns:
        List[Dict[str, Any]]: List of recent loop summaries
    """
    if 'loops' not in memory:
        return []
    
    # Sort loops by timestamp (newest first)
    sorted_loops = sorted(
        memory['loops'],
        key=lambda loop: loop.get('timestamp', ''),
        reverse=True
    )
    
    # Return the most recent loops
    return sorted_loops[:count]

def get_belief_references_over_time(loops: List[Dict[str, Any]], beliefs: List[str]) -> Dict[str, List[bool]]:
    """
    Tracks which beliefs are referenced in each loop over time.
    
    Args:
        loops (List[Dict[str, Any]]): List of loop summaries
        beliefs (List[str]): List of system beliefs
        
    Returns:
        Dict[str, List[bool]]: Dictionary mapping belief to list of boolean values
                              indicating whether it was referenced in each loop
    """
    # Initialize result dictionary
    belief_references = {belief: [] for belief in beliefs}
    
    # Check each loop for references to each belief
    for loop in loops:
        loop_summary = loop.get('summary', '')
        
        for belief in beliefs:
            # Calculate match score for this belief
            match_score = scan_text_for_belief(loop_summary, belief)
            
            # Consider it referenced if score is above threshold
            is_referenced = match_score > 0.3
            
            # Add to the reference history for this belief
            belief_references[belief].append(is_referenced)
    
    return belief_references
