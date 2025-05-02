"""
Agent Trust Delta Monitoring Module

This module is responsible for monitoring trust scores for different agent personas,
calculating trust deltas based on loop performance, and providing agent performance reports.
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
    elif key == "agent_trust_scores":
        return {
            "SAGE": 0.85,
            "NOVA": 0.82,
            "CRITIC": 0.79,
            "PESSIMIST": 0.76,
            "CEO": 0.83,
            "HAL": 0.80
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

async def get_agent_trust_scores() -> Dict[str, float]:
    """
    Get current trust scores for all agents.
    
    Returns:
        Dict mapping agent names to trust scores
    """
    scores = await read_from_memory("agent_trust_scores")
    if not isinstance(scores, dict):
        # Default scores if none exist
        return {
            "SAGE": 0.80,
            "NOVA": 0.80,
            "CRITIC": 0.80,
            "PESSIMIST": 0.80,
            "CEO": 0.80,
            "HAL": 0.80
        }
    return scores

async def update_agent_trust_score(agent: str, delta: float) -> Dict[str, Any]:
    """
    Update the trust score for an agent.
    
    Args:
        agent: The name of the agent
        delta: The amount to adjust the trust score by
        
    Returns:
        Dict with update result
    """
    # Get current trust scores
    scores = await get_agent_trust_scores()
    
    # Get current score for the agent
    current_score = scores.get(agent, 0.8)
    
    # Calculate new score
    new_score = current_score + delta
    
    # Ensure score is between 0 and 1
    new_score = max(0.0, min(1.0, new_score))
    
    # Update score
    scores[agent] = round(new_score, 2)
    
    # Write updated scores to memory
    await write_to_memory("agent_trust_scores", scores)
    
    return {
        "agent": agent,
        "previous_score": current_score,
        "delta": delta,
        "new_score": new_score
    }

async def calculate_trust_delta(loop_id: str) -> Dict[str, Any]:
    """
    Calculate the trust delta for an agent based on loop performance.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with trust delta calculation
    """
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    if "error" in trace:
        return {
            "error": trace["error"],
            "loop_id": loop_id
        }
    
    # Extract relevant information
    agent = trace.get("orchestrator_persona", "")
    if not agent:
        return {
            "error": "No orchestrator persona found in loop trace",
            "loop_id": loop_id
        }
    
    alignment_score = trace.get("alignment_score", 0.0)
    drift_score = trace.get("drift_score", 0.0)
    rerun_count = trace.get("rerun_count", 0)
    
    # Calculate base delta based on alignment score
    # Higher alignment = positive delta
    base_delta = (alignment_score - 0.75) * 0.1
    
    # Adjust for drift score
    # Higher drift = negative delta
    drift_adjustment = -drift_score * 0.1
    
    # Adjust for reruns
    # More reruns = negative delta
    rerun_adjustment = -rerun_count * 0.02
    
    # Calculate total delta
    total_delta = base_delta + drift_adjustment + rerun_adjustment
    
    # Limit maximum delta to prevent extreme changes
    total_delta = max(-0.1, min(0.1, total_delta))
    
    # Round to 2 decimal places
    total_delta = round(total_delta, 2)
    
    return {
        "loop_id": loop_id,
        "agent": agent,
        "trust_delta": total_delta,
        "factors": {
            "alignment_score": alignment_score,
            "drift_score": drift_score,
            "rerun_count": rerun_count,
            "base_delta": round(base_delta, 2),
            "drift_adjustment": round(drift_adjustment, 2),
            "rerun_adjustment": round(rerun_adjustment, 2)
        }
    }

async def process_loop_for_trust_delta(loop_id: str) -> Dict[str, Any]:
    """
    Process a loop to calculate and apply trust delta.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dict with processing result
    """
    # Calculate trust delta
    delta_result = await calculate_trust_delta(loop_id)
    if "error" in delta_result:
        return delta_result
    
    # Extract agent and delta
    agent = delta_result["agent"]
    delta = delta_result["trust_delta"]
    
    # Update agent trust score
    update_result = await update_agent_trust_score(agent, delta)
    
    # Get loop trace
    trace = await get_loop_trace(loop_id)
    
    # Add trust delta to loop trace
    if "error" not in trace:
        if "agent_trust_delta" not in trace:
            trace["agent_trust_delta"] = {}
        
        trace["agent_trust_delta"][agent] = delta
        
        # Write updated trace to memory
        await write_to_memory(f"loop_trace[{loop_id}]", trace)
    
    return {
        "loop_id": loop_id,
        "agent": agent,
        "trust_delta": delta,
        "updated_trust_score": update_result["new_score"],
        "factors": delta_result["factors"]
    }

async def process_all_loops_for_trust_delta(loop_ids: List[str]) -> Dict[str, Any]:
    """
    Process multiple loops to calculate and apply trust deltas.
    
    Args:
        loop_ids: List of loop IDs to process
        
    Returns:
        Dict mapping loop IDs to processing results
    """
    results = {}
    
    for loop_id in loop_ids:
        result = await process_loop_for_trust_delta(loop_id)
        results[loop_id] = result
    
    return results

async def get_agent_performance_report(agent: str) -> Dict[str, Any]:
    """
    Get a performance report for an agent.
    
    Args:
        agent: The name of the agent
        
    Returns:
        Dict with performance report
    """
    # Get current trust score
    scores = await get_agent_trust_scores()
    trust_score = scores.get(agent, 0.8)
    
    # Get all loop IDs
    # In a real implementation, this would query the database for all loop IDs
    # For this mock implementation, we'll use a hardcoded list
    loop_ids = ["loop_001", "loop_002", "loop_003", "loop_004", "loop_005"]
    
    # Collect loops orchestrated by this agent
    agent_loops = []
    for loop_id in loop_ids:
        trace = await get_loop_trace(loop_id)
        if "error" not in trace and trace.get("orchestrator_persona") == agent:
            agent_loops.append(loop_id)
    
    # Calculate performance metrics
    total_loops = len(agent_loops)
    
    if total_loops > 0:
        # Collect metrics from loops
        alignment_scores = []
        drift_scores = []
        rerun_counts = []
        
        for loop_id in agent_loops:
            trace = await get_loop_trace(loop_id)
            if "error" not in trace:
                alignment_scores.append(trace.get("alignment_score", 0.0))
                drift_scores.append(trace.get("drift_score", 0.0))
                rerun_counts.append(trace.get("rerun_count", 0))
        
        # Calculate averages
        avg_alignment = sum(alignment_scores) / total_loops if alignment_scores else 0.0
        avg_drift = sum(drift_scores) / total_loops if drift_scores else 0.0
        avg_reruns = sum(rerun_counts) / total_loops if rerun_counts else 0.0
        
        # Calculate success rate (loops with alignment > 0.8)
        success_count = sum(1 for score in alignment_scores if score > 0.8)
        success_rate = success_count / total_loops if total_loops > 0 else 0.0
        
        performance_metrics = {
            "total_loops": total_loops,
            "average_alignment": round(avg_alignment, 2),
            "average_drift": round(avg_drift, 2),
            "average_reruns": round(avg_reruns, 2),
            "success_rate": round(success_rate, 2)
        }
    else:
        performance_metrics = {
            "total_loops": 0,
            "average_alignment": 0.0,
            "average_drift": 0.0,
            "average_reruns": 0.0,
            "success_rate": 0.0
        }
    
    # Determine performance level
    if trust_score >= 0.9:
        performance_level = "excellent"
    elif trust_score >= 0.8:
        performance_level = "good"
    elif trust_score >= 0.7:
        performance_level = "satisfactory"
    elif trust_score >= 0.6:
        performance_level = "needs_improvement"
    else:
        performance_level = "poor"
    
    # Create report
    report = {
        "agent": agent,
        "trust_score": trust_score,
        "performance_level": performance_level,
        "performance_metrics": performance_metrics,
        "loops_orchestrated": agent_loops,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return report

async def compare_agent_performance(agent1: str, agent2: str) -> Dict[str, Any]:
    """
    Compare the performance of two agents.
    
    Args:
        agent1: The name of the first agent
        agent2: The name of the second agent
        
    Returns:
        Dict with comparison result
    """
    # Get performance reports
    report1 = await get_agent_performance_report(agent1)
    report2 = await get_agent_performance_report(agent2)
    
    # Extract trust scores
    trust_score1 = report1["trust_score"]
    trust_score2 = report2["trust_score"]
    
    # Calculate trust score delta
    trust_score_delta = trust_score1 - trust_score2
    
    # Extract performance metrics
    metrics1 = report1["performance_metrics"]
    metrics2 = report2["performance_metrics"]
    
    # Compare metrics
    metric_comparisons = {}
    
    for metric in ["average_alignment", "average_drift", "average_reruns", "success_rate"]:
        value1 = metrics1.get(metric, 0.0)
        value2 = metrics2.get(metric, 0.0)
        delta = value1 - value2
        
        # For drift and reruns, lower is better
        if metric in ["average_drift", "average_reruns"]:
            better_agent = agent1 if delta < 0 else agent2 if delta > 0 else "tie"
        else:
            better_agent = agent1 if delta > 0 else agent2 if delta < 0 else "tie"
        
        metric_comparisons[metric] = {
            "agent1_value": value1,
            "agent2_value": value2,
            "delta": round(delta, 2),
            "better_agent": better_agent
        }
    
    # Determine overall better agent
    better_count1 = sum(1 for comp in metric_comparisons.values() if comp["better_agent"] == agent1)
    better_count2 = sum(1 for comp in metric_comparisons.values() if comp["better_agent"] == agent2)
    
    if better_count1 > better_count2:
        overall_better = agent1
    elif better_count2 > better_count1:
        overall_better = agent2
    else:
        # If tied on metrics, use trust score
        overall_better = agent1 if trust_score1 > trust_score2 else agent2 if trust_score2 > trust_score1 else "tie"
    
    # Generate recommendation
    if overall_better == "tie":
        recommendation = f"Both {agent1} and {agent2} perform similarly. Choose based on specific task requirements."
    else:
        recommendation = f"{overall_better} generally performs better and is recommended for most tasks."
    
    # Create comparison result
    comparison = {
        "agent1": agent1,
        "agent2": agent2,
        "trust_score_delta": round(trust_score_delta, 2),
        "metric_comparisons": metric_comparisons,
        "overall_better_agent": overall_better,
        "recommendation": recommendation,
        "timestamp": datetime.utcnow().isoformat(),
        "comparison": {
            "trust_scores": {
                agent1: trust_score1,
                agent2: trust_score2
            },
            "metrics": metric_comparisons,
            "conclusion": recommendation
        }
    }
    
    return comparison
