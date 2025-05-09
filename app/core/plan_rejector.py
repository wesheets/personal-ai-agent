import json
import os
import uuid
from datetime import datetime, timezone

class PlanRejector:
    def __init__(self, 
                 plan_selection_log_path="/home/ubuntu/personal-ai-agent/app/logs/loop_plan_selection_log.json",
                 rejection_log_path="/home/ubuntu/personal-ai-agent/app/logs/plan_rejection_log.json",
                 emotion_state_path="/home/ubuntu/personal-ai-agent/app/memory/agent_emotion_state.json",
                 trust_score_path="/home/ubuntu/personal-ai-agent/app/memory/agent_trust_score.json", # Hypothetical
                 invariants_path="/home/ubuntu/personal-ai-agent/app/memory/promethios_invariants.json" # Hypothetical
                 ):
        self.plan_selection_log_path = plan_selection_log_path
        self.rejection_log_path = rejection_log_path
        self.emotion_state_path = emotion_state_path
        self.trust_score_path = trust_score_path
        self.invariants_path = invariants_path
        self.thresholds = self._load_thresholds()

    def _load_thresholds(self):
        return {
            "emotion": {
                "max_negative_valence": -0.7,
                "min_positive_valence": 0.2, 
                "max_arousal_if_negative": 0.8 
            },
            "trust": {
                "min_score": 0.5
            },
            "invariants": {
                "allow_critical_violations": False,
                "max_non_critical_violations": 0 # Stricter: allow 0 non-critical for now
            }
        }

    def _load_json_data(self, file_path, default_value=None):
        try:
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, "r") as f:
                    return json.load(f)
            return default_value if default_value is not None else [] # Default to list for logs
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {file_path}: {e}. Returning default: {default_value}")
            return default_value if default_value is not None else []

    def _get_selected_plan_for_loop(self, loop_id):
        selections = self._load_json_data(self.plan_selection_log_path, default_value=[])
        loop_selections = [s for s in selections if s.get("loop_id") == loop_id]
        if not loop_selections:
            return None, None
        loop_selections.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        latest_selection = loop_selections[0]
        return latest_selection.get("selected_plan_id"), latest_selection.get("comparison_set_id")

    def _get_current_governance_metrics(self, loop_id, plan_id):
        # Mock data for testing, will be replaced or augmented by actual data sources
        mock_emotion = {"valence": 0.5, "arousal": 0.3}
        if loop_id == "loop_0051_emotion_fail": mock_emotion = {"valence": -0.8, "arousal": 0.5}
        elif loop_id == "loop_0051_emotion_arousal_fail": mock_emotion = {"valence": -0.5, "arousal": 0.9}

        mock_trust = {"score": 0.8}
        if loop_id == "loop_0052_trust_fail": mock_trust = {"score": 0.4}

        mock_invariants = {"status": "pass", "violated_critical_invariants": [], "violated_non_critical_invariants": []}
        if loop_id == "loop_0051_invariant_crit_fail": 
            mock_invariants = {"status": "fail", "violated_critical_invariants": ["inv_critical_001"], "violated_non_critical_invariants": []}
        elif loop_id == "loop_0052_invariant_noncrit_fail":
             mock_invariants = {"status": "fail", "violated_critical_invariants": [], "violated_non_critical_invariants": ["inv_noncrit_001", "inv_noncrit_002"]}

        emotion_data = self._load_json_data(self.emotion_state_path, default_value={})
        current_emotion = emotion_data.get(loop_id, emotion_data.get("default", mock_emotion))

        trust_data = self._load_json_data(self.trust_score_path, default_value={})
        current_trust = trust_data.get(loop_id, trust_data.get("default", mock_trust))
        
        current_invariants = mock_invariants # Simplified for now

        return {
            "emotion": current_emotion,
            "trust": current_trust,
            "invariants": current_invariants
        }

# Part 1 End. evaluate_plan, _log_rejection, process_rejection_for_loop and main to follow.



    def evaluate_plan(self, loop_id, plan_id, comparison_set_id):
        metrics = self._get_current_governance_metrics(loop_id, plan_id)
        rejections = []

        # Emotion Check
        emotion_val = metrics["emotion"].get("valence", 0)
        emotion_aro = metrics["emotion"].get("arousal", 0)
        if emotion_val < self.thresholds["emotion"]["max_negative_valence"]:
            rejections.append({
                "reason": f"Emotional negative valence ({emotion_val}) below threshold ({self.thresholds['emotion']['max_negative_valence']}).",
                "metric": "emotion.negative_valence",
                "value": emotion_val,
                "threshold": self.thresholds["emotion"]["max_negative_valence"],
                "condition": "less_than"
            })
        if emotion_val > 0 and emotion_val < self.thresholds["emotion"]["min_positive_valence"]:
             rejections.append({
                "reason": f"Emotional positive valence ({emotion_val}) below threshold ({self.thresholds['emotion']['min_positive_valence']}).",
                "metric": "emotion.positive_valence",
                "value": emotion_val,
                "threshold": self.thresholds["emotion"]["min_positive_valence"],
                "condition": "less_than_positive_min"
            })
        if emotion_val < 0 and emotion_aro > self.thresholds["emotion"]["max_arousal_if_negative"]:
            rejections.append({
                "reason": f"High arousal ({emotion_aro}) during negative valence ({emotion_val}) exceeds threshold ({self.thresholds['emotion']['max_arousal_if_negative']}).",
                "metric": "emotion.arousal_when_negative",
                "value": emotion_aro,
                "threshold": self.thresholds["emotion"]["max_arousal_if_negative"],
                "condition": "greater_than_if_negative_valence"
            })

        # Trust Check
        trust_score = metrics["trust"].get("score", 1.0)
        if trust_score < self.thresholds["trust"]["min_score"]:
            rejections.append({
                "reason": f"Trust score ({trust_score}) below minimum threshold ({self.thresholds['trust']['min_score']}).",
                "metric": "trust.score",
                "value": trust_score,
                "threshold": self.thresholds["trust"]["min_score"],
                "condition": "less_than"
            })

        # Invariants Check
        critical_violations = metrics["invariants"].get("violated_critical_invariants", [])
        non_critical_violations = metrics["invariants"].get("violated_non_critical_invariants", [])
        if not self.thresholds["invariants"]["allow_critical_violations"] and critical_violations:
            rejections.append({
                "reason": f"Critical invariant violations are not allowed. Found: {critical_violations}.",
                "metric": "invariants.critical_violations",
                "value": len(critical_violations),
                "threshold": 0,
                "condition": "greater_than"
            })
        if len(non_critical_violations) > self.thresholds["invariants"]["max_non_critical_violations"]:
            rejections.append({
                "reason": f"Number of non-critical invariant violations ({len(non_critical_violations)}) exceeds threshold ({self.thresholds['invariants']['max_non_critical_violations']}). Violations: {non_critical_violations}",
                "metric": "invariants.non_critical_violations",
                "value": len(non_critical_violations),
                "threshold": self.thresholds["invariants"]["max_non_critical_violations"],
                "condition": "greater_than"
            })

        if rejections:
            first_rejection = rejections[0]
            rejection_details = {
                "log_entry_id": str(uuid.uuid4()),
                "loop_id": loop_id,
                "plan_id": plan_id,
                "comparison_set_id": comparison_set_id,
                "rejection_reason": first_rejection["reason"],
                "triggering_metric": first_rejection["metric"],
                "threshold_details": {
                    "metric_path": first_rejection["metric"],
                    "threshold_value": first_rejection["threshold"],
                    "actual_value": first_rejection["value"],
                    "condition": first_rejection["condition"]
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "governance_context": metrics,
                "all_rejection_triggers": rejections
            }
            return True, rejection_details
        return False, None

    def _log_rejection(self, rejection_details):
        log_data = self._load_json_data(self.rejection_log_path, default_value=[])
        log_data.append(rejection_details)
        try:
            os.makedirs(os.path.dirname(self.rejection_log_path), exist_ok=True)
            with open(self.rejection_log_path, "w") as f:
                json.dump(log_data, f, indent=2)
            print(f"Plan rejection logged to {self.rejection_log_path}")
        except IOError as e:
            print(f"Error writing rejection log to {self.rejection_log_path}: {e}")

    def process_rejection_for_loop(self, loop_id):
        selected_plan_id, comparison_set_id = self._get_selected_plan_for_loop(loop_id)
        if not selected_plan_id:
            print(f"No selected plan found for loop_id: {loop_id} in {self.plan_selection_log_path}")
            return None

        print(f"Evaluating plan {selected_plan_id} for loop {loop_id} (from comparison set {comparison_set_id})...")
        is_rejected, rejection_details = self.evaluate_plan(loop_id, selected_plan_id, comparison_set_id)

        if is_rejected:
            print(f"Plan {selected_plan_id} for loop {loop_id} is REJECTED.")
            self._log_rejection(rejection_details)
            return rejection_details
        else:
            print(f"Plan {selected_plan_id} for loop {loop_id} meets all thresholds and is APPROVED.")
            return None

if __name__ == "__main__":
    print("Running PlanRejector example...")
    rejector = PlanRejector()

    dummy_plan_selections = [
        {
            "log_id": "sel_001", "loop_id": "loop_0051_emotion_fail", "selected_plan_id": "plan_E_fail", 
            "comparison_set_id": "cs_test_E", "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "log_id": "sel_002", "loop_id": "loop_0052_trust_fail", "selected_plan_id": "plan_T_fail", 
            "comparison_set_id": "cs_test_T", "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "log_id": "sel_003", "loop_id": "loop_0051_invariant_crit_fail", "selected_plan_id": "plan_I_crit_fail", 
            "comparison_set_id": "cs_test_I_crit", "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "log_id": "sel_004", "loop_id": "loop_0052_invariant_noncrit_fail", "selected_plan_id": "plan_I_noncrit_fail", 
            "comparison_set_id": "cs_test_I_noncrit", "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "log_id": "sel_005", "loop_id": "loop_0050_pass", "selected_plan_id": "plan_P_pass", 
            "comparison_set_id": "cs_test_P", "timestamp": datetime.now(timezone.utc).isoformat()
        }
    ]
    os.makedirs(os.path.dirname(rejector.plan_selection_log_path), exist_ok=True)
    with open(rejector.plan_selection_log_path, "w") as f:
        json.dump(dummy_plan_selections, f, indent=2)
    print(f"Created dummy plan selection log at {rejector.plan_selection_log_path}")

    rejector.process_rejection_for_loop("loop_0051_emotion_fail")
    rejector.process_rejection_for_loop("loop_0052_trust_fail")
    rejector.process_rejection_for_loop("loop_0051_invariant_crit_fail")
    rejector.process_rejection_for_loop("loop_0052_invariant_noncrit_fail")
    rejector.process_rejection_for_loop("loop_0050_pass")
    rejector.process_rejection_for_loop("loop_not_in_log")

    print("PlanRejector example finished.")

