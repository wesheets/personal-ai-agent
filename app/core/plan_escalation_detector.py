import json
import os
import uuid
from datetime import datetime, timezone

class PlanEscalationDetector:
    def __init__(self,
                 multi_plan_comparison_path="/home/ubuntu/personal-ai-agent/app/logs/multi_plan_comparison.json",
                 plan_rejection_log_path="/home/ubuntu/personal-ai-agent/app/logs/plan_rejection_log.json",
                 loop_plan_selection_log_path="/home/ubuntu/personal-ai-agent/app/logs/loop_plan_selection_log.json", # Added for context
                 plan_escalation_log_path="/home/ubuntu/personal-ai-agent/app/logs/plan_escalation_log.json",
                 fallback_config=None):
        self.multi_plan_comparison_path = multi_plan_comparison_path
        self.plan_rejection_log_path = plan_rejection_log_path
        self.loop_plan_selection_log_path = loop_plan_selection_log_path
        self.plan_escalation_log_path = plan_escalation_log_path
        self.fallback_config = fallback_config if fallback_config is not None else {"enabled": False, "default_fallback_strategy": "no_further_action_defined"}

    def _load_json_data(self, file_path, default_value=None):
        try:
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, "r") as f:
                    return json.load(f)
            return default_value if default_value is not None else []
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {file_path}: {e}. Returning default: {default_value}")
            return default_value if default_value is not None else []

    def _get_latest_comparison_set_id_for_loop(self, loop_id):
        selections = self._load_json_data(self.loop_plan_selection_log_path, default_value=[])
        loop_selections = [s for s in selections if s.get("loop_id") == loop_id]
        if not loop_selections:
            return None
        loop_selections.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return loop_selections[0].get("comparison_set_id")

    def _get_candidate_plans_for_loop(self, loop_id, comparison_set_id):
        comparisons = self._load_json_data(self.multi_plan_comparison_path, default_value=[])
        target_comparison_set = next((cs for cs in comparisons if cs.get("comparison_set_id") == comparison_set_id and cs.get("loop_id") == loop_id), None)
        if target_comparison_set:
            return [plan.get("plan_id") for plan in target_comparison_set.get("candidate_plans", []) if plan.get("plan_id")]
        return []

    def _get_rejected_plans_for_loop(self, loop_id, comparison_set_id):
        rejections = self._load_json_data(self.plan_rejection_log_path, default_value=[])
        # Filter rejections for the specific loop_id and comparison_set_id
        # Note: The plan_rejection_log.json from Batch 27.2 already includes comparison_set_id
        loop_specific_rejections = {r.get("plan_id") for r in rejections 
                                    if r.get("loop_id") == loop_id and 
                                       r.get("comparison_set_id") == comparison_set_id and 
                                       r.get("plan_id")}
        return loop_specific_rejections

    def _log_escalation(self, loop_id, comparison_set_id, candidate_plan_ids, rejected_plan_ids, recommended_action, operator_alert_flag, fallback_triggered=False, fallback_details=None):
        escalation_entry = {
            "log_entry_id": str(uuid.uuid4()),
            "loop_id": loop_id,
            "comparison_set_id": comparison_set_id,
            "escalation_reason": "All candidate plans rejected by governance thresholds.",
            "rejected_plan_ids": list(rejected_plan_ids), # Ensure it's a list
            "governance_summary": {
                "total_plans_considered": len(candidate_plan_ids),
                "total_plans_rejected": len(rejected_plan_ids)
            },
            "recommended_action": recommended_action,
            "operator_alert_flag": operator_alert_flag,
            "fallback_triggered": fallback_triggered,
            "fallback_details": fallback_details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        log_data = self._load_json_data(self.plan_escalation_log_path, default_value=[])
        log_data.append(escalation_entry)
        try:
            os.makedirs(os.path.dirname(self.plan_escalation_log_path), exist_ok=True)
            with open(self.plan_escalation_log_path, "w") as f:
                json.dump(log_data, f, indent=2)
            print(f"Escalation logged to {self.plan_escalation_log_path} for loop {loop_id}")
        except IOError as e:
            print(f"Error writing escalation log to {self.plan_escalation_log_path}: {e}")
        return escalation_entry

    def _trigger_fallback(self, loop_id, rejected_plan_ids):
        strategy = self.fallback_config.get("default_fallback_strategy", "no_further_action_defined")
        print(f"Fallback triggered for loop {loop_id}. Strategy: {strategy}")
        # Placeholder for actual fallback logic
        if strategy == "attempt_regeneration_simple":
            # Here, you would call a plan generator, e.g.:
            # plan_generator.regenerate_plans(loop_id, rejected_plan_ids, strategy_params={...})
            # For now, just log the attempt.
            return f"Attempted plan regeneration with strategy: {strategy}. (Actual regeneration not yet implemented)"
        elif strategy == "log_and_alert_operator":
            return "Fallback strategy: Logged and operator alert recommended."
        return "Fallback strategy: No specific action defined or executed."

    def check_for_escalation(self, loop_id):
        comparison_set_id = self._get_latest_comparison_set_id_for_loop(loop_id)
        if not comparison_set_id:
            print(f"No comparison set ID found for loop {loop_id} in {self.loop_plan_selection_log_path}. Cannot check for escalation.")
            return None

        candidate_plan_ids = self._get_candidate_plans_for_loop(loop_id, comparison_set_id)
        if not candidate_plan_ids:
            print(f"No candidate plans found for loop {loop_id}, comparison set {comparison_set_id} in {self.multi_plan_comparison_path}. Cannot determine escalation.")
            return None

        rejected_plan_ids_set = self._get_rejected_plans_for_loop(loop_id, comparison_set_id)

        # Check if all candidate plans are in the set of rejected plans
        all_rejected = True
        for cp_id in candidate_plan_ids:
            if cp_id not in rejected_plan_ids_set:
                all_rejected = False
                break
        
        if all_rejected:
            print(f"Escalation condition met for loop {loop_id}: All {len(candidate_plan_ids)} candidate plans were rejected.")
            recommended_action = "operator_review_required"
            operator_alert_flag = True
            fallback_triggered = False
            fallback_details = None

            if self.fallback_config.get("enabled", False):
                fallback_details = self._trigger_fallback(loop_id, list(rejected_plan_ids_set))
                fallback_triggered = True
                # Adjust recommended action based on fallback strategy outcome if needed
                if self.fallback_config.get("default_fallback_strategy") == "attempt_regeneration_simple":
                    recommended_action = "trigger_fallback_procedure"
                    operator_alert_flag = False # Assuming fallback might resolve it
                elif self.fallback_config.get("default_fallback_strategy") == "log_and_alert_operator":
                    recommended_action = "operator_review_required"
                    operator_alert_flag = True
            else:
                recommended_action = "operator_review_required" # Default if fallback is not enabled
                operator_alert_flag = True

            return self._log_escalation(loop_id, comparison_set_id, candidate_plan_ids, list(rejected_plan_ids_set), recommended_action, operator_alert_flag, fallback_triggered, fallback_details)
        else:
            print(f"No escalation needed for loop {loop_id}. Not all candidate plans were rejected.")
            return None

if __name__ == "__main__":
    # Example Usage (requires dummy log files to be set up as per tests)
    print("Running PlanEscalationDetector example...")
    # Ensure dummy log directories exist
    os.makedirs("/home/ubuntu/personal-ai-agent/app/logs", exist_ok=True)

    # Create dummy multi_plan_comparison.json
    dummy_multi_plan = [
        {
            "comparison_set_id": "cs_loop0052_1", "loop_id": "loop_0052",
            "candidate_plans": [{"plan_id": "planA"}, {"plan_id": "planB"}]
        }
    ]
    with open("/home/ubuntu/personal-ai-agent/app/logs/multi_plan_comparison.json", "w") as f:
        json.dump(dummy_multi_plan, f)

    # Create dummy plan_rejection_log.json (all plans rejected for loop_0052, cs_loop0052_1)
    dummy_rejections = [
        {"loop_id": "loop_0052", "comparison_set_id": "cs_loop0052_1", "plan_id": "planA", "rejection_reason": "Trust too low"},
        {"loop_id": "loop_0052", "comparison_set_id": "cs_loop0052_1", "plan_id": "planB", "rejection_reason": "Emotion too negative"}
    ]
    with open("/home/ubuntu/personal-ai-agent/app/logs/plan_rejection_log.json", "w") as f:
        json.dump(dummy_rejections, f)
    
    # Create dummy loop_plan_selection_log.json
    dummy_loop_selections = [
        {"loop_id": "loop_0052", "comparison_set_id": "cs_loop0052_1", "selected_plan_id": "planA", "timestamp": datetime.now(timezone.utc).isoformat()}
    ]
    with open("/home/ubuntu/personal-ai-agent/app/logs/loop_plan_selection_log.json", "w") as f:
        json.dump(dummy_loop_selections, f)

    detector_no_fallback = PlanEscalationDetector(fallback_config={"enabled": False})
    print("\n--- Checking loop_0052 (no fallback) ---")
    detector_no_fallback.check_for_escalation("loop_0052")

    detector_with_fallback = PlanEscalationDetector(fallback_config={"enabled": True, "default_fallback_strategy": "attempt_regeneration_simple"})
    print("\n--- Checking loop_0052 (with fallback) ---")
    detector_with_fallback.check_for_escalation("loop_0052")
    
    # Clean up dummy escalation log if created
    if os.path.exists("/home/ubuntu/personal-ai-agent/app/logs/plan_escalation_log.json"):
        os.remove("/home/ubuntu/personal-ai-agent/app/logs/plan_escalation_log.json")

    print("\nPlanEscalationDetector example finished.")

