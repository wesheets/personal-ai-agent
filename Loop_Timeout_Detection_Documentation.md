# Loop Timeout and Frozen Task Detection Documentation

## Overview

The Loop Timeout and Frozen Task Detection feature prevents agents from getting stuck mid-execution by detecting when a loop or agent runs longer than allowed, logging it, and halting further execution. This feature enhances system reliability by ensuring that agents don't run indefinitely, which could block the entire loop execution process.

## Components

### 1. Schema Registry Timeouts

Each agent in the schema registry has a defined `timeout_seconds` value that specifies the maximum allowed execution time:

```json
"agents": {
    "hal": {
        "role": "initial builder",
        "dependencies": [],
        "produces": ["README.md", "requirements.txt"],
        "unlocks": ["nova"],
        "timeout_seconds": 30
    },
    "nova": {
        "role": "logic writer",
        "dependencies": ["hal"],
        "produces": ["api_routes", "logic_modules"],
        "unlocks": ["critic"],
        "timeout_seconds": 45
    },
    ...
}
```

### 2. Loop Monitor Module

The `loop_monitor.py` module provides the core functionality for tracking agent execution and detecting timeouts:

- **log_agent_execution_start**: Logs when an agent begins execution
- **log_agent_execution_complete**: Logs when an agent completes execution
- **check_for_frozen_agents**: Detects agents that have exceeded their timeout
- **get_agent_execution_status**: Retrieves execution status for agents
- **reset_frozen_agents**: Resets frozen agents to allow loop continuation

### 3. Debug Routes

The following API endpoints expose the timeout detection functionality:

- **GET /api/debug/agent/timeout/{project_id}**: Checks for agents that have exceeded their timeout
- **GET /api/debug/agent/execution/{project_id}**: Gets execution status for all agents or a specific agent
- **POST /api/debug/agent/reset/{project_id}**: Resets frozen agents to allow them to run again
- **POST /api/debug/agent/start/{project_id}/{agent}**: Logs agent execution start
- **POST /api/debug/agent/complete/{project_id}/{agent}**: Logs agent execution completion

## How It Works

1. **Execution Logging**: When an agent starts running, its start time is logged in the project state.
2. **Timeout Detection**: The system periodically checks if any running agents have exceeded their timeout by comparing the current time with their start time.
3. **Alert Generation**: If an agent exceeds its timeout, it's marked as frozen and an alert is logged in the project state.
4. **Recovery**: Frozen agents can be reset to allow the loop to continue.

## Usage Examples

### Checking for Frozen Agents

```bash
curl -X GET "http://localhost:8000/api/debug/agent/timeout/my_project_123"
```

Response:
```json
{
  "project_id": "my_project_123",
  "frozen_agents": [
    {
      "agent": "nova",
      "duration": 67.5,
      "timeout": 45,
      "loop": 2,
      "start_time": "2025-04-20T12:15:30.123456"
    }
  ],
  "count": 1,
  "timestamp": "2025-04-20 12:23:00"
}
```

### Getting Agent Execution Status

```bash
curl -X GET "http://localhost:8000/api/debug/agent/execution/my_project_123"
```

Response:
```json
{
  "project_id": "my_project_123",
  "agent_executions": {
    "hal": [
      {
        "agent": "hal",
        "start_time": "2025-04-20T12:10:00.123456",
        "end_time": "2025-04-20T12:12:30.123456",
        "status": "completed",
        "duration": 150.0,
        "loop": 1
      }
    ],
    "nova": [
      {
        "agent": "nova",
        "start_time": "2025-04-20T12:15:30.123456",
        "status": "running",
        "loop": 2
      }
    ]
  },
  "current_status": {
    "hal": "completed",
    "nova": "running"
  },
  "has_frozen_agents": false,
  "loop_alerts": []
}
```

### Resetting Frozen Agents

```bash
curl -X POST "http://localhost:8000/api/debug/agent/reset/my_project_123"
```

Response:
```json
{
  "status": "success",
  "message": "Reset 1 frozen agents",
  "reset_count": 1,
  "project_id": "my_project_123"
}
```

### Logging Agent Execution Start

```bash
curl -X POST "http://localhost:8000/api/debug/agent/start/my_project_123/critic"
```

Response:
```json
{
  "status": "success",
  "message": "Project state updated for my_project_123",
  "project_id": "my_project_123"
}
```

### Logging Agent Execution Completion

```bash
curl -X POST "http://localhost:8000/api/debug/agent/complete/my_project_123/critic?status=completed"
```

Response:
```json
{
  "status": "success",
  "message": "Project state updated for my_project_123",
  "project_id": "my_project_123"
}
```

## Integration with Orchestrator

The Loop Timeout and Frozen Task Detection feature can be integrated with the Orchestrator to automatically:

1. Check for frozen agents before starting a new agent
2. Reset frozen agents when detected
3. Skip frozen agents and continue with the next agent in the loop
4. Log timeout events for later analysis

## Testing

A comprehensive test script (`test_loop_monitor.py`) is provided to verify the functionality:

```bash
python test_loop_monitor.py
```

The test script verifies:
- Agent execution logging
- Timeout detection
- Resetting frozen agents
- Handling multiple agents with different timeout states

## Benefits

- **Prevents Stuck Loops**: Ensures agents don't run indefinitely and block the system
- **Improves Reliability**: Automatically detects and logs problematic agent executions
- **Enables Recovery**: Provides mechanisms to reset frozen agents and continue execution
- **Enhances Observability**: Offers detailed execution status and history for debugging

## Future Enhancements

- Automatic recovery of frozen agents without manual intervention
- Configurable timeout values through API
- Timeout notifications via webhooks or email
- Historical timeout analysis to identify problematic agents
