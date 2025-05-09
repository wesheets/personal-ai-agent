# Batch 27.3: Escalation & Fallback Logic - Implementation Design

Date: 2025-05-09

## 1. Introduction

This document details the implementation design for Batch 27.3, which introduces logic to handle scenarios where all candidate plans for an agent loop are rejected. It covers the design of the `PlanEscalationDetector` component, the schema for `plan_escalation_log.json`, the configurable fallback mechanism, and integration with existing systems. This design is based on the requirements outlined in `batch_27_3_requirements_analysis.md`.

## 2. Core Components Design

### 2.1. `plan_escalation_log.schema.json`

**Location:** `app/schemas/plan_escalation_log.schema.json`

**Objective:** Define the structure for entries in the `plan_escalation_log.json` file.

**Schema Definition:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PlanEscalationLogEntry",
  "description": "Schema for an entry in the plan_escalation_log.json file, recording instances where all plans for a loop were rejected.",
  "type": "object",
  "properties": {
    "log_entry_id": {
      "description": "Unique identifier for this log entry.",
      "type": "string",
      "format": "uuid"
    },
    "loop_id": {
      "description": "The identifier of the loop for which all plans were rejected.",
      "type": "string"
    },
    "comparison_set_id": {
      "description": "Identifier for the set of plans that were compared and subsequently all rejected for this loop.",
      "type": ["string", "null"]
    },
    "escalation_reason": {
      "description": "A human-readable reason for the escalation.",
      "type": "string",
      "examples": ["All candidate plans rejected by governance thresholds."]
    },
    "rejected_plan_ids": {
      "description": "A list of all plan IDs that were considered and rejected for this loop.",
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "governance_summary": {
        "description": "A summary of governance metrics or rejection reasons for the rejected plans (optional, could be detailed).",
        "type": "object",
        "properties": {
            "total_plans_considered": {"type": "integer"},
            "total_plans_rejected": {"type": "integer"}
        }
    },
    "recommended_action": {
      "description": "A system-recommended next action or status.",
      "type": "string",
      "enum": ["trigger_fallback_procedure", "operator_review_required", "no_further_action_defined"]
    },
    "operator_alert_flag": {
      "description": "Boolean flag indicating if an operator alert is explicitly recommended.",
      "type": "boolean",
      "default": false
    },
    "fallback_triggered": {
        "description": "Boolean flag indicating if fallback logic was triggered as a result of this escalation.",
        "type": "boolean",
        "default": false
    },
    "fallback_details": {
        "description": "Details about the fallback action taken, if any.",
        "type": ["string", "null"]
    },
    "timestamp": {
      "description": "UTC timestamp of when the escalation was logged (ISO 8601 format).",
      "type": "string",
      "format": "date-time"
    }
  },
  "required": [
    "log_entry_id",
    "loop_id",
    "escalation_reason",
    "rejected_plan_ids",
    "recommended_action",
    "timestamp"
  ]
}
```

### 2.2. `PlanEscalationDetector` Component

**Location:** `app/core/plan_escalation_detector.py`

**Class Name:** `PlanEscalationDetector`

**Objective:** To detect if all candidate plans for a given `loop_id` have been rejected, log this event, and potentially trigger fallback logic.

**Key Attributes:**
*   `multi_plan_comparison_path`: Path to `multi_plan_comparison.json`.
*   `plan_rejection_log_path`: Path to `plan_rejection_log.json`.
*   `plan_escalation_log_path`: Path to `plan_escalation_log.json`.
*   `fallback_config`: Configuration for fallback behavior (e.g., `{"enabled": true, "strategy": "regenerate_with_adjusted_weights"}`).

**Core Methods:**

1.  `__init__(self, multi_plan_comparison_path, plan_rejection_log_path, plan_escalation_log_path, fallback_config)`:
    *   Initializes paths and configuration.

2.  `_load_json_data(self, file_path, default_value=None)`: (Helper, potentially shared or inherited)
    *   Loads JSON data from a file, handles file not found or empty file scenarios.

3.  `_get_candidate_plans_for_loop(self, loop_id, comparison_set_id)`:
    *   Reads `multi_plan_comparison.json`.
    *   Filters entries for the given `loop_id` and `comparison_set_id` (if provided, otherwise latest for loop_id).
    *   Returns a list of all candidate `plan_id`s that were considered in that set.

4.  `_get_rejected_plans_for_loop(self, loop_id, comparison_set_id)`:
    *   Reads `plan_rejection_log.json`.
    *   Filters entries for the given `loop_id` and `comparison_set_id`.
    *   Returns a set of `plan_id`s that were explicitly rejected.

5.  `check_for_escalation(self, loop_id)`:
    *   **Step 1: Identify Target Comparison Set:** Determine the relevant `comparison_set_id` for the `loop_id`. This might involve looking at the latest entry for `loop_id` in `loop_plan_selection_log.json` (from Batch 27.1) to find which set of plans was being processed before rejections.
    *   **Step 2: Get Candidate Plans:** Call `_get_candidate_plans_for_loop(loop_id, comparison_set_id)`.
    *   **Step 3: Get Rejected Plans:** Call `_get_rejected_plans_for_loop(loop_id, comparison_set_id)`.
    *   **Step 4: Determine if All Rejected:** If the set of candidate plan IDs is non-empty and is a subset of or equal to the set of rejected plan IDs, then an escalation condition is met.
    *   **Step 5: Log Escalation:** If escalation is needed, call `_log_escalation()`.
    *   **Step 6: Trigger Fallback (if configured):** If escalation occurred and `self.fallback_config["enabled"]` is true, call a method to trigger fallback (e.g., `_trigger_fallback()`). Update escalation log with fallback status.
    *   Returns: Escalation details if an escalation occurred, otherwise `None`.

6.  `_log_escalation(self, loop_id, comparison_set_id, candidate_plan_ids, rejected_plan_ids, recommended_action, operator_alert_flag, fallback_triggered=False, fallback_details=None)`:
    *   Constructs the log entry according to `plan_escalation_log.schema.json`.
    *   Appends the entry to `plan_escalation_log.json`.

7.  `_trigger_fallback(self, loop_id, rejected_plan_ids)`:
    *   **Initial Simple Implementation:** Logs that fallback is triggered. For Batch 27.3, this might involve:
        *   Printing a message.
        *   Potentially calling a (mocked or very simple) `PlanGenerator.regenerate_plans(loop_id, strategy="conservative_fallback")`.
        *   The actual regeneration logic with "adjusted weights" is complex and can be a placeholder call for now.
    *   Returns: Details of the fallback action taken (e.g., "Fallback triggered: Attempting plan regeneration with conservative strategy.").

### 2.3. Fallback Logic Mechanism

**Approach:** Integrate a simple fallback trigger within `PlanEscalationDetector` initially. A separate `FallbackPlanner` class might be overkill for the initial scope but can be a future extension.

**Configuration:**
*   A simple JSON configuration file or a dictionary passed to `PlanEscalationDetector`:
    ```json
    {
      "fallback_enabled": true, // or false
      "default_fallback_strategy": "log_and_alert_operator" // or "attempt_regeneration_simple"
    }
    ```

**Triggering:** The `_trigger_fallback` method in `PlanEscalationDetector` will be called if `fallback_enabled` is true.

**Initial Action (Batch 27.3):**
*   If `default_fallback_strategy` is `"log_and_alert_operator"`, the `recommended_action` in the escalation log will be `"operator_review_required"` and `operator_alert_flag` will be `true`.
*   If `default_fallback_strategy` is `"attempt_regeneration_simple"`, it will log this attempt. A call to a plan generation function (potentially a modified `PlanGenerator` or a new simple one) could be made. This generation function would be a placeholder or a very basic version for this batch, e.g., it might just log that it was called with a specific strategy.

## 3. Integration with Existing System

*   The `PlanEscalationDetector` will likely be invoked by a main control loop or orchestrator after the `PlanSelector` (Batch 27.1) and `PlanRejector` (Batch 27.2) have completed their processing for a given `loop_id`.
*   The orchestrator needs to check the result of `PlanEscalationDetector.check_for_escalation(loop_id)`.
*   If an escalation occurs and fallback is triggered, the orchestrator might need to re-initiate the planning/selection/rejection cycle with the new plans generated by the fallback mechanism (if any).

**Workflow Sketch:**
1.  Loop starts (e.g., `loop_0052`).
2.  `MultiPlanOrchestrator` (Batch 27.0) generates candidate plans -> `multi_plan_comparison.json`.
3.  `PlanSelector` (Batch 27.1) selects the best plan -> `loop_plan_selection_log.json`.
4.  `PlanRejector` (Batch 27.2) evaluates the selected plan. If rejected, logs to `plan_rejection_log.json`.
    *   *Modification needed*: If a plan is rejected, the system needs to know if there are other plans to try from the `multi_plan_comparison.json` for the *same* `loop_id` and `comparison_set_id`. The `PlanSelector` might need to be enhanced to pick the *next best* plan if the top one is rejected, or the orchestrator handles this iteration.
5.  **After all plans in a comparison set for `loop_id` have been evaluated and potentially rejected:**
    *   The orchestrator calls `PlanEscalationDetector.check_for_escalation(loop_id)`.
    *   If escalation occurs:
        *   Escalation is logged to `plan_escalation_log.json`.
        *   If fallback is enabled and triggered, `PlanEscalationDetector` attempts fallback (e.g., calls a plan regeneration function).
        *   The orchestrator then decides the next step (e.g., operator alert, or if fallback generated new plans, re-evaluate them).

## 4. Data Flow

1.  **Input to `PlanEscalationDetector` for `loop_id`:**
    *   `multi_plan_comparison.json`: To get all candidate plan IDs for the loop's comparison set.
    *   `plan_rejection_log.json`: To get all rejected plan IDs for the loop's comparison set.
    *   `loop_plan_selection_log.json`: To identify the relevant `comparison_set_id` for the current `loop_id`.
    *   Fallback configuration.
2.  **Output:**
    *   `plan_escalation_log.json`: Updated with new escalation entries.
    *   Status/result indicating if escalation occurred and if fallback was attempted.

## 5. Testing Considerations

*   **Test Data:** Need `multi_plan_comparison.json` and `plan_rejection_log.json` samples that simulate:
    *   No rejections.
    *   Some plans rejected, but not all.
    *   All plans for a specific `loop_id` and `comparison_set_id` rejected.
*   **Unit Tests for `PlanEscalationDetector`:**
    *   Correctly identifies all-rejected scenarios.
    *   Correctly identifies not-all-rejected scenarios.
    *   Logs to `plan_escalation_log.json` with correct schema and content.
    *   Triggers fallback (mocked) correctly based on configuration.
*   **Integration Test (`scripts/run_escalation_check.py`):**
    *   An end-to-end test for a `loop_id` (e.g., `loop_0052`) designed to have all its plans rejected.
    *   Verify the creation of `plan_escalation_log.json` entry.
    *   Verify fallback attempt if configured.

This design provides a clear path for implementing the escalation and fallback logic for Batch 27.3.
