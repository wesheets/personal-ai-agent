# Project-Scoped Summarize Module

## Overview

The Project-Scoped Summarize Module provides functionality to generate concise summaries of memory traces scoped by project_id. This module allows users to retrieve summaries of all memories associated with a specific project, with optional filtering by agent_id and memory_type.

## Endpoints

### POST /app/modules/project-summarize

Generates a summary of memory entries filtered by project_id and optional parameters.

#### Request Body

```json
{
  "project_id": "proj-legacy-ai",
  "agent_id": "hal-9000",
  "memory_type": "observation",
  "store_summary": false,
  "limit": 50
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_id | string | Yes | Project identifier for filtering memories |
| agent_id | string | No | Optional agent identifier for filtering memories |
| memory_type | string | No | Optional memory type for filtering memories |
| store_summary | boolean | No | Whether to store the summary as a memory entry (default: false) |
| limit | integer | No | Maximum number of memories to consider (default: 50) |

#### Response

```json
{
  "status": "success",
  "summary": "HAL-9000 focused on system diagnostics, error analysis, and performance optimization.",
  "project_id": "proj-legacy-ai",
  "memory_count": 42,
  "memory_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

| Field | Type | Description |
|-------|------|-------------|
| status | string | "success" if successful, "failure" if error occurred |
| summary | string | Generated summary text |
| project_id | string | Project identifier (echoed from request) |
| memory_count | integer | Number of memories summarized |
| memory_id | string | ID of the stored summary memory (only if store_summary=true) |

## Implementation Details

### Memory Filtering

The module filters memories based on the following criteria:
- project_id (required): Only memories with matching project_id are included
- agent_id (optional): If provided, only memories from the specified agent are included
- memory_type (optional): If provided, only memories of the specified type are included

### Summary Generation

The module uses the existing `summarize_memories()` function from the memory_summarizer module to generate natural language summaries of the filtered memories. The summary focuses on the main themes or topics present in the memories.

### Optional Memory Storage

If `store_summary` is set to `true`, the generated summary is stored as a new memory entry with:
- memory_type: "project_summary"
- tags: ["project_summary", "compressed", project_id]
- project_id: The project_id from the request
- status: "completed"

## Usage Examples

### Basic Usage

```bash
curl -X POST https://api.example.com/app/modules/project-summarize \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-legacy-ai"
  }'
```

### Filtering by Agent

```bash
curl -X POST https://api.example.com/app/modules/project-summarize \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-legacy-ai",
    "agent_id": "hal-9000"
  }'
```

### Storing the Summary

```bash
curl -X POST https://api.example.com/app/modules/project-summarize \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-legacy-ai",
    "store_summary": true
  }'
```

## Integration with Other Modules

The Project-Scoped Summarize Module integrates with:

1. **Memory Writer Module**: For retrieving memories and optionally storing summaries
2. **Projects Module**: For scoping summaries to specific projects
3. **Memory Summarizer Module**: For generating the actual summary text

## Error Handling

The module handles the following error scenarios:

1. **Missing project_id**: Returns a 422 Validation Error
2. **No memories found**: Returns a success response with a message indicating no memories were found
3. **Internal errors**: Returns a 500 error with details about the failure

## Security Considerations

- The module only returns memories that match the specified project_id
- No authentication is currently implemented; this should be added in a future update
- The module does not expose sensitive memory content outside of the specified project scope
