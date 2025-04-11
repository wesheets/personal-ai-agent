# Orchestrator Build Module

## Overview

The Orchestrator Build module provides functionality for executing pre-generated task plans by dynamically assigning each task to an agent based on skill match and availability. This module serves as the execution engine for plans created by the Orchestrator Scope module.

## Endpoint

```
POST /api/modules/orchestrator/build
```

## Purpose

This module allows Promethios to execute a pre-generated task plan (from `/orchestrator/scope`), dynamically assigning each task to an agent based on skill match and availability. It handles the process of:

1. Finding the best-fit agent for each task
2. Delegating tasks to appropriate agents
3. Logging all results in memory
4. Handling cases where no valid agent is found

## Request Format

```json
{
  "plan_id": "plan-87234",
  "tasks": [
    {
      "task_id": "task-001",
      "description": "Summarize project onboarding logs",
      "required_skills": ["summarization", "memory_search"]
    },
    {
      "task_id": "task-002",
      "description": "Reflect on the user's recent actions",
      "required_skills": ["reflection", "context_analysis"]
    }
  ],
  "project_id": "project-123"
}
```

### Request Fields

| Field | Type | Description |
|-------|------|-------------|
| `plan_id` | string | Unique identifier for the plan being executed |
| `tasks` | array | List of tasks to be executed |
| `tasks[].task_id` | string | Unique identifier for the task |
| `tasks[].description` | string | Description of the task to be performed |
| `tasks[].required_skills` | array | List of skills required to perform the task |
| `project_id` | string (optional) | Project identifier for context |

## Response Format

```json
{
  "status": "executing",
  "delegated_tasks": [
    {
      "task_id": "task-001",
      "assigned_agent": "ash",
      "delegation_task_id": "task-001-delegated"
    },
    {
      "task_id": "task-002",
      "assigned_agent": "hal",
      "delegation_task_id": "task-002-delegated"
    }
  ],
  "memory_id": "xyz123"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Status of the plan execution ("executing" or "failed") |
| `delegated_tasks` | array | List of successfully delegated tasks |
| `delegated_tasks[].task_id` | string | Original task identifier |
| `delegated_tasks[].assigned_agent` | string | Agent assigned to the task |
| `delegated_tasks[].delegation_task_id` | string | New task identifier for the delegation |
| `memory_id` | string | Identifier for the memory entry containing the build log |

## Core Logic

The module implements the following core logic:

1. **Agent Selection**: For each task in the plan, the module uses the `/agent/verify_task` endpoint to find the best-fit agent based on required skills.
2. **Task Delegation**: Once an appropriate agent is found, the task is delegated using the `delegate_task_internal` function.
3. **Memory Logging**: All results, including successful delegations and unassigned tasks, are logged in memory with type "build_log".
4. **Fallback Handling**: If no valid agent is found for a task, it is logged as unassigned with the reason.

## Integration Points

The module integrates with several existing components:

1. **Agent Verification**: Uses `verify_agent_for_task` from `app.modules.agent_verify` to determine agent qualification.
2. **Task Delegation**: Uses `delegate_task_internal` from `app.modules.agent_fallback` to delegate tasks to agents.
3. **Memory System**: Uses `write_memory` from `app.modules.memory_writer` to log build results.

## Error Handling

The module implements comprehensive error handling:

1. **Missing Agents**: If an agent doesn't exist, the task is logged as unassigned.
2. **Missing Skills**: If no agent has the required skills, the task is logged as unassigned.
3. **Delegation Failures**: If delegation fails, the error is captured and the task is logged as unassigned.
4. **Partial Execution**: The module continues processing tasks even if some fail, ensuring partial plan execution.

## Memory Structure

The module creates a memory entry with the following structure:

```json
{
  "agent_id": "orchestrator",
  "type": "build_log",
  "content": {
    "plan_id": "plan-87234",
    "delegated_tasks": [
      {
        "task_id": "task-001",
        "assigned_agent": "ash",
        "delegation_task_id": "task-001-delegated"
      }
    ],
    "unassigned_tasks": [
      {
        "task_id": "task-002",
        "reason": "No qualified agent found: Agent lacks required skills: context_analysis."
      }
    ],
    "timestamp": "2025-04-11T23:08:51.123456"
  },
  "tags": ["build_log", "plan:plan-87234"],
  "project_id": "project-123",
  "status": "executing",
  "task_type": "build",
  "task_id": "plan-87234"
}
```

## Usage Examples

### Example 1: Executing a Plan with Multiple Tasks

```python
import requests
import json

url = "https://api.example.com/api/modules/orchestrator/build"
payload = {
  "plan_id": "plan-87234",
  "tasks": [
    {
      "task_id": "task-001",
      "description": "Summarize project onboarding logs",
      "required_skills": ["summarization", "memory_search"]
    },
    {
      "task_id": "task-002",
      "description": "Reflect on the user's recent actions",
      "required_skills": ["reflection", "context_analysis"]
    }
  ],
  "project_id": "project-123"
}
headers = {
  "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(json.dumps(response.json(), indent=2))
```

### Example 2: Checking Build Status

After executing a plan, you can check the build status by retrieving the memory entry:

```python
import requests

url = f"https://api.example.com/api/modules/memory/read?memory_id={memory_id}"
headers = {
  "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
print(json.dumps(response.json(), indent=2))
```

## Future Enhancements

1. **Parallel Execution**: Implement parallel task execution for improved performance.
2. **Retry Mechanism**: Add retry logic for failed delegations.
3. **Progress Tracking**: Implement real-time progress tracking for plan execution.
4. **Conditional Execution**: Support conditional task execution based on previous task results.
5. **Priority Queuing**: Add support for task prioritization within a plan.
