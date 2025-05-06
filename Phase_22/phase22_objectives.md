## Phase 22: Agent Archetypes, Complexity Budgeting & Schema Proposals

This document outlines the objectives, required files, and key tasks for Phase 22, based on the execution plan `batch_22_execution_plan.locked (2).json`.

### Batch 22.0: Define Archetypes & Introduce Complexity Budget

**Objective:** Define loop archetypes and initialize the complexity budget surface.

**Key Tasks & Requirements:**
1.  **Dependency Check:** Ensure batch 16.1 and 21.1 are `verified: true` in the execution plan. (Manual check for now, will be part of batch setup).
2.  **Define Archetypes:**
    *   Define loop archetypes (e.g., Explore, Optimize, Refactor, etc.).
    *   Define classification criteria for these archetypes.
    *   Document these definitions (e.g., in `phase22_schema_surface_identification.md` or a dedicated archetypes document).
3.  **Build Complexity Budget Surface:**
    *   Create schema file: `app/schemas/complexity_budget.schema.json`.
    *   Create memory surface file: `app/memory/complexity_budget.json`.
    *   Define initial budget allocations within `complexity_budget.json`.
4.  **Functional Validation:**
    *   Verify archetype definitions are documented.
    *   Verify complexity budget surface and schema are created and initialized.
5.  **Log Wiring & Validate:** Follow standard procedures for creating/updating:
    *   `/home/ubuntu/wiring_manifest.updated_phase22_36.json`
    *   `/home/ubuntu/file_tree.updated_post_phase36.json`
    *   `/home/ubuntu/promethios_file_tree_plan.v3.1.5_runtime_synced.json`
    *   Adhere to CRITICAL FILE HANDLING INSTRUCTIONS for these files.
6.  **Update Status:** If validation succeeds, set `verified: true` for batch 22.0 in the execution plan.

**Components to Build or Verify:**
*   `app/memory/complexity_budget.json`
*   `app/schemas/complexity_budget.schema.json`
*   Documentation for loop archetypes.

**Expected Artifacts (for Batch 22.0):**
*   `/home/ubuntu/personal-ai-agent/app/memory/complexity_budget.json` (entire file updated)
*   `/home/ubuntu/personal-ai-agent/app/schemas/complexity_budget.schema.json`
*   `/home/ubuntu/wiring_manifest.updated_phase22_36.json` (entire file updated)
*   `/home/ubuntu/file_tree.updated_post_phase36.json` (entire file updated)
*   `/home/ubuntu/promethios_file_tree_plan.v3.1.5_runtime_synced.json` (entire file updated)

### Batch 22.1: Implement Archetype Classifier & Activate Complexity Budgeting Influence

(Details to be extracted and added as Batch 22.0 progresses)

### Batch 22.2: Implement Schema Change Proposal Mechanism

(Details to be extracted and added as Batch 22.1 progresses)

