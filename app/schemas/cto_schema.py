"""
CTO Agent Schema Definitions

This module defines the schemas for CTO agent requests and responses.
The CTO agent is responsible for auditing project memory, validating schema compliance,
and identifying potential issues in the system.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CTOAuditRequest(BaseModel):
    """
    Schema for CTO agent audit request.
    """
    project_id: str = Field(..., description="Unique identifier for the project to audit")
    tools: Optional[List[str]] = Field(
        default=["audit_memory", "validate_schema", "check_reflection"],
        description="List of tools to use for the audit"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_123",
                "tools": ["audit_memory", "validate_schema", "check_reflection"]
            }
        }

class CTOIssue(BaseModel):
    """
    Schema for an issue identified by the CTO agent.
    """
    issue_type: str = Field(..., description="Type of issue (schema_violations, weak_reflection, agent_shortfall)")
    details: Any = Field(..., description="Details about the issue")
    severity: Optional[str] = Field(
        default="warning", 
        description="Severity level of the issue (info, warning, error)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "issue_type": "schema_violations",
                "details": {"missing_fields": ["reflection", "action_plan"]},
                "severity": "warning"
            }
        }

class CTOAuditResult(BaseModel):
    """
    Schema for CTO agent audit result.
    """
    status: str = Field(..., description="Status of the audit (success, error)")
    project_id: str = Field(..., description="Project identifier that was audited")
    loop: int = Field(..., description="Current loop count for the project")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the audit"
    )
    issues_found: bool = Field(..., description="Whether any issues were found")
    issues: Dict[str, Any] = Field(
        default={},
        description="Dictionary of issues found during the audit"
    )
    summary: str = Field(..., description="Summary of the audit results")
    message: Optional[str] = Field(None, description="Error message if status is error")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "project_id": "proj_123",
                "loop": 5,
                "timestamp": "2025-04-24T18:42:37.123456",
                "issues_found": True,
                "issues": {
                    "schema_violations": {"missing_fields": ["reflection", "action_plan"]},
                    "weak_reflection": {"confidence": 0.3}
                },
                "summary": "CTO audit after loop 5: issues found"
            }
        }

class CTOErrorResult(BaseModel):
    """
    Schema for CTO agent error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    project_id: Optional[str] = Field(None, description="Project identifier if applicable")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
