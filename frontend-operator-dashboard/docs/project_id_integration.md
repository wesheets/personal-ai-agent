# Project ID Integration Across Memory and Task Modules

This document describes how project_id is integrated across memory and task modules to enable scoped orchestration and recall.

## Overview

The project_id field is used to associate memories and task executions with specific projects, allowing for:

- Scoped summarization
- Vertical reporting
- AI agent awareness of goal continuity
- Orchestrator planning scope

## Endpoints Supporting project_id

### 1. Memory Write Endpoint (`/app/modules/write`)

**Request Body:**

```json
{
  "agent_id": "Forge",
  "memory_type": "reflection",
  "content": "Loop completed with no errors.",
  "tags": ["test", "integration"],
  "project_id": "proj-legacy-ai"
}
```

**Implementation Details:**

- The `MemoryEntry` model includes `project_id` as an optional field
- The `memory_write` function passes `project_id` to the `write_memory` function
- The `write_memory` function stores `project_id` in the memory object

### 2. Memory Read Endpoint (`/app/modules/read`)

**Query Parameters:**

- `agent_id`: ID of the agent whose memories to retrieve (required)
- `project_id`: Filter by project context (optional)
- Other optional filters: `type`, `tag`, `limit`, `since`, `task_id`, `thread_id`

**Example Usage:**

```
GET /app/modules/read?agent_id=Forge&project_id=proj-legacy-ai
```

**Implementation Details:**

- Accepts `project_id` as an optional query parameter
- Filters memories with:
  ```python
  if project_id:
      filtered_memories = [
          m for m in filtered_memories
          if "project_id" in m and m["project_id"] == project_id
      ]
  ```

### 3. Task Status Endpoints (`/app/task/status`)

#### POST Endpoint

**Request Body:**

```json
{
  "task_id": "task-123",
  "project_id": "proj-legacy-ai",
  "agent_id": "Forge",
  "memory_trace_id": "trace-456",
  "status": "completed",
  "output": "Task completed successfully"
}
```

**Implementation Details:**

- The `TaskStatusInput` model includes `project_id` as a required field
- The POST endpoint stores `project_id` in the log entry
- The endpoint passes `project_id` to `write_memory` when storing task status

#### GET Endpoint

**Query Parameters:**

- `task_id`: Filter by task ID (optional)
- `project_id`: Filter by project ID (optional)
- `agent_id`: Filter by agent ID (optional)
- `memory_trace_id`: Filter by memory trace ID (optional)

**Example Usage:**

```
GET /app/task/status?project_id=proj-legacy-ai
```

**Implementation Details:**

- Accepts `project_id` as an optional query parameter
- Filters task logs with:
  ```python
  if project_id:
      filtered_logs = [log for log in filtered_logs if log["project_id"] == project_id]
  ```

## Testing

A comprehensive test script is available at `/tests/test_project_id_integration.py` to verify project_id integration across all endpoints.

The test script verifies:

1. Writing a memory with project_id
2. Reading memories filtered by project_id
3. Posting task status with project_id
4. Getting task status filtered by project_id

## Why This Matters

Adding project_id completes the context loop across:

- Agent memory
- Task traces
- Project goal evolution
- Orchestrator planning scope

This enables:

- Scoped summarization
- Vertical reporting
- AI agent awareness of goal continuity
