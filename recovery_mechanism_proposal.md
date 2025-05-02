# Proposal: High-Level Recovery Mechanism

This document outlines a high-level strategy for handling failures during the Promethios bootstrap process, particularly for high-risk batches that involve code generation or modification.

**Core Principles:**

1.  **Fail Fast, Log Thoroughly:** Detect failures as early as possible (e.g., during validation steps) and log detailed context about the failure (batch ID, step, error message, component state).
2.  **Prioritize Stability:** Prevent a failed batch from corrupting the core system or preventing future execution attempts.
3.  **Operator Notification:** Ensure the operator is informed promptly about failures and the system's current state.
4.  **Attempted Automated Recovery (Optional/Future):** Explore possibilities for automated rollback or repair, potentially involving dedicated recovery logic or leveraging agents like `architect_agent.py`.
5.  **Manual Intervention Point:** Provide clear points for operator intervention and decision-making.

**Proposed Failure Handling Workflow:**

1.  **Failure Detection:**
    *   Validation steps (syntax check, linting, functional validation, unit tests) defined in the execution plan (as per `execution_plan_validation_proposal.md`) fail.
    *   Execution of generated/modified code results in a runtime crash or unhandled exception.
    *   The validation tool (`validate_functional_surface.py`) detects unexpected changes or inconsistencies after a batch execution.

2.  **Immediate Actions upon Failure:**
    *   **Halt Execution:** Stop the current batch processing immediately.
    *   **Log Failure Details:** Record comprehensive failure information in a dedicated error log (e.g., `/home/ubuntu/logs/bootstrap_errors.log`). Include:
        *   Timestamp
        *   Batch ID (e.g., 15.14)
        *   Failed Step (e.g., `post_build_validation.syntax_check`, `runtime_execution`)
        *   Component Involved
        *   Error Message / Stack Trace
        *   Relevant state information (if possible)
    *   **Mark Batch as Failed:** Update the `batch_15_execution_plan.json` to mark the current batch status explicitly as `failed` (instead of just `verified: false`). Add a `failure_reason` field.
        ```json
        "verified": false,
        "status": "failed", 
        "failure_reason": "Syntax check failed for app/agents/architect_agent.py",
        ```

3.  **State Management / Rollback (Initial Approach):**
    *   **No Automatic Rollback (Initially):** Given the complexity, automatic rollback is high-risk initially. The primary goal is to *prevent* the faulty code from being committed or integrated further.
    *   **Isolate Changes:** Ensure that failed changes within the workspace (`/home/ubuntu/personal-ai-agent/`) are not automatically pushed or merged. The proposed `commit_strategy` field in the execution plan helps manage this.
    *   **Rely on Version Control:** For manual recovery, rely on Git to discard faulty changes (`git checkout <file>`, `git reset --hard HEAD`).

4.  **Automated Recovery Attempt (Future Enhancement):**
    *   **Trigger Recovery Logic:** If a failure occurs, potentially trigger a dedicated recovery script or agent.
    *   **`architect_agent.py` Role:** As suggested, `architect_agent.py` could potentially be invoked to analyze the failure log and the faulty component. It might attempt to:
        *   Identify the root cause (based on error logs and code analysis).
        *   Suggest a fix or generate a patch.
        *   This requires `architect_agent.py` to be robust and capable of operating on potentially broken code.
    *   **Recovery Plan File:** Generating a `recovery_plan_trigger.json` or similar could signal the need for recovery and pass context to the recovery mechanism.

5.  **Operator Notification & Intervention:**
    *   **Notify Operator:** Send a clear notification to the operator via `message_ask_user` detailing the failure, the batch status, and the current state.
    *   **Provide Logs:** Attach relevant error logs.
    *   **Request Instructions:** Ask the operator how to proceed:
        *   Retry the batch (after manual fixes)?
        *   Skip the batch?
        *   Attempt automated recovery (if implemented)?
        *   Abort the bootstrap process?

**Recovery Strategy Summary:**

*   **Short-Term:** Focus on robust failure detection via enhanced validation, detailed logging, halting execution, marking the batch as failed in the plan, preventing faulty commits, and notifying the operator for manual intervention (likely involving Git commands to revert changes).
*   **Mid-Term:** Implement the proposed validation steps within the execution plan structure.
*   **Long-Term:** Explore automated recovery mechanisms, potentially using `architect_agent.py` or dedicated recovery scripts, triggered by failure events and guided by failure logs.

This approach prioritizes safety and operator control initially, while laying the groundwork for more automated recovery in the future.
