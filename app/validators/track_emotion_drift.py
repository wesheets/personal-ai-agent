#!/usr/bin/env python3

import json
import os
from datetime import datetime

# Define absolute file paths
BASE_DIR = "/home/ubuntu/personal-ai-agent"
AGENT_EMOTION_PROFILE_PATH = os.path.join(BASE_DIR, "app/memory/agent_emotion_profile.json")
EMOTION_DRIFT_TRACKER_PATH = os.path.join(BASE_DIR, "app/memory/emotion_drift_tracker.json")

def track_emotion_drift(agent_id: str, loop_id: str, outcome: str, regret_score: float, justification_ref: str):
    """Tracks emotion drift based on loop outcomes and updates the agent's emotion profile."""
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(AGENT_EMOTION_PROFILE_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(EMOTION_DRIFT_TRACKER_PATH), exist_ok=True)

    # Load agent emotion profile
    try:
        with open(AGENT_EMOTION_PROFILE_PATH, "r") as f:
            emotion_profile = json.load(f)
    except FileNotFoundError:
        emotion_profile = {}
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {AGENT_EMOTION_PROFILE_PATH}. Initializing as empty.")
        emotion_profile = {} 

    # Load emotion drift tracker
    try:
        with open(EMOTION_DRIFT_TRACKER_PATH, "r") as f:
            drift_tracker = json.load(f)
        if not isinstance(drift_tracker, list):
            print(f"Warning: {EMOTION_DRIFT_TRACKER_PATH} does not contain a list. Initializing as empty list.")
            drift_tracker = []
    except FileNotFoundError:
        drift_tracker = []
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {EMOTION_DRIFT_TRACKER_PATH}. Initializing as empty list.")
        drift_tracker = []

    # Update emotion profile based on outcome (simplified logic)
    if agent_id not in emotion_profile:
        emotion_profile[agent_id] = {"happiness": 0.5, "sadness": 0.5, "last_updated_utc": timestamp} 
    else:
        # Ensure basic structure exists if loading an old profile
        if "happiness" not in emotion_profile[agent_id]: emotion_profile[agent_id]["happiness"] = 0.5
        if "sadness" not in emotion_profile[agent_id]: emotion_profile[agent_id]["sadness"] = 0.5

    if outcome == "success":
        emotion_profile[agent_id]["happiness"] = min(1.0, emotion_profile[agent_id]["happiness"] + 0.1)
        emotion_profile[agent_id]["sadness"] = max(0.0, emotion_profile[agent_id]["sadness"] - 0.1)
    elif outcome == "failure":
        emotion_profile[agent_id]["happiness"] = max(0.0, emotion_profile[agent_id]["happiness"] - 0.1)
        emotion_profile[agent_id]["sadness"] = min(1.0, emotion_profile[agent_id]["sadness"] + 0.1)
    
    emotion_profile[agent_id]["last_updated_utc"] = timestamp

    # Log drift event
    drift_event = {
        "timestamp": timestamp,
        "agent_id": agent_id,
        "loop_id": loop_id,
        "outcome": outcome,
        "regret_score": regret_score,
        "justification_ref": justification_ref,
        "updated_emotion_profile_snapshot": emotion_profile[agent_id].copy() # Log a snapshot
    }
    drift_tracker.append(drift_event)

    # Save updated files
    try:
        with open(AGENT_EMOTION_PROFILE_PATH, "w") as f:
            json.dump(emotion_profile, f, indent=2)
    except IOError as e:
        print(f"Error writing to {AGENT_EMOTION_PROFILE_PATH}: {e}")

    try:
        with open(EMOTION_DRIFT_TRACKER_PATH, "w") as f:
            json.dump(drift_tracker, f, indent=2)
    except IOError as e:
        print(f"Error writing to {EMOTION_DRIFT_TRACKER_PATH}: {e}")

    # print(f"Emotion drift tracked for agent {agent_id} in loop {loop_id}.") # Reduced verbosity for library use

if __name__ == "__main__":
    print(f"Executing test run of track_emotion_drift.py...")
    # Example usage (for testing purposes)
    # Ensure the memory directory exists for the test
    os.makedirs(os.path.join(BASE_DIR, "app/memory"), exist_ok=True)
    
    # Clean up old test files if they exist to ensure a clean test
    if os.path.exists(AGENT_EMOTION_PROFILE_PATH):
        os.remove(AGENT_EMOTION_PROFILE_PATH)
    if os.path.exists(EMOTION_DRIFT_TRACKER_PATH):
        os.remove(EMOTION_DRIFT_TRACKER_PATH)

    track_emotion_drift(
        agent_id="test_agent_alpha", 
        loop_id="test_loop_001", 
        outcome="success", 
        regret_score=0.1,
        justification_ref="justification_for_001"
    )
    track_emotion_drift(
        agent_id="test_agent_alpha", 
        loop_id="test_loop_002", 
        outcome="failure", 
        regret_score=0.8,
        justification_ref="justification_for_002"
    )
    track_emotion_drift(
        agent_id="test_agent_beta", 
        loop_id="test_loop_003", 
        outcome="success", 
        regret_score=0.05,
        justification_ref="justification_for_003"
    )
    print(f"Test execution of track_emotion_drift complete. Check contents of:")
    print(f"  {AGENT_EMOTION_PROFILE_PATH}")
    print(f"  {EMOTION_DRIFT_TRACKER_PATH}")

