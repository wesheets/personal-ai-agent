import unittest
import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, mock_open

# The test is run from the project root (/home/ubuntu/personal-ai-agent),
# which is automatically added to sys.path by `python -m unittest`.
# Therefore, imports can be relative to this project root.
from app.core.plan_rejector import PlanRejector

TEST_DATA_DIR = "/home/ubuntu/personal-ai-agent/app/test_data/batch_27_2"
TEST_LOGS_DIR = "/home/ubuntu/personal-ai-agent/app/logs" # For plan_rejection_log.json
TEST_PLAN_SELECTION_LOG = os.path.join(TEST_DATA_DIR, "sample_loop_plan_selection_log.json")
TEST_EMOTION_STATE = os.path.join(TEST_DATA_DIR, "mock_agent_emotion_state.json")
TEST_TRUST_SCORE = os.path.join(TEST_DATA_DIR, "mock_agent_trust_score.json")
TEST_INVARIANTS = os.path.join(TEST_DATA_DIR, "mock_promethios_invariants.json")
TEST_REJECTION_LOG = os.path.join(TEST_LOGS_DIR, "test_plan_rejection_log.json")

class TestPlanRejector(unittest.TestCase):

    def setUp(self):
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
        os.makedirs(TEST_LOGS_DIR, exist_ok=True)

        self.plan_selection_log_path = TEST_PLAN_SELECTION_LOG
        self.emotion_state_path = TEST_EMOTION_STATE
        self.trust_score_path = TEST_TRUST_SCORE
        self.invariants_path = TEST_INVARIANTS # This is used by mock in PlanRejector for now
        self.rejection_log_path = TEST_REJECTION_LOG

        if os.path.exists(self.rejection_log_path):
            os.remove(self.rejection_log_path)

        self.rejector = PlanRejector(
            plan_selection_log_path=self.plan_selection_log_path,
            rejection_log_path=self.rejection_log_path,
            emotion_state_path=self.emotion_state_path,
            trust_score_path=self.trust_score_path,
            invariants_path=self.invariants_path
        )

    def tearDown(self):
        if os.path.exists(self.rejection_log_path):
            os.remove(self.rejection_log_path)

    def test_01_load_thresholds(self):
        thresholds = self.rejector._load_thresholds()
        self.assertIn("emotion", thresholds)
        self.assertIn("trust", thresholds)
        self.assertIn("invariants", thresholds)
        self.assertEqual(thresholds["emotion"]["max_negative_valence"], -0.7)

    def test_02_get_selected_plan_for_loop_found(self):
        plan_id, cs_id = self.rejector._get_selected_plan_for_loop("loop_0051_emotion_fail")
        self.assertEqual(plan_id, "plan_E_fail_A")
        self.assertEqual(cs_id, "cs_test_E_A")

    def test_03_get_selected_plan_for_loop_not_found(self):
        plan_id, cs_id = self.rejector._get_selected_plan_for_loop("loop_not_exists")
        self.assertIsNone(plan_id)
        self.assertIsNone(cs_id)

    def test_04_get_current_governance_metrics_emotion_fail(self):
        metrics = self.rejector._get_current_governance_metrics("loop_0051_emotion_fail", "plan_E_fail_A")
        self.assertEqual(metrics["emotion"]["valence"], -0.8)

    def test_05_get_current_governance_metrics_trust_fail(self):
        metrics = self.rejector._get_current_governance_metrics("loop_0052_trust_fail", "plan_T_fail")
        self.assertEqual(metrics["trust"]["score"], 0.4)

    def test_06_get_current_governance_metrics_invariant_crit_fail(self):
        metrics = self.rejector._get_current_governance_metrics("loop_0051_invariant_crit_fail", "plan_I_crit_fail")
        self.assertIn("inv_critical_001", metrics["invariants"]["violated_critical_invariants"])

    def test_07_get_current_governance_metrics_pass(self):
        metrics = self.rejector._get_current_governance_metrics("loop_0050_pass", "plan_P_pass")
        self.assertEqual(metrics["emotion"]["valence"], 0.6)
        self.assertEqual(metrics["trust"]["score"], 0.9)
        self.assertEqual(len(metrics["invariants"]["violated_critical_invariants"]), 0)

    def test_08_evaluate_plan_rejection_emotion_valence(self):
        is_rejected, details = self.rejector.evaluate_plan("loop_0051_emotion_fail", "plan_E_fail_A", "cs_test_E_A")
        self.assertTrue(is_rejected)
        self.assertIsNotNone(details)
        self.assertEqual(details["triggering_metric"], "emotion.negative_valence")
        self.assertEqual(details["rejection_reason"], "Emotional negative valence (-0.8) below threshold (-0.7).")

    def test_09_evaluate_plan_rejection_emotion_arousal(self):
        is_rejected, details = self.rejector.evaluate_plan("loop_0051_emotion_arousal_fail", "plan_E_fail_B", "cs_test_E_B")
        self.assertTrue(is_rejected)
        self.assertIsNotNone(details)
        self.assertEqual(details["triggering_metric"], "emotion.arousal_when_negative")

    def test_10_evaluate_plan_rejection_trust(self):
        is_rejected, details = self.rejector.evaluate_plan("loop_0052_trust_fail", "plan_T_fail", "cs_test_T")
        self.assertTrue(is_rejected)
        self.assertIsNotNone(details)
        self.assertEqual(details["triggering_metric"], "trust.score")

    def test_11_evaluate_plan_rejection_invariant_critical(self):
        is_rejected, details = self.rejector.evaluate_plan("loop_0051_invariant_crit_fail", "plan_I_crit_fail", "cs_test_I_crit")
        self.assertTrue(is_rejected)
        self.assertIsNotNone(details)
        self.assertEqual(details["triggering_metric"], "invariants.critical_violations")

    def test_12_evaluate_plan_rejection_invariant_non_critical(self):
        original_thresholds = self.rejector.thresholds.copy()
        self.rejector.thresholds["invariants"]["max_non_critical_violations"] = 1 
        is_rejected, details = self.rejector.evaluate_plan("loop_0052_invariant_noncrit_fail", "plan_I_noncrit_fail", "cs_test_I_noncrit")
        self.assertTrue(is_rejected)
        self.assertIsNotNone(details)
        self.assertEqual(details["triggering_metric"], "invariants.non_critical_violations")
        self.rejector.thresholds = original_thresholds

    def test_13_evaluate_plan_approval(self):
        is_rejected, details = self.rejector.evaluate_plan("loop_0050_pass", "plan_P_pass", "cs_test_P")
        self.assertFalse(is_rejected)
        self.assertIsNone(details)

    def test_14_log_rejection(self):
        _, rejection_details = self.rejector.evaluate_plan("loop_0051_emotion_fail", "plan_E_fail_A", "cs_test_E_A")
        self.rejector._log_rejection(rejection_details)
        self.assertTrue(os.path.exists(self.rejection_log_path))
        with open(self.rejection_log_path, "r") as f:
            log_data = json.load(f)
        self.assertEqual(len(log_data), 1)
        self.assertEqual(log_data[0]["loop_id"], "loop_0051_emotion_fail")
        self.assertEqual(log_data[0]["plan_id"], "plan_E_fail_A")

    def test_15_process_rejection_for_loop_rejected(self):
        result = self.rejector.process_rejection_for_loop("loop_0051_emotion_fail")
        self.assertIsNotNone(result)
        self.assertEqual(result["triggering_metric"], "emotion.negative_valence")
        self.assertTrue(os.path.exists(self.rejection_log_path))

    def test_16_process_rejection_for_loop_approved(self):
        result = self.rejector.process_rejection_for_loop("loop_0050_pass")
        self.assertIsNone(result)
        if os.path.exists(self.rejection_log_path):
            with open(self.rejection_log_path, "r") as f:
                log_data = json.load(f)
                for entry in log_data:
                    self.assertNotEqual(entry["loop_id"], "loop_0050_pass")
        else:
            self.assertFalse(os.path.exists(self.rejection_log_path))

    def test_17_process_rejection_for_loop_no_plan_found(self):
        result = self.rejector.process_rejection_for_loop("loop_id_not_in_selection_log")
        self.assertIsNone(result)
        # Check if rejection_log_path exists before trying to open it
        log_exists_for_non_existent_loop = False
        if os.path.exists(self.rejection_log_path):
            with open(self.rejection_log_path, "r") as f:
                log_data = json.load(f)
                if any(entry["loop_id"] == "loop_id_not_in_selection_log" for entry in log_data):
                    log_exists_for_non_existent_loop = True
        self.assertFalse(log_exists_for_non_existent_loop)

if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)

