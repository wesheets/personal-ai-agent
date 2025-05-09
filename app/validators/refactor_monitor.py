#!/usr/bin/env python3

import json
import os
import uuid
from datetime import datetime

# Define paths relative to PROJECT_ROOT
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REFACTOR_SUGGESTION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/refactor_suggestion_log.json")

def load_json_file(path, default_value=None):
    if default_value is None:
        default_value = []
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, 'r') as f:
                return json.load(f)
        return default_value
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value

def save_json_file(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def generate_refactor_suggestion(trigger_reason: str, loop_id: str, component: str, recommended_action: str, confidence_score: float):
    """
    Generates a refactor suggestion and logs it.
    
    Args:
        trigger_reason: The reason for the suggestion (e.g., high emotional volatility, high regret).
        loop_id: The ID of the loop where the trigger occurred.
        component: The component or module that should be refactored.
        recommended_action: The suggested action to take.
        confidence_score: A score indicating the confidence in this suggestion.
    """
    suggestion = {
        "suggestion_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "trigger_reason": trigger_reason,
        "loop_id": loop_id,
        "component": component,
        "recommended_action": recommended_action,
        "confidence_score": confidence_score
    }
    
    suggestions = load_json_file(REFACTOR_SUGGESTION_LOG_PATH)
    suggestions.append(suggestion)
    save_json_file(suggestions, REFACTOR_SUGGESTION_LOG_PATH)
    print(f"Refactor suggestion logged: {suggestion['suggestion_id']}")

# Example usage (can be called from loop_controller.py or other relevant modules)
if __name__ == "__main__":
    # Simulate some conditions that trigger a refactor suggestion
    generate_refactor_suggestion(
        trigger_reason="High Emotional Volatility",
        loop_id="loop_123",
        component="EmotionProcessingModule",
        recommended_action="Review and simplify emotion update logic.",
        confidence_score=0.85
    )
    
    generate_refactor_suggestion(
        trigger_reason="High Regret Score",
        loop_id="loop_456",
        component="DecisionMakingUnit",
        recommended_action="Re-evaluate decision thresholds and parameters.",
        confidence_score=0.92
    )

