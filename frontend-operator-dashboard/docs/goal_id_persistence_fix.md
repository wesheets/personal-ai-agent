# Goal ID Persistence Fix

## Problem

The `/memory/thread` endpoint was returning an empty thread because the `goal_id` wasn't being stored at the top level of memory objects. Instead, it was only being stored in the `metadata` field, making it difficult to efficiently query memories by `goal_id`.

## Solution

### 1. Updated `write_memory()` Function in `memory_writer.py`

Added `goal_id` as a parameter to the function signature and included it at the top level of the memory object:

```python
def write_memory(agent_id: str, type: str, content: str, tags: list, project_id: Optional[str] = None,
                status: Optional[str] = None, task_type: Optional[str] = None, task_id: Optional[str] = None,
                memory_trace_id: Optional[str] = None, metadata: Optional[Dict] = None, goal_id: Optional[str] = None):
    # ...
    memory = {
        "memory_id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "type": type,
        "content": content,
        "tags": tags,
        "timestamp": datetime.utcnow().isoformat(),
        "project_id": project_id,
        "status": status,
        "task_type": task_type,
        "task_id": task_id,
        "memory_trace_id": memory_trace_id,
        "goal_id": goal_id,  # Add goal_id at the top level
        "metadata": metadata
    }
    # ...
```

### 2. Updated `MemoryWriteRequest` Model in `memory.py`

Added `goal_id` as a direct field in the request model to allow it to be passed directly in the request body:

```python
class MemoryWriteRequest(BaseModel):
    agent_id: str
    user_id: Optional[str] = None
    memory_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    project_id: Optional[str] = None
    status: Optional[str] = None
    task_type: Optional[str] = None
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    memory_trace_id: Optional[str] = None
    goal_id: Optional[str] = None  # Added goal_id field
```

### 3. Modified `memory_write_endpoint` Function

Updated the endpoint to extract `goal_id` from both the request body and metadata, with priority given to the direct field:

```python
# Extract goal_id from request or metadata if present
goal_id = request.goal_id
if not goal_id and request.metadata and "goal_id" in request.metadata:
    goal_id = request.metadata["goal_id"]

# Write memory with all provided parameters
memory = write_memory(
    agent_id=request.agent_id,
    type=request.memory_type,
    content=request.content,
    tags=tags,
    project_id=request.project_id,
    status=request.status,
    task_type=request.task_type,
    task_id=request.task_id,
    memory_trace_id=request.memory_trace_id,
    metadata=request.metadata,
    goal_id=goal_id
)
```

## Testing

Created a test script (`test_goal_id_persistence.py`) to verify that memories with `goal_id` can be properly retrieved via the `/memory/thread` endpoint. The test:

1. Writes a memory with a `goal_id` using the `/memory/write` endpoint
2. Retrieves the memory using the `/memory/thread` endpoint with the same `goal_id`
3. Verifies that the memory is correctly returned in the thread and that the `goal_id` is present at the top level

## Benefits

This fix ensures that:

1. The `goal_id` is stored at the top level of memory objects, making it more efficient to query memories by `goal_id`
2. The `/memory/thread` endpoint can properly retrieve memories filtered by `goal_id`
3. Both direct `goal_id` field and `goal_id` in metadata are supported, maintaining backward compatibility

## Future Considerations

1. Consider adding a database index on the `goal_id` column for even more efficient querying
2. Add validation to ensure `goal_id` is consistent between the direct field and metadata
3. Update other endpoints to support direct `goal_id` parameter for consistency
