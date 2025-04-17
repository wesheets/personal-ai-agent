# Phase 6.1 Agent Timing & Synchronization Documentation

## Overview
This document provides comprehensive documentation for the Phase 6.1 Agent Timing & Synchronization features implemented in the personal AI agent system. These features enable better coordination between agents, intelligent recovery from blocked states, and improved state management.

## Features

### 1. Agent Retry and Recovery Flow
The agent retry and recovery flow allows agents to be blocked when dependencies are not met and automatically unblocked when conditions are satisfied.

#### Key Components:
- **Module**: `app/modules/agent_retry.py`
- **Main Functions**:
  - `register_blocked_agent(project_id, agent_id, blocked_due_to, unblock_condition)`: Registers an agent as blocked due to a dependency
  - `check_for_unblocked_agents(project_id)`: Checks for agents that can be unblocked based on current project state
  - `get_retry_status(project_id, agent_id)`: Gets the current retry status of an agent
  - `mark_agent_retry_attempted(project_id, agent_id)`: Marks an agent as having attempted a retry

#### Usage Example:
```python
from app.modules.agent_retry import register_blocked_agent

# Register NOVA agent as blocked due to HAL not completing initial files
register_blocked_agent(
    project_id="demo_project_001",
    agent_id="nova",
    blocked_due_to="hal",
    unblock_condition="initial_files_created"
)
```

### 2. Project State Watch Hooks
The project state watch hooks provide a mechanism for monitoring changes to project state and triggering actions when specific conditions are met.

#### Key Components:
- **Module**: `app/modules/project_state_watch.py`
- **Main Functions**:
  - `subscribe_to_state_changes(project_id)`: Creates a subscription to monitor state changes for a project
  - `get_state_changes(subscription_id)`: Gets the changes that have occurred since the last check
  - `unsubscribe(subscription_id)`: Removes a subscription

#### Usage Example:
```python
from app.modules.project_state_watch import subscribe_to_state_changes, get_state_changes

# Subscribe to state changes
subscription_id = subscribe_to_state_changes("demo_project_001")

# Later, check for changes
changes = get_state_changes(subscription_id)
for change in changes:
    print(f"Field {change['field']} changed from {change['old_value']} to {change['new_value']}")
```

### 3. Post-Block Memory Updates
The post-block memory updates feature allows agents to log information about blocked and unblocked states, providing a history of agent interactions and dependencies.

#### Key Components:
- **Module**: `app/modules/memory_block_writer.py`
- **Main Functions**:
  - `write_block_memory(block_data)`: Logs information when an agent is blocked
  - `write_unblock_memory(unblock_data)`: Logs information when an agent is unblocked

#### Usage Example:
```python
from app.modules.memory_block_writer import write_block_memory

# Log block memory when NOVA is blocked by HAL
write_block_memory({
    "project_id": "demo_project_001",
    "agent": "nova",
    "action": "blocked",
    "content": "NOVA agent blocked - HAL has not created initial files yet",
    "blocked_due_to": "hal",
    "unblock_condition": "initial_files_created"
})
```

### 4. Passive Reflection Engine
The passive reflection engine allows agents to re-evaluate tasks after being blocked, taking into account the updated project state.

#### Key Components:
- **Module**: `app/modules/passive_reflection.py`
- **Main Functions**:
  - `start_reflection(project_id, interval)`: Starts passive reflection for a project
  - `stop_reflection(project_id)`: Stops passive reflection for a project
  - `re_evaluate_task(project_id, agent_id, task)`: Re-evaluates a task for an agent after being unblocked

#### Usage Example:
```python
from app.modules.passive_reflection import start_reflection, re_evaluate_task

# Start reflection for a project
start_reflection("demo_project_001", interval=60)

# Re-evaluate a task after an agent is unblocked
task = {"original_task": "Create UI", "project_id": "demo_project_001"}
updated_task = re_evaluate_task("demo_project_001", "nova", task)
```

### 5. Intelligent Reset Flags
The intelligent reset flags feature allows for resetting agent state when needed, enabling recovery from errors or inconsistent states.

#### Key Components:
- **Module**: `app/modules/reset_flags.py`
- **Main Functions**:
  - `reset_agent_state(project_id, agent_id)`: Resets the state of a specific agent
  - `reset_project_state(project_id, full_reset)`: Resets the state of an entire project
  - `get_reset_status(project_id)`: Gets the reset status of a project

#### Usage Example:
```python
from app.modules.reset_flags import reset_agent_state, reset_project_state

# Reset state for a specific agent
reset_agent_state("demo_project_001", "hal")

# Reset state for an entire project (partial reset)
reset_project_state("demo_project_001", full_reset=False)
```

### 6. API Endpoints
The API endpoints provide a way to interact with the agent timing and synchronization features through HTTP requests.

#### Key Components:
- **Module**: `routes/reset_routes.py`
- **Endpoints**:
  - `POST /api/reset/agent`: Resets the state of a specific agent
  - `POST /api/reset/project`: Resets the state of an entire project
  - `GET /api/reset/status`: Gets the reset status of a project

#### Usage Example:
```bash
# Reset agent state
curl -X POST http://localhost:8000/api/reset/agent \
  -H "Content-Type: application/json" \
  -d '{"project_id": "demo_project_001", "agent_id": "hal"}'

# Reset project state
curl -X POST http://localhost:8000/api/reset/project \
  -H "Content-Type: application/json" \
  -d '{"project_id": "demo_project_001", "full_reset": false}'

# Get reset status
curl -X GET http://localhost:8000/api/reset/status?project_id=demo_project_001
```

## Integration with Agent Runner

All agent implementations in `app/modules/agent_runner.py` have been updated to integrate with the new features:

1. **HAL Agent**:
   - Checks project state before execution
   - Starts passive reflection for the project
   - Re-evaluates tasks after being unblocked

2. **NOVA Agent**:
   - Checks if HAL has created initial files
   - Registers as blocked if dependencies are not met
   - Re-evaluates tasks after being unblocked

3. **CRITIC Agent**:
   - Checks if NOVA has created UI files
   - Registers as blocked if dependencies are not met
   - Logs block memory with detailed information
   - Re-evaluates tasks after being unblocked

4. **ASH Agent**:
   - Checks if project is ready for deployment
   - Registers as blocked if project status is not ready
   - Logs block memory with detailed information
   - Re-evaluates tasks after being unblocked

## Testing

A comprehensive test script (`test_phase_6_1.py`) has been created to test all the implemented features. The script tests:

1. Agent retry flow
2. Project state watch
3. Memory block writer
4. Passive reflection engine
5. Intelligent reset flags

## Conclusion

The Phase 6.1 Agent Timing & Synchronization features provide a robust framework for agent coordination and synchronization in the personal AI agent system. These features enable agents to work together more effectively, recover from blocked states intelligently, and maintain consistent project state throughout the development process.
