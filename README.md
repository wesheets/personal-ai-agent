# CTO Agent Upgrade: System Pattern Watcher

This project extends the CTO agent with loop pattern scanning and multi-loop health trend analysis capabilities to detect systemic issues over time in the Promethios system.

## Features

- Multi-loop pattern analysis to detect slow systemic issues
- System health score calculation (0.0 to 1.0)
- Detection of declining reflection quality
- Monitoring of schema drift frequency
- Identification of agent skipping patterns
- System health endpoint for monitoring
- Comprehensive trend analysis documentation

## Project Structure

```
app/
├── agents/
│   └── cto_agent.py         # Extended with system trends analysis
├── routes/
│   └── debug_routes.py      # Added system-health endpoint
├── tests/
│   └── test_system_trends.py # Tests for trend analysis functionality
└── memory.py                # Updated with new memory structures
```

## Implementation Details

### System Trends Analysis

The CTO agent now includes an `analyze_system_trends` function that:
- Analyzes reflection quality trends
- Monitors schema drift frequency
- Detects patterns of agent skipping
- Calculates an overall system health score
- Logs audit history and warnings

### New Memory Structures

- `reflection_scores`: Array of reflection quality scores
- `drift_logs`: Records of schema validation failures
- `loop_snapshots`: Snapshots of loop state
- `cto_audit_history`: History of system health audits
- `cto_warnings`: Warnings for declining system health
- `system_health_score`: Overall health metric (0.0-1.0)

### New API Endpoint

- `GET /api/debug/cto/system-health/{project_id}`: Get system health analysis

## Usage

The system trends analysis is automatically triggered after each loop audit:

```python
from app.agents.cto_agent import run_cto_agent

# Run CTO agent (includes system trends analysis)
result = run_cto_agent(project_id)
```

To manually trigger a system trends analysis:

```python
from app.agents.cto_agent import analyze_system_trends

# Analyze system trends
result = analyze_system_trends(project_id)
print(f"System health score: {result['system_health_score']}")
```

## Testing

Run tests with pytest:

```
pytest app/tests/test_system_trends.py
```

## Documentation

See [SYSTEM_TRENDS_DOCUMENTATION.md](SYSTEM_TRENDS_DOCUMENTATION.md) for detailed information about the system trends analysis functionality.
