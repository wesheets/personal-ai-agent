# Agent Debug & Cognition Tracker Suite Implementation

## Tasks
- [x] Step 1: Confirm `debug_tracker.md` and `debug_logger.py` from the previous task are active.

- [x] Step 2: Create `/api/orchestrator/consult` route
  - [x] Add `consult.py` route file
  - [x] Implement InstructionSchema handling
  - [x] Trigger agent tool.run() logic
  - [x] Write outputs to memory
  - [x] Write reflection tagged to goal
  - [x] Return appropriate status

- [x] Step 3: Create `/modules/instruction_validator.py`
  - [x] Implement validation of expected outputs
  - [x] Return "complete" or "failed" status
  - [x] Log validation results

- [x] Step 4: Create stubs
  - [x] Create `agent_tool_runner.py`
  - [x] Create `agent_reflection.py`
  - [x] Create `extract_outputs_from_memory` function

- [x] Step 5: Enhance `/tests/run_debug_sequence.py`
  - [x] Add test for sample instruction to HAL
  - [x] Log response and memory to debug_tracker.md

- [x] Step 6: Wire `log_test_result()` into components
  - [x] Agent tool execution step
  - [x] Reflection writing step
  - [x] Instruction validation result
  - [x] Failure/exception traces

- [ ] Step 7: Push to branch `feature/phase-11-tracker`
  - [ ] Create branch
  - [ ] Commit changes
  - [ ] Push to GitHub
  - [ ] Notify when ready
