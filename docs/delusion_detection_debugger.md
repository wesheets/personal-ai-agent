# Delusion Detection and Debugger Agent

This documentation covers the implementation of two key modules for improving agent reliability and self-correction:

1. **Delusion Detection System**: Identifies when an agent is repeating previously failed approaches
2. **Debugger Agent**: Analyzes failures to determine root causes and suggest recovery paths

## Delusion Detection System

The Delusion Detection system prevents agents from repeatedly trying approaches that have already failed by:

- Generating plan hashes to identify similar plans
- Comparing current plans to previously rejected ones
- Injecting warnings when potential delusions are detected

### Key Components

- **Plan Hashing**: Generates unique fingerprints of plans based on their structure
- **Similarity Detection**: Uses bit-level comparison with non-linear scaling to identify similar plans
- **Warning Injection**: Adds alerts to memory when a plan resembles a previously failed one

### Usage

```python
from orchestrator.modules.delusion_detector import detect_plan_delusion, store_rejected_plan

# Check if current plan resembles previously failed plans
updated_memory = detect_plan_delusion(
    plan,
    loop_id,
    memory,
    similarity_threshold=0.85
)

# Store a failed plan for future reference
updated_memory = store_rejected_plan(
    plan,
    loop_id,
    failure_reason,
    memory
)
```

## Debugger Agent

The Debugger Agent helps diagnose and recover from failures by:

- Parsing failure logs to identify root causes
- Generating patch plans for recovery
- Creating detailed debugger reports with suggested fixes

### Key Components

- **Failure Log Parser**: Analyzes error messages to determine failure types
- **Patch Plan Generator**: Creates step-by-step recovery plans based on failure type
- **Agent Routing**: Determines which specialized agent should handle the failure
- **Memory Integration**: Stores failure reports for future reference

### Usage

```python
from agents.debugger_agent import debug_loop_failure

# Debug a loop failure and get recovery suggestions
updated_memory = debug_loop_failure(
    loop_id,
    failure_logs,
    memory,
    loop_context
)
```

## Loop Controller Integration

Both systems are integrated with the loop controller for seamless operation:

```python
from orchestrator.modules.loop_controller import handle_loop_execution, handle_loop_failure

# Check for delusions before executing a loop
execution_result = handle_loop_execution(
    plan,
    loop_id,
    memory,
    config
)

# Handle failures with debugging and plan registration
failure_result = handle_loop_failure(
    loop_id,
    failure_logs,
    plan,
    failure_reason,
    memory,
    config
)
```

## Configuration Options

Both systems support configuration options:

### Delusion Detection Configuration

```python
delusion_config = {
    "enabled": True,              # Enable/disable delusion detection
    "similarity_threshold": 0.85, # Threshold for considering plans similar
    "block_execution": False      # Whether to block execution of similar plans
}
```

### Debugger Agent Configuration

```python
debugger_config = {
    "enabled": True,        # Enable/disable debugger agent
    "auto_reroute": False   # Automatically reroute to suggested agent
}
```

## Schema Definitions

The implementation includes JSON schemas for standardizing data formats:

- `schemas/delusion_alert.schema.json`: Format for delusion warnings
- `schemas/debugger_report.schema.json`: Format for debugger reports

## Testing

Comprehensive unit tests are included for both modules:

- `tests/orchestrator/test_delusion_detector.py`: Tests for delusion detection
- `tests/agents/test_debugger_agent.py`: Tests for debugger agent

Run tests with:

```bash
python -m unittest tests/orchestrator/test_delusion_detector.py
python -m unittest tests/agents/test_debugger_agent.py
```
