#!/usr/bin/env python3

import os
import json
import sys

# Add the project root to the Python path to allow importing app.core modules
PROJECT_ROOT = "/home/ubuntu/personal-ai-agent"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.core.governance_reconciler import GovernanceReconciler

TEST_DATA_DIR = os.path.join(PROJECT_ROOT, "app/test_data/batch_28_1")
LOGS_DIR = os.path.join(PROJECT_ROOT, "app/logs")
MEMORY_DIR = os.path.join(PROJECT_ROOT, "app/memory") # For current state files if reconciler uses them

def main():
    print("Starting Batch 28.1 Governance Reconciliation Test Script...")

    # Ensure mock data files are where the reconciler expects them (or configure reconciler to use test paths)
    # The reconciler is currently hardcoded to look in app/logs and app/memory relative to project_base_path.
    # For this test, we will copy our mock files to those locations temporarily, or adjust config.
    # For a cleaner test, the reconciler should accept full paths for its input files via config.
    # Let's adjust the config for the test to point to our mock data directly.

    test_config = {
        "output_log_path": os.path.join(LOGS_DIR, "governance_value_alignment_log.json"), # Output will be in actual logs dir
        "loops_to_reconcile": ["loop_0041a", "loop_0041b", "loop_0051", "loop_0052", "loop_missing_data"], # Test a missing data case too
        "project_base_path": PROJECT_ROOT, # This is used by reconciler to construct default paths
        
        # Override default paths to point to our mock data for this test run
        "multi_plan_comparison_log_path": os.path.join(TEST_DATA_DIR, "mock_multi_plan_comparison.json"),
        "loop_selection_log_path": os.path.join(TEST_DATA_DIR, "mock_loop_plan_selection_log.json"),
        "plan_rejection_log_path": os.path.join(TEST_DATA_DIR, "mock_plan_rejection_log.json"),
        "plan_escalation_log_path": os.path.join(TEST_DATA_DIR, "mock_plan_escalation_log.json"),
        
        "emotion_profile_path": os.path.join(TEST_DATA_DIR, "mock_agent_emotion_profile.json"),
        # For current_emotion_state, the reconciler will try its default path in memory_dir.
        # We can place a mock current state there, or let it use the profile as fallback.
        "current_emotion_state_path": os.path.join(TEST_DATA_DIR, "mock_agent_emotion_state_current.json"), # Point to a mock current state
        "invariants_path": os.path.join(TEST_DATA_DIR, "mock_promethios_invariants.json"),
        "belief_index_path": os.path.join(TEST_DATA_DIR, "mock_belief_weight_index.json") # Assuming we might create this
    }

    # Create a dummy belief_index.json for completeness if it doesn't exist
    dummy_belief_path = os.path.join(TEST_DATA_DIR, "mock_belief_weight_index.json")
    if not os.path.exists(dummy_belief_path):
        with open(dummy_belief_path, "w") as f:
            json.dump({"info": "Mock belief index for testing.", "beliefs": []}, f)
            print(f"Created dummy mock_belief_weight_index.json at {dummy_belief_path}")

    # The reconciler itself creates the output log directory if it doesn't exist.

    print(f"Initializing GovernanceReconciler with test config:")
    for key, value in test_config.items():
        if "path" in key.lower(): # Only print path related configs for brevity
             print(f"  {key}: {value}")

    reconciler = GovernanceReconciler(test_config)
    reconciler.run_reconciliation()

    print("--- Test Script Finished ---")
    print(f"Output log should be at: {test_config['output_log_path']}")
    print("Please verify the content of the log for correctness and schema conformance.")

if __name__ == "__main__":
    main()

