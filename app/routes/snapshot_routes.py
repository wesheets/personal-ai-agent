"""
Snapshot Routes

This module provides API routes for loop-level snapshot and rewind functionality,
enabling recovery from incomplete agent chains, failed routes, or memory corruption.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import traceback

# Import schemas
from app.schemas.loop_snapshot_schema import (
    LoopSnapshot,
    SnapshotSaveRequest,
    SnapshotRestoreRequest,
    SnapshotResponse
)

# Import snapshot manager
from app.utils.snapshot_manager import (
    save_snapshot,
    load_snapshot,
    list_snapshots,
    delete_snapshot,
    get_memory_state
)

# Import manifest manager if available
try:
    from app.utils.manifest_manager import register_route
    manifest_available = True
except ImportError:
    manifest_available = False
    logging.warning("⚠️ Manifest manager not available, routes will not be registered")

# Configure logging
logger = logging.getLogger("app.routes.snapshot_routes")

# Create router
router = APIRouter(tags=["loop_snapshot"])

# Register routes with manifest if available
if manifest_available:
    try:
        register_route("/loop/snapshot/save", "POST", "SnapshotSaveRequest", "active")
        register_route("/loop/snapshot/restore", "POST", "SnapshotRestoreRequest", "active")
        register_route("/loop/snapshot/list", "GET", "None", "active")
        logging.info("✅ Snapshot routes registered with manifest")
    except Exception as e:
        logging.error(f"❌ Failed to register snapshot routes with manifest: {str(e)}")

@router.post("/loop/snapshot/save", response_model=SnapshotResponse)
async def save_loop_snapshot(request: SnapshotSaveRequest):
    """
    Save a snapshot of the current loop state.
    
    This endpoint captures the current state of a loop, including memory state
    and agent sequence, allowing for later recovery if needed.
    """
    try:
        # Get the current memory state for the loop
        memory_state = await get_memory_state(request.loop_id)
        
        # Get agent sequence (simplified for now)
        # In a real implementation, this would come from the orchestrator
        agent_sequence = memory_state.get("agent_sequence", ["hal", "critic", "orchestrator"])
        
        # Save the snapshot
        success = await save_snapshot(
            loop_id=request.loop_id,
            memory_state=memory_state,
            agents=agent_sequence,
            notes=request.notes or ""
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save snapshot")
        
        # Return success response
        return SnapshotResponse(
            status="success",
            loop_id=request.loop_id,
            timestamp=datetime.utcnow(),
            message="Snapshot saved successfully",
            snapshot_data=None
        )
    
    except Exception as e:
        logger.error(f"❌ Error saving snapshot: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error saving snapshot: {str(e)}")

@router.post("/loop/snapshot/restore", response_model=SnapshotResponse)
async def restore_loop_snapshot(request: SnapshotRestoreRequest):
    """
    Restore a loop from a previously saved snapshot.
    
    This endpoint loads a snapshot and returns the saved state,
    allowing the orchestrator to resume from a known-good point.
    """
    try:
        # Load the snapshot
        snapshot = await load_snapshot(request.loop_id)
        
        if not snapshot:
            raise HTTPException(status_code=404, detail=f"No snapshot found for loop {request.loop_id}")
        
        # Return the snapshot data
        return SnapshotResponse(
            status="success",
            loop_id=request.loop_id,
            timestamp=datetime.utcnow(),
            message="Snapshot restored successfully",
            snapshot_data=snapshot
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error(f"❌ Error restoring snapshot: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error restoring snapshot: {str(e)}")

@router.get("/loop/snapshot/list/{loop_id}")
async def list_loop_snapshots(loop_id: str):
    """
    List all snapshots for a loop.
    
    This endpoint returns metadata about available snapshots for a loop.
    """
    try:
        # Get the list of snapshots
        snapshots = await list_snapshots(loop_id)
        
        # Return the list
        return {
            "status": "success",
            "loop_id": loop_id,
            "snapshots": snapshots
        }
    
    except Exception as e:
        logger.error(f"❌ Error listing snapshots: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error listing snapshots: {str(e)}")

@router.delete("/loop/snapshot/{loop_id}")
async def delete_loop_snapshot(loop_id: str):
    """
    Delete a snapshot for a loop.
    
    This endpoint removes a previously saved snapshot.
    """
    try:
        # Delete the snapshot
        success = await delete_snapshot(loop_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete snapshot")
        
        # Return success response
        return {
            "status": "success",
            "loop_id": loop_id,
            "message": "Snapshot deleted successfully"
        }
    
    except Exception as e:
        logger.error(f"❌ Error deleting snapshot: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error deleting snapshot: {str(e)}")
