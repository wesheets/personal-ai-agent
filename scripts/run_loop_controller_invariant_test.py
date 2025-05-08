import json
import os
from datetime import datetime, timezone
import sys

# Add the 'app' directory to sys.path to allow imports like 'from utils.invariant_logger ...'
# Assumes this script is in personal-ai-agent/app/controllers/
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.append(APP_DIR)

# Import the new InvariantLogger class
from utils.invariant_logger import InvariantLogger

INVARIANTS_PATH = "/home/ubuntu/personal-ai-agent/app/memory/promethios_invariants.json"

def get_timestamp():
    return datetime.now(timezone.utc).isoformat()

class LoopController:
    def __init__(self, loop_id):
        self.loop_id = loop_id
        self.invariants = self._load_invariants()
        # Instantiate the InvariantLogger
        self.logger = InvariantLogger() # Uses default log path

    def _load_invariants(self):
        """Loads enabled invariants scoped to loop_controller from the JSON file."""
        try:
            if not os.path.exists(INVARIANTS_PATH):
                print(f"Warning: Invariants file not found at {INVARIANTS_PATH}. LoopController will operate without file-based invariants.")
                return []
            with open(INVARIANTS_PATH, "r") as f:
                data = json.load(f)
            
            applicable_invariants = []
            for invariant in data.get("invariants", []):
                if invariant.get("enabled") and "loop_controller" in invariant.get("scope", []):
                    applicable_invariants.append(invariant)
            # print(f"LoopController ({self.loop_id}): Loaded {len(applicable_invariants)} applicable invariants.") # Debug
            return applicable_invariants
        except Exception as e:
            print(f"Error loading or parsing invariants for LoopController ({self.loop_id}): {e}")
            return []

    def pre_action_invariant_check(self, action_details, agent_context):
        """
        Checks proposed action against applicable cognitive invariants before execution.
        Args:
            action_details (dict): Example: {"action_type": "critical_memory_modification", "complexity_score": 80.0, ...}
            agent_context (dict): Example: {"agent_id": "core_updater_agent", "agent_trust_score": 0.8, ...}
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
                current_complexity = action_details.get(metric_key)
                if current_complexity is not None and threshold is not None and float(current_complexity) > float(threshold):
                    violation_message = f"Potential violation of {invariant_id} in loop {self.loop_id}: Action complexity ({current_complexity}) exceeds threshold ({threshold})."
                    violation_detected_for_this_invariant = True
            
            elif invariant_id == "MIN_TRUST_SCORE_FOR_ACTION": 
                threshold = params.get("threshold_value")
                action_categories = params.get("action_categories", []) # Expected to be a list of strings
                trust_score_key = params.get("trust_score_key", "agent_trust_score")
                current_action_type = action_details.get("action_type") # Expected to be a string
                agent_trust_score = agent_context.get(trust_score_key)
                is_critical_action = False
                if isinstance(current_action_type, str) and isinstance(action_categories, list):
                    if any(cat.lower() in current_action_type.lower() for cat in action_categories):
                        is_critical_action = True
                
                if is_critical_action and agent_trust_score is not None and threshold is not None and float(agent_trust_score) < float(threshold):
                    violation_message = f"Potential violation of {invariant_id} in loop {self.loop_id}: Agent trust score ({agent_trust_score}) is below threshold ({threshold}) for action type ({current_action_type})."
                    violation_detected_for_this_invariant = True

            # Add other invariant checks here as elif blocks

            if violation_detected_for_this_invariant:
                violation_args_for_logger = {
                    "component": "loop_controller.py",
                    "invariant_id": invariant_id,
                    "details": violation_message,
                    "proposed_action": action_details, # Pass the full action_details
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

    def run_loop_phase(self, phase_name, action_details, agent_context):
        """Simulates running a phase of a loop, with pre-action checks."""
        print(f"\nLoop {self.loop_id} - Phase: {phase_name}")
        print(f"Action details: {action_details}")
        print(f"Agent context: {agent_context}")
        
        violations_args = self.pre_action_invariant_check(action_details, agent_context)
        if violations_args:
            print(f"Loop {self.loop_id} - {phase_name}: {len(violations_args)} invariant violations detected and logged.")
        else:
            print(f"Loop {self.loop_id} - {phase_name}: No invariant violations detected. Proceeding (simulated).")
        
        # Simulate action execution
        print(f"Loop {self.loop_id} - {phase_name}: Action execution completed (simulated).")
        return not violations_args # Return True if no violations (action succeeded), False otherwise

if __name__ == "__main__":
    print("Testing LoopController with actual InvariantLogger...")

    # Ensure invariants file exists for testing, creating a dummy one if necessary
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
                        "description": "Maximum complexity allowed for an action in the loop.",
                        "parameters": {"threshold_value": 100.0, "metric_source_key": "complexity_score"}, 
                        "enabled": True, 
                        "scope": ["mutation_guard", "loop_controller"]
                    },
                    {
                        "invariant_id": "MIN_TRUST_SCORE_FOR_ACTION", 
                        "description": "Minimum agent trust score required for certain categories of actions.",
                        "parameters": {"threshold_value": 0.75, "action_categories": ["critical_memory_modification", "system_configuration_change"], "trust_score_key": "agent_trust_score"}, 
                        "enabled": True, 
                        "scope": ["loop_controller"]
                    }
            ]}, f, indent=2)

    controller1 = LoopController(loop_id="lc_main_test_001")
    print(f"Loaded {len(controller1.invariants)} invariants scoped to LoopController ({controller1.loop_id}).")

    # Test case 1: Complexity violation
    action1 = {"action_type": "complex_data_processing", "complexity_score": 120.0, "source_data": "dataset_alpha"}
    context1 = {"agent_id": "data_processor_v1", "agent_trust_score": 0.9, "batch_id": "25.3_lc_main_test"}
    controller1.run_loop_phase("high_complexity_task", action1, context1)

    # Test case 2: Trust score violation for critical action category
    action2 = {"action_type": "critical_memory_modification_beta", "complexity_score": 30.0, "target_memory_address": "0xDEADBEEF"}
    context2 = {"agent_id": "memory_manager_v2", "agent_trust_score": 0.5, "batch_id": "25.3_lc_main_test"}
    controller1.run_loop_phase("low_trust_critical_op", action2, context2)

    # Test case 3: No violation
    action3 = {"action_type": "standard_logging_operation", "complexity_score": 10.0, "log_message": "Routine check complete."}
    context3 = {"agent_id": "system_monitor_agent", "agent_trust_score": 0.95, "batch_id": "25.3_lc_main_test"}
    controller1.run_loop_phase("routine_logging", action3, context3)

    # Test case 4: Critical action with sufficient trust score (no violation for trust, but check complexity)
    action4 = {"action_type": "system_configuration_change_gamma", "complexity_score": 90.0, "config_param": "timeout_ms", "new_value": 5000}
    context4 = {"agent_id": "config_admin_agent", "agent_trust_score": 0.8, "batch_id": "25.3_lc_main_test"}
    controller1.run_loop_phase("trusted_critical_config", action4, context4)
    
    # Test case 5: Critical action with sufficient trust score AND high complexity (should trigger complexity violation)
    action5 = {"action_type": "system_configuration_change_delta", "complexity_score": 150.0, "config_param": "max_connections", "new_value": 1000}
    context5 = {"agent_id": "config_admin_agent_pro", "agent_trust_score": 0.9, "batch_id": "25.3_lc_main_test"}
    controller1.run_loop_phase("trusted_high_complexity_config", action5, context5)

    print("\nLoopController testing complete. Check invariant_violation_log.json for logged entries.")

