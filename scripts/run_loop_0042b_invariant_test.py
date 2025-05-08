#!/usr/bin/env python3
import sys
import os
import json
from datetime import datetime, timezone

# Add the project root to the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.controllers.loop_controller import LoopController
from app.utils.invariant_logger import InvariantLogger # To ensure log file path is known

INVARIANTS_FILE_PATH = os.path.join(PROJECT_ROOT, "app/memory/promethios_invariants.json")
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, "app/logs/invariant_violation_log.json")

def get_timestamp():
    return datetime.now(timezone.utc).isoformat()

def setup_test_invariants_for_0042b():
    """Ensures promethios_invariants.json has relevant invariants for the test, especially MIN_TRUST_SCORE_FOR_ACTION."""
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
            },
            {
                "invariant_id": "MIN_TRUST_SCORE_FOR_ACTION",
                "description": "Minimum agent trust score for critical actions.",
                "parameters": {"threshold_value": 0.75, "action_categories": ["critical_memory_modification", "system_config_update"], "trust_score_key": "agent_trust_score"},
                "enabled": True,
                "scope": ["loop_controller"]
            }
        ]
    }
    with open(INVARIANTS_FILE_PATH, "w") as f:
        json.dump(invariants_data, f, indent=2)
    print(f"Test invariants for loop_0042b set up at {INVARIANTS_FILE_PATH}")

def run_test_scenario_0042b():
    """
    Simulates a scenario for loop_0042b: triggering a MIN_TRUST_SCORE_FOR_ACTION violation.
    This will be logged by the LoopController.
    """
    print("\n--- Running Test Scenario loop_0042b: Minimum Trust Score Violation ---")

    # 1. Setup invariants for this test
    setup_test_invariants_for_0042b()

    # 2. Instantiate the LoopController
    loop_id_0042b = "loop_0042b_trust_score_test"
    controller = LoopController(loop_id=loop_id_0042b)
    print(f"LoopController instantiated for loop_id: {loop_id_0042b}")

    # 3. Define action details that should violate MIN_TRUST_SCORE_FOR_ACTION (threshold 0.75)
    action_violating_trust = {
        "action_type": "critical_memory_modification_A", # Matches a category in invariants
        "complexity_score": 50.0, # Low complexity, should not trigger complexity budget
        "details": "Attempting to modify a critical memory segment."
    }
    agent_context_low_trust = {
        "agent_id": "test_agent_low_trust",
        "agent_trust_score": 0.5, # Below threshold of 0.75
        "batch_id": "25.3",
        "current_loop_id": loop_id_0042b
    }

    print(f"Executing run_loop_phase with action designed to violate trust score invariant...")
    controller.run_loop_phase(
        phase_name="invariant_check_phase_C_trust_violating",
        action_details=action_violating_trust,
        agent_context=agent_context_low_trust
    )

    # 4. (Optional) Define another action that should NOT violate trust score
    action_passing_trust_critical = {
        "action_type": "critical_memory_modification_B",
        "complexity_score": 60.0,
        "details": "Modifying another critical segment with sufficient trust."
    }
    agent_context_high_trust = {
        "agent_id": "test_agent_high_trust",
        "agent_trust_score": 0.8, # Above threshold
        "batch_id": "25.3",
        "current_loop_id": loop_id_0042b
    }
    print(f"\nExecuting run_loop_phase with critical action and sufficient trust score...")
    controller.run_loop_phase(
        phase_name="invariant_check_phase_D_trust_passing_critical",
        action_details=action_passing_trust_critical,
        agent_context=agent_context_high_trust
    )
    
    action_passing_trust_non_critical = {
        "action_type": "non_critical_logging_task",
        "complexity_score": 10.0,
        "details": "Logging routine information."
    }
    # Using low trust context, but action is not in critical_categories
    print(f"\nExecuting run_loop_phase with non-critical action and low trust score (should pass)...")
    controller.run_loop_phase(
        phase_name="invariant_check_phase_E_trust_passing_non_critical",
        action_details=action_passing_trust_non_critical,
        agent_context=agent_context_low_trust 
    )

    print("\nTest Scenario loop_0042b finished.")
    print(f"Check \'{LOG_FILE_PATH}\' for a violation entry related to MIN_TRUST_SCORE_FOR_ACTION from component \'loop_controller.py\'.")

if __name__ == "__main__":
    run_test_scenario_0042b()

