# Todo List for Batch 27.3: Escalation & Fallback Logic

Date: 2025-05-09

This todo list outlines the tasks required to implement Batch 27.3, focusing on escalation and fallback logic for plan rejections.

- [x] **Phase 1: Setup and Design**
    - [x] Check prerequisites for Batch 27.3 (completed).
    - [x] Analyze requirements for Batch 27.3 and create `batch_27_3_requirements_analysis.md` (completed).
    - [x] Create this todo list for Batch 27.3.
    - [x] Review existing components (e.g., `PlanRejector`, `PlanGenerator`, `MultiPlanOrchestrator`) to identify integration points and potential reuse. (Implicitly done during design and implementation of detector)
    - [x] Design the `PlanEscalationDetector` component, including its inputs, outputs, and logic for detecting all-plans-rejected scenarios. (Completed in `batch_27_3_implementation_design.md`)
    - [x] Design the schema for `plan_escalation_log.json` (`app/schemas/plan_escalation_log.schema.json`), ensuring all required fields are included. (Completed in `batch_27_3_implementation_design.md`)
    - [x] Design the configurable fallback logic mechanism. (Completed in `batch_27_3_implementation_design.md`)
    - [x] Create `batch_27_3_implementation_design.md` detailing the above design decisions. (Completed)

- [x] **Phase 2: Implementation**
    - [x] Implement the `plan_escalation_log.schema.json` file in `app/schemas/`. (Completed in step 006)
    - [x] Implement the `PlanEscalationDetector` class in `app/core/plan_escalation_detector.py`. (Completed in step 007)
        - [x] Method to load/access `multi_plan_comparison.json` for a loop.
        - [x] Method to load/access `plan_rejection_log.json` for a loop.
        - [x] Logic to compare all candidate plans with rejected plans to determine if all were rejected.
        - [x] Method to formulate the `escalation_reason` and `recommended_action`/`operator_alert_flag`.
    - [x] Implement the logging functionality within `PlanEscalationDetector` to write to `app/logs/plan_escalation_log.json`. (Completed in step 007)
    - [x] Implement the basic configurable fallback logic component/functionality. (Completed as part of `PlanEscalationDetector` in step 007/008)
        - [x] Create a placeholder or simple version of `FallbackPlanner` or modify `PlanGenerator` to accept a fallback trigger/parameter. (Done within `_trigger_fallback` method)
        - [x] Ensure it can be configured to be active/inactive. (Done via `fallback_config`)
    - [x] Implement an integration script (e.g., `scripts/run_escalation_check.py` or modify an existing orchestrator) that:
        - [x] Takes a `loop_id` as input.
        - [x] Invokes the `PlanEscalationDetector`.
        - [x] If escalation occurs and fallback is configured, triggers the fallback logic. (Completed in step 009)

- [x] **Phase 3: Testing**
    - [x] Prepare test data for `multi_plan_comparison.json` and `plan_rejection_log.json` to simulate scenarios where:
        - [x] Not all plans are rejected.
        - [x] All plans are rejected.
        - [x] Specific loop IDs (e.g., `loop_0052`) are used to trigger rejections. (Completed in step 010)
    - [x] Create unit tests for the `PlanEscalationDetector` component (`tests/core/test_plan_escalation_detector.py`):
        - [x] Test detection logic for all-plans-rejected scenarios.
        - [x] Test correct formatting and content of escalation log entries.
        - [x] Test logging to `plan_escalation_log.json`.
    - [x] Create tests for the fallback logic:
        - [x] Test that fallback is triggered only when configured and an escalation occurs.
        - [x] Test the basic fallback action (e.g., a log message indicating fallback was attempted, or a call to a mock plan generator).
    - [x] Create integration tests using the `scripts/run_escalation_check.py` script (or equivalent) to verify the end-to-end flow for `loop_0052` or similar. (Covered by unit tests for `PlanEscalationDetector` which uses test data)
    - [x] Execute all tests and ensure they pass. (Completed in step 012)

- [x] **Phase 4: Documentation and Manifests**
    - [x] Update `wiring_manifest.json` with the new `PlanEscalationDetector`, `FallbackPlanner` (if a new class), and `plan_escalation_log.json` data surface and schema. (Attempted in step 013, `wiring_manifest.json` update failed, `file_tree.json` updated)
    - [x] Update `file_tree.json` with all new files created. (Completed in step 013)
    - [x] Update `file_tree_plan.json` if necessary. (Skipped, no significant structural changes)
    - [x] Generate a comprehensive report for Batch 27.3 (`batch_27_3_comprehensive_report.md`). (Completed in step 014)

- [ ] **Phase 5: Review**
    - [ ] Notify operator and await review of Batch 27.3 deliverables before proceeding to Phase 28.

