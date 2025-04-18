# AGENT_RUNNERS Debug Trap Implementation

This document outlines the changes made to debug the AGENT_RUNNERS loading failure issue.

## Problem

The `/api/agent/run` endpoint was returning an error:
```json
{
  "status": "error",
  "message": "AGENT_RUNNERS not available, cannot execute agent"
}
```

Despite the AGENT_RUNNERS dictionary being clearly defined in `agent_runner.py`.

## Changes Implemented

### 1. Enhanced Debug Trap in agent_routes.py

Added a more detailed debug trap at the top of `routes/agent_routes.py`:

```python
try:
    from app.modules.agent_runner import AGENT_RUNNERS
    print("✅ AGENT_RUNNERS loaded with keys:", list(AGENT_RUNNERS.keys()))
except Exception as e:
    print("❌ Failed to import AGENT_RUNNERS:", e)
    AGENT_RUNNERS = {}
```

### 2. Added Runtime AGENT_RUNNERS Check

Added a runtime check inside the `/agent/run` route handler:

```python
# Runtime check for AGENT_RUNNERS
print("🔍 Runtime AGENT_RUNNERS keys:", list(AGENT_RUNNERS.keys()))
```

### 3. Added SAGE Check in system_summary_routes.py

Updated `routes/system_summary_routes.py` with similar debug traps:

```python
try:
    from app.modules.agent_runner import AGENT_RUNNERS
    print("✅ AGENT_RUNNERS loaded with keys:", list(AGENT_RUNNERS.keys()))
except Exception as e:
    print("❌ Failed to import AGENT_RUNNERS:", e)
    AGENT_RUNNERS = {}
```

Added SAGE-specific check:

```python
print("🔍 Checking for 'sage' in AGENT_RUNNERS:", "sage" in AGENT_RUNNERS)
```

## Expected Outcomes

These debug traps will help identify:

1. Whether the imports are failing or being overwritten
2. If AGENT_RUNNERS is available at runtime
3. If SAGE is properly loaded for system summary generation

## Testing Instructions

After deployment, test the complete workflow sequence:

1. POST `/api/project/start`
2. GET `/api/system/status?project_id=demo_001`
3. POST `/api/agent/run`
4. POST `/api/system/summary`

The debug logs will show exactly where any issues are occurring in the agent loading process.
