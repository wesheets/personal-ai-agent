#!/usr/bin/env python3

import os
import json
import uuid
from datetime import datetime, timezone

class GovernanceReconciler:
    def __init__(self, config):
        self.config = config
        self.alignment_log_entries = []
        self.output_log_path = self.config.get("output_log_path", "/home/ubuntu/personal-ai-agent/app/logs/governance_value_alignment_log.json")
        self.loops_to_reconcile = self.config.get("loops_to_reconcile", ["loop_0041a", "loop_0041b", "loop_0051", "loop_0052"])
        self.project_base_path = self.config.get("project_base_path", "/home/ubuntu/personal-ai-agent")
        self.logs_dir = os.path.join(self.project_base_path, "app/logs")
        self.memory_dir = os.path.join(self.project_base_path, "app/memory")

        # Default paths, can be overridden by test_config
        self.multi_plan_comparison_log_path = self.config.get("multi_plan_comparison_log_path", os.path.join(self.logs_dir, "multi_plan_comparison.json"))
        self.loop_selection_log_path = self.config.get("loop_selection_log_path", os.path.join(self.logs_dir, "loop_plan_selection_log.json"))
        self.plan_rejection_log_path = self.config.get("plan_rejection_log_path", os.path.join(self.logs_dir, "plan_rejection_log.json"))
        self.plan_escalation_log_path = self.config.get("plan_escalation_log_path", os.path.join(self.logs_dir, "plan_escalation_log.json"))
        self.emotion_profile_path = self.config.get("emotion_profile_path", os.path.join(self.memory_dir, "agent_emotion_profile.json"))
        self.current_emotion_state_path = self.config.get("current_emotion_state_path", os.path.join(self.memory_dir, "agent_emotion_state.json"))
        self.invariants_path = self.config.get("invariants_path", os.path.join(self.memory_dir, "promethios_invariants.json"))
        self.belief_index_path = self.config.get("belief_index_path", os.path.join(self.memory_dir, "belief_weight_index.json"))
        print(f"GovernanceReconciler initialized. Output log: {self.output_log_path}")
        print(f"Loops to reconcile: {self.loops_to_reconcile}")

    def _load_json_data(self, file_path, is_critical=False, default_value=None):
        if not os.path.exists(file_path):
            print(f"Warning: File not found - {file_path}")
            if is_critical: print(f"Critical file {file_path} missing.")
            return default_value
        try:
            with open(file_path, "r") as f:
                if os.path.getsize(file_path) == 0:
                    print(f"Warning: File is empty - {file_path}")
                    return default_value if default_value is not None else [] if isinstance(default_value, list) else {} if isinstance(default_value, dict) else None
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
            return default_value
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return default_value

    def _get_loop_decision_data(self, loop_id):
        print(f"Gathering decision data for loop_id: {loop_id}")
        decision_data = {
            "loop_id": loop_id, "selected_plan_id": None, "selected_plan_details": None,
            "candidate_plans_summary": [], "rejections": [], "escalations": [],
            "decision_point": "unknown", "original_loop_timestamp_utc": None, "data_source_notes": ""
        }
        loop_selections = self._load_json_data(self.loop_selection_log_path, default_value=[])
        if isinstance(loop_selections, list):
            for selection in loop_selections:
                if isinstance(selection, dict) and selection.get("loop_id") == loop_id:
                    decision_data["selected_plan_id"] = selection.get("selected_plan_id")
                    decision_data["selected_plan_details"] = selection
                    decision_data["decision_point"] = "plan_selection"
                    decision_data["original_loop_timestamp_utc"] = selection.get("timestamp")
                    decision_data["data_source_notes"] += f"Selected plan info from {self.loop_selection_log_path}. "
                    break
        else: decision_data["data_source_notes"] += f"Could not load or parse {self.loop_selection_log_path} as list. "
        multi_plan_comparisons = self._load_json_data(self.multi_plan_comparison_log_path, default_value=[])
        if isinstance(multi_plan_comparisons, list):
            for comparison_set in multi_plan_comparisons:
                if isinstance(comparison_set, dict) and comparison_set.get("loop_id") == loop_id:
                    for plan_eval in comparison_set.get("plan_evaluations", []):
                        decision_data["candidate_plans_summary"].append({
                            "plan_id": plan_eval.get("plan_id"),
                            "final_weighted_score": plan_eval.get("final_weighted_score"),
                            "trust_alignment_score": plan_eval.get("scores", {}).get("trust_alignment")
                        })
                    if not decision_data["original_loop_timestamp_utc"]: decision_data["original_loop_timestamp_utc"] = comparison_set.get("timestamp")
                    decision_data["data_source_notes"] += f"Candidate plan info from {self.multi_plan_comparison_log_path}. "
                    break
        else: decision_data["data_source_notes"] += f"Could not load or parse {self.multi_plan_comparison_log_path} as list. "
        plan_rejections = self._load_json_data(self.plan_rejection_log_path, default_value=[])
        if isinstance(plan_rejections, list):
            for rejection in plan_rejections:
                if isinstance(rejection, dict) and rejection.get("loop_id") == loop_id:
                    decision_data["rejections"].append(rejection)
                    if decision_data["decision_point"] == "unknown": decision_data["decision_point"] = "plan_rejection"
                    if not decision_data["original_loop_timestamp_utc"]: decision_data["original_loop_timestamp_utc"] = rejection.get("timestamp")
            if any(r.get("loop_id") == loop_id for r in plan_rejections): decision_data["data_source_notes"] += f"Rejection info from {self.plan_rejection_log_path}. "
        else: decision_data["data_source_notes"] += f"Could not load or parse {self.plan_rejection_log_path} as list. "
        plan_escalations = self._load_json_data(self.plan_escalation_log_path, default_value=[])
        if isinstance(plan_escalations, list):
            for escalation in plan_escalations:
                if isinstance(escalation, dict) and escalation.get("loop_id") == loop_id:
                    decision_data["escalations"].append(escalation)
                    if decision_data["decision_point"] not in ["plan_selection", "plan_rejection"]: decision_data["decision_point"] = "plan_escalation"
                    if not decision_data["original_loop_timestamp_utc"]: decision_data["original_loop_timestamp_utc"] = escalation.get("timestamp")
            if any(e.get("loop_id") == loop_id for e in plan_escalations): decision_data["data_source_notes"] += f"Escalation info from {self.plan_escalation_log_path}. "
        else: decision_data["data_source_notes"] += f"Could not load or parse {self.plan_escalation_log_path} as list. "
        if not decision_data["selected_plan_id"] and not decision_data["rejections"] and not decision_data["escalations"] and not decision_data["candidate_plans_summary"]:
            print(f"No decision data found for loop_id: {loop_id} in any primary log.")
            decision_data["data_source_notes"] += "No primary decision data found. "
            return None
        return decision_data

    def _get_governance_context(self, loop_id, loop_timestamp_utc=None):
        print(f"Gathering governance context for loop_id: {loop_id}")
        context = {
            "original_loop_timestamp_utc": loop_timestamp_utc, "agent_emotion_state": None,
            "agent_emotion_profile": None, "promethios_invariants": None,
            "trust_score_inputs_and_outputs": {"source_note": ""}, "belief_weight_index": None, "data_source_notes": ""
        }
        context["agent_emotion_profile"] = self._load_json_data(self.emotion_profile_path, default_value={})
        if context["agent_emotion_profile"]: context["data_source_notes"] += f"Emotion profile loaded from {self.emotion_profile_path}. "
        else: context["data_source_notes"] += f"Emotion profile not found or empty at {self.emotion_profile_path}. "
        current_emotion_state = self._load_json_data(self.current_emotion_state_path, default_value={})
        if current_emotion_state:
            context["agent_emotion_state"] = current_emotion_state
            context["data_source_notes"] += f"Using CURRENT emotion state from {self.current_emotion_state_path} as proxy. "
        elif context["agent_emotion_profile"]:
            context["agent_emotion_state"] = context["agent_emotion_profile"]
            context["data_source_notes"] += f"Current emotion state missing; using emotion profile as proxy for state. "
        else:
            context["data_source_notes"] += f"Current emotion state and profile both unavailable. Emotion state reconciliation will be limited. "
            context["agent_emotion_state"] = {"simulated": True, "message": "No emotion data available"}
        context["promethios_invariants"] = self._load_json_data(self.invariants_path, default_value={})
        if context["promethios_invariants"]: context["data_source_notes"] += f"Invariants loaded from {self.invariants_path}. "
        else: context["data_source_notes"] += f"Invariants not found or empty at {self.invariants_path}. "
        context["belief_weight_index"] = self._load_json_data(self.belief_index_path, default_value={})
        if context["belief_weight_index"]: context["data_source_notes"] += f"Belief index loaded from {self.belief_index_path}. "
        else: context["data_source_notes"] += f"Belief index not found or empty at {self.belief_index_path}. "
        return context

    def _reconcile_emotion(self, decision_data, governance_context):
        print(f"Reconciling emotion for loop {decision_data['loop_id']}")
        misalignments = []
        emotion_state = governance_context.get("agent_emotion_state")
        selected_plan_id = decision_data.get("selected_plan_id")
        if not emotion_state or emotion_state.get("simulated"):
            governance_context.setdefault("data_source_notes", "")
            governance_context["data_source_notes"] += "Emotion state data insufficient for detailed reconciliation. "
            if selected_plan_id:
                 misalignments.append({
                    "misalignment_id": str(uuid.uuid4()), "governance_surface_type": "emotion_state",
                    "governance_surface_detail": "Agent emotional state awareness",
                    "expected_value_or_behavior": "Emotion state should be available and considered for decisions.",
                    "actual_value_or_behavior": "Emotion state was missing or heavily simulated.",
                    "discrepancy_description": "Decision made with potentially inadequate emotional context due to missing/simulated state data.",
                    "severity": "informational"
                })
        return misalignments

    def _reconcile_trust(self, decision_data, governance_context):
        print(f"Reconciling trust for loop {decision_data['loop_id']}")
        misalignments = []
        trust_info_snapshot = governance_context.setdefault("trust_score_inputs_and_outputs", {})
        trust_info_snapshot["source_note"] = ""
        trust_info_snapshot["processed_plans"] = []
        selected_plan_id = decision_data.get("selected_plan_id")
        fallback_threshold = 0.6
        if selected_plan_id:
            plan_trust_score = None
            score_source = "unknown"
            for plan_summary in decision_data.get("candidate_plans_summary", []):
                if plan_summary.get("plan_id") == selected_plan_id:
                    if plan_summary.get("trust_alignment_score") is not None:
                        plan_trust_score = plan_summary.get("trust_alignment_score")
                        score_source = "extracted_from_multi_plan_comparison"
                        break
            trust_info_snapshot["processed_plans"].append({
                "plan_id": selected_plan_id, "trust_score": plan_trust_score,
                "score_source": score_source, "threshold_applied": fallback_threshold
            })
            if plan_trust_score is not None:
                trust_info_snapshot["source_note"] += f"Trust score for selected plan {selected_plan_id} found in multi_plan_comparison. "
                if plan_trust_score < fallback_threshold:
                    misalignments.append({
                        "misalignment_id": str(uuid.uuid4()), "governance_surface_type": "trust_score",
                        "governance_surface_detail": f"Selected plan {selected_plan_id}",
                        "expected_value_or_behavior": f">= {fallback_threshold} (based on extracted score)",
                        "actual_value_or_behavior": plan_trust_score,
                        "discrepancy_description": f"Selected plan trust score {plan_trust_score} is below fallback threshold {fallback_threshold}.",
                        "severity": "medium"
                    })
            else:
                trust_info_snapshot["source_note"] += f"Trust score for selected plan {selected_plan_id} not found in multi_plan_comparison; fallback threshold check applied. "
                pass 
        return misalignments

    def _reconcile_invariants(self, decision_data, governance_context):
        print(f"Reconciling invariants for loop {decision_data['loop_id']}")
        misalignments = []
        active_invariants = governance_context.get("promethios_invariants", {}).get("active_invariants", [])
        if not active_invariants:
            governance_context.setdefault("data_source_notes", "")
            governance_context["data_source_notes"] += "No active invariants found or invariants file missing for reconciliation. "
            return misalignments
        return misalignments

    def _reconcile_beliefs(self, decision_data, governance_context):
        print(f"Reconciling beliefs for loop {decision_data['loop_id']}")
        misalignments = []
        belief_index = governance_context.get("belief_weight_index", {})
        if not belief_index:
            governance_context.setdefault("data_source_notes", "")
            governance_context["data_source_notes"] += "Belief index not found or empty for reconciliation. "
            return misalignments
        return misalignments

    def _calculate_alignment_score(self, misalignments):
        print(f"Calculating alignment score based on {len(misalignments)} misalignments.")
        if not misalignments: return 1.0
        score = 1.0
        for m in misalignments:
            severity = m.get("severity", "low").lower()
            if severity == "critical": score -= 0.75
            elif severity == "high": score -= 0.5
            elif severity == "medium": score -= 0.25
            elif severity == "low": score -= 0.1
        return max(0.0, score)

    def reconcile_loop(self, loop_id):
        print(f"Starting reconciliation for loop_id: {loop_id}")
        decision_data = self._get_loop_decision_data(loop_id)
        if not decision_data:
            print(f"No decision data found for loop {loop_id}. Skipping reconciliation for this loop.")
            log_entry = {
                "log_entry_id": str(uuid.uuid4()), "loop_id": loop_id, "decision_point": "data_unavailable",
                "reconciliation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "alignment_score": "N/A - No decision data",
                "misalignments": [{"misalignment_id": str(uuid.uuid4()), "governance_surface_type": "loop_data",
                                   "governance_surface_detail": "Primary decision logs",
                                   "expected_value_or_behavior": "Available decision logs for reconciliation.",
                                   "actual_value_or_behavior": "Missing or incomplete.",
                                   "discrepancy_description": f"Could not retrieve sufficient decision data for loop {loop_id} to perform reconciliation.",
                                   "severity": "critical"}],
                "governance_context_snapshot": {"data_source_notes": "Attempted to load decision data, but critical components were missing."},
                "processed_plan_details": None
            }
            self.alignment_log_entries.append(log_entry)
            return
        governance_context = self._get_governance_context(loop_id, decision_data.get("original_loop_timestamp_utc"))
        all_misalignments = []
        all_misalignments.extend(self._reconcile_emotion(decision_data, governance_context))
        all_misalignments.extend(self._reconcile_trust(decision_data, governance_context))
        all_misalignments.extend(self._reconcile_invariants(decision_data, governance_context))
        all_misalignments.extend(self._reconcile_beliefs(decision_data, governance_context))
        alignment_score = self._calculate_alignment_score(all_misalignments)
        log_entry = {
            "log_entry_id": str(uuid.uuid4()), "loop_id": loop_id,
            "decision_point": decision_data.get("decision_point", "unknown"),
            "reconciliation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "alignment_score": alignment_score, "misalignments": all_misalignments,
            "governance_context_snapshot": governance_context,
            "processed_plan_details": decision_data.get("selected_plan_details")
        }
        self.alignment_log_entries.append(log_entry)
        print(f"Reconciliation for loop {loop_id} complete. Alignment score: {alignment_score}")

    def run_reconciliation(self):
        print("Starting governance value reconciliation process...")
        self.alignment_log_entries = []
        for loop_id in self.loops_to_reconcile:
            self.reconcile_loop(loop_id)
        self._write_log_to_file()
        print("Governance value reconciliation process finished.")

    def _write_log_to_file(self):
        print(f"Writing alignment log to {self.output_log_path}")
        output_dir = os.path.dirname(self.output_log_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created directory: {output_dir}")
            except OSError as e:
                print(f"Error creating directory {output_dir}: {e}. Cannot write log.")
                return
        try:
            with open(self.output_log_path, "w") as f:
                json.dump(self.alignment_log_entries, f, indent=2)
            print(f"Successfully wrote {len(self.alignment_log_entries)} entries to {self.output_log_path}")
        except Exception as e:
            print(f"Error writing log to {self.output_log_path}: {e}")

if __name__ == "__main__":
    print("Running GovernanceReconciler directly (for testing)...")
    mock_config = {
        "output_log_path": "/home/ubuntu/personal-ai-agent/app/logs/governance_value_alignment_log.json",
        "loops_to_reconcile": ["loop_0051", "loop_0052", "loop_0041a", "loop_0041b", "loop_missing_data"],
        "project_base_path": "/home/ubuntu/personal-ai-agent",
    }
    base = mock_config["project_base_path"]
    log_dir_for_test = os.path.join(base, "app/logs")
    mem_dir_for_test = os.path.join(base, "app/memory")
    if not os.path.exists(log_dir_for_test): os.makedirs(log_dir_for_test)
    if not os.path.exists(mem_dir_for_test): os.makedirs(mem_dir_for_test)
    dummy_multi_plan_path = os.path.join(log_dir_for_test, "multi_plan_comparison.json") 
    if not os.path.exists(dummy_multi_plan_path):
        with open(dummy_multi_plan_path, "w") as f:
            json.dump([{"loop_id": "loop_0051", "timestamp": datetime.now(timezone.utc).isoformat(),
                        "plan_evaluations": [{"plan_id": "plan_A", "final_weighted_score": 0.8, "scores": {"trust_alignment": 0.9}},
                                             {"plan_id": "plan_B", "final_weighted_score": 0.7, "scores": {"trust_alignment": 0.5}}]}], f)
    dummy_loop_select_path = os.path.join(log_dir_for_test, "loop_plan_selection_log.json")
    if not os.path.exists(dummy_loop_select_path):
         with open(dummy_loop_select_path, "w") as f:
            json.dump([{"loop_id": "loop_0051", "selected_plan_id": "plan_A", "timestamp": datetime.now(timezone.utc).isoformat()}], f)
    reconciler = GovernanceReconciler(mock_config) 
    reconciler.run_reconciliation()
    print("Direct test run finished.")

