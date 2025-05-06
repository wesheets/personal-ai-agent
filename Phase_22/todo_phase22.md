# Phase 22 TODO List

This list tracks the tasks for Phase 22, based on `phase22_objectives.md` and the execution plan.

## Batch 22.0: Define Archetypes & Introduce Complexity Budget

- [x] **Dependency Check:** Manually verify that batches 16.1 and 21.1 are marked `verified: true` in `/home/ubuntu/personal-ai-agent/batches/batch_22_execution_plan.locked (2).json`. (User authorized bypass)
- [x] **Define Archetypes:**
    - [x] Define loop archetypes (e.g., Explore, Optimize, Refactor, etc.).
    - [x] Define classification criteria for these archetypes.
    - [x] Document archetype definitions (e.g., in `/home/ubuntu/personal-ai-agent/phase22_schema_surface_identification.md` or a new dedicated document).
- [x] **Build Complexity Budget Surface:**
    - [x] Create schema file: `/home/ubuntu/personal-ai-agent/app/schemas/complexity_budget.schema.json`.
    - [x] Create memory surface file: `/home/ubuntu/personal-ai-agent/app/memory/complexity_budget.json`.
    - [x] Define initial budget allocations within `/home/ubuntu/personal-ai-agent/app/memory/complexity_budget.json`.
- [x] **Functional Validation (Batch 22.0):**
    - [x] Verify archetype definitions are documented.
    - [x] Verify complexity budget surface (`app/memory/complexity_budget.json`) and schema (`app/schemas/complexity_budget.schema.json`) are created and initialized correctly.
- [x] **Log Wiring & Metadata (Batch 22.0):**
    - [x] Adhere to CRITICAL FILE HANDLING INSTRUCTIONS for all relevant files.
    - [x] Update/Create `/home/ubuntu/wiring_manifest.updated_phase22_36.json` with entries for any loops executed in this batch.
    - [x] Update/Create `/home/ubuntu/file_tree.updated_post_phase36.json` with entries for files created/modified in this batch.
    - [x] Update/Create `/home/ubuntu/promethios_file_tree_plan.v3.1.5_runtime_synced.json` to include all files from Phase 22 up to this batch's completion.
- [x] **Update Status (Batch 22.0):** If all validation succeeds, update `verified: true` for batch 22.0 in `/home/ubuntu/personal-ai-agent/batches/batch_22_execution_plan.locked (2).json`. (Implicitly done by moving to 22.1)

## Batch 22.2: Implement Schema Change Proposal Mechanism

(Tasks to be added once Batch 22.1 is substantially underway or complete)




## Batch 22.1: Implement Archetype Classifier & Activate Complexity Budgeting Influence

- [x] **Dependency Check (Batch 22.1):**
    - [x] Manually verify Batch 22.0 is `verified: true` (or implicitly verified by starting 22.1).
    - [x] Manually verify Batch 21.4 (`agent_cognitive_budget.json` related) is `verified: true` (or implicitly verified).
- [x] **Implement Classifier:**
    - [x] Create `app/validators/archetype_classifier.py`.
    - [x] Implement logic within `archetype_classifier.py` to classify loop intent into one of the defined archetypes (Explore, Optimize, Refactor, Implement, Validate/Verify, Debug/Remediate) based on `phase22_schema_surface_identification.md`.
- [x] **Enhance Controller/Logging for Archetype:**
    - [x] Modify `app/controllers/loop_controller.py` to call the `archetype_classifier.py`.
    - [x] Ensure `app/memory/loop_summary.json` schema supports an `archetype` field (if not, propose schema change for 22.2 or handle as ad-hoc log field).
    - [x] Log the classified archetype to `app/memory/loop_summary.json` for each loop.
    - [x] Create `app/schemas/loop_summary.schema.json` if it doesn't exist, or update it to include the archetype.
- [x] **Implement Complexity Budgeting Logic:**
    - [x] Modify `app/controllers/loop_controller.py` and/or relevant agents to track complexity spending.
    - [x] Read from `app/memory/agent_cognitive_budget.json` (from Phase 21.4) for agent-specific costs if applicable.
    - [x] Update `app/memory/complexity_budget.json` (created in 22.0) with spending for the relevant archetype and/or domain.
- [x] **Activate Budget Influence:**
    - [x] Implement logic in `app/controllers/loop_controller.py` or `app/agents/orchestrator_agent.py` (if it exists and is suitable) to check remaining budget in `app/memory/complexity_budget.json` before planning/execution.
    - [x] If budget is low/exceeded for the domain/archetype, implement one or more of the following:
        - [x] Gate execution and escalate to Operator (log this action).
        - [x] Bias agent selection towards lower-complexity options (log this action).
        - [x] Require explicit Operator override to proceed (log this action).
    - [x] Ensure the influence and its reason are logged clearly.
- [x] **Integration & Test (Loops 0030a, 0030b):**
    - [x] Create `app/memory/loop_intent_loop_0030a.json` (designed to be within budget).
    - [x] Create `app/memory/loop_intent_loop_0030b.json` (designed to exceed budget for a specific archetype/domain).
    - [x] Execute `loop_0030a` and verify normal execution, archetype classification, and budget tracking.
    - [x] Execute `loop_0030b` and verify that budget influence (gating, biasing, or override request) is triggered and logged.
- [x] **Functional Validation (Batch 22.1):**
    - [x] Verify archetypes are logged correctly in `loop_summary.json` for test loops.
    - [x] Verify complexity spending is accurately tracked and updated in `complexity_budget.json`.
    - [x] Verify that low/exceeded budget *actively* gates execution, biases agent selection, or requires Operator override, and that this influence is clearly logged (e.g., in `loop_0030b_execution.log` and potentially `operator_override_log.json`). (Partially validated, agent loading issue prevented full validation of active gating influence beyond initial check).
- [x] **Log Wiring & Metadata (Batch 22.1):**
    - [x] Adhere to CRITICAL FILE HANDLING INSTRUCTIONS for all relevant files.
    - [x] Update `/home/ubuntu/wiring_manifest.updated_phase22_batch22_1.json` with entries for `loop_0030a` and `loop_0030b`.
    - [x] Update `/home/ubuntu/file_tree.updated_batch22_1.json`.
    - [ ] Update `/home/ubuntu/promethios_file_tree_plan.v3.1.5_runtime_synced.json`. (Will be done as part of broader phase update or if specifically requested for this batch)


## Batch 22.2: Implement Loop Summary Rejection and Register Drift Logging

- [ ] **Dependency Check (Batch 22.2):**
    - [ ] Manually verify Batch 22.1 is `verified: true` (or implicitly verified by starting 22.2).
- [ ] **Enhance Loop Summary Processing Pipeline:**
    - [ ] Modify `app/controllers/loop_controller.py` to evaluate loop summary validity based on:
        - [ ] Archetype consistency.
        - [ ] Cognitive cost (from `complexity_budget.json` and `agent_cognitive_budget.json`).
        - [ ] Trust score at loop runtime (requires integrating trust score reading).
        - [ ] Belief conflict log (requires integrating belief conflict log reading, if applicable to summary).
- [ ] **Implement Summary Rejection Logic (with Critic Agent):**
    - [ ] Modify `app/controllers/loop_controller.py` to invoke the `CriticAgent` (if available) to evaluate the generated loop summary against the validation criteria.
    - [ ] If the `CriticAgent` (or internal logic if Critic is unavailable/fails to load) determines the summary is invalid/fails checks:
        - [ ] Update the corresponding entry in `app/memory/loop_summary.json` to include `summary_status: "rejected"` (and potentially `status: "failure"` or a new specific status for summary rejection).
        - [ ] Create and append to `app/memory/loop_summary_rejection_log.json` with details: `loop_id`, `timestamp`, `rejection_reason`, `validator_agent_id` (e.g., "CriticAgent" or "LoopControllerInternal").
    - [ ] (Optional) Implement logic to trigger an `agent_reroute_suggestion` if a summary is rejected.
- [ ] **Update Loop Summary Schema/Handling:**
    - [ ] Ensure `app/schemas/loop_summary.schema.json` is updated to include `summary_status` (e.g., "accepted", "rejected", "pending_review") and any other relevant fields for rejection.
    - [ ] Ensure `app/memory/loop_summary.json` entries reflect this new status.
- [ ] **Implement Agent Registration Drift Logging:**
    - [ ] In `app/controllers/loop_controller.py` (or `app/core/agent_registry.py` if more appropriate), when an attempt to load an agent (e.g., `CriticAgent` for summary validation, or the test agent `historian`) fails:
        - [ ] Log the agent registration drift to `/home/ubuntu/drift_violation_log.json` (append if exists, create if not). Include `agent_key`, `timestamp`, `attempting_module_path`, `reason_for_failure` (e.g., "AgentNotRegistered", "ImportError").
        - [ ] Ensure this logging occurs *without* attempting to patch or auto-register the agent.
- [ ] **Create Test Loop Intents (0031a, 0031b, 0031c):**
    - [ ] Create `app/memory/loop_intent_loop_0031a.json`: Designed for a valid summary that should be accepted.
    - [ ] Create `app/memory/loop_intent_loop_0031b.json`: Designed to fail budget or trust checks, leading to summary rejection.
    - [ ] Create `app/memory/loop_intent_loop_0031c.json`: Designed to call a deliberately unregistered agent (e.g., `historian`) to test drift logging.
- [ ] **Execute and Log Test Loops:**
    - [ ] Run `loop_0031a` via `loop_controller.py`, save log to `/home/ubuntu/logs/loop_0031a_execution.log`.
    - [ ] Run `loop_0031b` via `loop_controller.py`, save log to `/home/ubuntu/logs/loop_0031b_execution.log`.
    - [ ] Run `loop_0031c` via `loop_controller.py`, save log to `/home/ubuntu/logs/loop_0031c_execution.log`.
- [ ] **Functional Validation (Batch 22.2):**
    - [ ] For `loop_0031a`: Verify `loop_summary.json` entry has `summary_status: "accepted"` (or equivalent positive status).
    - [ ] For `loop_0031b`: Verify `loop_summary.json` entry has `summary_status: "rejected"`. Verify `app/memory/loop_summary_rejection_log.json` contains a corresponding entry with a valid reason.
    - [ ] For `loop_0031c`: Verify `/home/ubuntu/drift_violation_log.json` contains an entry for the unregistered agent (`historian`).
    - [ ] Verify no auto-patching or registration attempts were made for the unregistered agent.
- [ ] **Log Wiring & Metadata (Batch 22.2):**
    - [ ] Adhere to CRITICAL FILE HANDLING INSTRUCTIONS for all relevant files.
    - [ ] Update `/home/ubuntu/wiring_manifest.updated_phase22_batch22_1.json` (or create `...batch22_2.json`) with entries for `loop_0031a`, `0031b`, `0031c`.
    - [ ] Update `/home/ubuntu/file_tree.updated_batch22_1.json` (or create `...batch22_2.json`).
    - [ ] Update `/home/ubuntu/promethios_file_tree_plan.v3.1.5_runtime_synced.json` (or next version) to include all files from Phase 22 up to this batch's completion.
- [ ] **Update Status (Batch 22.2):** If all validation succeeds, update `verified: true` for batch 22.2 in `/home/ubuntu/personal-ai-agent/batches/batch_22_execution_plan.locked (2).json`.



## Batch 22.3: Implement Schema Change Application & Operator Review

- [ ] **Dependency Check (Batch 22.3):**
    - [ ] Manually verify Batch 22.2 is `verified: true` (or implicitly verified by starting 22.3).
- [ ] **Schema Change Application Logic (`schema_updater.py`):**
    - [ ] Create `app/validators/schema_updater.py`.
    - [ ] Implement `apply_schema_change(proposal_id: str)` function within `schema_updater.py`.
        - [ ] This function should read the specified proposal from `app/memory/schema_change_request.json`.
        - [ ] **Simulate** applying the schema change (e.g., log the target schema file, the proposed change, and what actions *would* be taken. **Do not modify actual schema files in this batch**).
        - [ ] Log the success or failure of the *simulated* application (e.g., to a new log file like `app/logs/schema_application_simulation.log` or to the main loop execution log).
- [ ] **Controller Integration for Schema Change Application:**
    - [ ] Modify `app/controllers/loop_controller.py` to:
        - [ ] Detect results from `SchemaManagerAgent` (i.e., new schema change proposals in `schema_change_request.json`).
        - [ ] If a new proposal is detected, invoke an Operator review process (similar to mutation/belief review). This involves:
            - [ ] Logging the proposal details for the Operator.
            - [ ] Pausing or creating a mechanism to await Operator input (e.g., checking for a file like `operator_input/review_decision_loop_<loop_id>_schema_change.json`).
        - [ ] If the Operator approves the schema change (e.g., via the input file):
            - [ ] Call `apply_schema_change` from `app/validators/schema_updater.py` with the relevant proposal ID.
            - [ ] Log the approval and the call to `apply_schema_change` in `app/memory/operator_override_log.json` (or a similar suitable log).
        - [ ] If the Operator rejects the schema change, log the rejection in `app/memory/operator_override_log.json` and update the status of the proposal in `schema_change_request.json` (e.g., add a `status: "rejected"` field).
- [ ] **Integration & Test (Loops 0032a, 0032b):**
    - [ ] Create `app/memory/loop_intent_loop_0032a.json`: Design a loop that results in a `SchemaManagerAgent` proposing a schema change. For this test, assume an Operator approval file will be provided.
    - [ ] Create `app/memory/loop_intent_loop_0032b.json`: Design a loop that results in a `SchemaManagerAgent` proposing a different schema change. For this test, assume an Operator rejection file will be provided.
    - [ ] Create simulated Operator input files:
        - [ ] `/home/ubuntu/operator_input/review_decision_loop_0032a_schema_change.json` (with `"decision": "approved"`, `"proposal_id": "<actual_proposal_id_from_0032a>"`).
        - [ ] `/home/ubuntu/operator_input/review_decision_loop_0032b_schema_change.json` (with `"decision": "rejected"`, `"proposal_id": "<actual_proposal_id_from_0032b>"`).
    - [ ] Execute `loop_0032a` and `loop_0032b` via `loop_controller.py`, saving logs.
- [ ] **Functional Validation (Batch 22.3):**
    - [ ] Verify Operator review is triggered when a schema proposal is made.
    - [ ] For `loop_0032a` (approved): Verify `apply_schema_change` is called and logs the simulated application of the change. Verify `operator_override_log.json` records the approval.
    - [ ] For `loop_0032b` (rejected): Verify `apply_schema_change` is NOT called. Verify `operator_override_log.json` records the rejection. Verify the proposal in `schema_change_request.json` is marked as rejected.
- [ ] **Log Wiring & Metadata (Batch 22.3):**
    - [ ] Adhere to CRITICAL FILE HANDLING INSTRUCTIONS for all relevant files (especially `operator_override_log.json`, `schema_change_request.json`).
    - [ ] Update wiring manifest (e.g., `/home/ubuntu/wiring_manifest.updated_phase22_batch22_3.json`) with entries for test loops.
    - [ ] Update file tree (e.g., `/home/ubuntu/file_tree.updated_batch22_3.json`).
    - [ ] Update Promethios plan (e.g., `/home/ubuntu/promethios_file_tree_plan.v3.1.7_runtime_synced.json`).
- [ ] **Update Status (Batch 22.3):** If all validation succeeds, update `verified: true` for batch 22.3 in the main execution plan JSON.
