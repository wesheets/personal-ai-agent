"""
Loop Summary Validator Module

This module is responsible for validating loop summaries for accuracy, completeness,
and integrity, and injecting validation results into loop traces.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import asyncio
import json
from datetime import datetime
import re
from collections import defaultdict

# Mock function for reading from memory
# In a real implementation, this would read from a database or storage system
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    # Simulate memory read
    await asyncio.sleep(0.1)
    
    # Mock data for testing
    if key == "loop_trace[loop_001]":
        return {
            "loop_id": "loop_001",
            "status": "finalized",
            "timestamp": "2025-04-20T10:00:00Z",
            "summary": "Analyzed quantum computing concepts with thorough examination of qubits, superposition, and entanglement. Identified potential applications in cryptography and optimization problems.",
            "orchestrator_persona": "SAGE",
            "alignment_score": 0.82,
            "drift_score": 0.18,
            "rerun_count": 0
        }
    elif key == "loop_trace[loop_002]":
        return {
            "loop_id": "loop_002",
            "status": "finalized",
            "timestamp": "2025-04-20T14:00:00Z",
            "summary": "Researched machine learning algorithms with focus on neural networks and deep learning. Evaluated performance characteristics and application domains.",
            "orchestrator_persona": "NOVA",
            "alignment_score": 0.79,
            "drift_score": 0.21,
            "rerun_count": 1,
            "rerun_trigger": ["alignment"],
            "rerun_reason": "alignment_threshold_not_met"
        }
    
    return None

# Mock function for writing to memory
# In a real implementation, this would write to a database or storage system
async def write_to_memory(key: str, value: Any) -> bool:
    """Write data to memory storage."""
    # Simulate memory write
    await asyncio.sleep(0.1)
    print(f"Writing to memory: {key} = {json.dumps(value, indent=2)}")
    return True

async def get_loop_trace(loop_id: str) -> Dict[str, Any]:
    """
    Get the trace for a specific loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with loop trace data
    """
    trace = await read_from_memory(f"loop_trace[{loop_id}]")
    if not isinstance(trace, dict):
        return {
            "error": f"Loop trace not found for {loop_id}",
            "loop_id": loop_id
        }
    
    return trace

def analyze_summary_content(summary: str) -> Dict[str, Any]:
    """
    Analyze the content of a summary for various metrics.
    
    Args:
        summary: The summary text to analyze
        
    Returns:
        Dict with analysis results
    """
    # Check if summary is empty or too short
    if not summary:
        return {
            "length": 0,
            "word_count": 0,
            "sentence_count": 0,
            "complexity_score": 0.0,
            "detail_level": "none",
            "issues": ["empty_summary"]
        }
    
    # Calculate basic metrics
    length = len(summary)
    words = summary.split()
    word_count = len(words)
    sentences = re.split(r'[.!?]+', summary)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Calculate average word length
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
    
    # Calculate average sentence length
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    # Calculate complexity score (based on word and sentence length)
    complexity_score = (avg_word_length * 0.5 + avg_sentence_length * 0.1) / 2
    
    # Determine detail level
    if word_count < 20:
        detail_level = "minimal"
    elif word_count < 50:
        detail_level = "low"
    elif word_count < 100:
        detail_level = "moderate"
    elif word_count < 200:
        detail_level = "high"
    else:
        detail_level = "extensive"
    
    # Check for potential issues
    issues = []
    
    if word_count < 10:
        issues.append("too_short")
    
    if avg_sentence_length > 30:
        issues.append("sentences_too_long")
    
    if avg_sentence_length < 5 and sentence_count > 1:
        issues.append("sentences_too_short")
    
    # Check for potential inflation (overly positive language)
    positive_terms = ["excellent", "outstanding", "remarkable", "exceptional", "extraordinary", "superb", "brilliant", "amazing", "incredible", "fantastic"]
    positive_count = sum(1 for word in words if word.lower() in positive_terms)
    
    if positive_count > word_count * 0.1:
        issues.append("potential_inflation")
    
    # Create analysis result
    analysis = {
        "length": length,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_word_length": round(avg_word_length, 2),
        "avg_sentence_length": round(avg_sentence_length, 2),
        "complexity_score": round(complexity_score, 2),
        "detail_level": detail_level,
        "issues": issues
    }
    
    return analysis

async def validate_loop_summary(loop_id: str) -> Dict[str, Any]:
    """
    Validate a loop summary for accuracy, completeness, and integrity.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with validation results
    """
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Extract summary
    summary = trace.get("summary", "")
    
    # Analyze summary content
    analysis = analyze_summary_content(summary)
    
    # Calculate summary integrity score
    # Base score starts at 1.0 and is reduced for each issue
    integrity_score = 1.0
    
    for issue in analysis.get("issues", []):
        if issue == "empty_summary":
            integrity_score = 0.0
            break
        elif issue == "too_short":
            integrity_score -= 0.3
        elif issue == "sentences_too_long":
            integrity_score -= 0.1
        elif issue == "sentences_too_short":
            integrity_score -= 0.1
        elif issue == "potential_inflation":
            integrity_score -= 0.2
    
    # Ensure score is between 0 and 1
    integrity_score = max(0.0, min(1.0, integrity_score))
    
    # Determine validation status
    if integrity_score < 0.3:
        validation_status = "invalid"
        summary_warning = "severe_issues"
    elif integrity_score < 0.6:
        validation_status = "questionable"
        summary_warning = "moderate_issues"
    elif integrity_score < 0.8:
        validation_status = "acceptable"
        summary_warning = "minor_issues"
    else:
        validation_status = "valid"
        summary_warning = None
    
    # Create validation result
    validation = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "summary_integrity_score": round(integrity_score, 2),
        "validation_status": validation_status,
        "summary_warning": summary_warning,
        "validation_details": {
            "content_analysis": analysis,
            "issues_detected": analysis.get("issues", [])
        }
    }
    
    return validation

async def inject_validation_into_loop_trace(loop_id: str) -> bool:
    """
    Inject validation results into a loop trace.
    
    Args:
        loop_id: The ID of the loop to update
        
    Returns:
        True if successful, False otherwise
    """
    # Get the loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return False
    
    # Generate the validation
    validation = await validate_loop_summary(loop_id)
    if "error" in validation:
        return False
    
    # Update the trace with the validation
    trace["summary_validation"] = validation
    
    # Extract key metrics for quick access
    trace["summary_integrity_score"] = validation["summary_integrity_score"]
    if validation.get("summary_warning"):
        trace["summary_warning"] = validation["summary_warning"]
    
    # Write the updated trace back to memory
    await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return True

async def validate_all_loops(loop_ids: List[str]) -> Dict[str, Any]:
    """
    Validate summaries for multiple loops.
    
    Args:
        loop_ids: List of loop IDs to validate
        
    Returns:
        Dict mapping loop IDs to validation results
    """
    results = {}
    
    for loop_id in loop_ids:
        validation = await validate_loop_summary(loop_id)
        await inject_validation_into_loop_trace(loop_id)
        results[loop_id] = validation
    
    return results
