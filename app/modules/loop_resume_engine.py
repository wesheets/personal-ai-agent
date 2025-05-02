"""
Loop Resume Engine Module

This module provides functionality for saving and restoring loop snapshots,
allowing the system to recover from crashes, freezes, or operator interventions
mid-loop. It enables Promethios to restore the last known-good memory snapshot,
resume the loop from where it left off, or propose a clean re-init with memory diffs.
"""

from datetime import datetime
from typing import Dict, Any
import logging
import copy
import json

from app.modules.project_state import read_project_state, update_project_state, write_project_state

# Configure logging
logger = logging.getLogger("app.modules.loop_resume_engine")

def _sanitize_for_storage(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes data for storage by removing circular references.
    
    Args:
        data: The data to sanitize
        
    Returns:
        Dict with circular references removed
    """
    # Create a deep copy to avoid modifying the original
    sanitized = copy.deepcopy(data)
    
    # Remove potentially circular references
    if "loop_snapshots" in sanitized:
        del sanitized["loop_snapshots"]
    if "last_snapshot" in sanitized:
        del sanitized["last_snapshot"]
        
    # Ensure the data is JSON serializable
    try:
        json.dumps(sanitized)
    except (TypeError, OverflowError) as e:
        logger.warning(f"Data contains non-serializable values: {str(e)}")
        # Further sanitize by converting non-serializable values to strings
        sanitized = _make_serializable(sanitized)
    
    return sanitized

def _make_serializable(obj):
    """
    Recursively converts non-serializable values to strings.
    
    Args:
        obj: The object to make serializable
        
    Returns:
        JSON serializable object
    """
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        return str(obj)

def save_loop_snapshot(project_id: str) -> Dict[str, Any]:
    """
    Saves a snapshot of the current project state.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Dict containing the snapshot data
    """
    try:
        # Read current project state
        snapshot = read_project_state(project_id)
        
        # Sanitize snapshot to remove circular references
        sanitized_snapshot = _sanitize_for_storage(snapshot)
        
        # Create snapshot data
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "loop": sanitized_snapshot.get("loop_count", 0),
            "snapshot": sanitized_snapshot
        }
        
        # Get existing snapshots
        current_state = read_project_state(project_id)
        loop_snapshots = current_state.get("loop_snapshots", [])
        
        # Add new snapshot
        loop_snapshots.append(data)
        
        # Update project state with snapshot
        result = update_project_state(project_id, {
            "loop_snapshots": loop_snapshots,
            "last_snapshot": data
        })
        
        logger.info(f"Saved loop snapshot for project {project_id} at loop {data['loop']}")
        return data
    
    except Exception as e:
        error_msg = f"Error saving loop snapshot for project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def restore_last_snapshot(project_id: str) -> Dict[str, Any]:
    """
    Restores the project state from the last saved snapshot.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Read current project state
        current_state = read_project_state(project_id)
        
        # Check if there's a last snapshot
        last = current_state.get("last_snapshot")
        if not last:
            logger.warning(f"No snapshot available for project {project_id}")
            return {"status": "no snapshot available", "project_id": project_id}
        
        # Get the snapshot data and make a clean copy
        snapshot_data = copy.deepcopy(last["snapshot"])
        
        # Create a new state object with only the essential fields
        # This avoids circular references by not including the snapshot history
        new_state = {
            "project_id": project_id,
            "status": snapshot_data.get("status", "active"),
            "files_created": snapshot_data.get("files_created", []),
            "agents_involved": snapshot_data.get("agents_involved", []),
            "latest_agent_action": snapshot_data.get("latest_agent_action"),
            "next_recommended_step": snapshot_data.get("next_recommended_step"),
            "tool_usage": snapshot_data.get("tool_usage", {}),
            "timestamp": datetime.utcnow().isoformat(),
            "last_updated_at": datetime.utcnow().isoformat(),
            "last_agent_triggered_at": snapshot_data.get("last_agent_triggered_at"),
            "loop_status": snapshot_data.get("loop_status", "running"),
            "loop_count": snapshot_data.get("loop_count", 0),
            "max_loops": snapshot_data.get("max_loops", 5),
            "last_completed_agent": snapshot_data.get("last_completed_agent"),
            "completed_steps": snapshot_data.get("completed_steps", []).copy(),  # Ensure we get a clean copy
            "loop_complete": snapshot_data.get("loop_complete", False),
            "agents": snapshot_data.get("agents", {}),
            "task_log": snapshot_data.get("task_log", []),
            "logic_modules": snapshot_data.get("logic_modules", {}),
            "registry": snapshot_data.get("registry", {})
        }
        
        # Preserve the snapshot history
        new_state["loop_snapshots"] = current_state.get("loop_snapshots", [])
        new_state["last_snapshot"] = last
        
        # Write the restored state directly using write_project_state instead of update_project_state
        # This ensures we completely replace the current state rather than merging with it
        result = write_project_state(project_id, new_state)
        
        logger.info(f"Restored project {project_id} to snapshot from {last['timestamp']} at loop {last['loop']}")
        return {
            "status": "restored", 
            "timestamp": last["timestamp"], 
            "loop": last["loop"],
            "project_id": project_id
        }
    
    except Exception as e:
        error_msg = f"Error restoring snapshot for project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def get_snapshot_history(project_id: str) -> Dict[str, Any]:
    """
    Gets the snapshot history for a project.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Dict containing the snapshot history
    """
    try:
        # Read current project state
        state = read_project_state(project_id)
        
        # Get snapshots
        snapshots = state.get("loop_snapshots", [])
        
        # Create summary data
        summary = []
        for snapshot in snapshots:
            summary.append({
                "timestamp": snapshot["timestamp"],
                "loop": snapshot["loop"],
                "agents_completed": snapshot["snapshot"].get("completed_steps", [])
            })
        
        return {
            "project_id": project_id,
            "snapshot_count": len(snapshots),
            "snapshots": summary,
            "has_last_snapshot": "last_snapshot" in state
        }
    
    except Exception as e:
        error_msg = f"Error getting snapshot history for project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e)
        }

def prompt_for_snapshot_restore(project_id: str, reason: str = "timeout") -> Dict[str, Any]:
    """
    Creates a prompt for the operator to restore from a snapshot.
    
    Args:
        project_id: The ID of the project
        reason: The reason for the prompt (e.g., "timeout", "crash", "operator_request")
        
    Returns:
        Dict containing the prompt data
    """
    try:
        # Read current project state
        state = read_project_state(project_id)
        
        # Check if there's a last snapshot
        last = state.get("last_snapshot")
        if not last:
            return {
                "status": "no snapshot available",
                "project_id": project_id,
                "prompt_required": False
            }
        
        # Create prompt data
        prompt = {
            "type": "snapshot_restore_prompt",
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "project_id": project_id,
            "last_snapshot": {
                "timestamp": last["timestamp"],
                "loop": last["loop"]
            },
            "current_loop": state.get("loop_count", 0),
            "prompt_required": True,
            "message": f"Loop has stalled due to {reason}. Restore from last snapshot at loop {last['loop']}?"
        }
        
        # Update project state with prompt
        result = update_project_state(project_id, {
            "restore_prompt": prompt
        })
        
        logger.info(f"Created snapshot restore prompt for project {project_id} due to {reason}")
        return prompt
    
    except Exception as e:
        error_msg = f"Error creating snapshot restore prompt for project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e),
            "prompt_required": False
        }

def auto_restore_if_configured(project_id: str, reason: str = "timeout") -> Dict[str, Any]:
    """
    Automatically restores from the last snapshot if loop_autoresume is enabled.
    
    Args:
        project_id: The ID of the project
        reason: The reason for the auto-restore (e.g., "timeout", "crash")
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Read current project state
        state = read_project_state(project_id)
        
        # Check if auto-resume is enabled
        if not state.get("loop_autoresume", False):
            # Create a prompt instead
            return prompt_for_snapshot_restore(project_id, reason)
        
        # Auto-restore from last snapshot
        result = restore_last_snapshot(project_id)
        
        if result["status"] == "restored":
            logger.info(f"Auto-restored project {project_id} from snapshot due to {reason}")
            
            # Add auto-restore event to project state
            update_project_state(project_id, {
                "auto_restore_events": state.get("auto_restore_events", []) + [{
                    "timestamp": datetime.utcnow().isoformat(),
                    "reason": reason,
                    "restored_to_loop": result["loop"]
                }]
            })
        
        return {
            "status": result["status"],
            "auto_restored": result["status"] == "restored",
            "reason": reason,
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat(),
            **result
        }
    
    except Exception as e:
        error_msg = f"Error in auto-restore for project {project_id}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "error": str(e),
            "auto_restored": False
        }
