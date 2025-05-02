# Proposal: Adding Validation Steps to batch_15_execution_plan.json

To incorporate more robust validation, especially for high-risk batches involving code generation or modification, we can enhance the structure of each batch definition in `batch_15_execution_plan.json`.

**Proposed New/Modified Fields:**

1.  **`risk_level`**: (Optional) A field to categorize the batch risk (e.g., `low`, `medium`, `high`). `high` could indicate code generation, modification of core components, or actions with potential side effects.
    ```json
    "risk_level": "high",
    ```

2.  **`pre_build_validation`**: (Optional) An array of validation steps to run *before* attempting to build or fetch the component. This could include checking tool availability or environment setup.
    ```json
    "pre_build_validation": [
      {"step": "check_tool", "tool_name": "python3.11"}
    ],
    ```

3.  **`post_build_validation`**: (Enhanced) Rename/repurpose `static_validation` and `functional_validation` within a more structured block. This block could reference steps defined in the `pre_commit_validation_policy.json`.
    ```json
    "post_build_validation": {
      "policy_ref": "pre_commit_validation_policy.json",
      "steps": [
        {"policy_step_ref": "syntax_check"},
        {"policy_step_ref": "linting", "optional": true},
        {"policy_step_ref": "stub_validation"} 
      ]
    },
    ```
    *Alternatively, instead of referencing an external policy, steps could be defined directly:* 
    ```json
    "post_build_validation": [
        {"step": "syntax_check_python", "command": "python3.11 -m py_compile <component_path>"},
        {"step": "functional_validation", "command": "python3.11 tools/validate_functional_surface.py --component <component_path>"}
    ],
    ```

4.  **`pre_push_validation`**: (New) An array of validation steps specifically designed to run *after* successful build and initial validation, but *before* any action that would persist the change (like a commit or PR trigger). This could include more comprehensive tests or checks.
    ```json
    "pre_push_validation": {
      "policy_ref": "pre_commit_validation_policy.json",
      "steps": [
        {"policy_step_ref": "unit_tests", "optional": true}
      ]
    },
    ```

5.  **`commit_strategy`**: (New) Defines how changes should be committed. Options could include `none` (default for low risk/stubs), `auto_commit` (for verified changes), `manual_review_required` (trigger PR or notification).
    ```json
    "commit_strategy": "manual_review_required", 
    ```

**Example Batch Snippet (High Risk):**

```json
{
  "batch": "15.14",
  "title": "Implement: architect_agent.py Logic",
  "phase": "Phase 2: Agent Implementation",
  "risk_level": "high",
  "prompt": "Objective: Implement core logic for architect_agent.py...",
  "components_to_build_or_verify": [
    "app/agents/architect_agent.py"
  ],
  "dependencies": ["15.13"],
  "pre_build_validation": [
      {"step": "check_tool", "tool_name": "python3.11"}
  ],
  "post_build_validation": {
      "policy_ref": "pre_commit_validation_policy.json",
      "steps": [
        {"policy_step_ref": "syntax_check"},
        {"policy_step_ref": "linting", "optional": true},
        {"policy_step_ref": "stub_validation"} 
      ]
  },
   "pre_push_validation": {
      "policy_ref": "pre_commit_validation_policy.json",
      "steps": [
        {"policy_step_ref": "unit_tests", "optional": true}
      ]
  },
  "commit_strategy": "manual_review_required",
  "verified": false
}
```

**Implementation Notes:**

*   The bootstrap execution loop (or a dedicated validation module) would need to interpret these new fields.
*   It would execute the specified validation commands/steps at the appropriate points in the batch lifecycle.
*   Failure at any mandatory validation step should halt the batch and trigger the defined recovery strategy.
*   Referencing an external policy (`pre_commit_validation_policy.json`) promotes consistency but requires the policy file to be maintained and accessible.

