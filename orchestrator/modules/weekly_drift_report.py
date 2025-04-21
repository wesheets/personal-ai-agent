"""
Weekly Drift Report Generator

This module aggregates recent drift summaries, CEO insights, CTO reports, and historian alerts
to produce a high-level reflection report every 7 loops (or on manual trigger).
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

def generate_weekly_drift_report(
    loop_range: List[str],
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a comprehensive weekly drift report by aggregating data from multiple sources.
    
    Args:
        loop_range (List[str]): List of loop IDs to include in the report
        memory (Dict[str, Any]): The memory dictionary containing agent outputs
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Weekly drift report with system health metrics and recommendations
    """
    # Use default config if none provided
    if config is None:
        config = {
            "critical_drift_threshold": 0.6,
            "critical_count_threshold": 2,
            "belief_reference_threshold": 0.3
        }
    
    # Generate report ID based on loop range
    report_id = f"drift_week_{int(loop_range[-1].split('_')[-1]) // 7:03d}"
    
    # Extract drift summaries for the specified loops
    drift_summaries = _extract_drift_summaries(loop_range, memory)
    
    # Extract CEO insights for the specified loops
    ceo_insights = _extract_ceo_insights(loop_range, memory)
    
    # Extract CTO reports for the specified loops
    cto_reports = _extract_cto_reports(loop_range, memory)
    
    # Extract historian alerts for the specified loops
    historian_alerts = _extract_historian_alerts(loop_range, memory)
    
    # Calculate drift summary statistics
    drift_summary_stats = _calculate_drift_summary_stats(drift_summaries)
    
    # Calculate belief engagement metrics
    belief_engagement = _calculate_belief_engagement(historian_alerts, config)
    
    # Calculate trust trend metrics
    trust_trend = _calculate_trust_trend(cto_reports)
    
    # Calculate mode usage statistics
    mode_usage = _calculate_mode_usage(loop_range, memory)
    
    # Generate recommendation based on metrics
    recommendation = _generate_recommendation(
        drift_summary_stats,
        belief_engagement,
        trust_trend,
        config
    )
    
    # Create weekly drift report
    weekly_drift_report = {
        "report_id": report_id,
        "loop_range": loop_range,
        "drift_summary_stats": drift_summary_stats,
        "belief_engagement": belief_engagement,
        "trust_trend": trust_trend,
        "mode_usage": mode_usage,
        "recommendation": recommendation,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return weekly_drift_report

def _extract_drift_summaries(loop_range: List[str], memory: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts drift summaries for the specified loops.
    
    Args:
        loop_range (List[str]): List of loop IDs to include
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        List[Dict[str, Any]]: List of drift summaries for the specified loops
    """
    if "drift_summaries" not in memory:
        return []
    
    loop_set = set(loop_range)
    return [
        summary for summary in memory["drift_summaries"]
        if summary.get("loop_id") in loop_set
    ]

def _extract_ceo_insights(loop_range: List[str], memory: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts CEO insights for the specified loops.
    
    Args:
        loop_range (List[str]): List of loop IDs to include
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        List[Dict[str, Any]]: List of CEO insights for the specified loops
    """
    if "ceo_insights" not in memory:
        return []
    
    loop_set = set(loop_range)
    return [
        insight for insight in memory["ceo_insights"]
        if insight.get("loop_id") in loop_set
    ]

def _extract_cto_reports(loop_range: List[str], memory: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts CTO reports for the specified loops.
    
    Args:
        loop_range (List[str]): List of loop IDs to include
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        List[Dict[str, Any]]: List of CTO reports for the specified loops
    """
    if "cto_reports" not in memory:
        return []
    
    loop_set = set(loop_range)
    return [
        report for report in memory["cto_reports"]
        if report.get("loop_id") in loop_set
    ]

def _extract_historian_alerts(loop_range: List[str], memory: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts historian alerts for the specified loops.
    
    Args:
        loop_range (List[str]): List of loop IDs to include
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        List[Dict[str, Any]]: List of historian alerts for the specified loops
    """
    if "historian_alerts" not in memory:
        return []
    
    loop_set = set(loop_range)
    return [
        alert for alert in memory["historian_alerts"]
        if alert.get("loop_id") in loop_set
    ]

def _calculate_drift_summary_stats(drift_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates statistics from drift summaries.
    
    Args:
        drift_summaries (List[Dict[str, Any]]): List of drift summaries
        
    Returns:
        Dict[str, Any]: Drift summary statistics
    """
    if not drift_summaries:
        return {
            "avg_drift_score": 0.0,
            "critical_drift_count": 0,
            "common_biases": []
        }
    
    # Calculate average drift score
    alignment_scores = []
    belief_alignment_scores = []
    health_scores = []
    
    for summary in drift_summaries:
        if "alignment_score" in summary:
            alignment_scores.append(summary["alignment_score"])
        
        if "belief_alignment_score" in summary:
            belief_alignment_scores.append(summary["belief_alignment_score"])
        
        if "health_score" in summary:
            health_scores.append(summary["health_score"])
    
    # Calculate average scores
    avg_alignment = sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
    avg_belief_alignment = sum(belief_alignment_scores) / len(belief_alignment_scores) if belief_alignment_scores else 0.0
    avg_health = sum(health_scores) / len(health_scores) if health_scores else 0.0
    
    # Calculate overall drift score (inverse of the average of alignment scores)
    # Higher drift score means more drift (worse)
    avg_drift_score = 1.0 - ((avg_alignment + avg_belief_alignment + avg_health) / 3.0)
    
    # Count critical drift occurrences
    critical_drift_count = sum(
        1 for summary in drift_summaries
        if summary.get("drift_severity") == "critical"
    )
    
    # Identify common bias tags
    all_bias_tags = []
    for summary in drift_summaries:
        if "bias_tags" in summary:
            all_bias_tags.extend(summary["bias_tags"])
    
    # Count occurrences of each bias tag
    bias_counter = Counter(all_bias_tags)
    
    # Get the most common bias tags (at least 2 occurrences)
    common_biases = [
        tag for tag, count in bias_counter.most_common()
        if count >= 2
    ]
    
    return {
        "avg_drift_score": round(avg_drift_score, 2),
        "critical_drift_count": critical_drift_count,
        "common_biases": common_biases
    }

def _calculate_belief_engagement(
    historian_alerts: List[Dict[str, Any]],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculates belief engagement metrics from historian alerts.
    
    Args:
        historian_alerts (List[Dict[str, Any]]): List of historian alerts
        config (Dict[str, Any]): Configuration options
        
    Returns:
        Dict[str, Any]: Belief engagement metrics
    """
    if not historian_alerts:
        return {
            "most_referenced": None,
            "least_referenced": None
        }
    
    # Extract missing beliefs from all alerts
    all_missing_beliefs = []
    for alert in historian_alerts:
        if "missing_beliefs" in alert:
            all_missing_beliefs.extend(alert["missing_beliefs"])
    
    # Count occurrences of each missing belief
    missing_belief_counter = Counter(all_missing_beliefs)
    
    # Get all beliefs from the first alert (assuming all alerts have the same belief set)
    all_beliefs = []
    for alert in historian_alerts:
        if "all_beliefs" in alert:
            all_beliefs = alert["all_beliefs"]
            break
    
    # If all_beliefs is not available in alerts, use a default empty list
    if not all_beliefs:
        # Try to infer beliefs from missing_beliefs across all alerts
        all_beliefs = list(set(all_missing_beliefs))
    
    # Calculate reference counts for each belief
    belief_reference_counts = {}
    
    for belief in all_beliefs:
        # A belief is referenced if it's NOT in the missing_beliefs
        # Count how many times it was NOT missing
        reference_count = len(historian_alerts) - missing_belief_counter.get(belief, 0)
        belief_reference_counts[belief] = reference_count
    
    # Find most and least referenced beliefs
    if belief_reference_counts:
        most_referenced = max(belief_reference_counts.items(), key=lambda x: x[1])[0]
        least_referenced = min(belief_reference_counts.items(), key=lambda x: x[1])[0]
    else:
        most_referenced = None
        least_referenced = None
    
    return {
        "most_referenced": most_referenced,
        "least_referenced": least_referenced
    }

def _calculate_trust_trend(cto_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates trust trend metrics from CTO reports.
    
    Args:
        cto_reports (List[Dict[str, Any]]): List of CTO reports
        
    Returns:
        Dict[str, Any]: Trust trend metrics
    """
    if not cto_reports:
        return {
            "avg_health_score": 0.0,
            "avg_trust_decay": 0.0
        }
    
    # Extract health scores and trust decay values
    health_scores = []
    trust_decay_values = []
    
    for report in cto_reports:
        if "health_score" in report:
            health_scores.append(report["health_score"])
        
        if "trust_decay" in report:
            trust_decay_values.append(report["trust_decay"])
    
    # Calculate averages
    avg_health_score = sum(health_scores) / len(health_scores) if health_scores else 0.0
    avg_trust_decay = sum(trust_decay_values) / len(trust_decay_values) if trust_decay_values else 0.0
    
    return {
        "avg_health_score": round(avg_health_score, 2),
        "avg_trust_decay": round(avg_trust_decay, 2)
    }

def _calculate_mode_usage(loop_range: List[str], memory: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculates mode usage statistics for the specified loops.
    
    Args:
        loop_range (List[str]): List of loop IDs to include
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Dict[str, int]: Mode usage counts
    """
    mode_counts = {
        "RESEARCHER": 0,
        "SAGE": 0,
        "RITUALIST": 0,
        "THOUGHT_PARTNER": 0,
        "BUILDER": 0
    }
    
    # Extract mode usage from loops
    if "loops" in memory:
        loop_set = set(loop_range)
        for loop in memory["loops"]:
            if loop.get("loop_id") in loop_set and "mode" in loop:
                mode = loop["mode"]
                if mode in mode_counts:
                    mode_counts[mode] += 1
                else:
                    mode_counts[mode] = 1
    
    # Remove modes with zero usage
    return {mode: count for mode, count in mode_counts.items() if count > 0}

def _generate_recommendation(
    drift_summary_stats: Dict[str, Any],
    belief_engagement: Dict[str, Any],
    trust_trend: Dict[str, Any],
    config: Dict[str, Any]
) -> str:
    """
    Generates a recommendation based on drift metrics.
    
    Args:
        drift_summary_stats (Dict[str, Any]): Drift summary statistics
        belief_engagement (Dict[str, Any]): Belief engagement metrics
        trust_trend (Dict[str, Any]): Trust trend metrics
        config (Dict[str, Any]): Configuration options
        
    Returns:
        str: Recommendation for system improvement
    """
    # Extract metrics
    avg_drift_score = drift_summary_stats.get("avg_drift_score", 0.0)
    critical_drift_count = drift_summary_stats.get("critical_drift_count", 0)
    common_biases = drift_summary_stats.get("common_biases", [])
    
    least_referenced_belief = belief_engagement.get("least_referenced")
    
    avg_health_score = trust_trend.get("avg_health_score", 0.0)
    avg_trust_decay = trust_trend.get("avg_trust_decay", 0.0)
    
    # Get thresholds from config
    critical_drift_threshold = config.get("critical_drift_threshold", 0.6)
    critical_count_threshold = config.get("critical_count_threshold", 2)
    
    # Check for critical conditions
    critical_conditions = []
    
    if avg_drift_score >= critical_drift_threshold:
        critical_conditions.append("high average drift")
    
    if critical_drift_count >= critical_count_threshold:
        critical_conditions.append(f"{critical_drift_count} critical drift incidents")
    
    if avg_trust_decay >= 0.15:
        critical_conditions.append("significant trust decay")
    
    if avg_health_score <= 0.5:
        critical_conditions.append("poor system health")
    
    # Generate recommendation based on conditions
    if critical_conditions:
        conditions_str = ", ".join(critical_conditions)
        return f"Pause building. Enter SAGE mode and reflect on system alignment due to {conditions_str}."
    
    # Check for moderate conditions
    if avg_drift_score >= 0.4:
        if "optimism_bias" in common_biases:
            return "Schedule emotional tone calibration session and enable Pessimist agent."
        elif least_referenced_belief:
            return f"Enter THOUGHT_PARTNER mode to reinforce the belief: '{least_referenced_belief}'."
        else:
            return "Reduce complexity of next few loops and focus on core functionality."
    
    if avg_trust_decay >= 0.1:
        return "Implement trust-building exercises and enable CRITIC for next several loops."
    
    # Default recommendation for healthy system
    return "Continue normal operation with standard monitoring."

def store_weekly_drift_report(memory: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stores a weekly drift report in memory.
    
    Args:
        memory (Dict[str, Any]): The memory dictionary
        report (Dict[str, Any]): The weekly drift report to store
        
    Returns:
        Dict[str, Any]: Updated memory with weekly drift report
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Initialize weekly_drift_reports if it doesn't exist
    if "weekly_drift_reports" not in updated_memory:
        updated_memory["weekly_drift_reports"] = []
    
    # Add report to memory
    updated_memory["weekly_drift_reports"].append(report)
    
    return updated_memory

def handle_critical_drift_pattern(memory: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles critical drift patterns by generating CTO warnings.
    
    Args:
        memory (Dict[str, Any]): The memory dictionary
        report (Dict[str, Any]): The weekly drift report
        
    Returns:
        Dict[str, Any]: Updated memory with CTO warnings
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Extract metrics
    drift_summary_stats = report.get("drift_summary_stats", {})
    avg_drift_score = drift_summary_stats.get("avg_drift_score", 0.0)
    critical_drift_count = drift_summary_stats.get("critical_drift_count", 0)
    
    # Check if escalation is needed
    needs_escalation = (avg_drift_score > 0.6 or critical_drift_count > 2)
    
    if not needs_escalation:
        return updated_memory
    
    # Initialize cto_warnings if it doesn't exist
    if "cto_warnings" not in updated_memory:
        updated_memory["cto_warnings"] = []
    
    # Create warning
    warning = {
        "type": "critical_drift_pattern",
        "report_id": report["report_id"],
        "message": f"Critical drift pattern detected: avg_drift={avg_drift_score}, critical_count={critical_drift_count}",
        "recommendation": report["recommendation"],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Add warning to memory
    updated_memory["cto_warnings"].append(warning)
    
    return updated_memory

def should_generate_weekly_report(
    current_loop_id: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Tuple[bool, List[str]]:
    """
    Determines if a weekly drift report should be generated.
    
    Args:
        current_loop_id (str): The current loop ID
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Tuple[bool, List[str]]: Whether a report should be generated and the loop range to include
    """
    # Use default config if none provided
    if config is None:
        config = {
            "report_frequency": 7,
            "min_loops_required": 3
        }
    
    # Extract loop number from loop ID
    try:
        current_loop_num = int(current_loop_id.split('_')[-1])
    except (ValueError, IndexError):
        return False, []
    
    # Get report frequency from config
    report_frequency = config.get("report_frequency", 7)
    min_loops_required = config.get("min_loops_required", 3)
    
    # Check if current loop is a multiple of the report frequency
    if current_loop_num % report_frequency != 0:
        return False, []
    
    # Calculate loop range
    start_loop_num = max(0, current_loop_num - report_frequency + 1)
    loop_range = [f"loop_{i:04d}" for i in range(start_loop_num, current_loop_num + 1)]
    
    # Check if we have enough loops
    if len(loop_range) < min_loops_required:
        return False, []
    
    return True, loop_range

def process_loop_with_weekly_drift_report(
    loop_id: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    manual_trigger: bool = False
) -> Dict[str, Any]:
    """
    Processes a loop with the weekly drift report generator.
    
    Args:
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        manual_trigger (bool): Whether this is a manual trigger
        
    Returns:
        Dict[str, Any]: Updated memory with weekly drift report
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "report_frequency": 7,
            "min_loops_required": 3,
            "critical_drift_threshold": 0.6,
            "critical_count_threshold": 2
        }
    
    # Skip processing if disabled
    if not config.get("enabled", True):
        return memory
    
    # Check if report should be generated
    should_generate, loop_range = should_generate_weekly_report(loop_id, memory, config)
    
    # Skip if report should not be generated and not manually triggered
    if not should_generate and not manual_trigger:
        return memory
    
    # If manually triggered but no loop range, use last 7 loops or all available loops
    if manual_trigger and not loop_range:
        # Extract all loop IDs from memory
        all_loop_ids = []
        if "loops" in memory:
            all_loop_ids = [loop.get("loop_id") for loop in memory["loops"] if "loop_id" in loop]
        
        # Sort loop IDs
        all_loop_ids.sort()
        
        # Use last 7 loops or all available loops
        loop_range = all_loop_ids[-7:] if len(all_loop_ids) > 7 else all_loop_ids
    
    # Generate weekly drift report
    report = generate_weekly_drift_report(loop_range, memory, config)
    
    # Store report in memory
    updated_memory = store_weekly_drift_report(memory, report)
    
    # Handle critical drift pattern if necessary
    updated_memory = handle_critical_drift_pattern(updated_memory, report)
    
    return updated_memory
