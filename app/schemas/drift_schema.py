"""
Drift Monitoring Schema Module

This module defines the data models for loop drift monitoring,
enabling detection of changes in loop outputs, agent behaviors, or schema versions.

memory_tag: phase3.0_sprint2_reflection_drift_plan_activation
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class DriftMonitorRequest(BaseModel):
    """
    Schema for drift monitoring requests.
    
    This schema defines the structure of requests to monitor drift
    between previous and current loop outputs.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    agent: str = Field(..., description="Agent that produced the output")
    current_output_tag: str = Field(..., description="Memory tag where the current output is stored")
    previous_output_tag: Optional[str] = Field(None, description="Memory tag where the previous output is stored")
    snapshot_id: Optional[str] = Field(None, description="Reference snapshot ID for comparison")
    threshold: Optional[float] = Field(0.25, description="Threshold for drift detection")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_003",
                "agent": "hal",
                "current_output_tag": "hal_build_task_response",
                "previous_output_tag": "hal_build_task_response_previous",
                "snapshot_id": None,
                "threshold": 0.25
            }
        }

class LoopDriftLog(BaseModel):
    """
    Schema for loop drift log responses.
    
    This schema defines the structure of drift monitoring results,
    including drift detection and scoring.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    agent: str = Field(..., description="Agent that produced the output")
    snapshot_id: Optional[str] = Field(None, description="Reference snapshot ID for comparison")
    previous_checksum: str = Field(..., description="Checksum of the previous output")
    current_checksum: str = Field(..., description="Checksum of the current output")
    drift_detected: bool = Field(..., description="Whether drift was detected")
    drift_score: Optional[float] = Field(None, description="Quantified measure of drift")
    explanation: Optional[str] = Field(None, description="Explanation of the drift detection")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the drift was detected")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_003",
                "agent": "hal",
                "snapshot_id": None,
                "previous_checksum": "a1b2c3d4e5f6",
                "current_checksum": "f6e5d4c3b2a1",
                "drift_detected": True,
                "drift_score": 0.75,
                "explanation": "Significant changes detected in output structure and content",
                "timestamp": "2025-04-24T16:15:00.123456"
            }
        }

class DriftMonitorResponse(BaseModel):
    """
    Schema for drift monitoring responses.
    
    This schema defines the structure of responses from the drift monitor,
    including the drift log and any recommended actions.
    """
    status: str = Field(..., description="Status of the drift monitoring")
    drift_log: LoopDriftLog = Field(..., description="The drift log")
    recommended_action: Optional[str] = Field(None, description="Recommended action based on drift")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "drift_detected",
                "drift_log": {
                    "loop_id": "loop_003",
                    "agent": "hal",
                    "snapshot_id": None,
                    "previous_checksum": "a1b2c3d4e5f6",
                    "current_checksum": "f6e5d4c3b2a1",
                    "drift_detected": True,
                    "drift_score": 0.75,
                    "explanation": "Significant changes detected in output structure and content",
                    "timestamp": "2025-04-24T16:15:00.123456"
                },
                "recommended_action": "trigger_critic_review"
            }
        }
