"""
Drift Trend Logger Utility

This module provides utilities for logging and analyzing drift trends over time.
It supports appending drift events to the drift history file and retrieving
recent drift history for analysis.
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

def log_drift_event(drift_event: Dict[str, Any]) -> None:
    """
    Log a drift event to the drift history file.
    
    Args:
        drift_event: Dictionary containing drift event data
    """
    # Ensure drift event has required fields
    required_fields = ["timestamp", "surface_health_score", "drift_issues_detected", 
                      "validation_source", "validation_summary"]
    
    for field in required_fields:
        if field not in drift_event:
            raise ValueError(f"Drift event missing required field: {field}")
    
    # Create logs directory if it doesn't exist
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    log_dir = os.path.join(base_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Path to drift history file
    drift_history_file = os.path.join(log_dir, "drift_history.jsonl")
    
    # Append drift event to drift history file
    with open(drift_history_file, "a") as f:
        f.write(json.dumps(drift_event) + "\n")

def get_recent_drift_history(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent drift history entries.
    
    Args:
        limit: Maximum number of entries to return
        
    Returns:
        List of recent drift history entries
    """
    # Create logs directory if it doesn't exist
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    log_dir = os.path.join(base_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Path to drift history file
    drift_history_file = os.path.join(log_dir, "drift_history.jsonl")
    
    # Check if drift history file exists
    if not os.path.exists(drift_history_file):
        return []
    
    # Read drift history file
    entries = []
    with open(drift_history_file, "r") as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
    
    # Sort entries by timestamp (newest first)
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Return limited number of entries
    return entries[:limit]

def get_recent_health_scores(limit: int = 5, score_type: str = "surface") -> List[float]:
    """
    Get recent health scores.
    
    Args:
        limit: Maximum number of scores to return
        score_type: Type of health score to retrieve (surface, endpoint, payload)
        
    Returns:
        List of recent health scores
    """
    entries = get_recent_drift_history(limit)
    
    if score_type == "endpoint":
        return [entry.get("endpoint_health_score", 0) for entry in entries if "endpoint_health_score" in entry]
    elif score_type == "payload":
        return [entry.get("payload_health_score", 0) for entry in entries if "payload_health_score" in entry]
    else:  # Default to surface health score
        return [entry.get("surface_health_score", 0) for entry in entries]

def calculate_health_trend(scores: List[float]) -> Dict[str, Any]:
    """
    Calculate health trend from a list of health scores.
    
    Args:
        scores: List of health scores (newest first)
        
    Returns:
        Dictionary with trend direction and magnitude
    """
    if not scores or len(scores) < 2:
        return {
            "direction": "stable",
            "magnitude": 0,
            "description": "Insufficient data for trend analysis"
        }
    
    # Calculate trend
    newest = scores[0]
    oldest = scores[-1]
    diff = newest - oldest
    
    # Determine direction
    if abs(diff) < 0.5:  # Less than 0.5% change is considered stable
        direction = "stable"
    elif diff > 0:
        direction = "improving"
    else:
        direction = "degrading"
    
    # Determine magnitude (absolute percentage change)
    magnitude = abs(diff)
    
    # Create description
    if direction == "stable":
        description = f"System health is stable at {newest:.1f}%"
    elif direction == "improving":
        description = f"System health is improving by {magnitude:.1f}% (from {oldest:.1f}% to {newest:.1f}%)"
    else:
        description = f"System health is degrading by {magnitude:.1f}% (from {oldest:.1f}% to {newest:.1f}%)"
    
    return {
        "direction": direction,
        "magnitude": magnitude,
        "description": description
    }

def get_drift_type_summary(limit: int = 5) -> Dict[str, int]:
    """
    Get summary of recent drift types.
    
    Args:
        limit: Maximum number of entries to analyze
        
    Returns:
        Dictionary with drift type counts
    """
    entries = get_recent_drift_history(limit)
    
    # Collect all drift types
    drift_type_counts = {}
    for entry in entries:
        if "drift_type_counts" in entry:
            for drift_type, count in entry["drift_type_counts"].items():
                drift_type_counts[drift_type] = drift_type_counts.get(drift_type, 0) + count
    
    return drift_type_counts

def get_payload_health_trend(limit: int = 5) -> Dict[str, Any]:
    """
    Get payload health trend from recent drift history.
    
    Args:
        limit: Maximum number of entries to analyze
        
    Returns:
        Dictionary with trend information
    """
    # Get recent payload health scores
    scores = get_recent_health_scores(limit, score_type="payload")
    
    # Calculate trend
    trend = calculate_health_trend(scores)
    
    # Get drift type summary
    drift_types = get_drift_type_summary(limit)
    
    # Add drift types to trend
    trend["drift_types"] = drift_types
    
    # Add most common drift type
    if drift_types:
        most_common_drift_type = max(drift_types.items(), key=lambda x: x[1])
        trend["most_common_drift_type"] = most_common_drift_type[0]
        trend["most_common_drift_count"] = most_common_drift_type[1]
    
    return trend
