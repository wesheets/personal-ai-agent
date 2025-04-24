"""
Loop Snapshot Schema

This module defines the data models for loop-level snapshot and rewind functionality,
allowing Promethios to safely recover from incomplete agent chains, failed routes,
or memory corruption.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class LoopSnapshot(BaseModel):
    """
    Schema for loop snapshots.
    
    This schema defines the structure of snapshots that capture the state
    of a loop at a specific point in time, enabling recovery and rewind capabilities.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the snapshot was created")
    agent_sequence: List[str] = Field(..., description="Sequence of agents that have been executed or are planned")
    memory_state: Dict[str, Any] = Field(..., description="Memory state at the time of snapshot")
    notes: Optional[str] = Field(None, description="Optional notes about the snapshot context")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "insight_loop_saas",
                "timestamp": "2025-04-24T15:45:00.123456",
                "agent_sequence": ["hal", "critic", "orchestrator"],
                "memory_state": {
                    "build_task": "Create a React component for user onboarding",
                    "hal_build_task_response": "// React component code here"
                },
                "notes": "Snapshot taken after HAL completed code generation"
            }
        }

class SnapshotSaveRequest(BaseModel):
    """
    Schema for snapshot save requests.
    
    This schema defines the structure of requests to save a loop snapshot.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    notes: Optional[str] = Field(None, description="Optional notes about the snapshot context")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "insight_loop_saas",
                "notes": "After HAL completion"
            }
        }

class SnapshotRestoreRequest(BaseModel):
    """
    Schema for snapshot restore requests.
    
    This schema defines the structure of requests to restore a loop from a snapshot.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop to restore")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "insight_loop_saas"
            }
        }

class SnapshotResponse(BaseModel):
    """
    Schema for snapshot operation responses.
    
    This schema defines the structure of responses for snapshot operations.
    """
    status: str = Field(..., description="Status of the operation")
    loop_id: str = Field(..., description="Loop identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the operation was performed")
    message: str = Field(..., description="Description of the operation result")
    snapshot_data: Optional[LoopSnapshot] = Field(None, description="Snapshot data (for restore operations)")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "loop_id": "insight_loop_saas",
                "timestamp": "2025-04-24T15:45:00.123456",
                "message": "Snapshot saved successfully",
                "snapshot_data": None
            }
        }
