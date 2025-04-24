"""
Fix Schema

This module defines the schemas for the fix endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class FixType(str, Enum):
    """Types of fixes that can be applied."""
    SCHEMA = "schema"
    MEMORY = "memory"
    LOOP = "loop"
    AGENT = "agent"
    PERMISSION = "permission"
    CONFIGURATION = "configuration"
    CUSTOM = "custom"


class FixRequest(BaseModel):
    """Request schema for applying a fix."""
    fix_type: FixType = Field(
        ..., 
        description="Type of fix to apply"
    )
    target_id: str = Field(
        ..., 
        description="Identifier for the target to fix (e.g., loop_id, agent_id)"
    )
    description: str = Field(
        ..., 
        description="Description of the issue to fix"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional parameters for the fix"
    )
    force: bool = Field(
        False, 
        description="Whether to force the fix even if it might cause data loss"
    )
    agent_id: Optional[str] = Field(
        None, 
        description="Agent ID requesting the fix"
    )
    loop_id: Optional[str] = Field(
        None, 
        description="Loop ID associated with the fix"
    )
    
    @validator('target_id')
    def target_id_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('target_id must not be empty')
        return v
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('description must not be empty')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "fix_type": "schema",
                "target_id": "loop_12345",
                "description": "Fix missing required fields in loop schema",
                "parameters": {
                    "fields": ["status", "created_at"],
                    "repair_strategy": "add_defaults"
                },
                "force": False,
                "agent_id": "FIXER",
                "loop_id": "loop_12345"
            }
        }


class FixResponse(BaseModel):
    """Response schema for fix application."""
    fix_id: str = Field(..., description="Unique identifier for the fix")
    fix_type: FixType = Field(..., description="Type of fix applied")
    target_id: str = Field(..., description="Identifier for the target that was fixed")
    status: str = Field(..., description="Status of the fix (e.g., 'success', 'partial', 'failed')")
    changes_made: List[str] = Field(..., description="List of changes made by the fix")
    warnings: List[str] = Field(default_factory=list, description="List of warnings generated during the fix")
    backup_id: Optional[str] = Field(None, description="Identifier for the backup created before applying the fix")
    agent_id: Optional[str] = Field(None, description="Agent ID that requested the fix")
    loop_id: Optional[str] = Field(None, description="Loop ID associated with the fix")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the fix"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "fix_id": "fix_12345",
                "fix_type": "schema",
                "target_id": "loop_12345",
                "status": "success",
                "changes_made": [
                    "Added default status field with value 'pending'",
                    "Added default created_at field with current timestamp"
                ],
                "warnings": [
                    "Some dependent fields may need manual review"
                ],
                "backup_id": "backup_67890",
                "agent_id": "FIXER",
                "loop_id": "loop_12345",
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }


class FixError(BaseModel):
    """Error response schema for fix application."""
    message: str = Field(..., description="Error message")
    fix_type: Optional[FixType] = Field(None, description="Requested fix type if available")
    target_id: Optional[str] = Field(None, description="Requested target ID if available")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Failed to apply fix: Target not found",
                "fix_type": "schema",
                "target_id": "loop_12345",
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }


class FixStatusRequest(BaseModel):
    """Request schema for checking fix status."""
    fix_id: str = Field(..., description="Unique identifier for the fix")
    
    class Config:
        schema_extra = {
            "example": {
                "fix_id": "fix_12345"
            }
        }


class FixStatusResponse(BaseModel):
    """Response schema for fix status."""
    fix_id: str = Field(..., description="Unique identifier for the fix")
    fix_type: FixType = Field(..., description="Type of fix")
    target_id: str = Field(..., description="Identifier for the target")
    status: str = Field(..., description="Status of the fix (e.g., 'pending', 'in_progress', 'success', 'failed')")
    progress: Optional[float] = Field(None, description="Fix progress as a percentage")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time (ISO format)")
    changes_made: Optional[List[str]] = Field(None, description="List of changes made by the fix if completed")
    warnings: Optional[List[str]] = Field(None, description="List of warnings generated during the fix if completed")
    error_message: Optional[str] = Field(None, description="Error message if fix failed")
    backup_id: Optional[str] = Field(None, description="Identifier for the backup created before applying the fix")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the status check"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "fix_id": "fix_12345",
                "fix_type": "schema",
                "target_id": "loop_12345",
                "status": "in_progress",
                "progress": 65.0,
                "estimated_completion": "2025-04-24T21:05:00Z",
                "changes_made": None,
                "warnings": None,
                "error_message": None,
                "backup_id": "backup_67890",
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }


class FixRollbackRequest(BaseModel):
    """Request schema for rolling back a fix."""
    fix_id: str = Field(..., description="Unique identifier for the fix to roll back")
    reason: Optional[str] = Field(None, description="Reason for rolling back the fix")
    
    class Config:
        schema_extra = {
            "example": {
                "fix_id": "fix_12345",
                "reason": "Fix caused unexpected side effects"
            }
        }


class FixRollbackResponse(BaseModel):
    """Response schema for fix rollback."""
    fix_id: str = Field(..., description="Unique identifier for the fix that was rolled back")
    rollback_id: str = Field(..., description="Unique identifier for the rollback operation")
    status: str = Field(..., description="Status of the rollback (e.g., 'success', 'partial', 'failed')")
    changes_reverted: List[str] = Field(..., description="List of changes that were reverted")
    warnings: List[str] = Field(default_factory=list, description="List of warnings generated during the rollback")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the rollback"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "fix_id": "fix_12345",
                "rollback_id": "rollback_67890",
                "status": "success",
                "changes_reverted": [
                    "Removed added status field",
                    "Removed added created_at field"
                ],
                "warnings": [
                    "Some dependent changes could not be reverted"
                ],
                "timestamp": "2025-04-24T21:10:00Z",
                "version": "1.0.0"
            }
        }
