"""
Vision Deviation Detection Module
This module provides functionality for detecting deviations from operator intent
and generating repair instructions for agents to correct the deviations.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger("modules.logic.evaluate_deviation_v1")

def evaluate_deviation(project_state: Dict[str, Any], feature_id: str) -> Dict[str, Any]:
    """
    Evaluate if there's a deviation between the implemented feature and operator intent.
    
    Args:
        project_state: The current project state
        feature_id: The identifier of the feature to evaluate
            
    Returns:
        Dict containing the evaluation results, including:
        - deviation_detected: Boolean indicating if a deviation was detected
        - confidence: Float indicating confidence in the deviation detection (0.0-1.0)
        - repair_instruction: String with instructions for repairing the deviation
        - assigned_agent: String with the agent ID recommended for the repair
    """
    try:
        logger.info(f"Evaluating deviation for feature: {feature_id}")
        print(f"🔍 Evaluating deviation for feature: {feature_id}")
        
        # Initialize result with default values
        result = {
            "deviation_detected": False,
            "confidence": 0.0,
            "repair_instruction": "",
            "assigned_agent": "",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check if result_summary exists in project state
        if "result_summary" not in project_state:
            logger.warning(f"No result_summary found in project state, skipping deviation check")
            print(f"⚠️ No result_summary found in project state, skipping deviation check")
            return result
        
        # Get the result summary for the feature
        result_summary = project_state.get("result_summary", {})
        feature_summary = result_summary.get(feature_id, {})
        
        if not feature_summary:
            logger.warning(f"No summary found for feature {feature_id}, skipping deviation check")
            print(f"⚠️ No summary found for feature {feature_id}, skipping deviation check")
            return result
        
        # Get the original intent and implemented result
        original_intent = feature_summary.get("original_intent", "")
        implemented_result = feature_summary.get("implemented_result", "")
        
        if not original_intent or not implemented_result:
            logger.warning(f"Missing original_intent or implemented_result for feature {feature_id}")
            print(f"⚠️ Missing original_intent or implemented_result for feature {feature_id}")
            return result
        
        # Perform deviation detection
        # In a real implementation, this would use NLP or other techniques to compare
        # the original intent with the implemented result
        # For this example, we'll use a simple keyword-based approach
        
        # Extract keywords from original intent
        intent_keywords = set(_extract_keywords(original_intent))
        
        # Extract keywords from implemented result
        result_keywords = set(_extract_keywords(implemented_result))
        
        # Calculate keyword overlap
        common_keywords = intent_keywords.intersection(result_keywords)
        total_keywords = intent_keywords.union(result_keywords)
        
        if len(total_keywords) == 0:
            # No keywords to compare
            return result
        
        # Calculate similarity score (Jaccard similarity)
        similarity = len(common_keywords) / len(total_keywords)
        
        # Determine if there's a deviation
        # If similarity is below threshold, consider it a deviation
        threshold = 0.7  # 70% similarity threshold
        
        if similarity < threshold:
            # Deviation detected
            result["deviation_detected"] = True
            result["confidence"] = 1.0 - similarity  # Higher confidence for lower similarity
            
            # Generate repair instruction
            missing_keywords = intent_keywords - result_keywords
            extra_keywords = result_keywords - intent_keywords
            
            repair_instruction = f"Feature {feature_id} deviates from original intent. "
            
            if missing_keywords:
                repair_instruction += f"Missing elements: {', '.join(missing_keywords)}. "
            
            if extra_keywords:
                repair_instruction += f"Extra elements: {', '.join(extra_keywords)}. "
            
            repair_instruction += "Please review and align implementation with original intent."
            
            result["repair_instruction"] = repair_instruction
            
            # Assign appropriate agent for repair
            # For this example, we'll use a simple heuristic:
            # - ASH for minor deviations (confidence < 0.5)
            # - NOVA for major deviations (confidence >= 0.5)
            if result["confidence"] < 0.5:
                result["assigned_agent"] = "ash"
            else:
                result["assigned_agent"] = "nova"
            
            logger.info(f"Deviation detected for feature {feature_id} with confidence {result['confidence']:.2f}")
            print(f"⚠️ Deviation detected for feature {feature_id} with confidence {result['confidence']:.2f}")
            print(f"🔧 Assigned to {result['assigned_agent']} for repair")
        else:
            logger.info(f"No deviation detected for feature {feature_id} (similarity: {similarity:.2f})")
            print(f"✅ No deviation detected for feature {feature_id} (similarity: {similarity:.2f})")
        
        return result
        
    except Exception as e:
        error_msg = f"Error evaluating deviation for feature {feature_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        # Return a safe default result
        return {
            "deviation_detected": False,
            "confidence": 0.0,
            "repair_instruction": "",
            "assigned_agent": "",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def _extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: The text to extract keywords from
            
    Returns:
        List of keywords
    """
    # In a real implementation, this would use NLP techniques
    # For this example, we'll use a simple approach:
    # - Convert to lowercase
    # - Split by whitespace
    # - Remove common stop words
    # - Remove punctuation
    
    # Simple list of stop words
    stop_words = {
        "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
        "at", "from", "by", "for", "with", "about", "against", "between",
        "into", "through", "during", "before", "after", "above", "below",
        "to", "of", "in", "on", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "having", "do", "does", "did", "doing",
        "can", "could", "should", "would", "may", "might", "must", "shall", "will"
    }
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    for char in ".,;:!?()[]{}-\"'":
        text = text.replace(char, " ")
    
    # Split by whitespace
    words = text.split()
    
    # Remove stop words
    keywords = [word for word in words if word not in stop_words and len(word) > 1]
    
    return keywords
