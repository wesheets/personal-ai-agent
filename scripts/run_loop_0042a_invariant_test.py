#!/usr/bin/env python3
import sys, os, json
from datetime import datetime, timezone
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.controllers.loop_controller import LoopController
from app.utils.invariant_logger import InvariantLogger

def get_timestamp():
    return datetime.now(timezone.utc).isoformat()

def run_invariant_trigger_loop():
    print("[TEST] Running loop_0042a to trigger invariant...")
    # The user's patch instantiates LoopController without loop_id, 
    # but my LoopController implementation requires it.
    # I will use the loop_id from my previous test script for consistency.
    loop_id_0042a = "loop_0042a_complexity_test" 
    loop = LoopController(loop_id=loop_id_0042a)
    
    # The user's patch calls loop.run(loop_id="loop_0042a")
    # My LoopController has run_loop_phase(phase_name, action_details, agent_context)
    # I need to simulate a scenario that would trigger an invariant via LoopController.
    # Based on my LoopController and Invariant setup, I'll use a high complexity action.
    
    # Re-using the setup from my run_loop_0042a_invariant_test.py for a complexity violation
    action_violating_complexity = {
        "action_type": "heavy_computation_task_via_patch",
        "complexity_score": 150.5, # Exceeds threshold of 100.0
        "parameters": {"input_size": "large", "iterations": 1000}
    }
    agent_context_0042a = {
        "agent_id": "test_agent_complex_patch",
        "agent_trust_score": 0.9, 
        "batch_id": "25.3_recovery_patch",
        "current_loop_id": loop_id_0042a
    }
    
    # Ensure invariants are set up as expected by this test
    # (This part was in my original test script, adapting it here)
    INVARIANTS_FILE_PATH = os.path.join(PROJECT_ROOT, "app/memory/promethios_invariants.json")
    os.makedirs(os.path.dirname(INVARIANTS_FILE_PATH), exist_ok=True)
    invariants_data = {
        "schema_version": "1.0",
        "last_updated_utc": get_timestamp(),
        "invariants": [
            {
                "invariant_id": "MAX_COMPLEXITY_BUDGET",
                "description": "Maximum complexity allowed for an action or mutation.",
                "parameters": {"threshold_value": 100.0, "metric_source_key": "complexity_score"},
                "enabled": True,
                "scope": ["mutation_guard", "loop_controller"]
            }
        ]
    }
    with open(INVARIANTS_FILE_PATH, "w") as f:
        json.dump(invariants_data, f, indent=2)
    print(f"[TEST] Test invariants for patched loop_0042a set up at {INVARIANTS_FILE_PATH}")

    loop.run_loop_phase(
        phase_name="patched_invariant_check_A",
        action_details=action_violating_complexity,
        agent_context=agent_context_0042a
    )
    print("[TEST] loop_0042a execution finished.")

if __name__ == "__main__":
    run_invariant_trigger_loop()

