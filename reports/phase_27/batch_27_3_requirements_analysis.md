# Batch 27.3: Escalation & Fallback Logic - Requirements Analysis

Date: 2025-05-09

## 1. Introduction

This document outlines the requirements for Batch 27.3, which focuses on implementing escalation and fallback logic within the agent's planning system. This functionality is crucial for handling scenarios where all proposed plans are rejected by the governance mechanisms (emotion, trust, invariants), ensuring the agent can either alert an operator or attempt to recover by generating alternative plans.

## 2. Objectives

As provided by the user, the core objectives for Batch 27.3 are:

1.  **Detect All-Plans-Rejected Scenarios:** The system must be able to identify when all candidate plans generated for a specific loop have been rejected by the `PlanRejector` component (from Batch 27.2).
2.  **Log Escalations:** When an all-plans-rejected scenario is detected, an entry must be logged to a new file named `plan_escalation_log.json`. This log entry must include:
    *   `loop_id`: The identifier of the loop for which plans were rejected.
    *   `escalation_reason`: A description of why the escalation occurred (e.g., "All candidate plans rejected by governance thresholds").
    *   `rejected_plan_ids`: A list of all plan IDs that were rejected for this loop.
    *   `recommended_action` or `operator_alert_flag`: Indication of the next step, which could be a system-recommended action (like triggering fallback) or a flag indicating an operator needs to be alerted.
    *   `timestamp`: The UTC timestamp of when the escalation was logged.
3.  **Schema Conformance for Escalation Log:** The `plan_escalation_log.json` file must conform to a newly defined JSON schema (`plan_escalation_log.schema.json`).
4.  **Implement Fallback Logic (Conditional):** If configured (e.g., via a flag or configuration setting), the system should trigger a fallback mechanism. An example of fallback logic is to regenerate plans, potentially with adjusted weights or parameters that might lead to more acceptable plans.
5.  **Update Manifests:** All relevant project manifests (`wiring_manifest.json`, `file_tree.json`, `file_tree_plan.json`) must be updated to reflect the new components, data surfaces, and schemas introduced in this batch.
6.  **Testing:** The escalation and fallback logic must be tested thoroughly. This includes using a loop ID like `loop_0052` (or a similar loop designed to trigger multiple plan rejections) to verify the rejection detection and subsequent escalation/fallback processes.
7.  **Operator Review:** Upon completion of Batch 27.3, an operator review is required before proceeding to Phase 28.

## 3. Functional Requirements

Based on the objectives, the following functional requirements are derived:

### FR1: Escalation Detection Module
*   **FR1.1:** The system shall include a module/component (e.g., `PlanEscalationDetector`) that monitors the outcomes of plan evaluations for a given `loop_id`.
*   **FR1.2:** This module must be able to determine if all candidate plans from a `multi_plan_comparison.json` set for a `loop_id` have been processed by `PlanRejector` and subsequently rejected.
*   **FR1.3:** Input to this module will likely be the `loop_id`, and it will need access to `multi_plan_comparison.json` (to know all plans considered) and `plan_rejection_log.json` (to see which ones were rejected).

### FR2: Escalation Logging
*   **FR2.1:** Upon detecting an all-plans-rejected scenario, the `PlanEscalationDetector` (or a related component) shall create a structured log entry.
*   **FR2.2:** The log entry must contain all fields specified in Objective 2 (loop_id, escalation_reason, rejected_plan_ids, recommended_action/operator_alert_flag, timestamp).
*   **FR2.3:** The log entry shall be appended to `app/logs/plan_escalation_log.json`.
*   **FR2.4:** The `plan_escalation_log.json` file must be created if it doesn't exist.

### FR3: Escalation Log Schema
*   **FR3.1:** A JSON schema file, `app/schemas/plan_escalation_log.schema.json`, shall be created.
*   **FR3.2:** This schema must define the structure, data types, and constraints for entries in `plan_escalation_log.json`.

### FR4: Fallback Logic Module (Configurable)
*   **FR4.1:** The system shall include a module/component for fallback logic (e.g., `FallbackPlanner` or an extension to `PlanGenerator`).
*   **FR4.2:** Activation of this fallback logic must be configurable (e.g., a global setting or a parameter passed during the escalation process).
*   **FR4.3:** If triggered, the fallback logic should attempt to generate new plans. This might involve:
    *   Using different generation parameters.
    *   Adjusting weights for plan evaluation criteria (if the plan generator uses such weights).
    *   Employing a different planning strategy.
*   **FR4.4:** The specifics of the fallback plan generation (e.g., "regenerate plans with adjusted weights") need to be defined during the design phase. For this batch, a simple mechanism to indicate a retry or a call to regenerate might be sufficient, with the actual adjustment logic being basic or a placeholder for future enhancement.

### FR5: Integration
*   **FR5.1:** The new components (`PlanEscalationDetector`, fallback mechanism) must be integrated into the main agent loop or control flow.
*   **FR5.2:** The `PlanEscalationDetector` should likely be invoked after the `PlanSelector` and `PlanRejector` have processed all plans for a loop.

## 4. Non-Functional Requirements

*   **NFR1: Modularity:** Components should be designed in a modular way for easier testing and maintenance.
*   **NFR2: Configurability:** Fallback logic activation should be configurable.
*   **NFR3: Testability:** All new logic must be highly testable, with clear test cases for rejection detection, escalation logging, and fallback triggering.
*   **NFR4: Clarity:** Log messages and escalation reasons should be clear and informative.

## 5. Data Requirements

*   **Input Data:**
    *   `app/logs/multi_plan_comparison.json`: To identify all candidate plans for a loop.
    *   `app/logs/plan_rejection_log.json`: To identify which plans were rejected.
    *   `loop_id`: To scope the detection and logging.
    *   Configuration for fallback logic activation.
*   **Output Data:**
    *   `app/logs/plan_escalation_log.json`: The primary output log file.
    *   Potentially, new plan proposals if fallback logic is triggered and successfully generates them (this might feed back into `multi_plan_comparison.json` for a subsequent loop or a special re-evaluation cycle).

## 6. Constraints and Assumptions

*   **C1:** The `PlanRejector` component from Batch 27.2 is assumed to be functional and correctly logs rejections.
*   **C2:** The `multi_plan_comparison.json` format is stable and provides necessary plan details.
*   **A1:** For this batch, the "adjusted weights" for fallback plan regeneration can be a simplified mechanism or a placeholder for more complex future logic.
*   **A2:** The primary focus is on detection, logging the escalation, and having a hook for fallback, rather than an exhaustive implementation of diverse fallback strategies.

## 7. Out of Scope for Batch 27.3

*   Complex, adaptive fallback strategies beyond a basic regeneration trigger.
*   User interface for managing escalations or configuring fallback parameters (beyond simple configuration files).
*   Real-time operator notification systems (the `operator_alert_flag` is a log-based indicator).

This analysis will serve as the foundation for the design and implementation of Batch 27.3.
