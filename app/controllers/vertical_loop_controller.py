#!/usr/bin/env python3
import json
import os
import uuid
from datetime import datetime, timezone

# Define paths relative to this script's assumed location in app/controllers/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) # This should point to app/
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
REFLECTION_THREAD_PATH = os.path.join(MEMORY_DIR, "reflection_thread.json")
LOOP_CONTEXT_PATH = os.path.join(MEMORY_DIR, "loop_context.json")
AGENT_EMOTION_STATE_PATH = os.path.join(MEMORY_DIR, "agent_emotion_state.json") # Added for Batch 35

def get_current_loop_context():
    """Gets current loop context from file."""
    if os.path.exists(LOOP_CONTEXT_PATH):
        try:
            with open(LOOP_CONTEXT_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading loop context: {e}")
            pass
    return {"current_loop_id": "unknown_loop", "current_step": "unknown_step", "batch_id": "unknown_batch"}

def get_active_emotion_state():
    """Loads the active emotion state from agent_emotion_state.json.
    CRITICAL FILE HANDLING: Loads the FULL prior version.
    Returns the latest entry or a default neutral state if not found/empty.
    """
    if not os.path.exists(AGENT_EMOTION_STATE_PATH):
        print(f"Warning: {AGENT_EMOTION_STATE_PATH} not found. Returning default emotion state.")
        return {"state": "NEUTRAL", "trust_score": 0.8, "timestamp": datetime.now(timezone.utc).isoformat(), "source": "default"}
    
    try:
        with open(AGENT_EMOTION_STATE_PATH, "r") as f_in:
            content = f_in.read()
            if not content.strip():
                print(f"Warning: {AGENT_EMOTION_STATE_PATH} is empty. Returning default emotion state.")
                return {"state": "NEUTRAL", "trust_score": 0.8, "timestamp": datetime.now(timezone.utc).isoformat(), "source": "default"}
            
            emotion_states = json.loads(content)
            if isinstance(emotion_states, list) and emotion_states:
                # Assuming the last entry is the most current one
                return emotion_states[-1] 
            else:
                print(f"Warning: {AGENT_EMOTION_STATE_PATH} did not contain a valid list of states or was empty. Returning default.")
                return {"state": "NEUTRAL", "trust_score": 0.8, "timestamp": datetime.now(timezone.utc).isoformat(), "source": "default"}
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {AGENT_EMOTION_STATE_PATH}. Returning default emotion state.")
        return {"state": "NEUTRAL", "trust_score": 0.8, "timestamp": datetime.now(timezone.utc).isoformat(), "source": "default"}
    except Exception as e:
        print(f"Error reading {AGENT_EMOTION_STATE_PATH}: {e}. Returning default emotion state.")
        return {"state": "NEUTRAL", "trust_score": 0.8, "timestamp": datetime.now(timezone.utc).isoformat(), "source": "default"}

# Note: The batch plan mentions "full load, merge, and save if updated" for agent_emotion_state.json.
# This function currently only READS. If the controller itself needs to UPDATE the emotion state,
# a separate function following the critical file handling for writing would be needed.

def add_reflection_entry(decision_point: str, justification: str, phase_summary: str = "N/A", context_shift: str = "N/A", outcome: str = "N/A", confidence_score: float = None, tags: list = None, emotional_context: dict = None):
    """
    Generates and appends a structured summary entry to reflection_thread.json.
    Includes emotional context if provided.
    """
    loop_context = get_current_loop_context()
    new_entry = {
        "reflection_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "batch_id": loop_context.get("batch_id", "unknown_batch"),
        "loop_id": loop_context.get("current_loop_id", "N/A"),
        "phase_summary": phase_summary,
        "decision_point": decision_point,
        "justification": justification,
        "context_shift": context_shift,
        "outcome": outcome,
        "confidence_score": confidence_score,
        "tags": tags if tags else [],
        "emotional_context_at_reflection": emotional_context if emotional_context else get_active_emotion_state() # Add current emotion if not passed
    }

    reflection_entries = []
    if os.path.exists(REFLECTION_THREAD_PATH):
        try:
            with open(REFLECTION_THREAD_PATH, "r") as f_in:
                content = f_in.read()
                if content.strip():
                    reflection_entries = json.loads(content)
                if not isinstance(reflection_entries, list):
                    reflection_entries = []
        except Exception as e:
            print(f"Error reading or parsing {REFLECTION_THREAD_PATH}, re-initializing: {e}")
            reflection_entries = []
    
    reflection_entries.append(new_entry)

    try:
        with open(REFLECTION_THREAD_PATH, "w") as f_out:
            json.dump(reflection_entries, f_out, indent=2)
        # print(f"Successfully appended reflection entry to {REFLECTION_THREAD_PATH}")
    except Exception as e:
        print(f"Error writing reflection entry to {REFLECTION_THREAD_PATH}: {e}")

# Placeholder for invoking an agent with emotional context
def invoke_agent(agent_name: str, task_details: dict, current_emotion: dict):
    print(f"Invoking {agent_name} for task: {task_details.get('description', 'N/A')}")
    print(f"Propagating emotional context to {agent_name}: {current_emotion}")
    # In a real scenario, this would call the agent's execution logic,
    # passing current_emotion as part of its input or context.
    # The agent (e.g., Orchestrator, Sage) would then use this.
    # For simulation, we just print.
    return {"status": "simulated_success", "output": f"{agent_name} processed task with emotion {current_emotion.get('state')}"}

def main_loop_iteration():
    print("Main loop iteration started.")
    current_emotion = get_active_emotion_state()
    print(f"Active emotion state for this iteration: {current_emotion}")

    # Example: Propagate emotion to an agent
    agent_output = invoke_agent(
        agent_name="OrchestratorAgent", 
        task_details={"description": "Plan next high-level steps"}, 
        current_emotion=current_emotion
    )
    print(f"OrchestratorAgent output: {agent_output}")

    add_reflection_entry(
        decision_point="Agent decided to use Tool X for Task Y",
        justification="Tool X is specialized for Task Y and has high trust score. User preference indicated speed.",
        phase_summary="Data Processing Phase",
        context_shift="Initial data analysis revealed unexpected patterns.",
        outcome="Task Y completed successfully with high accuracy.",
        confidence_score=0.95,
        tags=["tool_selection", "data_processing", "user_preference"],
        emotional_context=current_emotion # Log emotion with reflection
    )
    print("Main loop iteration finished.")

if __name__ == "__main__":
    print("Vertical Loop Controller - Batch 35 Simulation")
    
    # Ensure batch_id is set in loop_context for simulation
    loop_ctx = get_current_loop_context()
    loop_ctx["batch_id"] = "35.0"
    loop_ctx["current_loop_id"] = "sim_loop_35_0_1"
    try:
        with open(LOOP_CONTEXT_PATH, "w") as f_lc:
            json.dump(loop_ctx, f_lc, indent=2)
    except Exception as e:
        print(f"Could not write simulated loop context: {e}")

    # Simulate reading agent_emotion_state.json (it's read by get_active_emotion_state)
    # If agent_emotion_state.json doesn't exist or is invalid, a default will be used.
    # For this simulation, ensure it exists with some data if you want to test specific emotions.
    # Example: Create a dummy agent_emotion_state.json if it doesn't exist for testing
    if not os.path.exists(AGENT_EMOTION_STATE_PATH):
        print(f"Creating dummy {AGENT_EMOTION_STATE_PATH} for simulation.")
        dummy_emotions = [
            {"loop_id": "sim_loop_prev", "timestamp": datetime.now(timezone.utc).isoformat(), "state": "CALM", "trust_score": 0.85, "source": "simulation_setup"}
        ]
        try:
            with open(AGENT_EMOTION_STATE_PATH, "w") as f_aes:
                json.dump(dummy_emotions, f_aes, indent=2)
        except Exception as e:
            print(f"Could not write dummy emotion state: {e}")

    add_reflection_entry(
        decision_point="Batch 35.0 Initialization - Emotion Propagation", 
        justification="Controller enhanced to read and propagate active emotion state from agent_emotion_state.json.",
        phase_summary="Batch 35.0 - Component 35.0.1",
        tags=["initialization", "emotion_propagation", "controller_update"]
    )
    main_loop_iteration()
    print("Vertical Loop Controller simulation finished.")

