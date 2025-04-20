# CTO Agent System Trends Analysis

This document provides information about the CTO agent's system trends analysis functionality, which monitors Promethios over time to detect systemic issues.

## Overview

The CTO agent now includes multi-loop pattern analysis that can detect slow systemic issues such as:

- Declining reflection quality
- Frequent schema drift
- Incomplete agent loops
- Loops that repeatedly skip validation
- Reuse of broken toolchains
- Long-term entropy

This functionality extends the original per-loop auditing with a system-wide perspective that tracks patterns across multiple loops.

## New Memory Structures

The following new memory structures have been added to support system trends analysis:

- `reflection_scores`: Array of reflection quality scores with timestamps
- `drift_logs`: Records of schema validation failures
- `loop_snapshots`: Snapshots of loop state for trend analysis
- `cto_audit_history`: History of system health audits
- `cto_warnings`: Warnings generated when system health declines
- `system_health_score`: Numeric score (0.0-1.0) representing overall system health

## System Health Score

The system health score is a numeric value between 0.0 and 1.0 that represents the overall health of the Promethios system:

- **1.0**: Perfect health, no issues detected
- **0.7-0.9**: Good health, minor issues
- **0.5-0.7**: Moderate health, some concerning patterns
- **0.3-0.5**: Poor health, significant issues detected
- **0.0-0.3**: Critical health, system requires immediate attention

The score is calculated based on multiple factors:
- Recent reflection quality
- Frequency of schema drift
- Pattern of agent skipping
- Other systemic issues

## API Endpoints

A new endpoint has been added to access system health information:

```
GET /api/debug/cto/system-health/{project_id}
```

This endpoint triggers a new analysis of system trends and returns the current system health status.

Additional endpoints for accessing trend data:

```
GET /api/debug/cto/audit-history/{project_id}
GET /api/debug/cto/warnings/{project_id}
```

## Integration with Orchestrator

The system trends analysis is automatically triggered after each loop audit. To manually trigger an analysis:

```python
from app.agents.cto_agent import analyze_system_trends

# Analyze system trends for a project
result = analyze_system_trends(project_id)
print(f"System health score: {result['system_health_score']}")
if result['issues']:
    print("Issues detected:")
    for issue in result['issues']:
        print(f"- {issue}")
```

## Helper Functions

New helper functions have been added to populate the data needed for trend analysis:

- `add_reflection_score(project_id, score, summary)`: Records a reflection quality score
- `log_schema_drift(project_id, drift_type, details)`: Logs a schema validation failure
- `snapshot_loop(project_id)`: Takes a snapshot of the current loop state

Example usage:

```python
from app.memory import add_reflection_score, log_schema_drift, snapshot_loop

# Record a reflection score
add_reflection_score(project_id, 0.8, "Good reflection with detailed analysis")

# Log a schema drift
log_schema_drift(project_id, "missing_field", {"field": "confidence", "object": "reflection"})

# Take a loop snapshot
snapshot_loop(project_id)
```

## Interpreting Results

When analyzing system trends, look for:

1. **Declining reflection quality**: Indicates the system may be losing its ability to self-reflect effectively
2. **Frequent schema drift**: Suggests structural inconsistencies are developing in the system
3. **Agent skipping patterns**: Shows that certain agents are being bypassed, potentially missing critical steps
4. **System health score trends**: A consistently declining score indicates systemic issues

## Responding to Warnings

When the CTO agent issues warnings about system health:

1. Review the specific issues identified
2. Check the audit history to see how the issues developed over time
3. Address the root causes rather than just the symptoms
4. Monitor the system health score after making changes to verify improvement

## Example Warning

```json
{
  "timestamp": "2025-04-20T12:30:45.123456",
  "warning": "System trending unhealthy",
  "detail": {
    "system_health_score": 0.3,
    "issues": [
      "Reflection quality declining",
      "Schema drift frequent",
      "Agents being skipped frequently"
    ],
    "loop_count": 15
  }
}
```

This warning indicates that the system health has declined to a critical level (0.3) after 15 loops, with multiple systemic issues detected.
