# Task Status Module Documentation

## Overview

The Task Status module provides endpoints for logging and querying task execution status as part of the System Lockdown Phase. This is a critical system tracing feature that allows tracking the status and output of every agent task in Promethios.

## Endpoints

### POST /app/task/status

Logs a completed task execution with trace data.

#### Input Schema

```json
{
  "task_id": "string",
  "project_id": "string",
  "agent_id": "string",
  "memory_trace_id": "string",
  "status": "completed | failed | partial",
  "output": "string or object (optional)",
  "error": "string (optional)",
  "duration_ms": "int (optional)",
  "timestamp": "optional (auto-generate if missing)"
}
```

#### Output Schema

```json
{
  "status": "success",
  "log_id": "uuid",
  "task_id": "...",
  "timestamp": "...",
  "stored": true
}
```

#### Example Usage

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/app/task/status"

# Log a successful task
payload = {
    "task_id": "task-123",
    "project_id": "project-456",
    "agent_id": "agent-789",
    "memory_trace_id": "trace-abc",
    "status": "completed",
    "output": "Task completed successfully with result: 42",
    "duration_ms": 1500
}

response = requests.post(BASE_URL, json=payload)
print(json.dumps(response.json(), indent=2))
```

### GET /app/task/status

Query task logs by various parameters.

#### Query Parameters

- `task_id`: Filter by task ID (optional)
- `project_id`: Filter by project ID (optional)
- `agent_id`: Filter by agent ID (optional)
- `memory_trace_id`: Filter by memory trace ID (optional)

#### Output Schema

```json
{
  "status": "success",
  "logs": [
    {
      "log_id": "uuid",
      "task_id": "string",
      "project_id": "string",
      "agent_id": "string",
      "memory_trace_id": "string",
      "status": "completed | failed | partial",
      "output": "string or object",
      "error": "string",
      "duration_ms": "int",
      "timestamp": "string"
    }
  ],
  "count": "int"
}
```

#### Example Usage

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/app/task/status"

# Query by task_id
response = requests.get(f"{BASE_URL}?task_id=task-123")
print(json.dumps(response.json(), indent=2))

# Query by project_id
response = requests.get(f"{BASE_URL}?project_id=project-456")
print(json.dumps(response.json(), indent=2))

# Query by agent_id
response = requests.get(f"{BASE_URL}?agent_id=agent-789")
print(json.dumps(response.json(), indent=2))

# Query by memory_trace_id
response = requests.get(f"{BASE_URL}?memory_trace_id=trace-abc")
print(json.dumps(response.json(), indent=2))
```

## Memory Behavior

Task status logs are stored in memory with the following metadata:

- `memory_type`: "task_status"
- `agent_id`: ID of the agent that executed the task
- `content`: Human-readable summary of the task status
- `tags`: ["task", "status", "sdk_compliant"]
- `project_id`: Project identifier for context
- `task_id`: Task identifier for tracing
- `memory_trace_id`: Memory trace identifier for linking
- `status`: Status of the task (completed, failed, partial)

## Logging

The module provides comprehensive logging capabilities:

- Success/failure logging to console
- Human-readable summaries for observers
- Structured logging for future UI audit tools

## Testing

A test script is provided at `/tests/test_task_status_endpoints.py` to validate:

- Schema enforcement
- Success and failure scenarios
- Memory/log writing
- Query functionality

To run the test script:

```bash
cd /home/ubuntu/personal-ai-agent
python tests/test_task_status_endpoints.py
```

## Integration

The Task Status module is integrated into the main application in `main.py`:

```python
from app.api.task import router as task_router  # Import the task router
app.include_router(task_router, prefix="/app")  # Mount the task status router
```

This makes the endpoints accessible at:
- POST /app/task/status
- GET /app/task/status

## SDK Compliance

This module complies with Promethios_Module_Contract_v1.0.0 by:
- Validating required input fields
- Returning structured responses with all required fields
- Writing memory with proper metadata and trace fields
- Providing comprehensive logging for failures or validation errors
