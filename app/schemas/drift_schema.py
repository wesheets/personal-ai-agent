"""
Drift Monitoring Schema Module

This module defines the data models for loop drift monitoring,
enabling detection of changes in loop outputs, agent behaviors, or schema versions.

memory_tag: phase3.0_sprint3_cognitive_loop_deepening
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

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
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
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

class DriftAutoHealRequest(BaseModel):
    """
    Schema for drift auto-healing requests.
    
    This schema defines the structure of requests to auto-heal drift
    in loop outputs or agent behaviors.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    agent: str = Field(..., description="Agent that produced the output")
    drift_log_id: Optional[str] = Field(None, description="ID of the drift log to heal")
    healing_strategy: str = Field("adaptive", description="Strategy for auto-healing")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters for healing")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_003",
                "agent": "hal",
                "drift_log_id": "drift_log_abc123",
                "healing_strategy": "adaptive",
                "parameters": {
                    "max_iterations": 3,
                    "convergence_threshold": 0.05
                }
            }
        }

class DriftAutoHealResponse(BaseModel):
    """
    Schema for drift auto-healing responses.
    
    This schema defines the structure of responses from the drift auto-healer,
    including the healing status and results.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
    """
    healing_id: str = Field(..., description="Unique identifier for the healing operation")
    status: str = Field(..., description="Status of the healing operation")
    loop_id: str = Field(..., description="Unique identifier for the loop")
    agent: str = Field(..., description="Agent that produced the output")
    healing_strategy: str = Field(..., description="Strategy used for auto-healing")
    started_at: str = Field(..., description="When the healing operation started")
    message: str = Field(..., description="Status message")
    
    class Config:
        schema_extra = {
            "example": {
                "healing_id": "heal_abc123",
                "status": "in_progress",
                "loop_id": "loop_003",
                "agent": "hal",
                "healing_strategy": "adaptive",
                "started_at": "2025-04-28T07:58:00Z",
                "message": "Auto-healing in progress, applying adaptive strategy"
            }
        }

class DriftLogEntry(BaseModel):
    """
    Schema for drift log entries.
    
    This schema defines the structure of individual drift log entries.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
    """
    log_id: str = Field(..., description="Unique identifier for the log entry")
    loop_id: str = Field(..., description="Unique identifier for the loop")
    agent: str = Field(..., description="Agent that produced the output")
    drift_score: float = Field(..., description="Quantified measure of drift")
    drift_detected: bool = Field(..., description="Whether drift was detected")
    timestamp: str = Field(..., description="When the drift was detected")
    healing_status: Optional[str] = Field(None, description="Status of any healing operations")
    
    class Config:
        schema_extra = {
            "example": {
                "log_id": "drift_log_abc123",
                "loop_id": "loop_003",
                "agent": "hal",
                "drift_score": 0.75,
                "drift_detected": True,
                "timestamp": "2025-04-28T07:45:00Z",
                "healing_status": "not_attempted"
            }
        }

class DriftLogResponse(BaseModel):
    """
    Schema for drift log responses.
    
    This schema defines the structure of responses from the drift log endpoint.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
    """
    status: str = Field(..., description="Status of the log retrieval")
    loop_id: Optional[str] = Field(None, description="Loop ID filter, if any")
    agent: Optional[str] = Field(None, description="Agent filter, if any")
    entries: List[DriftLogEntry] = Field(..., description="List of drift log entries")
    count: int = Field(..., description="Number of log entries")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "loop_id": "loop_003",
                "agent": None,
                "entries": [
                    {
                        "log_id": "drift_log_abc123",
                        "loop_id": "loop_003",
                        "agent": "hal",
                        "drift_score": 0.75,
                        "drift_detected": True,
                        "timestamp": "2025-04-28T07:45:00Z",
                        "healing_status": "not_attempted"
                    },
                    {
                        "log_id": "drift_log_def456",
                        "loop_id": "loop_003",
                        "agent": "critic",
                        "drift_score": 0.15,
                        "drift_detected": False,
                        "timestamp": "2025-04-28T07:46:00Z",
                        "healing_status": None
                    }
                ],
                "count": 2
            }
        }
