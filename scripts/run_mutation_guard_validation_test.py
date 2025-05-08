import json
import os
from datetime import datetime, timezone
import sys

# Add the 'app' directory to sys.path to allow imports like 'from utils.invariant_logger ...'
# Assumes this script is in personal-ai-agent/app/validators/
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.append(APP_DIR)

# Import the new InvariantLogger class
from utils.invariant_logger import InvariantLogger

INVARIANTS_PATH = "/home/ubuntu/personal-ai-agent/app/memory/promethios_invariants.json"

def get_timestamp():
    return datetime.now(timezone.utc).isoformat()

class MutationGuard:
    def __init__(self):
        self.invariants = self._load_invariants()
        # Instantiate the InvariantLogger
        self.logger = InvariantLogger() # Uses default log path

    def _load_invariants(self):
        """Loads enabled invariants scoped to mutation_guard from the JSON file."""
        try:
            if not os.path.exists(INVARIANTS_PATH):
                print(f"Warning: Invariants file not found at {INVARIANTS_PATH}. MutationGuard will operate without file-based invariants.")
                return []
            with open(INVARIANTS_PATH, 'r') as f:
                data = json.load(f)
            
            applicable_invariants = []
            for invariant in data.get("invariants", []):
                if invariant.get("enabled") and "mutation_guard" in invariant.get("scope", []):
                    applicable_invariants.append(invariant)
            # print(f"MutationGuard: Loaded {len(applicable_invariants)} applicable invariants.") # Debug
            return applicable_invariants
        except Exception as e:
            print(f"Error loading or parsing invariants in MutationGuard: {e}")
            return []

    def check_mutation(self, mutation_proposal, agent_context):
        """
        Checks a mutation proposal against applicable cognitive invariants.
        Args:
            mutation_proposal (dict): Example: {"mutation_type": "core_schema_modification", "complexity_score": 150.0, ...}
            agent_context (dict): Example: {"agent_id": "architect_v2", "agent_trust_score": 0.6, ...}
        Returns:
            list: A list of dictionaries, each representing the arguments passed to log_violation for a detected violation.
                  Empty if no violations.
        """
        detected_violations_args = []
        if not self.invariants:
            return detected_violations_args

        for invariant in self.invariants:
            invariant_id = invariant.get("invariant_id")
            params = invariant.get("parameters", {})
            violation_detected_for_this_invariant = False
            violation_message = ""

            if invariant_id == "MAX_COMPLEXITY_BUDGET":
                threshold = params.get("threshold_value")
                metric_key = params.get("metric_source_key", "complexity_score")
                current_complexity = mutation_proposal.get(metric_key)
                if current_complexity is not None and threshold is not None and float(current_complexity) > float(threshold):
                    violation_message = f"Potential violation of {invariant_id}: Complexity ({current_complexity}) exceeds threshold ({threshold})."
                    violation_detected_for_this_invariant = True

            elif invariant_id == "MIN_TRUST_SCORE_FOR_CRITICAL_MUTATION":
                threshold = params.get("threshold_value")
                mutation_type_key = params.get("mutation_type_key", "mutation_type")
                critical_types = params.get("critical_mutation_types", [])
                trust_score_key = params.get("trust_score_key", "agent_trust_score")
                
                current_mutation_type = mutation_proposal.get(mutation_type_key)
                agent_trust_score = agent_context.get(trust_score_key)

                if current_mutation_type in critical_types and agent_trust_score is not None and threshold is not None and float(agent_trust_score) < float(threshold):
                    violation_message = f"Potential violation of {invariant_id}: Agent trust score ({agent_trust_score}) is below threshold ({threshold}) for critical mutation type ({current_mutation_type})."
                    violation_detected_for_this_invariant = True
            
            # Add other invariant checks here as elif blocks

            if violation_detected_for_this_invariant:
                violation_args_for_logger = {
                    "component": "mutation_guard.py",
                    "invariant_id": invariant_id,
                    "details": violation_message,
                    "proposed_action": mutation_proposal, # Pass the full mutation proposal
                    "status": "logged_only" # As per Batch 25.3 design
                }
                self.logger.log_violation(
                    component=violation_args_for_logger["component"],
                    invariant_id=violation_args_for_logger["invariant_id"],
                    details=violation_args_for_logger["details"],
                    proposed_action=violation_args_for_logger["proposed_action"],
                    status=violation_args_for_logger["status"]
                )
                detected_violations_args.append(violation_args_for_logger)

        return detected_violations_args

if __name__ == "__main__":
    print("Testing MutationGuard with actual InvariantLogger...")

    # Ensure invariants file exists for testing, creating a dummy one if necessary
    # This is for standalone testing of this script.
    if not os.path.exists(INVARIANTS_PATH):
        os.makedirs(os.path.dirname(INVARIANTS_PATH), exist_ok=True)
        print(f"Creating dummy invariants file at {INVARIANTS_PATH} for testing.")
        with open(INVARIANTS_PATH, "w") as f:
            json.dump({
                "schema_version": "1.0",
                "last_updated_utc": get_timestamp(),
                "invariants": [
                    {
                        "invariant_id": "MAX_COMPLEXITY_BUDGET",
                        "description": "Complexity cap for mutations.",
                        "parameters": {"threshold_value": 100.0, "metric_source_key": "complexity_score"},
                        "enabled": True,
                        "scope": ["mutation_guard", "loop_controller"]
                    },
                    {
                        "invariant_id": "MIN_TRUST_SCORE_FOR_CRITICAL_MUTATION",
                        "description": "Minimum agent trust score required for critical mutations.",
                        "parameters": {"threshold_value": 0.75, "mutation_type_key": "mutation_type", "critical_mutation_types": ["core_schema_modification"], "trust_score_key": "agent_trust_score"},
                        "enabled": True,
                        "scope": ["mutation_guard"]
                    },
                    {
                        "invariant_id": "UNUSED_INVARIANT_FOR_TESTING",
                        "description": "This invariant is not checked by current logic but ensures loading works.",
                        "parameters": {},
                        "enabled": True,
                        "scope": ["mutation_guard"]
                    }
                ]
            }, f, indent=2)
    
    guard = MutationGuard()
    print(f"Loaded {len(guard.invariants)} invariants scoped to MutationGuard.")

    # Test case 1: Complexity violation
    proposal1 = {"mutation_type": "data_append", "complexity_score": 150.0, "data": "large_data_set"}
    context1 = {"agent_id": "data_ingestor_agent", "agent_trust_score": 0.9, "current_loop_id": "mg_test_loop_001", "batch_id": "25.3_mg_test"}
    print(f"\nChecking proposal1: {proposal1}")
    violations1 = guard.check_mutation(proposal1, context1)
    print(f"Test 1 Violations logged: {len(violations1)}")
    if violations1:
        print(f"Violation details (args passed to logger): {json.dumps(violations1, indent=2)}")

    # Test case 2: Trust score violation for critical mutation
    proposal2 = {"mutation_type": "core_schema_modification", "complexity_score": 50.0, "schema_change": "drop_column_x"}
    context2 = {"agent_id": "schema_manager_agent", "agent_trust_score": 0.6, "current_loop_id": "mg_test_loop_002", "batch_id": "25.3_mg_test"}
    print(f"\nChecking proposal2: {proposal2}")
    violations2 = guard.check_mutation(proposal2, context2)
    print(f"Test 2 Violations logged: {len(violations2)}")
    if violations2:
        print(f"Violation details (args passed to logger): {json.dumps(violations2, indent=2)}")

    # Test case 3: No violation
    proposal3 = {"mutation_type": "ui_text_update", "complexity_score": 10.0, "text_id": "welcome_message"}
    context3 = {"agent_id": "ux_agent", "agent_trust_score": 0.95, "current_loop_id": "mg_test_loop_003", "batch_id": "25.3_mg_test"}
    print(f"\nChecking proposal3: {proposal3}")
    violations3 = guard.check_mutation(proposal3, context3)
    print(f"Test 3 Violations logged: {len(violations3)}")
    if violations3:
        print(f"Violation details (args passed to logger): {json.dumps(violations3, indent=2)}")

    # Test case 4: Critical mutation with sufficient trust score (no violation)
    proposal4 = {"mutation_type": "core_schema_modification", "complexity_score": 90.0, "schema_change": "add_index_y"}
    context4 = {"agent_id": "db_admin_agent", "agent_trust_score": 0.8, "current_loop_id": "mg_test_loop_004", "batch_id": "25.3_mg_test"}
    print(f"\nChecking proposal4: {proposal4}")
    violations4 = guard.check_mutation(proposal4, context4)
    print(f"Test 4 Violations logged: {len(violations4)}")
    if violations4:
        print(f"Violation details (args passed to logger): {json.dumps(violations4, indent=2)}")

    print("\nMutationGuard testing complete. Check invariant_violation_log.json for logged entries.")

