import unittest
import json
import os
import shutil
import uuid
from datetime import datetime, timezone

# Add the project root to the Python path to allow importing app modules
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) # Corrected path
sys.path.append(PROJECT_ROOT)

from app.core.plan_escalation_detector import PlanEscalationDetector

class TestPlanEscalationDetector(unittest.TestCase):
    TEST_DATA_BASE_PATH = os.path.join(PROJECT_ROOT, "app", "test_data", "batch_27_3")
    LOG_DIR = os.path.join(PROJECT_ROOT, "app", "logs") # Test logs will go here
    
    # Define paths for test input files (these will be copied from TEST_DATA_BASE_PATH)
    MULTI_PLAN_COMPARISON_PATH = os.path.join(LOG_DIR, "multi_plan_comparison.json")
    PLAN_REJECTION_LOG_PATH = os.path.join(LOG_DIR, "plan_rejection_log.json")
    LOOP_PLAN_SELECTION_LOG_PATH = os.path.join(LOG_DIR, "loop_plan_selection_log.json")
    PLAN_ESCALATION_LOG_PATH = os.path.join(LOG_DIR, "plan_escalation_log.json")

    def setUp(self):
        # Create a clean log directory for each test
        if os.path.exists(self.LOG_DIR):
            shutil.rmtree(self.LOG_DIR)
        os.makedirs(self.LOG_DIR, exist_ok=True)
        
        # Clear escalation log if it exists from previous runs, as it's appended to
        if os.path.exists(self.PLAN_ESCALATION_LOG_PATH):
            os.remove(self.PLAN_ESCALATION_LOG_PATH)

    def tearDown(self):
        # Clean up the log directory after tests
        if os.path.exists(self.LOG_DIR):
            shutil.rmtree(self.LOG_DIR)

    def _prepare_log_files(self, multi_plan_file, rejection_log_file, selection_log_content=None):
        # Copy specified test data files to the active log directory
        shutil.copy(os.path.join(self.TEST_DATA_BASE_PATH, multi_plan_file), self.MULTI_PLAN_COMPARISON_PATH)
        shutil.copy(os.path.join(self.TEST_DATA_BASE_PATH, rejection_log_file), self.PLAN_REJECTION_LOG_PATH)
        
        # Create a dummy loop_plan_selection_log.json if content is provided
        if selection_log_content:
            with open(self.LOOP_PLAN_SELECTION_LOG_PATH, "w") as f:
                json.dump(selection_log_content, f, indent=2)
        elif not os.path.exists(self.LOOP_PLAN_SELECTION_LOG_PATH): # Create empty if not provided and not exists
             with open(self.LOOP_PLAN_SELECTION_LOG_PATH, "w") as f:
                json.dump([], f, indent=2)

    def test_01_no_escalation_partial_rejection(self):
        print("Running test_01_no_escalation_partial_rejection")
        loop_id_test = "loop_0050"
        comparison_set_id_test = "cs_loop0050_1"
        dummy_selection_log = [
            {"loop_id": loop_id_test, "comparison_set_id": comparison_set_id_test, "selected_plan_id": "planD", "timestamp": datetime.now(timezone.utc).isoformat()}
        ]
        self._prepare_log_files(
            "multi_plan_comparison_loop_0050.json", 
            "plan_rejection_log_loop_0050_partial_rejection.json",
            selection_log_content=dummy_selection_log
        )
        
        detector = PlanEscalationDetector(
            multi_plan_comparison_path=self.MULTI_PLAN_COMPARISON_PATH,
            plan_rejection_log_path=self.PLAN_REJECTION_LOG_PATH,
            loop_plan_selection_log_path=self.LOOP_PLAN_SELECTION_LOG_PATH,
            plan_escalation_log_path=self.PLAN_ESCALATION_LOG_PATH,
            fallback_config={"enabled": False}
        )
        result = detector.check_for_escalation(loop_id_test)
        self.assertIsNone(result, "Escalation should not occur for partial rejection.")
        self.assertFalse(os.path.exists(self.PLAN_ESCALATION_LOG_PATH) or (os.path.exists(self.PLAN_ESCALATION_LOG_PATH) and os.path.getsize(self.PLAN_ESCALATION_LOG_PATH) == 0) , "Escalation log should not be created or should be empty.")

    def test_02_escalation_all_rejected_no_fallback(self):
        print("Running test_02_escalation_all_rejected_no_fallback")
        loop_id_test = "loop_0052"
        comparison_set_id_test = "cs_loop0052_1"
        dummy_selection_log = [
            {"loop_id": loop_id_test, "comparison_set_id": comparison_set_id_test, "selected_plan_id": "planE_L0052", "timestamp": datetime.now(timezone.utc).isoformat()}
        ]
        self._prepare_log_files(
            "multi_plan_comparison_loop_0052.json", 
            "plan_rejection_log_loop_0052_all_rejected.json",
            selection_log_content=dummy_selection_log
        )

        detector = PlanEscalationDetector(
            multi_plan_comparison_path=self.MULTI_PLAN_COMPARISON_PATH,
            plan_rejection_log_path=self.PLAN_REJECTION_LOG_PATH,
            loop_plan_selection_log_path=self.LOOP_PLAN_SELECTION_LOG_PATH,
            plan_escalation_log_path=self.PLAN_ESCALATION_LOG_PATH,
            fallback_config={"enabled": False}
        )
        result = detector.check_for_escalation(loop_id_test)
        self.assertIsNotNone(result, "Escalation should occur when all plans are rejected.")
        self.assertEqual(result["loop_id"], loop_id_test)
        self.assertEqual(result["recommended_action"], "operator_review_required")
        self.assertTrue(result["operator_alert_flag"])
        self.assertFalse(result["fallback_triggered"])
        self.assertTrue(os.path.exists(self.PLAN_ESCALATION_LOG_PATH))
        with open(self.PLAN_ESCALATION_LOG_PATH, "r") as f:
            log_data = json.load(f)
            self.assertEqual(len(log_data), 1)
            self.assertEqual(log_data[0]["loop_id"], loop_id_test)
            self.assertEqual(len(log_data[0]["rejected_plan_ids"]), 2) # planE_L0052, planF_L0052

    def test_03_escalation_all_rejected_fallback_log_alert(self):
        print("Running test_03_escalation_all_rejected_fallback_log_alert")
        loop_id_test = "loop_0052"
        comparison_set_id_test = "cs_loop0052_1"
        dummy_selection_log = [
            {"loop_id": loop_id_test, "comparison_set_id": comparison_set_id_test, "selected_plan_id": "planE_L0052", "timestamp": datetime.now(timezone.utc).isoformat()}
        ]
        self._prepare_log_files(
            "multi_plan_comparison_loop_0052.json", 
            "plan_rejection_log_loop_0052_all_rejected.json",
            selection_log_content=dummy_selection_log
        )

        detector = PlanEscalationDetector(
            multi_plan_comparison_path=self.MULTI_PLAN_COMPARISON_PATH,
            plan_rejection_log_path=self.PLAN_REJECTION_LOG_PATH,
            loop_plan_selection_log_path=self.LOOP_PLAN_SELECTION_LOG_PATH,
            plan_escalation_log_path=self.PLAN_ESCALATION_LOG_PATH,
            fallback_config={"enabled": True, "default_fallback_strategy": "log_and_alert_operator"}
        )
        result = detector.check_for_escalation(loop_id_test)
        self.assertIsNotNone(result)
        self.assertTrue(result["fallback_triggered"])
        self.assertEqual(result["recommended_action"], "operator_review_required")
        self.assertTrue(result["operator_alert_flag"])
        self.assertIn("Fallback strategy: Logged and operator alert recommended.", result["fallback_details"])

    def test_04_escalation_all_rejected_fallback_regenerate(self):
        print("Running test_04_escalation_all_rejected_fallback_regenerate")
        loop_id_test = "loop_0052"
        comparison_set_id_test = "cs_loop0052_1"
        dummy_selection_log = [
            {"loop_id": loop_id_test, "comparison_set_id": comparison_set_id_test, "selected_plan_id": "planE_L0052", "timestamp": datetime.now(timezone.utc).isoformat()}
        ]
        self._prepare_log_files(
            "multi_plan_comparison_loop_0052.json", 
            "plan_rejection_log_loop_0052_all_rejected.json",
            selection_log_content=dummy_selection_log
        )

        detector = PlanEscalationDetector(
            multi_plan_comparison_path=self.MULTI_PLAN_COMPARISON_PATH,
            plan_rejection_log_path=self.PLAN_REJECTION_LOG_PATH,
            loop_plan_selection_log_path=self.LOOP_PLAN_SELECTION_LOG_PATH,
            plan_escalation_log_path=self.PLAN_ESCALATION_LOG_PATH,
            fallback_config={"enabled": True, "default_fallback_strategy": "attempt_regeneration_simple"}
        )
        result = detector.check_for_escalation(loop_id_test)
        self.assertIsNotNone(result)
        self.assertTrue(result["fallback_triggered"])
        self.assertEqual(result["recommended_action"], "trigger_fallback_procedure")
        self.assertFalse(result["operator_alert_flag"])
        self.assertIn("Attempted plan regeneration with strategy: attempt_regeneration_simple", result["fallback_details"])

    def test_05_no_comparison_set_found(self):
        print("Running test_05_no_comparison_set_found")
        loop_id_test = "loop_0053_no_selection_log"
        # No loop_plan_selection_log entry for this loop_id
        self._prepare_log_files(
            "multi_plan_comparison_loop_0052.json", # Use some existing data, won't be reached
            "plan_rejection_log_loop_0052_all_rejected.json"
        )
        detector = PlanEscalationDetector(
            multi_plan_comparison_path=self.MULTI_PLAN_COMPARISON_PATH,
            plan_rejection_log_path=self.PLAN_REJECTION_LOG_PATH,
            loop_plan_selection_log_path=self.LOOP_PLAN_SELECTION_LOG_PATH,
            plan_escalation_log_path=self.PLAN_ESCALATION_LOG_PATH,
            fallback_config={"enabled": False}
        )
        result = detector.check_for_escalation(loop_id_test)
        self.assertIsNone(result, "Escalation should not occur if no comparison set ID is found.")

    def test_06_no_candidate_plans_found(self):
        print("Running test_06_no_candidate_plans_found")
        loop_id_test = "loop_0054_no_candidates"
        comparison_set_id_test = "cs_loop0054_1"
        dummy_selection_log = [
            {"loop_id": loop_id_test, "comparison_set_id": comparison_set_id_test, "selected_plan_id": "planX", "timestamp": datetime.now(timezone.utc).isoformat()}
        ]
        # Create an empty multi_plan_comparison for this specific comparison_set_id
        with open(self.MULTI_PLAN_COMPARISON_PATH, "w") as f:
            json.dump([{"comparison_set_id": comparison_set_id_test, "loop_id": loop_id_test, "candidate_plans": []}], f)
        shutil.copy(os.path.join(self.TEST_DATA_BASE_PATH, "plan_rejection_log_loop_0052_all_rejected.json"), self.PLAN_REJECTION_LOG_PATH)
        with open(self.LOOP_PLAN_SELECTION_LOG_PATH, "w") as f:
            json.dump(dummy_selection_log, f, indent=2)

        detector = PlanEscalationDetector(
            multi_plan_comparison_path=self.MULTI_PLAN_COMPARISON_PATH,
            plan_rejection_log_path=self.PLAN_REJECTION_LOG_PATH,
            loop_plan_selection_log_path=self.LOOP_PLAN_SELECTION_LOG_PATH,
            plan_escalation_log_path=self.PLAN_ESCALATION_LOG_PATH,
            fallback_config={"enabled": False}
        )
        result = detector.check_for_escalation(loop_id_test)
        self.assertIsNone(result, "Escalation should not occur if no candidate plans are found for the comparison set.")

if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)

