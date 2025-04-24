"""
Output Policy Schema Module

This module defines the data models for output policy enforcement,
ensuring agents operate within system-wide constraints.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class OutputPolicyRequest(BaseModel):
    """
    Schema for output policy enforcement requests.
    
    This schema defines the structure of requests to validate
    agent outputs against system-wide constraints.
    """
    agent_id: str = Field(..., description="Unique identifier for the agent")
    output_type: str = Field(..., description="Type of output (e.g., 'text', 'code', 'comment')")
    content: str = Field(..., description="Content to be validated")
    context: Optional[str] = Field(None, description="Additional context for validation")
    loop_id: Optional[str] = Field(None, description="Loop ID for logging violations")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "hal",
                "output_type": "code",
                "content": "function calculateSum(a, b) { return a + b; }",
                "context": "JavaScript function to calculate sum of two numbers",
                "loop_id": "loop_12345"
            }
        }

class OutputPolicyResult(BaseModel):
    """
    Schema for output policy enforcement results.
    
    This schema defines the structure of responses from output
    policy enforcement, including whether the output was approved
    and any actions taken.
    """
    approved: bool = Field(..., description="Whether the output was approved")
    content: str = Field(..., description="Original or modified content")
    violation_type: Optional[str] = Field(None, description="Type of violation if not approved")
    reason: Optional[str] = Field(None, description="Reason for violation if not approved")
    action: str = Field(..., description="Action taken (e.g., 'allowed', 'blocked', 'rewritten')")
    risk_tags: Optional[List[str]] = Field(None, description="Tags indicating types of risk detected")
    risk_details: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed information about risks detected")
    checked_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="When the policy was checked")
    
    class Config:
        schema_extra = {
            "example": {
                "approved": True,
                "content": "function calculateSum(a, b) { return a + b; }",
                "violation_type": None,
                "reason": None,
                "action": "allowed",
                "risk_tags": [],
                "risk_details": [],
                "checked_at": "2025-04-24T16:38:00.000Z"
            }
        }

class PolicyLogEntry(BaseModel):
    """
    Schema for policy log entries.
    
    This schema defines the structure of log entries for policy
    enforcement, including details about the policy check and result.
    """
    agent_id: str = Field(..., description="Unique identifier for the agent")
    output_type: str = Field(..., description="Type of output")
    action: str = Field(..., description="Action taken")
    risk_tags: List[str] = Field(default_factory=list, description="Tags indicating types of risk detected")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="When the log entry was created")
    loop_id: Optional[str] = Field(None, description="Loop ID for the policy check")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "hal",
                "output_type": "code",
                "action": "allowed",
                "risk_tags": [],
                "timestamp": "2025-04-24T16:38:00.000Z",
                "loop_id": "loop_12345"
            }
        }

class PolicyLogRequest(BaseModel):
    """
    Schema for policy log requests.
    
    This schema defines the structure of requests to retrieve
    policy enforcement logs.
    """
    agent_id: Optional[str] = Field(None, description="Filter by agent ID")
    output_type: Optional[str] = Field(None, description="Filter by output type")
    action: Optional[str] = Field(None, description="Filter by action")
    limit: int = Field(10, description="Maximum number of log entries to return")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "hal",
                "output_type": "code",
                "action": "blocked",
                "limit": 10
            }
        }

class PolicyLogResponse(BaseModel):
    """
    Schema for policy log responses.
    
    This schema defines the structure of responses to policy
    log requests, including a list of log entries.
    """
    logs: List[PolicyLogEntry] = Field(default_factory=list, description="List of policy log entries")
    total: int = Field(..., description="Total number of log entries matching the request")
    
    class Config:
        schema_extra = {
            "example": {
                "logs": [
                    {
                        "agent_id": "hal",
                        "output_type": "code",
                        "action": "blocked",
                        "risk_tags": ["malicious"],
                        "timestamp": "2025-04-24T16:38:00.000Z",
                        "loop_id": "loop_12345"
                    }
                ],
                "total": 1
            }
        }
