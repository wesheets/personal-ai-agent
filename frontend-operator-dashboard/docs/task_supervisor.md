# Task Supervisor Module

## Overview

The Task Supervisor Module provides centralized monitoring for all agent activities, preventing runaway execution, detecting agents exceeding system caps, logging structured audit events, and enforcing emergency halts. This is the backbone of the Promethios Security Framework v3.

## Core Responsibilities

| Action                            | Behavior                                                           |
| --------------------------------- | ------------------------------------------------------------------ |
| 🌀 Loop exceeded                  | Log warning, halt agent, tag memory                                |
| 🧠 Delegation exceeds depth       | Deny + log                                                         |
| 🪞 Reflection recursion triggered | Warn + pause task thread                                           |
| 🛑 lockdown_mode == true          | Halt ALL agent activity, return structured error                   |
| 📊 Log all events                 | Structured to task_log.jsonl or memory (memory_type: system_alert) |

## Functions

### monitor_loop(task_id: str, loop_count: int)

Monitors loop count for a task and halts if it exceeds the maximum.

**Parameters:**

- `task_id` (str): The ID of the task to monitor
- `loop_count` (int): The current loop count

**Returns:**

- Dict with status, reason, and event details

**Example:**

```python
result = monitor_loop("task-123", 2)
if result["status"] != "ok":
    # Handle halted task
    print(f"Task halted: {result['reason']}")
```

### monitor_delegation(agent_id: str, delegation_depth: int)

Monitors delegation depth for an agent and halts if it exceeds the maximum.

**Parameters:**

- `agent_id` (str): The ID of the agent to monitor
- `delegation_depth` (int): The current delegation depth

**Returns:**

- Dict with status, reason, and event details

**Example:**

```python
result = monitor_delegation("agent-456", 1)
if result["status"] != "ok":
    # Handle halted delegation
    print(f"Delegation halted: {result['reason']}")
```

### monitor_reflection(agent_id: str, reflection_count: int)

Monitors reflection recursion for an agent and warns if it shows signs of recursion.

**Parameters:**

- `agent_id` (str): The ID of the agent to monitor
- `reflection_count` (int): The current reflection count

**Returns:**

- Dict with status, reason, and event details

**Example:**

```python
result = monitor_reflection("agent-789", 2)
if result["status"] != "ok":
    # Handle warned reflection
    print(f"Reflection warned: {result['reason']}")
```

### halt_task(task_id_or_agent: str, reason: str)

Halts a task or agent due to a supervision violation.

**Parameters:**

- `task_id_or_agent` (str): The ID of the task or agent to halt
- `reason` (str): The reason for halting the task

**Returns:**

- Dict with status, task_id_or_agent, reason, timestamp, and halt_id

**Example:**

```python
result = halt_task("task-123", "manual_halt")
print(f"Task halted: {result['halt_id']}")
```

### log_supervision_event(event: Dict)

Logs a supervision event to the task log file and console.

**Parameters:**

- `event` (Dict): The event to log

**Example:**

```python
event = {
    "event_type": "custom_event",
    "risk_level": "medium",
    "reason": "Custom monitoring event"
}
log_supervision_event(event)
```

### get_supervision_status()

Gets the current status of the task supervision system.

**Returns:**

- Dict with status, lockdown_mode, system_caps, event_counts, log_file, and timestamp

**Example:**

```python
status = get_supervision_status()
print(f"Supervision status: {status['status']}")
print(f"Event counts: {status['event_counts']}")
```

## Event Types

The Task Supervisor logs the following event types:

| Event Type                | Description                                   | Risk Level |
| ------------------------- | --------------------------------------------- | ---------- |
| loop_monitored            | Normal loop monitoring                        | low/medium |
| loop_exceeded             | Loop count exceeds maximum                    | high       |
| delegation_monitored      | Normal delegation monitoring                  | low/medium |
| delegation_depth_exceeded | Delegation depth exceeds maximum              | high       |
| reflection_monitored      | Normal reflection monitoring                  | low/medium |
| reflection_recursion      | Reflection count indicates possible recursion | high       |
| task_halted               | Task or agent halted due to violation         | high       |
| lockdown_enforced         | Global lockdown mode active                   | critical   |

## JSON Structure for Logs

Events are logged to `task_log.jsonl` in the following format:

```json
{
  "timestamp": "2025-04-11T21:00:00.000Z",
  "event_type": "loop_exceeded",
  "task_id": "task-123",
  "loop_count": 4,
  "max_loops": 3,
  "risk_level": "high",
  "reason": "Loop count 4 exceeds maximum 3",
  "event_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Error Response Examples

### Loop Exceeded

```json
{
  "status": "error",
  "reason": "loop_exceeded",
  "loop_count": 4,
  "task_id": "task-123",
  "event": {
    "timestamp": "2025-04-11T21:00:00.000Z",
    "event_type": "loop_exceeded",
    "task_id": "task-123",
    "loop_count": 4,
    "max_loops": 3,
    "risk_level": "high",
    "reason": "Loop count 4 exceeds maximum 3"
  }
}
```

### Delegation Depth Exceeded

```json
{
  "status": "error",
  "reason": "delegation_depth_exceeded",
  "delegation_depth": 3,
  "agent_id": "agent-456",
  "event": {
    "timestamp": "2025-04-11T21:00:00.000Z",
    "event_type": "delegation_depth_exceeded",
    "agent_id": "agent-456",
    "delegation_depth": 3,
    "max_depth": 2,
    "risk_level": "high",
    "reason": "Delegation depth 3 exceeds maximum 2"
  }
}
```

### Lockdown Mode Active

```json
{
  "status": "error",
  "reason": "lockdown_mode_active",
  "task_id": "task-123",
  "event": {
    "timestamp": "2025-04-11T21:00:00.000Z",
    "event_type": "lockdown_enforced",
    "task_id": "task-123",
    "risk_level": "critical",
    "reason": "Global lockdown mode active"
  }
}
```

## Enabling/Disabling Logs or Escalations

### Logging Configuration

The Task Supervisor logs events to both the console and a file. You can configure the logging level in your application's logging configuration:

```python
import logging
logging.getLogger("app.modules.task_supervisor").setLevel(logging.INFO)  # or DEBUG, WARNING, ERROR
```

### Disabling Memory Integration

If you want to disable writing events to memory, you can modify the `log_supervision_event` function to skip memory writing:

```python
# In task_supervisor.py
def log_supervision_event(event: Dict[str, Any], write_to_memory: bool = True):
    # ... existing code ...

    # Write to memory store if available and enabled
    if write_to_memory and event.get("risk_level") in ["medium", "high", "critical"]:
        try:
            from app.modules.memory_writer import write_memory
            # ... memory writing code ...
        except Exception as e:
            logger.error(f"Failed to write supervision event to memory: {str(e)}")
```

### Lockdown Mode

The global `lockdown_mode` flag can be set to `True` to halt all agent activity. This will be imported from `lockdown_mode.py` in a future update, but for now it's set to `False` by default.

## Integration Points

The Task Supervisor is integrated with the following modules:

1. **Loop Module** (`/loop`): Calls `monitor_loop()` before executing a loop
2. **Delegate Module** (`/delegate`): Calls `monitor_delegation()` before delegating a task
3. **Reflect Module** (`/reflect`): Calls `monitor_reflection()` before generating a reflection
4. **System Status** (`/system/status`): Includes supervision status for debugging

## System Caps

The Task Supervisor enforces the following system caps:

- `max_loops_per_task`: Maximum number of loops allowed per task (default: 3)
- `max_delegation_depth`: Maximum delegation depth allowed (default: 2)

These caps are defined in `config/system_caps.json` and can be modified to adjust the system's behavior.
