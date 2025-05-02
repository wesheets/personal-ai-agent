"""
GUARDIAN Agent Schema Definitions

This module defines the schemas for GUARDIAN agent requests and responses.
The GUARDIAN agent is responsible for handling escalations, system halts,
operator alerts, and rollback operations.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class GuardianAlertRequest(BaseModel):
    """
    Schema for GUARDIAN agent alert request.
    """
    alert_type: str = Field(
        ..., 
        description="Type of alert (security, performance, compliance, error)"
    )
    severity: str = Field(
        ..., 
        description="Severity level (low, medium, high, critical)"
    )
    loop_id: Optional[str] = Field(
        None, 
        description="Unique identifier for the loop if applicable"
    )
    project_id: Optional[str] = Field(
        None, 
        description="Project identifier if applicable"
    )
    description: str = Field(
        ..., 
        description="Detailed description of the alert"
    )
    tools: Optional[List[str]] = Field(
        default=["halt", "alert_operator", "rollback_loop", "raise_flag"],
        description="List of tools to use for the alert"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "alert_type": "security",
                "severity": "high",
                "loop_id": "loop_123",
                "project_id": "proj_456",
                "description": "Potential unauthorized access detected",
                "tools": ["halt", "alert_operator"]
            }
        }


class GuardianResponse(BaseModel):
    """
    Schema for GUARDIAN agent response.
    """
    status: str = Field(
        ..., 
        description="Status of the response (success, error, pending)"
    )
    alert_id: str = Field(
        ..., 
        description="Unique identifier for the alert"
    )
    alert_type: str = Field(
        ..., 
        description="Type of alert that was processed"
    )
    severity: str = Field(
        ..., 
        description="Severity level of the alert"
    )
    actions_taken: List[str] = Field(
        ..., 
        description="List of actions taken in response to the alert"
    )
    system_status: str = Field(
        ..., 
        description="Current status of the system (running, halted, degraded)"
    )
    operator_notified: bool = Field(
        ..., 
        description="Whether the operator was notified"
    )
    rollback_status: Optional[str] = Field(
        None, 
        description="Status of rollback operation if applicable"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the response"
    )
    message: Optional[str] = Field(
        None, 
        description="Additional message or error details"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "alert_id": "alert_789",
                "alert_type": "security",
                "severity": "high",
                "actions_taken": ["system_halt", "operator_notification"],
                "system_status": "halted",
                "operator_notified": True,
                "rollback_status": None,
                "timestamp": "2025-04-24T19:05:40Z",
                "message": "System halted successfully, awaiting operator intervention"
            }
        }


class GuardianRollbackRequest(BaseModel):
    """
    Schema for GUARDIAN agent rollback request.
    """
    loop_id: str = Field(
        ..., 
        description="Unique identifier for the loop to rollback"
    )
    reason: str = Field(
        ..., 
        description="Reason for the rollback"
    )
    rollback_to_step: Optional[int] = Field(
        None, 
        description="Specific step to rollback to, if applicable"
    )
    tools: Optional[List[str]] = Field(
        default=["rollback_loop"],
        description="List of tools to use for the rollback"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_123",
                "reason": "Critical error in step 3",
                "rollback_to_step": 2,
                "tools": ["rollback_loop"]
            }
        }


class GuardianRollbackResult(BaseModel):
    """
    Schema for GUARDIAN agent rollback result.
    """
    status: str = Field(
        ..., 
        description="Status of the rollback (success, error, pending)"
    )
    loop_id: str = Field(
        ..., 
        description="Unique identifier for the rolled back loop"
    )
    original_step: int = Field(
        ..., 
        description="Original step before rollback"
    )
    current_step: int = Field(
        ..., 
        description="Current step after rollback"
    )
    reason: str = Field(
        ..., 
        description="Reason for the rollback"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the rollback"
    )
    message: Optional[str] = Field(
        None, 
        description="Additional message or error details"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "loop_id": "loop_123",
                "original_step": 3,
                "current_step": 2,
                "reason": "Critical error in step 3",
                "timestamp": "2025-04-24T19:05:40Z",
                "message": "Loop successfully rolled back to step 2"
            }
        }


# Fallback schema for handling errors
class GuardianErrorResult(BaseModel):
    """
    Schema for GUARDIAN agent error result.
    """
    status: str = Field(
        "error", 
        description="Status of the operation"
    )
    message: str = Field(
        ..., 
        description="Error message"
    )
    alert_type: Optional[str] = Field(
        None, 
        description="Type of alert if applicable"
    )
    severity: Optional[str] = Field(
        None, 
        description="Severity level if applicable"
    )
    loop_id: Optional[str] = Field(
        None, 
        description="Loop identifier if applicable"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "message": "Failed to halt system: insufficient permissions",
                "alert_type": "security",
                "severity": "high",
                "loop_id": "loop_123",
                "timestamp": "2025-04-24T19:05:40Z"
            }
        }
