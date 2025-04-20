# Snapshot-Based Loop Resume Engine Documentation

## Overview

The Snapshot-Based Loop Resume Engine provides a robust recovery mechanism for the Promethios system, enabling it to handle crashes, freezes, or operator interventions mid-loop. This feature allows the system to:

1. Restore the last known-good memory snapshot
2. Resume the loop from where it left off
3. Propose a clean re-initialization with memory diffs

This documentation covers the implementation details, usage examples, and integration points for the Loop Resume Engine.

## Components

### 1. Loop Resume Engine Module

The core functionality is implemented in `app/modules/loop_resume_engine.py`, which provides:

- **Snapshot Management**: Functions to save and restore snapshots of project state
- **Automatic Recovery**: Capability to automatically restore from snapshots when timeouts occur
- **Operator Prompts**: Interface for prompting operators about restoration options
- **History Tracking**: Functionality to track and retrieve snapshot history

### 2. Loop Monitor Integration

The Loop Resume Engine integrates with the existing Loop Monitor (`app/modules/loop_monitor.py`) to:

- Detect frozen agents that exceed their timeout thresholds
- Trigger automatic snapshot restoration when timeouts occur
- Save snapshots when agents complete execution

### 3. Debug Routes

The system exposes several API endpoints in `routes/debug_routes.py` for manual snapshot management:

- `/api/debug/loop/snapshot/save/{project_id}`: Manually save a snapshot
- `/api/debug/loop/snapshot/restore/{project_id}`: Restore from the last snapshot
- `/api/debug/loop/snapshot/history/{project_id}`: View snapshot history

## Key Functions

### Saving Snapshots

```python
def save_loop_snapshot(project_id: str) -> Dict[str, Any]:
    """
    Saves a snapshot of the current project state.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Dict containing the snapshot data
    """
```

This function:
- Reads the current project state
- Sanitizes it to remove circular references
- Creates a timestamped snapshot
- Adds it to the project's snapshot history
- Updates the project state with the new snapshot

### Restoring Snapshots

```python
def restore_last_snapshot(project_id: str) -> Dict[str, Any]:
    """
    Restores the project state from the last saved snapshot.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Dict containing the result of the operation
    """
```

This function:
- Reads the current project state
- Retrieves the last saved snapshot
- Creates a new state object with essential fields from the snapshot
- Preserves the snapshot history
- Writes the restored state to completely replace the current state

### Automatic Restoration

```python
def auto_restore_if_configured(project_id: str, reason: str = "timeout") -> Dict[str, Any]:
    """
    Automatically restores from the last snapshot if loop_autoresume is enabled.
    
    Args:
        project_id: The ID of the project
        reason: The reason for the auto-restore (e.g., "timeout", "crash")
        
    Returns:
        Dict containing the result of the operation
    """
```

This function:
- Checks if auto-resume is enabled for the project
- If enabled, automatically restores from the last snapshot
- If not enabled, creates a prompt for the operator
- Logs the auto-restore event in the project state

## Usage Examples

### Saving a Snapshot

Snapshots can be saved programmatically:

```python
from app.modules.loop_resume_engine import save_loop_snapshot

# Save a snapshot of the current project state
result = save_loop_snapshot("my_project_123")
print(f"Snapshot saved at loop {result['loop']}")
```

Or via the API endpoint:

```bash
curl -X GET "http://localhost:8000/api/debug/loop/snapshot/save/my_project_123"
```

### Restoring from a Snapshot

Snapshots can be restored programmatically:

```python
from app.modules.loop_resume_engine import restore_last_snapshot

# Restore from the last snapshot
result = restore_last_snapshot("my_project_123")
if result["status"] == "restored":
    print(f"Project restored to loop {result['loop']}")
else:
    print(f"Restoration failed: {result['message']}")
```

Or via the API endpoint:

```bash
curl -X GET "http://localhost:8000/api/debug/loop/snapshot/restore/my_project_123"
```

### Viewing Snapshot History

Snapshot history can be retrieved programmatically:

```python
from app.modules.loop_resume_engine import get_snapshot_history

# Get snapshot history
history = get_snapshot_history("my_project_123")
print(f"Project has {history['snapshot_count']} snapshots")
for snapshot in history['snapshots']:
    print(f"Loop {snapshot['loop']} at {snapshot['timestamp']}")
```

Or via the API endpoint:

```bash
curl -X GET "http://localhost:8000/api/debug/loop/snapshot/history/my_project_123"
```

## Integration with Loop Monitor

The Loop Resume Engine integrates with the Loop Monitor to automatically handle timeouts:

1. When the Loop Monitor detects a frozen agent, it calls `auto_restore_if_configured`
2. If auto-resume is enabled, the system automatically restores from the last snapshot
3. If auto-resume is disabled, the system creates a prompt for the operator

Additionally, the Loop Monitor saves snapshots when agents complete execution:

```python
def log_agent_complete_route(project_id: str, agent: str, status: str = "completed"):
    # Log agent execution complete
    result = log_agent_execution_complete(project_id, agent, status)
    
    # Save snapshot after agent completion
    if status == "completed":
        snapshot_result = save_snapshot_on_agent_complete(project_id, agent)
```

## Configuration

The Loop Resume Engine can be configured at the project level:

- **Auto-Resume**: Set `loop_autoresume` to `true` in the project state to enable automatic restoration
- **Snapshot Frequency**: By default, snapshots are saved when agents complete execution, but can also be saved manually

## Error Handling

The Loop Resume Engine includes comprehensive error handling:

- All functions catch and log exceptions
- Functions return error information in the result object
- The system preserves the snapshot history even when errors occur

## Security Considerations

- Snapshots are stored in the project state and are subject to the same security controls
- API endpoints for snapshot management are protected by the same authentication as other debug endpoints
- Snapshots do not contain sensitive information like API keys or credentials

## Performance Considerations

- Snapshots are sanitized to remove circular references and non-serializable values
- The system maintains a history of snapshots, which could grow large for long-running projects
- Consider implementing a cleanup mechanism for old snapshots in production environments

## Future Enhancements

Potential future enhancements for the Loop Resume Engine include:

1. **Snapshot Pruning**: Automatically remove old snapshots to prevent excessive memory usage
2. **Differential Snapshots**: Store only the differences between snapshots to reduce storage requirements
3. **Scheduled Snapshots**: Save snapshots at regular intervals rather than only when agents complete
4. **Snapshot Tagging**: Allow operators to tag snapshots with custom labels for easier identification
5. **Snapshot Comparison**: Provide tools to compare different snapshots to identify changes
6. **Snapshot Export/Import**: Allow snapshots to be exported and imported between environments

## Conclusion

The Snapshot-Based Loop Resume Engine provides a robust recovery mechanism for the Promethios system, enabling it to handle crashes, freezes, or operator interventions mid-loop. By automatically saving and restoring snapshots, the system can maintain continuity and recover from failures without losing progress.
