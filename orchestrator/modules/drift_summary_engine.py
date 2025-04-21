"""
Drift Summary Engine

This module aggregates signals from Historian, CEO, CTO, and Pessimist agents
to produce a unified drift snapshot after each loop.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

def generate_drift_summary(
    loop_id: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a comprehensive drift summary by aggregating data from multiple agents.
    
    Args:
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary containing agent outputs
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Drift summary with severity assessment and recommendations
    """
    # Use default config if none provided
    if config is None:
        config = {
            "severity_thresholds": {
                "critical": {
                    "alignment_score": 0.4,
                    "belief_alignment_score": 0.4,
                    "health_score": 0.5,
                    "trust_decay": 0.2
                },
                "moderate": {
                    "alignment_score": 0.6,
                    "belief_alignment_score": 0.6,
                    "health_score": 0.7,
                    "trust_decay": 0.1
                }
            }
        }
    
    # Extract data from CEO insights
    alignment_score = _extract_ceo_alignment_score(loop_id, memory)
    
    # Extract data from Historian alerts
    belief_alignment_score = _extract_historian_alignment_score(loop_id, memory)
    
    # Extract data from CTO reports
    health_score, trust_decay = _extract_cto_health_metrics(loop_id, memory)
    
    # Extract data from Pessimist alerts
    bias_tags, tone_confidence = _extract_pessimist_metrics(loop_id, memory)
    
    # Calculate drift severity
    severity = _calculate_drift_severity(
        alignment_score,
        belief_alignment_score,
        health_score,
        trust_decay,
        bias_tags,
        config.get("severity_thresholds", {})
    )
    
    # Generate recommendation based on severity and metrics
    recommendation = _generate_recommendation(
        severity,
        alignment_score,
        belief_alignment_score,
        health_score,
        trust_decay,
        bias_tags
    )
    
    # Create drift summary
    drift_summary = {
        "loop_id": loop_id,
        "drift_severity": severity,
        "alignment_score": round(alignment_score, 2) if alignment_score is not None else None,
        "belief_alignment_score": round(belief_alignment_score, 2) if belief_alignment_score is not None else None,
        "health_score": round(health_score, 2) if health_score is not None else None,
        "trust_decay": round(trust_decay, 2) if trust_decay is not None else None,
        "bias_tags": bias_tags,
        "recommendation": recommendation,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Remove None values
    drift_summary = {k: v for k, v in drift_summary.items() if v is not None}
    
    return drift_summary

def _extract_ceo_alignment_score(loop_id: str, memory: Dict[str, Any]) -> Optional[float]:
    """
    Extracts alignment score from CEO insights.
    
    Args:
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Optional[float]: Alignment score or None if not found
    """
    if "ceo_insights" not in memory:
        return None
    
    for insight in memory["ceo_insights"]:
        if insight.get("loop_id") == loop_id and "alignment_score" in insight:
            return insight["alignment_score"]
    
    return None

def _extract_historian_alignment_score(loop_id: str, memory: Dict[str, Any]) -> Optional[float]:
    """
    Extracts belief alignment score from Historian alerts.
    
    Args:
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Optional[float]: Belief alignment score or None if not found
    """
    if "historian_alerts" not in memory:
        return None
    
    for alert in memory["historian_alerts"]:
        if alert.get("loop_id") == loop_id and "loop_belief_alignment_score" in alert:
            return alert["loop_belief_alignment_score"]
    
    return None

def _extract_cto_health_metrics(loop_id: str, memory: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    """
    Extracts health score and trust decay from CTO reports.
    
    Args:
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Tuple[Optional[float], Optional[float]]: Health score and trust decay, or None if not found
    """
    health_score = None
    trust_decay = None
    
    # Check CTO reports
    if "cto_reports" in memory:
        for report in memory["cto_reports"]:
            if report.get("loop_id") == loop_id:
                health_score = report.get("health_score")
                trust_decay = report.get("trust_decay")
                break
    
    # Check loops for health score if not found in reports
    if health_score is None and "loops" in memory:
        for loop in memory["loops"]:
            if loop.get("loop_id") == loop_id and "loop_health_score" in loop:
                health_score = loop["loop_health_score"]
                break
    
    return health_score, trust_decay

def _extract_pessimist_metrics(loop_id: str, memory: Dict[str, Any]) -> Tuple[List[str], Optional[float]]:
    """
    Extracts bias tags and tone confidence from Pessimist alerts.
    
    Args:
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        
    Returns:
        Tuple[List[str], Optional[float]]: Bias tags and tone confidence, or empty list and None if not found
    """
    bias_tags = []
    tone_confidence = None
    
    if "pessimist_alerts" in memory:
        for alert in memory["pessimist_alerts"]:
            if alert.get("loop_id") == loop_id:
                if "bias_tags" in alert:
                    bias_tags = alert["bias_tags"]
                
                if "details" in alert and "tone_score" in alert["details"]:
                    tone_confidence = alert["details"]["tone_score"]
                elif "confidence" in alert:
                    tone_confidence = alert["confidence"]
                
                break
    
    return bias_tags, tone_confidence

def _calculate_drift_severity(
    alignment_score: Optional[float],
    belief_alignment_score: Optional[float],
    health_score: Optional[float],
    trust_decay: Optional[float],
    bias_tags: List[str],
    thresholds: Dict[str, Dict[str, float]]
) -> str:
    """
    Calculates drift severity based on agent metrics.
    
    Args:
        alignment_score (Optional[float]): CEO alignment score
        belief_alignment_score (Optional[float]): Historian belief alignment score
        health_score (Optional[float]): CTO health score
        trust_decay (Optional[float]): CTO trust decay
        bias_tags (List[str]): Pessimist bias tags
        thresholds (Dict[str, Dict[str, float]]): Severity thresholds
        
    Returns:
        str: Drift severity ("low", "moderate", or "critical")
    """
    # Default to low severity
    severity = "low"
    
    # Get thresholds
    critical_thresholds = thresholds.get("critical", {})
    moderate_thresholds = thresholds.get("moderate", {})
    
    # Check for critical severity
    critical_conditions = 0
    total_conditions = 0
    
    if alignment_score is not None:
        total_conditions += 1
        if alignment_score <= critical_thresholds.get("alignment_score", 0.4):
            critical_conditions += 1
    
    if belief_alignment_score is not None:
        total_conditions += 1
        if belief_alignment_score <= critical_thresholds.get("belief_alignment_score", 0.4):
            critical_conditions += 1
    
    if health_score is not None:
        total_conditions += 1
        if health_score <= critical_thresholds.get("health_score", 0.5):
            critical_conditions += 1
    
    if trust_decay is not None:
        total_conditions += 1
        if trust_decay >= critical_thresholds.get("trust_decay", 0.2):
            critical_conditions += 1
    
    # Add bias tags as a condition
    if bias_tags:
        total_conditions += 1
        if len(bias_tags) >= 2:
            critical_conditions += 1
    
    # Calculate critical ratio
    if total_conditions > 0:
        critical_ratio = critical_conditions / total_conditions
        
        if critical_ratio >= 0.5:
            return "critical"
    
    # Check for moderate severity
    moderate_conditions = 0
    
    if alignment_score is not None:
        if alignment_score <= moderate_thresholds.get("alignment_score", 0.6):
            moderate_conditions += 1
    
    if belief_alignment_score is not None:
        if belief_alignment_score <= moderate_thresholds.get("belief_alignment_score", 0.6):
            moderate_conditions += 1
    
    if health_score is not None:
        if health_score <= moderate_thresholds.get("health_score", 0.7):
            moderate_conditions += 1
    
    if trust_decay is not None:
        if trust_decay >= moderate_thresholds.get("trust_decay", 0.1):
            moderate_conditions += 1
    
    # Add bias tags as a condition
    if bias_tags:
        if len(bias_tags) >= 1:
            moderate_conditions += 1
    
    # Calculate moderate ratio
    if total_conditions > 0:
        moderate_ratio = moderate_conditions / total_conditions
        
        if moderate_ratio >= 0.5:
            return "moderate"
    
    return severity

def _generate_recommendation(
    severity: str,
    alignment_score: Optional[float],
    belief_alignment_score: Optional[float],
    health_score: Optional[float],
    trust_decay: Optional[float],
    bias_tags: List[str]
) -> str:
    """
    Generates a recommendation based on drift severity and metrics.
    
    Args:
        severity (str): Drift severity
        alignment_score (Optional[float]): CEO alignment score
        belief_alignment_score (Optional[float]): Historian belief alignment score
        health_score (Optional[float]): CTO health score
        trust_decay (Optional[float]): CTO trust decay
        bias_tags (List[str]): Pessimist bias tags
        
    Returns:
        str: Recommendation for addressing drift
    """
    if severity == "critical":
        # Identify the most critical issues
        critical_issues = []
        
        if alignment_score is not None and alignment_score <= 0.4:
            critical_issues.append("CEO alignment")
        
        if belief_alignment_score is not None and belief_alignment_score <= 0.4:
            critical_issues.append("belief alignment")
        
        if health_score is not None and health_score <= 0.5:
            critical_issues.append("loop health")
        
        if trust_decay is not None and trust_decay >= 0.2:
            critical_issues.append("trust decay")
        
        if len(bias_tags) >= 2:
            critical_issues.append("bias detection")
        
        if critical_issues:
            issues_str = ", ".join(critical_issues)
            return f"System reset recommended due to critical issues with {issues_str}"
        else:
            return "System reset recommended due to critical drift detected"
    
    elif severity == "moderate":
        # Identify the most significant issues
        if alignment_score is not None and alignment_score <= 0.5:
            return "Re-engage Thought Partner and rerun Sage"
        
        if belief_alignment_score is not None and belief_alignment_score <= 0.5:
            return "Review system beliefs and reinforce core principles"
        
        if health_score is not None and health_score <= 0.6:
            return "Enable CRITIC by default for next several loops"
        
        if trust_decay is not None and trust_decay >= 0.15:
            return "Implement trust-building exercises and reduce agent autonomy"
        
        if "optimism_bias" in bias_tags:
            return "Adjust tone settings and enable pessimist agent for next loop"
        
        return "Monitor system closely and consider targeted interventions"
    
    else:  # low severity
        return "Continue normal operation with standard monitoring"

def store_drift_summary(memory: Dict[str, Any], drift_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stores a drift summary in memory.
    
    Args:
        memory (Dict[str, Any]): The memory dictionary
        drift_summary (Dict[str, Any]): The drift summary to store
        
    Returns:
        Dict[str, Any]: Updated memory with drift summary
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Initialize drift_summaries if it doesn't exist
    if "drift_summaries" not in updated_memory:
        updated_memory["drift_summaries"] = []
    
    # Add drift summary to memory
    updated_memory["drift_summaries"].append(drift_summary)
    
    return updated_memory

def handle_critical_drift(memory: Dict[str, Any], drift_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles critical drift by generating CTO warnings.
    
    Args:
        memory (Dict[str, Any]): The memory dictionary
        drift_summary (Dict[str, Any]): The drift summary with critical severity
        
    Returns:
        Dict[str, Any]: Updated memory with CTO warnings
    """
    # Create a copy of memory to avoid modifying the original
    updated_memory = memory.copy()
    
    # Only handle critical drift
    if drift_summary.get("drift_severity") != "critical":
        return updated_memory
    
    # Initialize cto_warnings if it doesn't exist
    if "cto_warnings" not in updated_memory:
        updated_memory["cto_warnings"] = []
    
    # Create warning
    warning = {
        "type": "critical_drift",
        "loop_id": drift_summary["loop_id"],
        "message": f"Critical drift detected: {drift_summary.get('recommendation', 'System reset recommended')}",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Add warning to memory
    updated_memory["cto_warnings"].append(warning)
    
    return updated_memory

def process_loop_with_drift_engine(
    loop_id: str,
    memory: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Processes a loop with the drift summary engine.
    
    Args:
        loop_id (str): The loop identifier
        memory (Dict[str, Any]): The memory dictionary
        config (Optional[Dict[str, Any]]): Configuration options
        
    Returns:
        Dict[str, Any]: Updated memory with drift summary and warnings
    """
    # Use default config if none provided
    if config is None:
        config = {
            "enabled": True,
            "severity_thresholds": {
                "critical": {
                    "alignment_score": 0.4,
                    "belief_alignment_score": 0.4,
                    "health_score": 0.5,
                    "trust_decay": 0.2
                },
                "moderate": {
                    "alignment_score": 0.6,
                    "belief_alignment_score": 0.6,
                    "health_score": 0.7,
                    "trust_decay": 0.1
                }
            }
        }
    
    # Skip processing if disabled
    if not config.get("enabled", True):
        return memory
    
    # Generate drift summary
    drift_summary = generate_drift_summary(loop_id, memory, config)
    
    # Store drift summary in memory
    updated_memory = store_drift_summary(memory, drift_summary)
    
    # Handle critical drift if necessary
    if drift_summary.get("drift_severity") == "critical":
        updated_memory = handle_critical_drift(updated_memory, drift_summary)
    
    return updated_memory
