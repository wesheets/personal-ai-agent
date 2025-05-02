"""
Historian Drift Report Module

This module is responsible for generating belief drift reports for loops,
comparing loops for belief drift, and injecting drift reports into loop traces.
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

async def get_all_loop_ids() -> List[str]:
    """
    Get all loop IDs.
    
    Returns:
        List of loop IDs
    """
    # In a real implementation, this would query the database for all loop IDs
    # For this mock implementation, we'll use a hardcoded list
    return ["loop_001", "loop_002", "loop_003", "loop_004", "loop_005"]

async def get_previous_loops(loop_id: str, limit: int = 5) -> List[str]:
    """
    Get the IDs of previous loops.
    
    Args:
        loop_id: The ID of the current loop
        limit: Maximum number of previous loops to return
        
    Returns:
        List of previous loop IDs
    """
    # In a real implementation, this would query the database for previous loops
    # For this mock implementation, we'll use a simple pattern
    
    # Extract the numeric part of the loop ID
    match = re.match(r"loop_(\d+)", loop_id)
    if not match:
        return []
    
    loop_num = int(match.group(1))
    
    # Generate previous loop IDs
    previous_loops = []
    for i in range(1, limit + 1):
        prev_num = loop_num - i
        if prev_num > 0:
            previous_loops.append(f"loop_{prev_num:03d}")
    
    return previous_loops

async def compare_loops(loop_id_1: str, loop_id_2: str) -> Dict[str, Any]:
    """
    Compare two loops for belief drift.
    
    Args:
        loop_id_1: The ID of the first loop
        loop_id_2: The ID of the second loop
        
    Returns:
        Dict with comparison results
    """
    # Get loop traces
    trace_1 = await get_loop_trace(loop_id_1)
    trace_2 = await get_loop_trace(loop_id_2)
    
    # Check for errors
    if "error" in trace_1:
        return {
            "error": trace_1["error"],
            "loop_id_1": loop_id_1,
            "loop_id_2": loop_id_2
        }
    
    if "error" in trace_2:
        return {
            "error": trace_2["error"],
            "loop_id_1": loop_id_1,
            "loop_id_2": loop_id_2
        }
    
    # Extract drift scores
    drift_1 = trace_1.get("drift_score", 0.0)
    drift_2 = trace_2.get("drift_score", 0.0)
    
    # Calculate delta
    delta = abs(drift_2 - drift_1)
    
    # Determine trend
    if drift_2 > drift_1:
        trend = "increasing"
    elif drift_2 < drift_1:
        trend = "decreasing"
    else:
        trend = "stable"
    
    # Check for flags
    flags = []
    
    # Flag if drift is increasing significantly
    if trend == "increasing" and delta > 0.1:
        flags.append("significant_drift_increase")
    
    # Flag if alignment is decreasing
    alignment_1 = trace_1.get("alignment_score", 0.0)
    alignment_2 = trace_2.get("alignment_score", 0.0)
    
    if alignment_2 < alignment_1:
        flags.append("alignment_decrease")
    
    # Flag if different orchestrators
    orchestrator_1 = trace_1.get("orchestrator_persona", "")
    orchestrator_2 = trace_2.get("orchestrator_persona", "")
    
    if orchestrator_1 and orchestrator_2 and orchestrator_1 != orchestrator_2:
        flags.append("orchestrator_change")
    
    # Create comparison result
    comparison = {
        "loop_id_1": loop_id_1,
        "loop_id_2": loop_id_2,
        "drift_1": drift_1,
        "drift_2": drift_2,
        "delta": delta,
        "trend": trend,
        "flags": flags,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return comparison

async def compare_multiple_loops(loop_ids: List[str]) -> Dict[str, Any]:
    """
    Compare multiple loops for belief drift trends.
    
    Args:
        loop_ids: List of loop IDs to compare
        
    Returns:
        Dict with comparison results
    """
    if len(loop_ids) < 2:
        return {
            "error": "At least two loops are required for comparison",
            "loop_ids": loop_ids
        }
    
    # Sort loop IDs
    sorted_ids = sorted(loop_ids)
    
    # Compare adjacent loops
    comparisons = []
    for i in range(len(sorted_ids) - 1):
        comparison = await compare_loops(sorted_ids[i], sorted_ids[i + 1])
        if "error" not in comparison:
            comparisons.append(comparison)
    
    # Calculate overall trend
    if not comparisons:
        return {
            "error": "No valid comparisons could be made",
            "loop_ids": loop_ids
        }
    
    # Count trends
    trend_counts = {"increasing": 0, "decreasing": 0, "stable": 0}
    for comp in comparisons:
        trend = comp.get("trend", "")
        if trend in trend_counts:
            trend_counts[trend] += 1
    
    # Determine dominant trend
    max_trend = max(trend_counts.items(), key=lambda x: x[1])
    dominant_trend = max_trend[0]
    
    # Calculate average delta
    total_delta = sum(comp.get("delta", 0.0) for comp in comparisons)
    avg_delta = total_delta / len(comparisons)
    
    # Collect all flags
    all_flags = set()
    for comp in comparisons:
        flags = comp.get("flags", [])
        all_flags.update(flags)
    
    # Create result
    result = {
        "loop_ids": sorted_ids,
        "comparisons": comparisons,
        "dominant_trend": dominant_trend,
        "average_delta": avg_delta,
        "flags": list(all_flags),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return result

async def generate_belief_drift_report(loop_id: str) -> Dict[str, Any]:
    """
    Generate a belief drift report for a loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with belief drift report
    """
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Get previous loops
    previous_loops = await get_previous_loops(loop_id)
    
    # Create list of loops to compare
    loops_to_compare = previous_loops + [loop_id]
    
    # Compare loops
    comparison_result = await compare_multiple_loops(loops_to_compare)
    
    # Extract drift score from trace
    drift_score = trace.get("drift_score", 0.0)
    
    # Determine drift level
    if drift_score < 0.1:
        drift_level = "minimal"
    elif drift_score < 0.2:
        drift_level = "low"
    elif drift_score < 0.3:
        drift_level = "moderate"
    elif drift_score < 0.4:
        drift_level = "high"
    else:
        drift_level = "extreme"
    
    # Create belief drift trend
    belief_drift_trend = {
        "loops_compared": loops_to_compare,
        "delta": comparison_result.get("average_delta", 0.0) if "error" not in comparison_result else 0.0,
        "trend": comparison_result.get("dominant_trend", "stable") if "error" not in comparison_result else "unknown",
        "flags": comparison_result.get("flags", []) if "error" not in comparison_result else []
    }
    
    # Create report
    report = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "drift_score": drift_score,
        "drift_level": drift_level,
        "belief_drift_trend": belief_drift_trend,
        "comparisons": comparison_result.get("comparisons", []) if "error" not in comparison_result else []
    }
    
    return report

async def inject_drift_report_into_loop_trace(loop_id: str) -> bool:
    """
    Inject a belief drift report into a loop trace.
    
    Args:
        loop_id: The ID of the loop to update
        
    Returns:
        True if successful, False otherwise
    """
    # Get the loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return False
    
    # Generate the drift report
    report = await generate_belief_drift_report(loop_id)
    if "error" in report:
        return False
    
    # Update the trace with the drift report
    trace["belief_drift_report"] = report
    
    # Extract key metrics for quick access
    trace["belief_drift_trend"] = report["belief_drift_trend"]
    
    # Write the updated trace back to memory
    await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return True

async def generate_drift_reports_for_all_loops() -> Dict[str, Any]:
    """
    Generate belief drift reports for all loops.
    
    Returns:
        Dict with generation results
    """
    # Get all loop IDs
    loop_ids = await get_all_loop_ids()
    
    # Generate reports for each loop
    results = {}
    for loop_id in loop_ids:
        report = await generate_belief_drift_report(loop_id)
        await inject_drift_report_into_loop_trace(loop_id)
        results[loop_id] = report
    
    # Calculate aggregate statistics
    total_loops = len(results)
    drift_levels = defaultdict(int)
    
    for report in results.values():
        if "error" not in report:
            drift_level = report.get("drift_level", "unknown")
            drift_levels[drift_level] += 1
    
    # Create summary report
    summary = {
        "total_loops_processed": total_loops,
        "drift_level_distribution": dict(drift_levels),
        "timestamp": datetime.utcnow().isoformat(),
        "results": results
    }
    
    return summary

async def compare_loops_for_belief_drift(loop_id_1: str, loop_id_2: str) -> Dict[str, Any]:
    """
    Compare two loops specifically for belief drift.
    
    Args:
        loop_id_1: The ID of the first loop
        loop_id_2: The ID of the second loop
        
    Returns:
        Dict with belief drift comparison results
    """
    # Use the existing compare_loops function as the base
    comparison = await compare_loops(loop_id_1, loop_id_2)
    
    # Check for errors
    if "error" in comparison:
        return comparison
    
    # Get loop traces
    trace_1 = await get_loop_trace(loop_id_1)
    trace_2 = await get_loop_trace(loop_id_2)
    
    # Extract summaries
    summary_1 = trace_1.get("summary", "")
    summary_2 = trace_2.get("summary", "")
    
    # Analyze belief drift in more detail
    belief_drift_analysis = {
        "drift_detected": comparison["delta"] > 0.1,
        "drift_score": comparison["delta"],
        "drift_direction": comparison["trend"],
        "drift_areas": []
    }
    
    # Identify potential drift areas based on flags
    if "significant_drift_increase" in comparison["flags"]:
        belief_drift_analysis["drift_areas"].append("belief_consistency")
    
    if "alignment_decrease" in comparison["flags"]:
        belief_drift_analysis["drift_areas"].append("core_alignment")
    
    if "orchestrator_change" in comparison["flags"]:
        belief_drift_analysis["drift_areas"].append("orchestration_approach")
    
    # Add more detailed analysis based on summaries
    # This would use NLP in a real implementation, but we'll use simple keyword matching for the mock
    keywords = {
        "ethics": ["ethic", "moral", "right", "wrong", "good", "bad", "should", "ought"],
        "reasoning": ["reason", "logic", "rational", "argument", "evidence", "conclusion"],
        "factual": ["fact", "data", "information", "statistic", "research", "study"],
        "methodology": ["method", "approach", "technique", "procedure", "process", "strategy"]
    }
    
    # Check for keyword presence differences
    for area, words in keywords.items():
        area_present_1 = any(word in summary_1.lower() for word in words)
        area_present_2 = any(word in summary_2.lower() for word in words)
        
        if area_present_1 != area_present_2:
            belief_drift_analysis["drift_areas"].append(area)
    
    # Enhance the comparison with belief drift analysis
    enhanced_comparison = {
        **comparison,
        "belief_drift_analysis": belief_drift_analysis,
        "analysis_timestamp": datetime.utcnow().isoformat()
    }
    
    return enhanced_comparison
