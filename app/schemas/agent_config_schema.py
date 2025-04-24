"""
Agent Configuration Schema

This module defines the schemas for agent configuration endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class PermissionLevel(str, Enum):
    """Permission levels for agent operations."""
    READ_ONLY = "read_only"
    BASIC = "basic"
    STANDARD = "standard"
    ELEVATED = "elevated"
    ADMIN = "admin"


class ToolPermission(BaseModel):
    """Permission configuration for a specific tool."""
    tool_id: str = Field(..., description="Unique identifier for the tool")
    enabled: bool = Field(True, description="Whether the tool is enabled for the agent")
    permission_level: PermissionLevel = Field(
        PermissionLevel.STANDARD, 
        description="Permission level required to use this tool"
    )
    rate_limit: Optional[int] = Field(
        None, 
        description="Maximum number of calls allowed per minute (None for unlimited)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "tool_id": "memory_search",
                "enabled": True,
                "permission_level": "standard",
                "rate_limit": 10
            }
        }


class FallbackBehavior(BaseModel):
    """Configuration for agent fallback behavior."""
    retry_count: int = Field(3, description="Number of retries before fallback")
    fallback_agent: Optional[str] = Field(
        None, 
        description="Agent ID to fallback to on failure (None for no fallback)"
    )
    error_response_template: Optional[str] = Field(
        None, 
        description="Template for error responses"
    )
    log_failures: bool = Field(True, description="Whether to log failures")
    
    class Config:
        schema_extra = {
            "example": {
                "retry_count": 3,
                "fallback_agent": "MEMORY",
                "error_response_template": "I'm sorry, I couldn't complete that task. {error_message}",
                "log_failures": True
            }
        }


class AgentConfigRequest(BaseModel):
    """Request schema for agent configuration."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    permissions: List[ToolPermission] = Field(
        [], 
        description="List of tool permissions for the agent"
    )
    fallback_behavior: Optional[FallbackBehavior] = Field(
        None, 
        description="Fallback behavior configuration"
    )
    memory_access_level: PermissionLevel = Field(
        PermissionLevel.STANDARD, 
        description="Permission level for memory access"
    )
    custom_settings: Optional[Dict[str, Any]] = Field(
        None, 
        description="Custom agent-specific settings"
    )
    
    @validator('agent_id')
    def agent_id_must_be_uppercase(cls, v):
        if not v.isupper():
            raise ValueError('agent_id must be uppercase')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "ORCHESTRATOR",
                "permissions": [
                    {
                        "tool_id": "memory_search",
                        "enabled": True,
                        "permission_level": "standard",
                        "rate_limit": 10
                    },
                    {
                        "tool_id": "file_write",
                        "enabled": True,
                        "permission_level": "elevated",
                        "rate_limit": 5
                    }
                ],
                "fallback_behavior": {
                    "retry_count": 3,
                    "fallback_agent": "MEMORY",
                    "error_response_template": "I'm sorry, I couldn't complete that task. {error_message}",
                    "log_failures": True
                },
                "memory_access_level": "standard",
                "custom_settings": {
                    "max_loop_iterations": 5,
                    "timeout_seconds": 300
                }
            }
        }


class AgentConfigResponse(BaseModel):
    """Response schema for agent configuration."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    config_updated: bool = Field(..., description="Whether the configuration was updated")
    permissions_count: int = Field(..., description="Number of tool permissions configured")
    memory_access_level: PermissionLevel = Field(
        ..., 
        description="Permission level for memory access"
    )
    fallback_configured: bool = Field(..., description="Whether fallback behavior is configured")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the configuration update"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "ORCHESTRATOR",
                "config_updated": True,
                "permissions_count": 2,
                "memory_access_level": "standard",
                "fallback_configured": True,
                "timestamp": "2025-04-24T20:38:03Z",
                "version": "1.0.0"
            }
        }


class AgentConfigError(BaseModel):
    """Error response schema for agent configuration."""
    message: str = Field(..., description="Error message")
    agent_id: Optional[str] = Field(None, description="Agent ID if available")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Failed to update agent configuration: Invalid tool ID",
                "agent_id": "ORCHESTRATOR",
                "timestamp": "2025-04-24T20:38:03Z",
                "version": "1.0.0"
            }
        }


class AgentConfigGetRequest(BaseModel):
    """Request schema for getting agent configuration."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    
    @validator('agent_id')
    def agent_id_must_be_uppercase(cls, v):
        if not v.isupper():
            raise ValueError('agent_id must be uppercase')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "ORCHESTRATOR"
            }
        }


class AgentConfigGetResponse(BaseModel):
    """Response schema for getting agent configuration."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    permissions: List[ToolPermission] = Field(
        [], 
        description="List of tool permissions for the agent"
    )
    fallback_behavior: Optional[FallbackBehavior] = Field(
        None, 
        description="Fallback behavior configuration"
    )
    memory_access_level: PermissionLevel = Field(
        ..., 
        description="Permission level for memory access"
    )
    custom_settings: Dict[str, Any] = Field(
        {}, 
        description="Custom agent-specific settings"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the response"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "ORCHESTRATOR",
                "permissions": [
                    {
                        "tool_id": "memory_search",
                        "enabled": True,
                        "permission_level": "standard",
                        "rate_limit": 10
                    },
                    {
                        "tool_id": "file_write",
                        "enabled": True,
                        "permission_level": "elevated",
                        "rate_limit": 5
                    }
                ],
                "fallback_behavior": {
                    "retry_count": 3,
                    "fallback_agent": "MEMORY",
                    "error_response_template": "I'm sorry, I couldn't complete that task. {error_message}",
                    "log_failures": True
                },
                "memory_access_level": "standard",
                "custom_settings": {
                    "max_loop_iterations": 5,
                    "timeout_seconds": 300
                },
                "timestamp": "2025-04-24T20:38:03Z",
                "version": "1.0.0"
            }
        }
