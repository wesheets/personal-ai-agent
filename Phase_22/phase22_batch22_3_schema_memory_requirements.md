# Phase 22, Batch 22.3: Schema and Memory Surface Requirements

**Batch ID:** 22.3
**Title:** Implement Schema Change Application & Operator Review
**Date Documented:** 2025-05-06

## 0. Introduction

This document outlines the schema surface and memory requirements for the implementation of Batch 22.3. This batch focuses on enabling Operator review and the (simulated) application of schema changes proposed by agents.

It assumes that the functionality for *proposing* schema changes (originally planned for Batch 22.2, involving `SchemaManagerAgent` and populating `schema_change_request.json`) is either already in place or will be implemented as a prerequisite for or concurrently with Batch 22.3 tasks that depend on it.

## 1. New Components for Schema Change Application & Review (Batch 22.3)

These components are to be newly created or significantly modified within Batch 22.3.

### 1.1. `app/validators/schema_updater.py` (New File)

*   **Purpose:** Contains the logic to process and simulate the application of an approved schema change proposal.
*   **Key Functions:**
    *   `apply_schema_change(proposal_id: str, schema_change_requests: list, operator_override_log: list) -> bool:`
        *   Reads the specified proposal by `proposal_id` from the `schema_change_requests` data (loaded from `app/memory/schema_change_request.json`).
        *   **Simulates** applying the schema change. This means it will log what changes *would* be made to the target schema file (e.g., adding a field, changing a type) but will **not** modify the actual schema file on disk in this batch.
        *   Logs the details of the simulation (target schema, proposed change, simulated actions) to a dedicated log or the main execution log (e.g., `app/logs/schema_application_simulation.log` or via standard Python logging).
        *   Updates the status of the proposal in `schema_change_requests` data to "applied_simulated".
        *   Returns `True` if simulation is successful, `False` otherwise.

### 1.2. `app/controllers/loop_controller.py` (Modifications)

*   **Purpose:** Integrate the schema change review and application workflow into the main loop.
*   **New Logic Sections:**
    *   **Detection of Schema Proposals:** Logic to check `schema_change_request.json` (or results from `SchemaManagerAgent`) for new proposals with status "pending_review".
    *   **Operator Review Invocation:**
        *   If a new proposal is found, log its details for the Operator.
        *   Implement a mechanism to await Operator input. This will involve checking for a specific file pattern, e.g., `/home/ubuntu/operator_input/review_decision_loop_<loop_id>_schema_change_<proposal_id>.json`.
    *   **Processing Operator Decision:**
        *   If an approval file is found:
            *   Call `schema_updater.apply_schema_change()` with the `proposal_id`.
            *   Log the approval event (including `proposal_id`, decision, loop_id) to `app/memory/operator_override_log.json`.
            *   Update the proposal's status in `schema_change_request.json` to "approved" before calling `apply_schema_change`, and then to "applied_simulated" by `apply_schema_change` itself.
        *   If a rejection file is found:
            *   Log the rejection event to `app/memory/operator_override_log.json`.
            *   Update the proposal's status in `schema_change_request.json` to "rejected".

### 1.3. Operator Input Files (New Pattern)

*   **Pattern:** `/home/ubuntu/operator_input/review_decision_loop_<loop_id>_schema_change_<proposal_id>.json`
*   **Purpose:** To provide Operator decisions (approve/reject) for schema change proposals.
*   **Expected JSON Structure:**
    ```json
    {
      "loop_id": "<loop_id_where_proposal_was_reviewed>",
      "proposal_id": "<unique_id_of_the_schema_proposal>",
      "decision": "approved" | "rejected",
      "operator_id": "<operator_identifier>", // Optional
      "justification": "<reason_for_decision>" // Optional
    }
    ```

### 1.4. Simulated Schema Application Log (Optional New Log File)

*   **Path:** `app/logs/schema_application_simulation.log` (or integrated into main execution logs).
*   **Purpose:** To record the details of simulated schema change applications performed by `schema_updater.py`.
*   **Potential Content (per entry):** `timestamp`, `proposal_id`, `target_schema_path`, `simulated_actions_description`, `status` ("success"/"failure").

## 2. Prerequisite Components for Schema Proposal (Assumed from original Batch 22.2 scope)

These components are necessary for Batch 22.3 to function. If the original scope of Batch 22.2 (Schema Change Proposal Mechanism) was altered or not fully implemented, these will need to be addressed.

### 2.1. `app/memory/schema_change_request.json` (Memory Surface)

*   **Purpose:** Stores formal proposals for schema changes made by agents or the Operator.
*   **Status:** Needs to be created if not already done. Batch 22.3 will read from and update the status of entries in this file.
*   **Associated Schema:** `app/schemas/schema_change_request.schema.json`
*   **Key Fields (per proposal entry):**
    *   `proposal_id`: Unique identifier for the proposal (e.g., UUID).
    *   `timestamp`: ISO 8601 timestamp of proposal creation.
    *   `proposing_agent_id`: Identifier of the agent making the proposal (e.g., "SchemaManagerAgent", "ArchitectAgent").
    *   `target_schema_path`: Filesystem path to the schema file to be changed (e.g., "app/schemas/belief_surface.schema.json").
    *   `proposed_change_description`: A clear description of the change. This could be a natural language description, a JSON Patch object, or a specific internal format.
    *   `justification`: Reason for the proposed change.
    *   `potential_impact`: Analysis of the potential impact of the change.
    *   `status`: Current status of the proposal. Enum: "pending_review", "approved", "rejected", "applied_simulated", "applied_live", "failed_simulation", "failed_application". (Batch 22.3 will primarily use "pending_review", "approved", "rejected", "applied_simulated").
    *   `loop_id_proposed`: The loop ID in which this proposal was generated.
    *   `loop_id_reviewed`: The loop ID in which this proposal was reviewed by the operator (populated by Batch 22.3).
    *   `operator_decision_details`: (Optional) Object to store operator's justification if provided.

### 2.2. `app/agents/schema_manager_agent.py` (or modified `ArchitectAgent`)

*   **Purpose:** Responsible for identifying the need for schema changes, formulating proposals, and saving them to `app/memory/schema_change_request.json` with status "pending_review".
*   **Status:** Needs to be created and functional if not already done.
*   **Expected Behavior:** This agent's output (a new entry in `schema_change_request.json`) is a trigger for the Batch 22.3 review workflow in `loop_controller.py`.

## 3. Existing Memory Surfaces to be Utilized/Modified

### 3.1. `app/memory/operator_override_log.json`

*   **Purpose:** To log all Operator decisions, including those related to schema change proposals.
*   **Modifications for Batch 22.3:** Ensure entries for schema change reviews can be accommodated.
*   **Required Fields for Schema Change Review Events (example):**
    *   `event_id`: Unique ID for the log entry.
    *   `timestamp`: ISO 8601 timestamp.
    *   `loop_id`: Loop ID during which the review occurred.
    *   `event_type`: "schema_change_review".
    *   `proposal_id`: Identifier of the schema proposal being reviewed.
    *   `decision`: "approved" | "rejected".
    *   `operator_id`: Identifier of the Operator (if available).
    *   `justification`: Operator's reasoning (if provided).
    *   `details`: Object containing reference to the proposal or key aspects.

## 4. Critical File Handling Reminder

The following critical files, if modified or created by Batch 22.3, must adhere to the standard handling instructions (load full, append/merge conformantly, save entire complete file):
*   `app/memory/schema_change_request.json`
*   `app/memory/operator_override_log.json`
*   `app/memory/loop_summary.json` (if loop summaries are affected by this process)
*   Standard metadata files: `file_tree.json`, `promethios_file_tree_plan...json`, `wiring_manifest...json`.

This document will guide the design and implementation phases of Batch 22.3.
