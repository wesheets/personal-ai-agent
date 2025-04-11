# Loop + Delegation Cap System Documentation

## Overview

The Loop + Delegation Cap System prevents infinite agent loops or runaway delegation chains by enforcing hard and soft caps across the `/loop`, `/delegate`, and `/reflect` endpoints. This system protects system stability, controls costs, and ensures agents don't spiral into recursive failure modes.

## Configuration

The system uses a configuration file at `config/system_caps.json` with the following structure:

```json
{
  "max_loops_per_task": 3,
  "max_delegation_depth": 2
}
```

These values are easily tunable by modifying the configuration file.

## Implementation Details

### 1. System Caps Loading

Both the agent module and memory module load the system caps configuration:

```python
# Path for system caps configuration
SYSTEM_CAPS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "system_caps.json")

# Load system caps configuration
def load_system_caps():
    try:
        if os.path.exists(SYSTEM_CAPS_FILE):
            with open(SYSTEM_CAPS_FILE, 'r') as f:
                return json.load(f)
        else:
            print(f"⚠️ System caps file not found at {SYSTEM_CAPS_FILE}, using default caps")
            return {
                "max_loops_per_task": 3,
                "max_delegation_depth": 2
            }
    except Exception as e:
        print(f"⚠️ Error loading system caps: {str(e)}")
        return {
            "max_loops_per_task": 3,
            "max_delegation_depth": 2
        }

# Load system caps
system_caps = load_system_caps()
```

### 2. Loop Cap Enforcement

The `/loop` endpoint now tracks loop count and enforces the maximum loops per task:

```python
# Get current loop count for this task
current_loop_count = loop_request.loop_count if loop_request.loop_count is not None else 0

# Check if max_loops_per_task has been reached
if current_loop_count >= system_caps["max_loops_per_task"]:
    # Log the failure to memory
    memory = write_memory(
        agent_id=loop_request.agent_id,
        type="system_halt",
        content=f"Loop limit exceeded: {current_loop_count} loops reached for task {loop_request.task_id}",
        tags=["error", "loop_limit", "system_halt"],
        project_id=loop_request.project_id,
        status="error",
        task_type=loop_request.task_type if loop_request.task_type else "loop",
        task_id=loop_request.task_id,
        memory_trace_id=loop_request.memory_trace_id
    )
    
    # Return error response
    return JSONResponse(
        status_code=429,  # Too Many Requests
        content={
            "status": "error",
            "reason": "Loop limit exceeded",
            "loop_count": current_loop_count,
            "task_id": loop_request.task_id if loop_request.task_id else "unknown"
        }
    )
```

### 3. Delegation Cap Enforcement

The `/delegate` endpoint now tracks delegation depth and enforces the maximum delegation depth:

```python
# Get current delegation depth
current_delegation_depth = delegate_request.delegation_depth if delegate_request.delegation_depth is not None else 0

# Check if max_delegation_depth has been reached
if current_delegation_depth >= system_caps["max_delegation_depth"]:
    # Log the failure to memory
    memory = write_memory(
        agent_id=delegate_request.from_agent,
        type="system_halt",
        content=f"Delegation depth exceeded: {current_delegation_depth} levels reached for delegation to {delegate_request.to_agent}",
        tags=["error", "delegation_limit", "system_halt"],
        status="error",
        task_type="delegate"
    )
    
    # Return error response
    return JSONResponse(
        status_code=429,  # Too Many Requests
        content={
            "status": "error",
            "reason": "Delegation depth exceeded",
            "delegation_depth": current_delegation_depth,
            "agent_id": delegate_request.to_agent
        }
    )
```

### 4. Reflection Auto-Cap

The `/reflect` endpoint now also enforces the loop cap when called as part of a loop:

```python
# Check if this reflection is part of a loop and enforce loop cap
current_loop_count = reflection_request.loop_count if reflection_request.loop_count is not None else 0

# Check if max_loops_per_task has been reached
if current_loop_count >= system_caps["max_loops_per_task"]:
    # Log the failure to memory
    memory = write_memory(
        agent_id=reflection_request.agent_id,
        type="system_halt",
        content=f"Reflection loop limit exceeded: {current_loop_count} loops reached for task {reflection_request.task_id}",
        tags=["error", "loop_limit", "system_halt", "reflection"],
        project_id=reflection_request.project_id,
        status="error",
        task_id=reflection_request.task_id,
        memory_trace_id=reflection_request.memory_trace_id
    )
    
    # Return error response
    return JSONResponse(
        status_code=429,  # Too Many Requests
        content={
            "status": "error",
            "reason": "Loop limit exceeded",
            "loop_count": current_loop_count,
            "task_id": reflection_request.task_id,
            "project_id": reflection_request.project_id,
            "memory_trace_id": reflection_request.memory_trace_id,
            "agent_id": reflection_request.agent_id
        }
    )
```

## Testing

A comprehensive test suite has been created at `tests/test_loop_and_delegation_caps.py` to validate the implementation:

1. **System Caps Configuration Test**: Verifies the configuration file exists and contains the required fields.
2. **Loop Cap Enforcement Test**: Ensures loops halt after the configured limit.
3. **Delegation Cap Enforcement Test**: Confirms delegation stops after the defined depth.
4. **Reflection Auto-Cap Test**: Validates that reflection also respects the loop cap.
5. **Configurable Cap Override Test**: Tests that the cap values can be overridden for testing.

## Error Handling

When a cap is exceeded, the system:

1. Logs the failure to memory with `type="system_halt"` and appropriate tags
2. Returns a structured error response with:
   - HTTP status code 429 (Too Many Requests)
   - Error reason
   - Current count (loop_count or delegation_depth)
   - Relevant identifiers (task_id or agent_id)

## Benefits

The Loop + Delegation Cap System provides several benefits:

1. **System Stability**: Prevents infinite loops and runaway delegation chains
2. **Cost Control**: Limits the number of API calls and computational resources
3. **Error Prevention**: Catches potential recursive failure modes
4. **Observability**: Logs system halts for monitoring and debugging

## Future Enhancements

Potential future enhancements to the system could include:

1. Dynamic cap adjustment based on system load
2. Per-agent or per-project cap configurations
3. Soft caps with warning notifications before hard limits
4. Graceful degradation modes for approaching limits
