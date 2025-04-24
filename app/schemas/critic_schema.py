"""
CRITIC Schema Module

This module defines the data models for CRITIC loop summary review and rejection,
enabling validation and accountability in the loop execution process.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class LoopSummaryReviewRequest(BaseModel):
    """
    Schema for loop summary review requests.
    
    This schema defines the structure of requests to the CRITIC agent
    for reviewing loop summaries and validating their integrity.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    agent: str = Field(..., description="Agent that produced the summary")
    output_tag: str = Field(..., description="Memory tag where the output is stored")
    schema_hash: Optional[str] = Field(None, description="Expected schema hash for validation")
    snapshot_id: Optional[str] = Field(None, description="Reference snapshot ID if available")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_003",
                "agent": "hal",
                "output_tag": "hal_build_task_response",
                "schema_hash": "a1b2c3d4e5f6",
                "snapshot_id": None
            }
        }

class LoopReflectionRejection(BaseModel):
    """
    Schema for loop reflection rejection responses.
    
    This schema defines the structure of rejection responses from the CRITIC agent
    when a loop summary fails validation checks.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    status: str = Field("rejected", description="Status of the review")
    reason: str = Field(..., description="Reason for rejection")
    recommendation: Optional[str] = Field(None, description="Recommended recovery action")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the rejection occurred")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_003",
                "status": "rejected",
                "reason": "Output from HAL did not match schema checksum",
                "recommendation": "Re-run HAL with fallback schema wrapping",
                "timestamp": "2025-04-24T16:04:00.123456"
            }
        }

class LoopReflectionApproval(BaseModel):
    """
    Schema for loop reflection approval responses.
    
    This schema defines the structure of approval responses from the CRITIC agent
    when a loop summary passes validation checks.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    status: str = Field("approved", description="Status of the review")
    message: str = Field(..., description="Approval message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the approval occurred")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_003",
                "status": "approved",
                "message": "HAL output validated successfully",
                "timestamp": "2025-04-24T16:04:00.123456"
            }
        }
