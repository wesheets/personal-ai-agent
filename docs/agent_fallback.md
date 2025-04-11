# Agent Fallback Module

## Overview

The Agent Fallback module provides functionality for agents to reroute tasks they cannot perform due to skill mismatch, failure, or reflection-based decision. This allows agents to delegate tasks to more suitable agents when they are unable to complete them.

## Endpoint

```
POST /api/modules/agent/fallback
```

## Purpose

This endpoint enables task rerouting by allowing agents to:
1. Identify tasks they cannot perform
2. Record fallback events in memory
3. Delegate tasks to more suitable agents
4. Track the delegation chain

## Request Format

```json
{
  "agent_id": "hal",
  "task_id": "task-4558",
  "reason": "missing_skills",
  "suggested_agent": "ash",
  "notes": "Agent HAL does not have summarization. Rerouting task to ASH."
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_id` | string | Yes | ID of the agent that cannot perform the task |
| `task_id` | string | Yes | ID of the task to be rerouted |
| `reason` | string | Yes | Reason for fallback (must be one of: "missing_skills", "failed_task", "reflection_decision") |
| `suggested_agent` | string | Yes | ID of the agent to reroute the task to |
| `notes` | string | Yes | Additional details about the fallback reason |
| `project_id` | string | No | Optional project ID for context |

## Response Format

```json
{
  "status": "rerouted",
  "new_agent": "ash",
  "delegation_task_id": "task-4558-delegated",
  "memory_id": "xyz123"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always "rerouted" when successful |
| `new_agent` | string | ID of the agent the task was rerouted to |
| `delegation_task_id` | string | ID of the newly created delegated task |
| `memory_id` | string | ID of the created fallback memory |

## Error Responses

### Missing Required Fields

```json
{
  "detail": "agent_id is required"
}
```

Status Code: 422 Unprocessable Entity

### Invalid Fallback Reason

```json
{
  "detail": "reason must be one of: missing_skills, failed_task, reflection_decision"
}
```

Status Code: 422 Unprocessable Entity

### Agent Not Found

```json
{
  "detail": "Agent with ID 'invalid-agent' not found"
}
```

Status Code: 404 Not Found

### Delegation Failure

```json
{
  "detail": "Delegation failed: Unable to assign task to agent"
}
```

Status Code: 500 Internal Server Error

## Internal Logic

1. The endpoint validates the fallback request, ensuring all required fields are present and valid
2. It verifies that both the source and target agents exist
3. It writes a fallback memory entry with type "fallback" and appropriate tags
4. It generates a new task ID for the delegated task by appending "-delegated" to the original task ID
5. It calls the delegate endpoint to reassign the task to the suggested agent
6. If delegation fails, it writes an error memory and returns an appropriate error response
7. If successful, it returns the delegation details including the new task ID and memory ID

## Memory Storage

Fallbacks are stored with the following attributes:
- `type`: "fallback"
- `tags`: ["fallback", "reason:{reason}", "to:{suggested_agent}"]
- `status`: "rerouted"
- All standard memory fields (agent_id, content, timestamp, etc.)

If delegation fails, an additional memory is created:
- `type`: "fallback_error"
- `tags`: ["fallback", "error", "reason:{reason}"]
- `status`: "error"

## Usage Examples

### Rerouting a Task Due to Missing Skills

```python
import requests

response = requests.post(
    "https://api.example.com/api/modules/agent/fallback",
    json={
        "agent_id": "hal",
        "task_id": "task-4558",
        "reason": "missing_skills",
        "suggested_agent": "ash",
        "notes": "Agent HAL does not have summarization. Rerouting task to ASH."
    }
)

print(response.json())
```

### Rerouting a Task Due to Failure

```python
import requests

response = requests.post(
    "https://api.example.com/api/modules/agent/fallback",
    json={
        "agent_id": "hal",
        "task_id": "task-4559",
        "reason": "failed_task",
        "suggested_agent": "ash",
        "notes": "Agent HAL failed to complete the task. Rerouting to ASH."
    }
)

print(response.json())
```

### Rerouting a Task Based on Reflection Decision

```python
import requests

response = requests.post(
    "https://api.example.com/api/modules/agent/fallback",
    json={
        "agent_id": "hal",
        "task_id": "task-4560",
        "reason": "reflection_decision",
        "suggested_agent": "ash",
        "notes": "Agent HAL determined ASH would be more efficient for this task."
    }
)

print(response.json())
```

## Integration with Other Modules

The Agent Fallback module integrates with:

1. **Memory Writer**: Uses the `write_memory` function to store fallback events
2. **Delegate Module**: Uses the delegate endpoint to reassign tasks
3. **Agent Registry**: Verifies agent existence and capabilities
4. **Task System**: References task IDs and creates new delegated tasks

## Future Enhancements

Potential future enhancements for the Agent Fallback module:

1. **Automatic Agent Selection**: Automatically determine the best agent for fallback based on task requirements
2. **Fallback Chain Tracking**: Track the complete chain of fallbacks for a task
3. **Fallback Analytics**: Provide insights into common fallback patterns and reasons
4. **Fallback Prevention**: Suggest improvements to reduce the need for fallbacks
5. **Partial Task Completion**: Allow agents to complete parts of tasks before falling back
