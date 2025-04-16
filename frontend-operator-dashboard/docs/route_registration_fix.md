# Route Registration and Method Handling for /loop, /delegate, /reflect Modules

## Overview

This document describes the implementation of proper route registration and method handling for the `/loop`, `/delegate`, and `/reflect` modules in the Promethios OS. These changes ensure that all cap-enforced endpoints are correctly registered, exposed, and respond properly to POST requests.

## Implementation Details

### 1. Created Dedicated Module Files

Three new dedicated module files were created in the `app/modules` directory:

- **loop.py**: Implements the `/loop` endpoint for executing cognitive loops for agents
- **delegate.py**: Implements the `/delegate` endpoint for delegating tasks between agents
- **reflect.py**: Implements the `/reflect` endpoint for generating agent reflections

Each module includes:

- A FastAPI router with proper route decorators
- System caps configuration loading
- Pydantic models for request validation
- Comprehensive error handling
- Cap enforcement logic

### 2. Fixed Route Decorators

All three endpoints now use the correct route decorator pattern:

```python
@router.post("/")
```

This ensures that the endpoints are triggered via clean POST requests at:

- `/app/modules/loop`
- `/app/modules/delegate`
- `/app/modules/reflect`

### 3. Enforced POST-Only Method Handling

The implementation ensures that all three routes:

- Reject GET requests properly (FastAPI handles this automatically)
- Parse POST JSON bodies cleanly using Pydantic models
- Match FastAPI convention for route handling

### 4. Updated Router Registration in main.py

The `main.py` file was updated to include the new module routers with the correct prefixes:

```python
# Import the new dedicated module routers
from app.modules.loop import router as loop_router
from app.modules.delegate import router as delegate_router
from app.modules.reflect import router as reflect_router

# Mount the new dedicated module routers
app.include_router(loop_router, prefix="/app/modules/loop")
app.include_router(delegate_router, prefix="/app/modules/delegate")
app.include_router(reflect_router, prefix="/app/modules/reflect")
```

### 5. Created Comprehensive Tests

A test script was created at `tests/test_route_registration.py` to validate:

- Endpoint registration and accessibility
- POST method handling and GET method rejection
- JSON payload parsing
- Cap enforcement with structured 429 responses

## Benefits

These changes provide several benefits:

1. **Clean API Structure**: Each endpoint now has a dedicated module file, making the codebase more maintainable
2. **Consistent Route Patterns**: All endpoints follow the same pattern for route registration and method handling
3. **Proper Error Handling**: Cap enforcement is consistently applied across all endpoints
4. **Improved Testing**: Comprehensive tests ensure the endpoints work as expected

## Usage Examples

### Loop Endpoint

```
POST /app/modules/loop
{
  "agent_id": "hal",
  "loop_type": "reflective",
  "task_id": "...",
  "loop_count": 0
}
```

### Delegate Endpoint

```
POST /app/modules/delegate
{
  "from_agent": "hal",
  "to_agent": "ash",
  "task": "Analyze this data",
  "delegation_depth": 0
}
```

### Reflect Endpoint

```
POST /app/modules/reflect
{
  "agent_id": "hal",
  "goal": "Understand recent actions",
  "task_id": "...",
  "project_id": "...",
  "memory_trace_id": "...",
  "loop_count": 0
}
```

## Cap Enforcement

All three endpoints enforce caps as configured in `system_caps.json`:

- `/loop` enforces `max_loops_per_task`
- `/delegate` enforces `max_delegation_depth`
- `/reflect` enforces `max_loops_per_task`

When a cap is exceeded, the endpoint returns a structured 429 response with details about the limit exceeded.
