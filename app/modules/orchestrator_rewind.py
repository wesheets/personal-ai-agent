"""
Orchestrator Rewind Integration

This module extends the orchestrator with loop rewind capabilities,
allowing recovery from incomplete agent chains, failed routes, or memory corruption.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import snapshot manager
try:
    from app.utils.snapshot_manager import load_snapshot, save_snapshot, get_memory_state
    snapshot_available = True
except ImportError:
    snapshot_available = False
    logging.warning("⚠️ Snapshot manager not available, rewind functionality will be limited")

# Configure logging
logger = logging.getLogger("app.modules.orchestrator_rewind")

async def suggest_rewind_plan(
    loop_id: str,
    error_type: str,
    error_message: str,
    current_agent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Suggest a rewind plan when a loop encounters an error.
    
    Args:
        loop_id: Unique identifier for the loop
        error_type: Type of error encountered (e.g., "schema_mismatch", "agent_failure")
        error_message: Detailed error message
        current_agent: The agent that encountered the error
        
    Returns:
        Dictionary containing the rewind plan suggestion
    """
    if not snapshot_available:
        return {
            "can_rewind": False,
            "reason": "Snapshot functionality not available",
            "suggestion": "Restart the loop manually"
        }
    
    try:
        # Check if a snapshot exists for this loop
        snapshot = await load_snapshot(loop_id)
        
        if not snapshot:
            return {
                "can_rewind": False,
                "reason": "No snapshot available for this loop",
                "suggestion": "Create a snapshot before attempting risky operations",
                "action": "create_snapshot"
            }
        
        # Determine rewind strategy based on error type
        if error_type == "schema_mismatch":
            return {
                "can_rewind": True,
                "reason": "Schema mismatch detected",
                "suggestion": "Rewind to last known good state and retry with schema validation",
                "snapshot_timestamp": snapshot.timestamp.isoformat() if hasattr(snapshot.timestamp, "isoformat") else str(snapshot.timestamp),
                "action": "rewind_and_validate"
            }
        
        elif error_type == "agent_failure":
            # Find the previous agent in the sequence
            agent_sequence = snapshot.agent_sequence
            previous_agent = None
            
            if current_agent and current_agent in agent_sequence:
                current_index = agent_sequence.index(current_agent)
                if current_index > 0:
                    previous_agent = agent_sequence[current_index - 1]
            
            return {
                "can_rewind": True,
                "reason": f"Agent failure: {current_agent}",
                "suggestion": f"Rewind to state after {previous_agent or 'previous agent'} and retry with different parameters",
                "snapshot_timestamp": snapshot.timestamp.isoformat() if hasattr(snapshot.timestamp, "isoformat") else str(snapshot.timestamp),
                "previous_agent": previous_agent,
                "action": "rewind_and_retry"
            }
        
        elif error_type == "memory_corruption":
            return {
                "can_rewind": True,
                "reason": "Memory corruption detected",
                "suggestion": "Restore from last known good snapshot and validate memory integrity",
                "snapshot_timestamp": snapshot.timestamp.isoformat() if hasattr(snapshot.timestamp, "isoformat") else str(snapshot.timestamp),
                "action": "restore_and_validate"
            }
        
        else:
            return {
                "can_rewind": True,
                "reason": f"Unknown error: {error_type}",
                "suggestion": "Restore from last snapshot and retry operation",
                "snapshot_timestamp": snapshot.timestamp.isoformat() if hasattr(snapshot.timestamp, "isoformat") else str(snapshot.timestamp),
                "action": "restore_and_retry"
            }
    
    except Exception as e:
        logger.error(f"❌ Error suggesting rewind plan: {str(e)}")
        return {
            "can_rewind": False,
            "reason": f"Error analyzing rewind options: {str(e)}",
            "suggestion": "Restart the loop manually and create regular snapshots"
        }

async def execute_rewind(
    loop_id: str,
    action: str,
    authorized: bool = False
) -> Dict[str, Any]:
    """
    Execute a rewind operation if authorized.
    
    Args:
        loop_id: Unique identifier for the loop
        action: Rewind action to perform (e.g., "rewind_and_validate")
        authorized: Whether the rewind is authorized
        
    Returns:
        Dictionary containing the result of the rewind operation
    """
    if not snapshot_available:
        return {
            "status": "error",
            "message": "Snapshot functionality not available",
            "loop_id": loop_id
        }
    
    if not authorized:
        return {
            "status": "pending_authorization",
            "message": "Rewind operation requires authorization",
            "loop_id": loop_id,
            "action": action
        }
    
    try:
        # Load the snapshot
        snapshot = await load_snapshot(loop_id)
        
        if not snapshot:
            return {
                "status": "error",
                "message": "No snapshot available for this loop",
                "loop_id": loop_id
            }
        
        # Execute the appropriate action
        if action == "rewind_and_validate":
            # Restore memory state from snapshot
            memory_state = snapshot.memory_state
            
            # Add validation flag to memory
            memory_state["_rewind_validation_required"] = True
            
            # Log the operation
            logger.info(f"✅ Executed rewind_and_validate for loop {loop_id}")
            
            return {
                "status": "success",
                "message": "Rewound to last snapshot with validation flag",
                "loop_id": loop_id,
                "memory_state": memory_state,
                "agent_sequence": snapshot.agent_sequence
            }
        
        elif action == "rewind_and_retry":
            # Restore memory state from snapshot
            memory_state = snapshot.memory_state
            
            # Add retry flag to memory
            memory_state["_rewind_retry_required"] = True
            
            # Log the operation
            logger.info(f"✅ Executed rewind_and_retry for loop {loop_id}")
            
            return {
                "status": "success",
                "message": "Rewound to last snapshot with retry flag",
                "loop_id": loop_id,
                "memory_state": memory_state,
                "agent_sequence": snapshot.agent_sequence
            }
        
        elif action == "restore_and_validate":
            # Restore memory state from snapshot
            memory_state = snapshot.memory_state
            
            # Add memory validation flag
            memory_state["_memory_validation_required"] = True
            
            # Log the operation
            logger.info(f"✅ Executed restore_and_validate for loop {loop_id}")
            
            return {
                "status": "success",
                "message": "Restored from snapshot with memory validation flag",
                "loop_id": loop_id,
                "memory_state": memory_state,
                "agent_sequence": snapshot.agent_sequence
            }
        
        elif action == "restore_and_retry":
            # Restore memory state from snapshot
            memory_state = snapshot.memory_state
            
            # Log the operation
            logger.info(f"✅ Executed restore_and_retry for loop {loop_id}")
            
            return {
                "status": "success",
                "message": "Restored from snapshot for retry",
                "loop_id": loop_id,
                "memory_state": memory_state,
                "agent_sequence": snapshot.agent_sequence
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown rewind action: {action}",
                "loop_id": loop_id
            }
    
    except Exception as e:
        logger.error(f"❌ Error executing rewind: {str(e)}")
        return {
            "status": "error",
            "message": f"Error executing rewind: {str(e)}",
            "loop_id": loop_id
        }

async def create_recovery_snapshot(loop_id: str, notes: str = "Auto-created recovery point") -> Dict[str, Any]:
    """
    Create a recovery snapshot before a potentially risky operation.
    
    Args:
        loop_id: Unique identifier for the loop
        notes: Notes about the snapshot context
        
    Returns:
        Dictionary containing the result of the snapshot operation
    """
    if not snapshot_available:
        return {
            "status": "error",
            "message": "Snapshot functionality not available",
            "loop_id": loop_id
        }
    
    try:
        # Get current memory state
        memory_state = await get_memory_state(loop_id)
        
        # Get agent sequence (simplified for now)
        agent_sequence = memory_state.get("agent_sequence", ["hal", "critic", "orchestrator"])
        
        # Save the snapshot
        success = await save_snapshot(
            loop_id=loop_id,
            memory_state=memory_state,
            agents=agent_sequence,
            notes=notes
        )
        
        if success:
            logger.info(f"✅ Created recovery snapshot for loop {loop_id}")
            return {
                "status": "success",
                "message": "Recovery snapshot created successfully",
                "loop_id": loop_id
            }
        else:
            return {
                "status": "error",
                "message": "Failed to create recovery snapshot",
                "loop_id": loop_id
            }
    
    except Exception as e:
        logger.error(f"❌ Error creating recovery snapshot: {str(e)}")
        return {
            "status": "error",
            "message": f"Error creating recovery snapshot: {str(e)}",
            "loop_id": loop_id
        }
