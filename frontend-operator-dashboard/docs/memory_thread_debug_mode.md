# Memory Thread Debug Mode and Goal ID Filtering Enhancement

## Overview

This document describes the implementation of a temporary debug mode in the `/memory/thread` endpoint and enhancements to the goal_id filtering logic to ensure memories are correctly retrieved.

## Problem Statement

The `/memory/thread` endpoint was not returning memories even when valid memories existed for a specified goal_id. This made it difficult to diagnose whether:

1. The memories were not being retrieved from the database at all
2. The memories were being retrieved but filtered out incorrectly
3. The goal_id filtering logic had issues with type matching or metadata parsing

## Solution Implemented

### 1. Debug Mode Parameter

Added a `debug_mode` parameter to the `/memory/thread` endpoint:

```python
@router.get("/thread")
async def memory_thread(
    goal_id: Optional[str] = None,
    task_id: Optional[str] = None,
    memory_trace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    order: Optional[str] = "asc",
    limit: Optional[int] = 50,
    debug_mode: Optional[bool] = False
):
```

### 2. Unfiltered Results in Debug Mode

Modified the endpoint to return all memories without filtering when in debug mode:

```python
# In debug mode, skip filtering and use all memories
if debug_mode:
    filtered_memories = [dict(m) for m in all_memories]
    logger.info(f"🔍 DEBUG MODE: Returning all {len(filtered_memories)} memories without filtering")

    # Add debug info for each memory
    for m in filtered_memories:
        logger.info(f"🔍 DEBUG: Memory ID: {m.get('memory_id')}, Type: {m.get('type')}, Goal ID: {m.get('goal_id')}")
        if m.get("metadata") and isinstance(m.get("metadata"), dict) and "goal_id" in m.get("metadata", {}):
            logger.info(f"🔍 DEBUG: Memory {m.get('memory_id')} has goal_id in metadata: {m.get('metadata', {}).get('goal_id')}")
```

### 3. Enhanced Debug Information in Response

Added comprehensive debug information to the response when in debug mode:

```python
# Add debug info to response if in debug mode
if debug_mode:
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "debug_info": {
                "total_memories_retrieved": len(all_memories),
                "memories_after_filtering": len(filtered_memories),
                "filters_applied": {
                    "goal_id": goal_id,
                    "task_id": task_id,
                    "memory_trace_id": memory_trace_id,
                    "agent_id": agent_id,
                    "user_id": user_id
                }
            },
            "thread": thread
        }
    )
```

### 4. Robust Goal ID Filtering Logic

Implemented a more robust goal_id filtering logic with detailed logging:

```python
# Filter by goal_id if provided
if goal_id:
    goal_id_match = False

    # Check top-level goal_id
    top_level_goal_id = m.get("goal_id")
    if top_level_goal_id is not None:
        logger.info(f"🔍 Comparing top-level goal_id: '{top_level_goal_id}' with filter: '{goal_id}'")
        if str(top_level_goal_id).strip() == str(goal_id).strip():
            logger.info(f"✅ MATCH: Top-level goal_id matched for memory {m.get('memory_id')}")
            goal_id_match = True

    # Check metadata goal_id if no match at top level
    if not goal_id_match and m.get("metadata"):
        metadata = m.get("metadata")
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                logger.warning(f"⚠️ Failed to parse metadata as JSON for memory {m.get('memory_id')}")

        if isinstance(metadata, dict) and "goal_id" in metadata:
            metadata_goal_id = metadata.get("goal_id")
            logger.info(f"🔍 Comparing metadata goal_id: '{metadata_goal_id}' with filter: '{goal_id}'")
            if str(metadata_goal_id).strip() == str(goal_id).strip():
                logger.info(f"✅ MATCH: Metadata goal_id matched for memory {m.get('memory_id')}")
                goal_id_match = True

    # Skip this memory if no goal_id match
    if not goal_id_match:
        logger.info(f"❌ NO MATCH: goal_id filter did not match for memory {m.get('memory_id')}")
        continue
```

### 5. Comprehensive Test Scripts

Created test scripts to verify the debug mode and goal_id filtering:

1. `test_memory_thread_debug.py` - Tests the debug mode with various scenarios
2. `test_memory_thread_direct.py` - A simplified test for direct database inspection

## Key Improvements

1. **Diagnostic Capability**: The debug mode allows for inspecting all memories without filtering
2. **Robust Metadata Handling**: Added support for parsing metadata stored as JSON strings
3. **Detailed Logging**: Added comprehensive logging for each step of the filtering process
4. **Type Safety**: Ensured consistent string comparison with explicit type casting
5. **Transparency**: Added debug information to the response for easier troubleshooting

## Usage

To use the debug mode, add the `debug_mode=true` query parameter to the `/memory/thread` endpoint:

```
GET /api/memory/thread?debug_mode=true
```

This will return all memories without filtering, along with detailed debug information.

To test a specific goal_id with debug mode:

```
GET /api/memory/thread?debug_mode=true&goal_id=goal_123
```

This will return all memories and show which ones matched the goal_id filter.

## Future Considerations

1. **Remove Debug Mode**: Once the filtering issues are resolved, the debug mode should be removed or disabled in production
2. **Performance Optimization**: The detailed logging should be removed or conditionally enabled in production
3. **Database Schema**: Consider adding an index on the goal_id column for better performance
