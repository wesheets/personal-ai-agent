import sys
import json
import os
from datetime import datetime, timezone

# Adjust path to import SageAgent
# Assuming sage_agent.py is in /home/ubuntu/personal-ai-agent/app/agents/
sys.path.append("/home/ubuntu/personal-ai-agent/app/agents")

# Define memory directory for reflection_thread.json, relative to where sage_agent.py expects it
# sage_agent.py uses BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) which is app/
# So MEMORY_DIR becomes app/memory/
APP_DIR_FOR_TEST = "/home/ubuntu/personal-ai-agent/app"
MEMORY_DIR_FOR_TEST = os.path.join(APP_DIR_FOR_TEST, "memory")
REFLECTION_THREAD_PATH_FOR_TEST = os.path.join(MEMORY_DIR_FOR_TEST, "reflection_thread.json")

# Ensure memory directory exists for the test if SageAgent tries to write reflection_thread.json
os.makedirs(MEMORY_DIR_FOR_TEST, exist_ok=True)

# Create an empty reflection_thread.json if it doesn't exist, so SageAgent can append to it
# SageAgent itself should handle loading/creating this file, but good to ensure dir exists.
# The user's spec for generate_explanation mentioned logging to reflection_thread.json
# This implies SageAgent was modified to do so.
if not os.path.exists(REFLECTION_THREAD_PATH_FOR_TEST):
    with open(REFLECTION_THREAD_PATH_FOR_TEST, "w") as f:
        json.dump([], f) # Assuming it's a list of reflections

try:
    from sage_agent import SageAgent
except ImportError as e:
    print(f"Error: Could not import SageAgent: {e}")
    print(f"Sys.path: {sys.path}")
    print(f"Attempted import from /home/ubuntu/personal-ai-agent/app/agents/sage_agent.py")
    sys.exit(1)

# Placeholder for helper functions if they are not part of SageAgent class
# These were in the user's spec for generate_explanation
def extract_agents(loop_trace):
    if not loop_trace or not isinstance(loop_trace.get("steps"), list):
        return ["Data unavailable"]
    agents = set()
    for step in loop_trace["steps"]:
        if isinstance(step, dict) and "agent" in step:
            agents.add(step["agent"])
    return list(agents) if agents else ["No agents recorded"]

def extract_major_decisions(justification_log):
    if not justification_log or not isinstance(justification_log, list):
        return ["Data unavailable"]
    decisions = []
    for entry in justification_log:
        if isinstance(entry, dict) and "decision_or_action" in entry:
            decisions.append(entry["decision_or_action"])
    return decisions if decisions else ["No major decisions recorded"]


def main():
    print("Starting SageAgent explanation test...")

    sample_loop_trace = {
        "loop_id": "test_loop_for_explanation_123",
        "goal": "test the explanation feature via existing run method",
        "steps": [
            {"agent": "Orchestrator", "action": "Plan generation for explanation"},
            {"agent": "SageAgent", "action": "Wisdom provided (explanation task)"},
            {"agent": "Critic", "action": "Reviewed explanation output"}
        ],
        "final_result": "Explanation test completed (mock)."
    }
    sample_justification_log = [
        {"log_id": "j1", "agent_name": "Orchestrator", "decision_or_action": "Generated plan for explanation task", "justification_narrative": "Plan to call Sage for explanation.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"log_id": "j2", "agent_name": "SageAgent", "decision_or_action": "Synthesized explanation for loop test_loop_for_explanation_123", "justification_narrative": "Processed loop trace and justifications.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"log_id": "j3", "agent_name": "Critic", "decision_or_action": "Approved explanation quality", "justification_narrative": "Explanation meets clarity standards.", "timestamp": datetime.now(timezone.utc).isoformat()}
    ]
    # This is the emotional state OF THE LOOP BEING EXPLAINED
    sample_loop_emotional_state = {
        "emotion": "reflective",
        "confidence": 0.88,
        "source": "internal_during_loop_test_loop_for_explanation_123"
    }

    sage = SageAgent() # Uses default name "SageAgent"

    # Construct query and augmented context for provide_wisdom, assuming it's the adapted entry point
    query_for_explanation = f"explain_loop_execution:{sample_loop_trace['loop_id']}"
    
    # This is Sage's own emotional context while performing the explanation task
    sage_current_emotional_context = {
        "state": "FOCUSED", 
        "trust_score": 0.95,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": { 
            "task_type": "generate_explanation",
            "loop_trace_input": sample_loop_trace,
            "justification_log_input": sample_justification_log,
            "loop_emotion_state_input": sample_loop_emotional_state
        }
    }
    
    print(f"Calling SageAgent.provide_wisdom for explanation of loop_id: {sample_loop_trace['loop_id']}")
    
    # It's assumed that in step 006, sage_agent.py was modified so that provide_wisdom
    # can parse these inputs from metadata and call an internal logic similar to
    # the user-specified generate_explanation(loop_trace, justification_log, emotion_state)
    # And that it was also modified to log to reflection_thread.json
    result = sage.provide_wisdom(query_for_explanation, sage_current_emotional_context)
    
    print("\n--- Explanation Result from SageAgent (expected in 'wisdom' field) ---")
    if result and result.get("status") == "success" and "wisdom" in result:
        explanation_content = result["wisdom"]
        # The user's spec for generate_explanation returned a dict. We expect that here.
        if isinstance(explanation_content, str):
            try:
                explanation_content = json.loads(explanation_content)
            except json.JSONDecodeError:
                print(f"Wisdom content is a string but not valid JSON: {explanation_content}")
        
        if isinstance(explanation_content, dict):
            print(json.dumps(explanation_content, indent=2))
            # Validate structure based on user's spec for generate_explanation
            expected_keys = ["summary", "key_agents", "decisions", "outcome"]
            actual_keys = explanation_content.keys()
            if all(key in actual_keys for key in expected_keys):
                print("\nValidation: Explanation structure (summary, key_agents, decisions, outcome) is correct.")
            else:
                print("\nValidation: Explanation structure is NOT as expected.")
                print(f"Expected keys: {expected_keys}, Got: {list(actual_keys)}")
        else:
            print(f"Validation: Explanation content is not a dictionary as expected. Got type: {type(explanation_content)}")
            print(f"Content: {explanation_content}")

    else:
        print("Error: SageAgent did not return a successful explanation in the expected format.")
        print(f"Full result: {result}")

    print(f"\n--- Checking reflection_thread.json (path: {REFLECTION_THREAD_PATH_FOR_TEST}) ---   ")
    if os.path.exists(REFLECTION_THREAD_PATH_FOR_TEST):
        with open(REFLECTION_THREAD_PATH_FOR_TEST, "r") as f:
            reflections = json.load(f)
        
        found_reflection = False
        if isinstance(reflections, list):
            for reflection_entry in reversed(reflections):
                if isinstance(reflection_entry, dict) and reflection_entry.get("loop_id") == sample_loop_trace["loop_id"]:
                    # Check for presence of explanation-like content
                    if "explanation" in reflection_entry or "explanation_summary" in reflection_entry or \
                       (isinstance(reflection_entry.get("content"), dict) and "summary" in reflection_entry["content"]):
                        print(f"Found reflection entry for loop_id {sample_loop_trace['loop_id']}:")
                        print(json.dumps(reflection_entry, indent=2))
                        found_reflection = True
                        break
        if not found_reflection:
            print(f"No specific explanation reflection found for loop_id {sample_loop_trace['loop_id']} in {REFLECTION_THREAD_PATH_FOR_TEST}.")
        else:
            print("Validation: Explanation appears to be logged to reflection_thread.json.")
    else:
        print(f"Error: {REFLECTION_THREAD_PATH_FOR_TEST} not found, cannot verify reflection logging.")

    print("\nSageAgent explanation test finished.")

if __name__ == "__main__":
    main()

