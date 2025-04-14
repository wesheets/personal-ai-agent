# Agent Debug & Cognition Tracker Suite Documentation

## Overview
The Agent Debug & Cognition Tracker Suite provides a comprehensive diagnostic toolkit for real-time tracking of agent instructions, tool usage, reflection, output validation, and retry logic. This system enables rapid testing of Phase 11.0–11.7 agent cognition without requiring a UI.

## Components

### 1. Debug Tracker and Logger
- `logs/debug_tracker.md`: Markdown file that tracks test status, agent routes, and results in a table format
- `src/utils/debug_logger.py`: Utility for logging test results with timestamps, modules, endpoints, status, and notes

### 2. Orchestrator Consult Route
- `app/api/orchestrator/consult.py`: API route that accepts an InstructionSchema with agent, goal, expected outputs, and checkpoints
- Triggers agent tool execution, writes outputs to memory, generates reflections, and validates results

### 3. Instruction Validator
- `app/modules/instruction_validator.py`: Module that validates whether agent memory includes all expected outputs
- Returns "complete" or "failed" status based on validation results
- Includes extract_outputs_from_memory function to retrieve agent outputs

### 4. Agent Tool Runner and Reflection
- `app/modules/agent_tool_runner.py`: Module for executing agent tools based on goals
- `app/modules/agent_reflection.py`: Module for generating reflections based on agent tool results

### 5. Test Script
- `tests/run_debug_sequence.py`: Script that tests all critical routes including the new orchestrator/consult route
- Logs responses and memory to debug_tracker.md

## Usage

### Testing Agent Cognition
To test agent cognition, send a POST request to `/api/orchestrator/consult` with the following payload:

```json
{
  "agent": "hal",
  "goal": "Write POST /login route for FastAPI",
  "expected_outputs": ["login.route", "login.handler"],
  "checkpoints": ["reflection"]
}
```

### Running Debug Sequence
To run the debug sequence test script:

```bash
cd /path/to/project
python tests/run_debug_sequence.py
```

Check `logs/debug_tracker.md` for detailed test results.

## Integration Points
The debug logging system is integrated at the following points:
- Agent tool execution steps
- Reflection writing steps
- Instruction validation results
- Failure and exception traces

## Expected Outcomes
This system allows full backend testing of Phase 11 autonomy:
- Instruction schema execution
- Memory logging
- Reflection tagging
- Output validation
- Retry loops (coming in Phase 11.3)

The toolkit confirms schema-compliant agent cognition without requiring a UI.
