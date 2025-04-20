feature/system-integrity-tests-v2
# System Integrity Test Suite

This project implements a comprehensive test suite for ensuring the Promethios cognitive OS is healthy, aligned, and schema-compliant.

## Features

- Validates project memory against schema
- Grades reflection quality and ensures minimum confidence threshold
- Checks loop snapshot consistency
- Confirms orchestrator decisions exist and are traceable
- Verifies CTO system health is above minimum threshold
- Confirms drift logs are empty or non-critical
- Validates agents are triggered in correct dependency order
- Monitors memory growth rate

# CTO Agent for Promethios

This project implements a CTO agent for the Promethios system that performs post-loop system audits, schema validation, and system health monitoring.

## Features

- Post-loop system audits
- Schema validation against registry
- Detection of soft decay patterns
- Structured reflection logging
- System warning flags for critical issues
- Debug endpoints for monitoring
main

## Project Structure

```
feature/system-integrity-tests-v2
tests/
├── test_system_integrity.py  # Main integrity test suite
└── test_meta_integrity.py    # Meta-tests to verify test suite functionality

.github/
└── workflows/
    └── system-health-check.yml  # GitHub Action for automated testing
```

## Test Functions

The test suite includes the following validation functions:

- `test_project_memory_schema()`: Validates memory against schema
- `test_reflection_confidence()`: Ensures reflection quality is above threshold
- `test_snapshot_presence()`: Verifies loop snapshots exist
- `test_orchestrator_decisions()`: Confirms decisions exist and are traceable
- `test_system_health_score()`: Checks CTO health score is above threshold
- `test_drift_logs_status()`: Confirms no critical drift logs
- `test_agent_dependency_order()`: Validates correct agent execution order
- `test_loop_snapshot_consistency()`: Checks snapshots are sequential
- `test_memory_growth_rate()`: Monitors for excessive memory growth

## GitHub Action

The included GitHub Action runs the test suite:
- On every push to the main branch
- Once per day via scheduled cron job

## Usage

Run the test suite locally:

```bash
pytest tests/test_system_integrity.py -v
```

Run meta-tests to verify test suite functionality:

```bash
pytest tests/test_meta_integrity.py -v

app/
├── agents/
│   └── cto_agent.py         # Core CTO agent implementation
├── routes/
│   └── debug_routes.py      # Debug endpoints for CTO reflections
├── utils/
│   ├── schema_utils.py      # Schema validation utilities
│   ├── reflection_analyzer.py # Reflection quality analysis
│   └── system_flag_manager.py # System flag management
├── tests/
│   └── test_cto_agent.py    # Tests for CTO agent functionality
├── main.py                  # FastAPI application
├── memory.py                # Project memory implementation
└── schema_registry.py       # Schema definitions
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install fastapi uvicorn pytest jsonschema
   ```

## Usage

The CTO agent is designed to be integrated into the Promethios agent system. It runs after each loop to audit the system and detect issues.

### Running the API

```
uvicorn app.main:app --reload
```

### API Endpoints

- `GET /api/debug/cto/reflection/{project_id}`: Get the most recent CTO reflection
- `GET /api/debug/cto/reflections/{project_id}`: Get all CTO reflections
- `GET /api/debug/cto/flags/{project_id}`: Get all system flags

## Testing

Run tests with pytest:

```
pytest app/tests/
main
```

## Integration

feature/system-integrity-tests-v2
To integrate with your existing Promethios system:

1. Copy the test files to your project's test directory
2. Copy the GitHub Action workflow to your .github/workflows directory
3. Ensure your project has the necessary dependencies (pytest)
4. Run the tests to verify system integrity

The CTO agent is registered in the agent registry and can be called by the orchestrator after each loop:

```python
from app.agents.cto_agent import run_cto_agent

# After completing a loop
result = run_cto_agent(project_id)
```
main
