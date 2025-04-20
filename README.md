# CTO Agent for Promethios

This project implements a CTO agent for the Promethios system that performs post-loop system audits, schema validation, and system health monitoring.

## Features

- Post-loop system audits
- Schema validation against registry
- Detection of soft decay patterns
- Structured reflection logging
- System warning flags for critical issues
- Debug endpoints for monitoring

## Project Structure

```
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
```

## Integration

The CTO agent is registered in the agent registry and can be called by the orchestrator after each loop:

```python
from app.agents.cto_agent import run_cto_agent

# After completing a loop
result = run_cto_agent(project_id)
```
