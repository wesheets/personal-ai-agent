# Memory Summarization Module Documentation

## Overview

The Memory Summarization Module enables agents (like SHIVA) to summarize their recent memories into a coherent natural language reflection. This feature is useful for:

- Reflection dashboards
- Agent context building
- Compact memory display in the Control Room

## API Endpoint

### POST /api/modules/memory/summarize

Summarizes recent memories for an agent into a coherent natural language summary.

#### Request Body

```json
{
  "agent_id": "shiva",
  "type": "training",
  "limit": 5
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| agent_id | string | Yes | ID of the agent whose memories to summarize |
| type | string | No | Filter memories by type |
| limit | integer | No | Maximum number of memories to summarize (default: 10) |

#### Response

```json
{
  "status": "ok",
  "summary": "SHIVA focused on marketing systems and headline branding related to warehouse transformations.",
  "memory_count": 5
}
```

| Field | Type | Description |
|-------|------|-------------|
| status | string | Status of the request ("ok" or "error") |
| summary | string | Natural language summary of the memories |
| memory_count | integer | Number of memories summarized |

## Implementation Details

### Summarization Logic

The module provides two approaches to summarization:

1. **Simple Concatenation** (Current Implementation)
   - Extracts tags from memories
   - Creates a natural language summary based on the agent ID and tags
   - Falls back to using memory content if no tags are available

2. **AI-Powered Summarization** (Placeholder for Future)
   - Uses OpenAI or similar services to generate more sophisticated summaries
   - Includes fallback to simple concatenation if AI summarization fails

### Files Modified/Created

1. **app/api/modules/memory.py**
   - Added `SummarizeRequest` Pydantic model
   - Implemented `/summarize` endpoint with memory filtering and summarization

2. **app/modules/memory_summarizer.py** (New File)
   - Implemented `summarize_memories` function for simple summarization
   - Added placeholder `summarize_memories_with_ai` function for future AI-powered summarization

## Testing

The implementation has been tested with various scenarios:

- Summarizing all memories for an agent
- Filtering memories by type
- Testing with empty memory sets
- Testing with different agent IDs

All tests produce coherent summaries that accurately reflect the content and tags of the memories.

## Future Enhancements

1. Implement the AI-powered summarization using OpenAI or similar services
2. Add more sophisticated filtering options (by date range, by specific tags)
3. Add caching for frequently requested summaries
4. Implement summary persistence for historical comparison
