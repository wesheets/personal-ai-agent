# System Delegation Log Feature Documentation

## Overview

The System Delegation Log feature provides a comprehensive logging system for tracking agent activities, delegations, and interactions throughout the project lifecycle. This feature enables users to monitor the execution flow between agents (HAL, NOVA, CRITIC, ASH), track blocking conditions, and understand the sequence of events that led to the current project state.

## Components

The System Delegation Log feature consists of three main components:

1. **Backend System Log Module**: Provides core functionality for logging events, retrieving logs, and managing log data.
2. **Agent Log Hooks**: Integration points in each agent function that log key events during execution.
3. **Frontend Delegation Log Panel**: UI component that displays log entries with filtering and auto-refresh capabilities.

## Backend System Log Module

Located in `memory/system_log.py`, this module provides the following functions:

- `log_event(agent_name, event_description, project_id, metadata)`: Records an event in the system log with timestamp and optional metadata.
- `get_system_log(project_id, limit, agent_filter)`: Retrieves log entries with optional filtering by project or agent.
- `clear_system_log()`: Clears all log entries (primarily for testing and maintenance).

The module uses in-memory storage for log entries with the following structure:

```json
{
  "timestamp": 1713369600,
  "formatted_time": "2025-04-17 14:00:00",
  "agent": "HAL",
  "event": "Starting execution with task: Create project structure",
  "project_id": "test-project",
  "metadata": { "additional_info": "value" }
}
```

## API Endpoints

The System Delegation Log feature exposes the following API endpoints in `routes/system_log_routes.py`:

- `GET /api/system/log`: Retrieves log entries with optional filtering by project_id, agent, and limit.
- `POST /api/system/log`: Adds a new log entry (primarily for testing and manual entries).
- `DELETE /api/system/log`: Clears all log entries (primarily for testing and maintenance).

## Agent Log Hooks

Log hooks have been implemented in all agent functions to record key events during execution:

### HAL Agent

The HAL agent logs events at the following points:
- When execution starts
- When retrying after being blocked
- After creating files
- When errors occur
- Upon successful completion

### NOVA Agent

The NOVA agent logs events at the following points:
- When execution starts
- When blocked by dependencies (e.g., waiting for HAL)
- During design actions
- When errors occur
- Upon successful completion

### CRITIC Agent

The CRITIC agent logs events at the following points:
- When execution starts
- During review actions
- When errors occur
- Upon successful completion

### ASH Agent

The ASH agent logs events at the following points:
- When execution starts
- During deployment actions
- When errors occur
- Upon successful completion

## Frontend Delegation Log Panel

The frontend component (`DelegationLogPanel.jsx`) provides a user interface for viewing system log entries with the following features:

- Filtering by agent (HAL, NOVA, CRITIC, ASH)
- Auto-refresh every 10 seconds
- Manual refresh button
- Color-coded agent labels for easy identification
- Responsive design for both desktop and mobile

The panel is integrated into the ControlRoom component and displays log entries in reverse chronological order (newest first).

## Usage Examples

### Logging an Event from an Agent

```python
from memory.system_log import log_event

# Log a simple event
log_event("HAL", "Starting execution with task: Create project structure", "demo_project")

# Log an event with metadata
log_event("NOVA", "Blocked: waiting for HAL", "demo_project", {"blocked_by": "HAL"})
```

### Retrieving Logs

```python
from memory.system_log import get_system_log

# Get all logs for a project
project_logs = get_system_log(project_id="demo_project")

# Get logs for a specific agent
hal_logs = get_system_log(project_id="demo_project", agent_filter="HAL")

# Get limited number of logs
recent_logs = get_system_log(limit=10)
```

## Implementation Details

### Error Handling

All log functions include robust error handling to ensure that logging failures don't disrupt agent execution. If the logging system fails, agents will continue to operate with minimal disruption.

### Performance Considerations

The in-memory storage provides fast access but doesn't persist across server restarts. For production environments, consider implementing a persistent storage solution.

## Testing

The System Delegation Log feature includes comprehensive tests:

- `test_system_log_backend.py`: Tests for backend functionality and API endpoints
- `test_delegation_log_panel.js`: Tests for frontend component functionality

## Future Enhancements

Potential future enhancements for the System Delegation Log feature:

1. Persistent storage for log entries
2. Advanced filtering and search capabilities
3. Log export functionality
4. Log visualization (timeline, dependency graphs)
5. Integration with external monitoring systems
