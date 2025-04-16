# Fix Route Prefix Collision in AgentRunner Endpoint

## Changes Implemented

This update fixes a route prefix collision in the AgentRunner endpoint that was causing 502 errors. The issue was that the route was being registered incorrectly as `/api/modules/agent/api/modules/agent/run` instead of the intended `/api/modules/agent/run`.

### Route Path Fix

The issue was caused by a duplicate prefix in the route registration:

1. In `app/api/modules/agent.py`, the router is defined with:

   ```python
   router = APIRouter(prefix="/modules/agent", tags=["Agent Modules"])
   ```

2. In `app/main.py`, the router is included with:

   ```python
   app.include_router(agent_module_router, prefix="/api")
   ```

3. The route decorator was using the full path:
   ```python
   @router.post("/api/modules/agent/run")
   ```

This created a duplicate prefix, resulting in the route being registered as:
`/api` + `/modules/agent` + `/api/modules/agent/run` = `/api/modules/agent/api/modules/agent/run`

### Solution

Changed the route decorator to use only the endpoint path without the prefix:

```python
@router.post("/run")
```

Now the route is correctly registered as:
`/api` + `/modules/agent` + `/run` = `/api/modules/agent/run`

### Echo Implementation

The simplified echo implementation remains intact:

```python
@router.post("/run")
async def run_agent_echo(request: Request):
    print("📣 AgentRunner echo route was hit!")
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "message": "AgentRunner route is working"
        }
    )
```

### Testing Results

The implementation was tested by importing the main application module, which triggers the startup sequence. The test output confirmed that the application starts up correctly with the updated route path.

When this route is hit in production, we expect to see the "📣 AgentRunner echo route was hit!" log message and receive a 200 response with the success message, confirming that the route is now correctly registered at `/api/modules/agent/run`.
