"""
Snapshot Manager Utility

This module provides utilities for saving and loading loop snapshots,
enabling recovery from incomplete agent chains, failed routes, or memory corruption.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import memory operations
try:
    from app.api.modules.memory import write_memory, read_memory
except ImportError:
    logging.warning("⚠️ Could not import memory operations, using mock implementations")
    # Mock implementations for testing
    async def write_memory(project_id, tag, value):
        return {"status": "success", "message": "Mock write successful"}
    
    async def read_memory(project_id, tag):
        return None

# Import schemas
try:
    from app.schemas.loop_snapshot_schema import LoopSnapshot
except ImportError:
    logging.warning("⚠️ Could not import LoopSnapshot schema, using fallback")
    # Fallback implementation
    class LoopSnapshot:
        def __init__(self, loop_id, timestamp, agent_sequence, memory_state, notes=None):
            self.loop_id = loop_id
            self.timestamp = timestamp
            self.agent_sequence = agent_sequence
            self.memory_state = memory_state
            self.notes = notes

# Configure logging
logger = logging.getLogger("app.utils.snapshot_manager")

async def save_snapshot(loop_id: str, memory_state: Dict[str, Any], agents: List[str], notes: str = "") -> bool:
    """
    Save a snapshot of the current loop state.
    
    Args:
        loop_id: Unique identifier for the loop
        memory_state: Current memory state to save
        agents: Sequence of agents that have been executed or are planned
        notes: Optional notes about the snapshot context
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        # Create snapshot object
        snapshot = LoopSnapshot(
            loop_id=loop_id,
            timestamp=datetime.utcnow(),
            agent_sequence=agents,
            memory_state=memory_state,
            notes=notes
        )
        
        # Convert to dictionary for storage
        snapshot_dict = snapshot.dict() if hasattr(snapshot, 'dict') else vars(snapshot)
        
        # Store in memory under the loop snapshot tag
        memory_tag = f"loop_snapshot_{loop_id}"
        result = await write_memory(loop_id, memory_tag, snapshot_dict)
        
        # Log the operation
        if result and result.get("status") == "success":
            logger.info(f"✅ Snapshot saved for loop {loop_id}")
            return True
        else:
            logger.error(f"❌ Failed to save snapshot for loop {loop_id}: {result}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error saving snapshot: {str(e)}")
        return False

async def create_recovery_snapshot(loop_id: str, notes: str = "Auto-created recovery point") -> Dict[str, Any]:
    """
    Create a recovery snapshot before a potentially risky operation.
    
    Args:
        loop_id: Unique identifier for the loop
        notes: Notes about the snapshot context
        
    Returns:
        Dictionary containing the result of the snapshot operation
    """
    try:
        # Get current memory state
        memory_state = await get_memory_state(loop_id)
        
        # Get agent sequence (simplified for now)
        agent_sequence = memory_state.get("agent_sequence", ["hal", "critic", "orchestrator", "forge"])
        
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

async def load_snapshot(loop_id: str) -> Optional[LoopSnapshot]:
    """
    Load the most recent snapshot for a loop.
    
    Args:
        loop_id: Unique identifier for the loop
        
    Returns:
        LoopSnapshot object if found, None otherwise
    """
    try:
        # Read from memory
        memory_tag = f"loop_snapshot_{loop_id}"
        snapshot_dict = await read_memory(loop_id, memory_tag)
        
        if not snapshot_dict:
            logger.warning(f"⚠️ No snapshot found for loop {loop_id}")
            return None
        
        # Convert timestamp string to datetime if needed
        if isinstance(snapshot_dict.get("timestamp"), str):
            try:
                snapshot_dict["timestamp"] = datetime.fromisoformat(snapshot_dict["timestamp"])
            except ValueError:
                snapshot_dict["timestamp"] = datetime.utcnow()
        
        # Create LoopSnapshot object
        try:
            # Try to use the Pydantic model if available
            snapshot = LoopSnapshot(**snapshot_dict)
        except TypeError:
            # Fallback to manual object creation
            snapshot = LoopSnapshot(
                loop_id=snapshot_dict.get("loop_id"),
                timestamp=snapshot_dict.get("timestamp", datetime.utcnow()),
                agent_sequence=snapshot_dict.get("agent_sequence", []),
                memory_state=snapshot_dict.get("memory_state", {}),
                notes=snapshot_dict.get("notes")
            )
        
        logger.info(f"✅ Snapshot loaded for loop {loop_id}")
        return snapshot
    
    except Exception as e:
        logger.error(f"❌ Error loading snapshot: {str(e)}")
        return None

async def list_snapshots(loop_id: str) -> List[Dict[str, Any]]:
    """
    List all snapshots for a loop.
    
    Args:
        loop_id: Unique identifier for the loop
        
    Returns:
        List of snapshot metadata (without full memory state)
    """
    try:
        # For now, we only support one snapshot per loop
        # This could be extended to support multiple snapshots with versioning
        memory_tag = f"loop_snapshot_{loop_id}"
        snapshot_dict = await read_memory(loop_id, memory_tag)
        
        if not snapshot_dict:
            return []
        
        # Return metadata without full memory state to reduce payload size
        metadata = {
            "loop_id": snapshot_dict.get("loop_id"),
            "timestamp": snapshot_dict.get("timestamp"),
            "agent_sequence": snapshot_dict.get("agent_sequence", []),
            "notes": snapshot_dict.get("notes"),
            "memory_keys": list(snapshot_dict.get("memory_state", {}).keys())
        }
        
        return [metadata]
    
    except Exception as e:
        logger.error(f"❌ Error listing snapshots: {str(e)}")
        return []

async def delete_snapshot(loop_id: str) -> bool:
    """
    Delete a snapshot for a loop.
    
    Args:
        loop_id: Unique identifier for the loop
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        # Write empty value to effectively delete
        memory_tag = f"loop_snapshot_{loop_id}"
        result = await write_memory(loop_id, memory_tag, None)
        
        # Log the operation
        if result and result.get("status") == "success":
            logger.info(f"✅ Snapshot deleted for loop {loop_id}")
            return True
        else:
            logger.error(f"❌ Failed to delete snapshot for loop {loop_id}: {result}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error deleting snapshot: {str(e)}")
        return False

async def get_loop_snapshot(loop_id: str) -> Dict[str, Any]:
    """
    Get a snapshot of the current loop state.
    This is a wrapper around load_snapshot that returns a dictionary format
    suitable for debug analysis.
    
    Args:
        loop_id: The ID of the loop to get a snapshot for
        
    Returns:
        Dictionary containing the loop snapshot data
    """
    snapshot = await load_snapshot(loop_id)
    if not snapshot:
        return {
            "loop_id": loop_id,
            "status": "not_found",
            "timestamp": datetime.now().isoformat(),
            "error": "No snapshot found for this loop ID"
        }
    
    return {
        "loop_id": loop_id,
        "status": "success",
        "timestamp": snapshot.timestamp,
        "agent_sequence": snapshot.agent_sequence,
        "memory_state": snapshot.memory_state,
        "notes": snapshot.notes
    }

async def get_memory_state(loop_id: str) -> Dict[str, Any]:
    """
    Get the current memory state for a loop.
    
    This is a helper function to collect all memory entries for a loop
    to create a comprehensive snapshot.
    
    Args:
        loop_id: Unique identifier for the loop
        
    Returns:
        Dictionary containing all memory entries for the loop
    """
    try:
        # This is a simplified implementation
        # In a real system, you would query all memory entries for the loop
        # For now, we'll return a basic structure with key memory tags
        
        # Common memory tags to check
        memory_tags = [
            "build_task",
            "hal_build_task_response",
            "critic_feedback",
            "orchestrator_plan",
            "agent_sequence",
            "loop_status"
        ]
        
        memory_state = {}
        
        # Read each memory tag
        for tag in memory_tags:
            try:
                value = await read_memory(loop_id, tag)
                if value is not None:
                    memory_state[tag] = value
            except Exception as tag_error:
                logger.warning(f"⚠️ Could not read memory tag {tag}: {str(tag_error)}")
        
        return memory_state
    
    except Exception as e:
        logger.error(f"❌ Error getting memory state: {str(e)}")
        return {}
