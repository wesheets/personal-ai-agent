# Agent Reflect Module

## Overview

The Agent Reflect module provides functionality for agents to reflect on the outcome of completed tasks and store reflection memory entries. This allows agents to record their thoughts on task execution, whether successful or failed, to improve future performance.

## Endpoint

```
POST /api/modules/agent/reflect
```

## Purpose

This endpoint enables post-task cognition by allowing agents to:

1. Reflect on completed tasks (both successful and failed)
2. Store structured reflection memories
3. Generate insights based on task execution details
4. Build a learning history that can inform future task execution

## Request Format

```json
{
  "agent_id": "hal",
  "task_id": "task-8734",
  "task_summary": "Summarized all onboarding-related memories",
  "outcome": "success",
  "notes": "Task completed with minimal memory coverage, agent used memory_search and summarization",
  "project_id": "project-123"
}
```

### Request Fields

| Field          | Type   | Required | Description                                                              |
| -------------- | ------ | -------- | ------------------------------------------------------------------------ |
| `agent_id`     | string | Yes      | ID of the agent that completed the task                                  |
| `task_id`      | string | Yes      | ID of the completed task                                                 |
| `task_summary` | string | Yes      | Brief summary of what the task involved                                  |
| `outcome`      | string | Yes      | Must be either "success" or "failure"                                    |
| `notes`        | string | Yes      | Additional details about task execution                                  |
| `project_id`   | string | No       | Optional project ID for context (auto-fetched from task if not provided) |

## Response Format

```json
{
  "status": "reflected",
  "memory_id": "xyz123",
  "reflection": "HAL successfully used memory_search to complete the onboarding summary task, suggesting stronger summarization confidence moving forward."
}
```

### Response Fields

| Field        | Type   | Description                                     |
| ------------ | ------ | ----------------------------------------------- |
| `status`     | string | Always "reflected" when successful              |
| `memory_id`  | string | ID of the created reflection memory             |
| `reflection` | string | Generated reflection text based on task details |

## Error Responses

### Missing Required Fields

```json
{
  "detail": "agent_id is required"
}
```

Status Code: 422 Unprocessable Entity

### Invalid Outcome Value

```json
{
  "detail": "outcome must be 'success' or 'failure'"
}
```

Status Code: 422 Unprocessable Entity

## Internal Logic

1. The endpoint accepts reflection input from the agent
2. It validates all required fields and the outcome value
3. If project_id is not provided, it attempts to fetch it from the task context
4. It generates a reflection based on the task details, outcome, and notes
5. It creates tags based on the outcome and standard reflection categories
6. It writes a memory entry of type "reflection" using the write_memory function
7. It returns the memory_id and generated reflection

## Memory Storage

Reflections are stored with the following attributes:

- `type`: "reflection"
- `tags`: ["reflection", "task_outcome", "learning", "success"/"failure"]
- `status`: The outcome value ("success" or "failure")
- All standard memory fields (agent_id, content, timestamp, etc.)

## Usage Examples

### Recording a Successful Task Reflection

```python
import requests

response = requests.post(
    "https://api.example.com/api/modules/agent/reflect",
    json={
        "agent_id": "hal",
        "task_id": "task-8734",
        "task_summary": "Summarized all onboarding-related memories",
        "outcome": "success",
        "notes": "Task completed with minimal memory coverage, agent used memory_search and summarization"
    }
)

print(response.json())
```

### Recording a Failed Task Reflection

```python
import requests

response = requests.post(
    "https://api.example.com/api/modules/agent/reflect",
    json={
        "agent_id": "hal",
        "task_id": "task-8735",
        "task_summary": "Failed to summarize onboarding-related memories",
        "outcome": "failure",
        "notes": "Task failed due to memory retrieval issues"
    }
)

print(response.json())
```

## Integration with Other Modules

The Agent Reflect module integrates with:

1. **Memory Writer**: Uses the `write_memory` function to store reflections
2. **Memory Reader**: Reflections can be queried via the `/read` endpoint with `memory_type=reflection`
3. **Task System**: References task IDs and can fetch project context from tasks

## Future Enhancements

Potential future enhancements for the Agent Reflect module:

1. **Enhanced Reflection Generation**: Implement more sophisticated reflection generation using LLMs
2. **Reflection Aggregation**: Provide endpoints to aggregate reflections across tasks or time periods
3. **Learning Patterns**: Identify patterns in agent performance based on reflection history
4. **Recommendation Engine**: Suggest improvements based on reflection history
5. **Reflection Visualization**: Create visual representations of agent learning over time
