"""
Drift Trend Logger Utility

This module provides utilities for logging drift trends over time.
It appends validation results to the drift history file in JSONL format.
"""

import os
import json
import datetime
from typing import Dict, Any, Optional


def log_drift_event(event_data: Dict[str, Any]) -> str:
    """
    Append a drift event to the drift history file.
    
    Args:
        event_data: Dictionary containing drift event data with the following keys:
            - surface_health_score: Float representing the overall health score
            - drift_issues_detected: Integer count of drift issues
            - validation_source: String indicating source ('startup' or 'post-merge')
            - validation_summary: String summary of the validation
            
    Returns:
        Path to the drift history file
    """
    # Ensure required fields are present
    required_fields = ['surface_health_score', 'drift_issues_detected', 
                      'validation_source', 'validation_summary']
    for field in required_fields:
        if field not in event_data:
            raise ValueError(f"Missing required field '{field}' in event data")
    
    # Add timestamp if not provided
    if 'timestamp' not in event_data:
        event_data['timestamp'] = datetime.datetime.now().isoformat()
    
    # Get base path and ensure logs directory exists
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    log_dir = os.path.join(base_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Path to drift history file
    history_file = os.path.join(log_dir, "drift_history.jsonl")
    
    # Append event to history file
    with open(history_file, 'a') as f:
        f.write(json.dumps(event_data) + '\n')
    
    return history_file


def get_recent_drift_history(limit: int = 10) -> list:
    """
    Get the most recent drift history entries.
    
    Args:
        limit: Maximum number of entries to return
        
    Returns:
        List of drift history entries, most recent first
    """
    # Get base path
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    history_file = os.path.join(base_path, "logs", "drift_history.jsonl")
    
    # Check if history file exists
    if not os.path.exists(history_file):
        return []
    
    # Read all entries
    entries = []
    with open(history_file, 'r') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    
    # Sort by timestamp (most recent first) and limit
    entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return entries[:limit]


def get_recent_health_scores(limit: int = 10) -> list:
    """
    Get the most recent health scores from the drift history.
    
    Args:
        limit: Maximum number of scores to return
        
    Returns:
        List of health scores, most recent first
    """
    entries = get_recent_drift_history(limit)
    return [entry.get('surface_health_score', 0) for entry in entries]


def calculate_health_trend(window: int = 5) -> Dict[str, Any]:
    """
    Calculate the trend in health scores over the specified window.
    
    Args:
        window: Number of entries to consider for trend calculation
        
    Returns:
        Dictionary with trend information:
            - current_score: Most recent health score
            - average_score: Average health score over the window
            - trend_direction: 'improving', 'declining', or 'stable'
            - trend_magnitude: Percentage change from first to last in window
    """
    scores = get_recent_health_scores(window)
    
    if not scores:
        return {
            'current_score': 0,
            'average_score': 0,
            'trend_direction': 'unknown',
            'trend_magnitude': 0
        }
    
    current_score = scores[0]
    average_score = sum(scores) / len(scores)
    
    if len(scores) < 2:
        trend_direction = 'stable'
        trend_magnitude = 0
    else:
        first_score = scores[-1]  # Oldest in the window
        if current_score > first_score:
            trend_direction = 'improving'
        elif current_score < first_score:
            trend_direction = 'declining'
        else:
            trend_direction = 'stable'
        
        # Calculate percentage change
        if first_score > 0:
            trend_magnitude = ((current_score - first_score) / first_score) * 100
        else:
            trend_magnitude = 0 if current_score == 0 else 100
    
    return {
        'current_score': current_score,
        'average_score': average_score,
        'trend_direction': trend_direction,
        'trend_magnitude': trend_magnitude
    }
