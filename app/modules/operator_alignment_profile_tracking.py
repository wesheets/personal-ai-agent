"""
Operator Alignment Profile Tracking Module

This module is responsible for tracking operator preferences and alignment profiles,
updating profiles based on loop analysis, and injecting profiles into loop traces.
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
            "rerun_count": 0,
            "operator_id": "operator_001"
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
            "rerun_reason": "alignment_threshold_not_met",
            "operator_id": "operator_001"
        }
    elif key == "operator_profile[operator_001]":
        return {
            "operator_id": "operator_001",
            "name": "Test Operator",
            "tone_preference": "formal",
            "detail_preference": "high",
            "tone_mismatch_tolerance": 0.25,
            "detail_mismatch_tolerance": 0.3,
            "last_updated": "2025-04-20T10:30:00Z"
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

async def get_operator_profile(operator_id: str) -> Dict[str, Any]:
    """
    Get the profile for an operator.
    
    Args:
        operator_id: The ID of the operator
        
    Returns:
        Dict with operator profile
    """
    profile = await read_from_memory(f"operator_profile[{operator_id}]")
    if not isinstance(profile, dict):
        # Create default profile if none exists
        profile = {
            "operator_id": operator_id,
            "name": f"Operator {operator_id}",
            "tone_preference": "neutral",
            "detail_preference": "medium",
            "tone_mismatch_tolerance": 0.3,
            "detail_mismatch_tolerance": 0.3,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    return profile

async def analyze_loop_for_operator_preferences(loop_id: str) -> Dict[str, Any]:
    """
    Analyze a loop to infer operator preferences.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with analysis results
    """
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Extract operator ID
    operator_id = trace.get("operator_id")
    if not operator_id:
        return {
            "error": "No operator ID found in loop trace",
            "loop_id": loop_id
        }
    
    # Extract relevant information
    summary = trace.get("summary", "")
    alignment_score = trace.get("alignment_score", 0.0)
    drift_score = trace.get("drift_score", 0.0)
    rerun_count = trace.get("rerun_count", 0)
    rerun_trigger = trace.get("rerun_trigger", [])
    rerun_reason = trace.get("rerun_reason", "")
    
    # Analyze summary for tone
    formal_terms = ["therefore", "furthermore", "consequently", "thus", "hence", "accordingly", "subsequently"]
    casual_terms = ["basically", "actually", "pretty", "kind of", "sort of", "you know", "anyway"]
    
    formal_count = sum(1 for term in formal_terms if term in summary.lower())
    casual_count = sum(1 for term in casual_terms if term in summary.lower())
    
    # Determine tone preference
    if formal_count > casual_count:
        inferred_tone = "formal"
    elif casual_count > formal_count:
        inferred_tone = "casual"
    else:
        inferred_tone = "neutral"
    
    # Analyze summary for detail level
    word_count = len(summary.split())
    
    # Determine detail preference
    if word_count > 100:
        inferred_detail = "high"
    elif word_count > 50:
        inferred_detail = "medium"
    else:
        inferred_detail = "low"
    
    # Infer tolerance levels
    # If the operator accepted a high drift score, they have high tolerance
    inferred_tone_tolerance = 0.4 if drift_score > 0.3 else 0.3 if drift_score > 0.2 else 0.2
    
    # If the operator triggered reruns, they have low tolerance
    if "detail" in rerun_trigger or rerun_reason == "detail_mismatch":
        inferred_detail_tolerance = 0.2
    else:
        inferred_detail_tolerance = 0.3
    
    # Create analysis result
    analysis = {
        "loop_id": loop_id,
        "operator_id": operator_id,
        "inferred_preferences": {
            "tone": inferred_tone,
            "detail": inferred_detail,
            "tone_tolerance": inferred_tone_tolerance,
            "detail_tolerance": inferred_detail_tolerance
        },
        "evidence": {
            "formal_term_count": formal_count,
            "casual_term_count": casual_count,
            "word_count": word_count,
            "drift_score": drift_score,
            "rerun_count": rerun_count,
            "rerun_trigger": rerun_trigger,
            "rerun_reason": rerun_reason
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return analysis

async def update_operator_profile_from_analysis(operator_id: str) -> Dict[str, Any]:
    """
    Update an operator profile based on loop analysis.
    
    Args:
        operator_id: The ID of the operator
        
    Returns:
        Dict with update result
    """
    # Get current profile
    profile = await get_operator_profile(operator_id)
    
    # Get all loop IDs
    # In a real implementation, this would query the database for all loop IDs
    # For this mock implementation, we'll use a hardcoded list
    loop_ids = ["loop_001", "loop_002", "loop_003", "loop_004", "loop_005"]
    
    # Collect loops for this operator
    operator_loops = []
    for loop_id in loop_ids:
        trace = await get_loop_trace(loop_id)
        if "error" not in trace and trace.get("operator_id") == operator_id:
            operator_loops.append(loop_id)
    
    if not operator_loops:
        return {
            "operator_id": operator_id,
            "updated": False,
            "reason": "No loops found for this operator",
            "profile": profile
        }
    
    # Analyze each loop
    analyses = []
    for loop_id in operator_loops:
        analysis = await analyze_loop_for_operator_preferences(loop_id)
        if "error" not in analysis:
            analyses.append(analysis)
    
    if not analyses:
        return {
            "operator_id": operator_id,
            "updated": False,
            "reason": "No valid analyses found",
            "profile": profile
        }
    
    # Aggregate preferences
    tone_counts = defaultdict(int)
    detail_counts = defaultdict(int)
    tone_tolerances = []
    detail_tolerances = []
    
    for analysis in analyses:
        prefs = analysis["inferred_preferences"]
        tone_counts[prefs["tone"]] += 1
        detail_counts[prefs["detail"]] += 1
        tone_tolerances.append(prefs["tone_tolerance"])
        detail_tolerances.append(prefs["detail_tolerance"])
    
    # Determine dominant preferences
    dominant_tone = max(tone_counts.items(), key=lambda x: x[1])[0]
    dominant_detail = max(detail_counts.items(), key=lambda x: x[1])[0]
    
    # Calculate average tolerances
    avg_tone_tolerance = sum(tone_tolerances) / len(tone_tolerances)
    avg_detail_tolerance = sum(detail_tolerances) / len(detail_tolerances)
    
    # Update profile
    updated_profile = profile.copy()
    updated_profile["tone_preference"] = dominant_tone
    updated_profile["detail_preference"] = dominant_detail
    updated_profile["tone_mismatch_tolerance"] = round(avg_tone_tolerance, 2)
    updated_profile["detail_mismatch_tolerance"] = round(avg_detail_tolerance, 2)
    updated_profile["last_updated"] = datetime.utcnow().isoformat()
    
    # Write updated profile to memory
    await write_to_memory(f"operator_profile[{operator_id}]", updated_profile)
    
    return {
        "operator_id": operator_id,
        "updated": True,
        "previous_profile": profile,
        "updated_profile": updated_profile,
        "analyses_used": len(analyses),
        "loops_analyzed": operator_loops
    }

async def process_loop_for_operator_profile(loop_id: str) -> Dict[str, Any]:
    """
    Process a loop to update operator profile.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with processing result
    """
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Extract operator ID
    operator_id = trace.get("operator_id")
    if not operator_id:
        return {
            "error": "No operator ID found in loop trace",
            "loop_id": loop_id
        }
    
    # Analyze loop
    analysis = await analyze_loop_for_operator_preferences(loop_id)
    if "error" in analysis:
        return analysis
    
    # Get current profile
    profile = await get_operator_profile(operator_id)
    
    # Determine profile updates
    updates = {}
    
    # Check if tone preference should be updated
    inferred_tone = analysis["inferred_preferences"]["tone"]
    current_tone = profile["tone_preference"]
    
    if inferred_tone != current_tone:
        updates["tone_preference"] = {
            "from": current_tone,
            "to": inferred_tone,
            "evidence": {
                "formal_count": analysis["evidence"]["formal_term_count"],
                "casual_count": analysis["evidence"]["casual_term_count"]
            }
        }
    
    # Check if detail preference should be updated
    inferred_detail = analysis["inferred_preferences"]["detail"]
    current_detail = profile["detail_preference"]
    
    if inferred_detail != current_detail:
        updates["detail_preference"] = {
            "from": current_detail,
            "to": inferred_detail,
            "evidence": {
                "word_count": analysis["evidence"]["word_count"]
            }
        }
    
    # Check if tolerance levels should be updated
    inferred_tone_tolerance = analysis["inferred_preferences"]["tone_tolerance"]
    current_tone_tolerance = profile["tone_mismatch_tolerance"]
    
    if abs(inferred_tone_tolerance - current_tone_tolerance) > 0.05:
        updates["tone_mismatch_tolerance"] = {
            "from": current_tone_tolerance,
            "to": inferred_tone_tolerance,
            "evidence": {
                "drift_score": analysis["evidence"]["drift_score"]
            }
        }
    
    inferred_detail_tolerance = analysis["inferred_preferences"]["detail_tolerance"]
    current_detail_tolerance = profile["detail_mismatch_tolerance"]
    
    if abs(inferred_detail_tolerance - current_detail_tolerance) > 0.05:
        updates["detail_mismatch_tolerance"] = {
            "from": current_detail_tolerance,
            "to": inferred_detail_tolerance,
            "evidence": {
                "rerun_trigger": analysis["evidence"]["rerun_trigger"],
                "rerun_reason": analysis["evidence"]["rerun_reason"]
            }
        }
    
    # Update profile if needed
    if updates:
        # Create updated profile
        updated_profile = profile.copy()
        
        if "tone_preference" in updates:
            updated_profile["tone_preference"] = updates["tone_preference"]["to"]
        
        if "detail_preference" in updates:
            updated_profile["detail_preference"] = updates["detail_preference"]["to"]
        
        if "tone_mismatch_tolerance" in updates:
            updated_profile["tone_mismatch_tolerance"] = updates["tone_mismatch_tolerance"]["to"]
        
        if "detail_mismatch_tolerance" in updates:
            updated_profile["detail_mismatch_tolerance"] = updates["detail_mismatch_tolerance"]["to"]
        
        updated_profile["last_updated"] = datetime.utcnow().isoformat()
        
        # Write updated profile to memory
        await write_to_memory(f"operator_profile[{operator_id}]", updated_profile)
        
        return {
            "loop_id": loop_id,
            "operator_id": operator_id,
            "profile_updated": True,
            "profile_updates": updates,
            "previous_profile": profile,
            "updated_profile": updated_profile
        }
    else:
        return {
            "loop_id": loop_id,
            "operator_id": operator_id,
            "profile_updated": False,
            "reason": "No significant changes detected",
            "current_profile": profile
        }

async def process_all_loops_for_operator_profiles(loop_ids: List[str]) -> Dict[str, Any]:
    """
    Process multiple loops to update operator profiles.
    
    Args:
        loop_ids: List of loop IDs to process
        
    Returns:
        Dict mapping operator IDs to processing results
    """
    # Group loops by operator
    operator_loops = defaultdict(list)
    
    for loop_id in loop_ids:
        trace = await get_loop_trace(loop_id)
        if "error" not in trace and "operator_id" in trace:
            operator_id = trace["operator_id"]
            operator_loops[operator_id].append(loop_id)
    
    # Process loops for each operator
    results = {}
    
    for operator_id, loops in operator_loops.items():
        operator_results = {
            "loops_processed": [],
            "profile_updates": {}
        }
        
        for loop_id in loops:
            result = await process_loop_for_operator_profile(loop_id)
            operator_results["loops_processed"].append(loop_id)
            
            if result.get("profile_updated", False):
                operator_results["profile_updates"][loop_id] = result["profile_updates"]
        
        # Get final profile
        profile = await get_operator_profile(operator_id)
        operator_results["final_profile"] = profile
        
        results[operator_id] = operator_results
    
    return results

async def inject_operator_profile_into_loop_trace(loop_id: str) -> bool:
    """
    Inject operator profile into a loop trace.
    
    Args:
        loop_id: The ID of the loop to update
        
    Returns:
        True if successful, False otherwise
    """
    # Get the loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return False
    
    # Extract operator ID
    operator_id = trace.get("operator_id")
    if not operator_id:
        return False
    
    # Get operator profile
    profile = await get_operator_profile(operator_id)
    
    # Update the trace with the profile
    trace["operator_profile"] = profile
    
    # Write the updated trace back to memory
    await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return True
